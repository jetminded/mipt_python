# uds_echo_server.py
"""Simple Unix Domain Socket echo server with multiprocessing"""

import multiprocessing
import socket
import os
import time


def uds_echo_server(socket_path):
    """UDS echo server - sends back whatever it receives"""

    # Remove old socket file if exists
    try:
        os.unlink(socket_path)
    except OSError:
        if os.path.exists(socket_path):
            print(f"[Server] Removing old socket: {socket_path}")
            os.remove(socket_path)

    # Create Unix Domain Socket
    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_socket.bind(socket_path)
    server_socket.listen(5)

    print(f"[Server] UDS echo server listening on: {socket_path}")
    print(f"[Server] Process PID: {multiprocessing.current_process().pid}")

    while True:
        # Wait for connection
        client_socket, _ = server_socket.accept()
        print(f"[Server] Client connected")

        # Receive and echo back
        data = client_socket.recv(1024)
        if data:
            print(f"[Server] Received: {data.decode()}")
            client_socket.send(data)  # Echo back
            print(f"[Server] Echoed: {data.decode()}")

        client_socket.close()
        print(f"[Server] Client disconnected")


def uds_echo_client(socket_path, message):
    """Client that sends message and receives echo"""
    time.sleep(0.5)  # Wait for server to start

    # Connect to Unix Domain Socket
    client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client_socket.connect(socket_path)

    print(f"[Client] Connected to {socket_path}")
    print(f"[Client] Sending: {message}")

    # Send message
    client_socket.send(message.encode())

    # Receive echo
    response = client_socket.recv(1024)
    print(f"[Client] Received echo: {response.decode()}")

    client_socket.close()


if __name__ == "__main__":
    SOCKET_PATH = "/tmp/my_uds_socket.sock"

    # Start server
    server = multiprocessing.Process(target=uds_echo_server, args=(SOCKET_PATH,))
    server.start()

    # Start client
    client = multiprocessing.Process(
        target=uds_echo_client,
        args=(SOCKET_PATH, "Hello, UDS Echo Server!")
    )
    client.start()

    client.join()

    # Stop server
    server.terminate()
    server.join()

    # Clean up socket file
    try:
        os.unlink(SOCKET_PATH)
    except OSError:
        pass

    print("[Main] Done")