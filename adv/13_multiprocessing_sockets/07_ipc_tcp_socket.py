# echo_server.py
"""Simple TCP echo server with multiprocessing"""

import multiprocessing
import socket
import time


def echo_server(port):
    """Echo server - sends back whatever it receives"""
    host = '127.0.0.1'

    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"[Server] Echo server running on {host}:{port}")
    print(f"[Server] Process PID: {multiprocessing.current_process().pid}")

    while True:
        # Wait for connection
        client_socket, client_addr = server_socket.accept()
        print(f"[Server] Client connected from {client_addr}")

        # Receive and echo back
        data = client_socket.recv(1024)
        if data:
            print(f"[Server] Received: {data.decode()}")
            client_socket.send(data)  # Echo back
            print(f"[Server] Echoed: {data.decode()}")

        client_socket.close()
        print(f"[Server] Client disconnected")


def echo_client(port, message):
    """Client that sends message and receives echo"""
    time.sleep(0.5)  # Wait for server to start

    host = '127.0.0.1'

    # Connect to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    print(f"[Client] Connected to {host}:{port}")
    print(f"[Client] Sending: {message}")

    # Send message
    client_socket.send(message.encode())

    # Receive echo
    response = client_socket.recv(1024)
    print(f"[Client] Received echo: {response.decode()}")

    client_socket.close()


if __name__ == "__main__":
    PORT = 12345

    # Start server
    server = multiprocessing.Process(target=echo_server, args=(PORT,))
    server.start()

    # Start client
    client = multiprocessing.Process(
        target=echo_client,
        args=(PORT, "Hello, Echo Server!")
    )
    client.start()

    client.join()

    # Stop server
    server.terminate()
    server.join()

    print("[Main] Done")