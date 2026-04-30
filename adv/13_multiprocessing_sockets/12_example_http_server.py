import socket
import threading
import os
import mimetypes
from pathlib import Path

mimetypes.init()
mimetypes.add_type('image/svg+xml', '.svg')
mimetypes.add_type('image/webp', '.webp')


def get_content_type(filepath):
    content_type, encoding = mimetypes.guess_type(filepath)
    if content_type is None:
        content_type = 'application/octet-stream'
    return content_type


def read_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"    Error reading file: {e}")
        return None


def handle_client(client_socket, client_address, www_dir):
    try:
        request_data = client_socket.recv(4096)
        if not request_data:
            return

        request_line = request_data.split(b'\r\n')[0].decode('utf-8', errors='ignore')
        parts = request_line.split()

        if len(parts) < 2:
            response = "HTTP/1.1 400 Bad Request\r\n\r\n"
            client_socket.send(response.encode())
            return

        method, path = parts[0], parts[1]

        print(f"\n[{client_address}] {method} {path}")

        if method not in ['GET', 'HEAD']:
            response = "HTTP/1.1 405 Method Not Allowed\r\nAllow: GET, HEAD\r\n\r\n"
            client_socket.send(response.encode())
            return

        if '..' in path or path.startswith('/..'):
            response = "HTTP/1.1 403 Forbidden\r\n\r\n"
            client_socket.send(response.encode())
            return

        if path == '/':
            filename = 'index.html'
        else:
            filename = path.lstrip('/')

        filepath = os.path.join(www_dir, filename)

        if not os.path.exists(filepath):
            error_body = "<h1>404 Not Found</h1><p>File not found</p>"
            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(error_body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
                f"{error_body}"
            )
            client_socket.send(response.encode())
            print(f"    404 Not Found: {filepath}")
            return

        if os.path.isdir(filepath):
            index_path = os.path.join(filepath, 'index.html')
            if os.path.exists(index_path):
                filepath = index_path
            else:
                error_body = "<h1>403 Forbidden</h1><p>Directory listing not allowed</p>"
                response = (
                    "HTTP/1.1 403 Forbidden\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    f"Content-Length: {len(error_body)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                    f"{error_body}"
                )
                client_socket.send(response.encode())
                print(f"    403 Forbidden: {filepath} is directory")
                return

        file_content = read_file(filepath)
        if file_content is None:
            error_body = "<h1>500 Internal Server Error</h1>"
            response = (
                "HTTP/1.1 500 Internal Server Error\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(error_body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
                f"{error_body}"
            )
            client_socket.send(response.encode())
            return

        content_type = get_content_type(filepath)

        response_header = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(file_content)}\r\n"
            "Cache-Control: no-cache\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        client_socket.send(response_header.encode())

        if method == 'GET':
            client_socket.send(file_content)

        print(f"    200 OK - {filepath} ({content_type})")

    except ConnectionResetError:
        print(f"    Client {client_address} disconnected")
    except Exception as e:
        print(f"    Error handling client {client_address}: {e}")
    finally:
        client_socket.close()


def start_server(host='127.0.0.1', port=8080, www_dir='www'):
    if not os.path.exists(www_dir):
        print(f"Error: Directory '{www_dir}' does not exist")
        return

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((host, port))
        server_socket.listen(10)

        print(f"Static HTTP Server Started")
        print(f"Address: http://{host}:{port}")
        print(f"Directory: {os.path.abspath(www_dir)}")
        print("Press Ctrl+C to stop")
        print("-" * 50)

        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address, www_dir)
            )
            client_thread.daemon = True
            client_thread.start()

    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()
        print("Socket closed")


if __name__ == "__main__":
    start_server(
        host='127.0.0.1',
        port=8080,
        www_dir='www'
    )