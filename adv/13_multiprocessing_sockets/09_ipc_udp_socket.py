# udp_echo_server.py
"""UDP echo server with multiprocessing"""

import multiprocessing
import socket
import time
import os


def udp_echo_server(host='127.0.0.1', port=12345):
    # Создаем UDP сокет
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))

    print(f"[UDP Server] Listening on {host}:{port}")
    print(f"[UDP Server] PID: {os.getpid()}")
    print(f"[UDP Server] Protocol: UDP (connectionless)")

    while True:
        try:
            # Получаем данные (UDP не требует accept)
            data, client_addr = server_socket.recvfrom(4096)

            print(f"[UDP Server] Received from {client_addr}: {data.decode()}")

            # Отправляем обратно тому же клиенту
            server_socket.sendto(data, client_addr)
            print(f"[UDP Server] Echoed to {client_addr}: {data.decode()}")

        except KeyboardInterrupt:
            print("\n[UDP Server] Shutting down...")
            break
        except Exception as e:
            print(f"[UDP Server] Error: {e}")

    server_socket.close()


def udp_client(host='127.0.0.1', port=12345, message="Hello, UDP!"):
    """UDP client that sends message and receives echo"""

    # Создаем UDP сокет
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Можно установить таймаут для ожидания ответа
    client_socket.settimeout(2)

    print(f"[UDP Client] Sending to {host}:{port}: {message}")

    # Отправляем (не нужно connect)
    client_socket.sendto(message.encode(), (host, port))

    try:
        response, server_addr = client_socket.recvfrom(4096)
        print(f"[UDP Client] Received from {server_addr}: {response.decode()}")
    except socket.timeout:
        print("[UDP Client] Timeout - no response received")

    client_socket.close()


if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 12345

    # Запускаем UDP сервер
    server = multiprocessing.Process(target=udp_echo_server, args=(HOST, PORT))
    server.start()

    time.sleep(0.5)  # Даем серверу время запуститься

    clients = []
    messages = ["Hello UDP!", "Message 2", "Keep coding!"]

    for i, msg in enumerate(messages):
        client = multiprocessing.Process(target=udp_client, args=(HOST, PORT, msg))
        clients.append(client)
        client.start()
        time.sleep(0.3)

    for client in clients:
        client.join()

    server.terminate()
    server.join()

    print("\n[Main] UDP Demo completed")