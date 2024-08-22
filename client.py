import socket
import sys


def create_client_socket():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(1)
        return client_socket
    except Exception as e:
        print("ERROR: Socket creation failed")
        exit()


def send_request(client_socket, server_address, request_type):
    packet = create_request_packet(request_type)
    try:
        client_socket.sendto(packet, server_address)
        print(f"Request sent to {server_address[0]}:{server_address[1]}")
        response, _ = client_socket.recvfrom(1024)
        handle_response(response)
    except socket.timeout:
        print("ERROR: Receiving timed out")
    except Exception as e:
        print("ERROR: Receiving failed")


def create_request_packet(request_type):
    magic_no = (0x36FB).to_bytes(2, 'big')
    packet_type = (0x0001).to_bytes(2, 'big')
    request_type = (request_type).to_bytes(2, 'big')
    packet = bytearray()
    packet.extend(magic_no)
    packet.extend(packet_type)
    packet.extend(request_type)
    return packet


def handle_response(data):
    if len(data) < 13:
        print("ERROR: Packet is too small to be a DT_Response")
        return

    magic_no = int.from_bytes(data[:2], 'big')
    packet_type = int.from_bytes(data[2:4], 'big')

    if magic_no != 0x36FB:
        print("ERROR: Packet magic number is incorrect")
        return
    if packet_type != 0x0002:
        print("ERROR: Packet is not a DT_Response")
        return

    text_length = data[12]
    text = data[13:13 + text_length].decode('utf-8')
    print(f"Response received:\nText: {text}")


def main():
    if len(sys.argv) != 4:
        print("ERROR: Incorrect number of command line arguments")
        exit()

    request_type = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])

    if request_type not in ('date', 'time'):
        print(f"ERROR: Request type '{request_type}' is not valid")
        exit()

    request_type = 0x0001 if request_type == 'date' else 0x0002

    client_socket = create_client_socket()
    try:
        server_address = (host, port)
        send_request(client_socket, server_address, request_type)
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()