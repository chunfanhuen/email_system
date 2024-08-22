import socket
import select
from datetime import datetime


def create_server_socket(port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('localhost', port))
        print(f"Binding to port {port}")
        return server_socket
    except Exception as e:
        print("ERROR: Socket creation failed")
        exit()


def handle_request(data, addr, language_code):
    if len(data) != 6:
        print("ERROR: Packet length incorrect for a DT_Request, dropping packet")
        return None

    magic_no, packet_type, request_type = int.from_bytes(data[:2], 'big'), int.from_bytes(data[2:4],
                                                                                          'big'), int.from_bytes(
        data[4:], 'big')

    if magic_no != 0x36FB:
        print("ERROR: Packet magic number is incorrect, dropping packet")
        return None
    if packet_type != 0x0001:
        print("ERROR: Packet is not a DT_Request, dropping packet")
        return None
    if request_type not in (0x0001, 0x0002):
        print("ERROR: Packet has invalid type, dropping packet")
        return None

    now = datetime.now()
    if request_type == 0x0001:
        text = f"Today's date is {now.strftime('%B')} {now.day}, {now.year}"
    else:
        text = f"The current time is {now.strftime('%H:%M')}"

    response_packet = create_response_packet(language_code, now, text)
    return response_packet


def create_response_packet(language_code, now, text):
    magic_no = (0x36FB).to_bytes(2, 'big')
    packet_type = (0x0002).to_bytes(2, 'big')
    language_code = (language_code).to_bytes(2, 'big')
    year = (now.year).to_bytes(2, 'big')
    month = (now.month).to_bytes(1, 'big')
    day = (now.day).to_bytes(1, 'big')
    hour = (now.hour).to_bytes(1, 'big')
    minute = (now.minute).to_bytes(1, 'big')
    text_bytes = text.encode('utf-8')
    length = (len(text_bytes)).to_bytes(1, 'big')

    packet = bytearray()
    packet.extend(magic_no)
    packet.extend(packet_type)
    packet.extend(language_code)
    packet.extend(year)
    packet.extend(month)
    packet.extend(day)
    packet.extend(hour)
    packet.extend(minute)
    packet.extend(length)
    packet.extend(text_bytes)

    return packet


def main():
    english_port = 12345
    maori_port = 12346
    german_port = 12347

    sockets = [
        create_server_socket(english_port),
        create_server_socket(maori_port),
        create_server_socket(german_port)
    ]

    try:
        while True:
            print("Waiting for requests...")
            readable, _, _ = select.select(sockets, [], [])
            for s in readable:
                data, addr = s.recvfrom(1024)
                language_code = sockets.index(s) + 1
                response = handle_request(data, addr, language_code)
                if response:
                    s.sendto(response, addr)
                    print("Response sent")
    finally:
        for s in sockets:
            s.close()


if __name__ == "__main__":
    main()