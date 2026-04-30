# Single producer single consumer каналы

import multiprocessing


def child_process(conn):
    """Child process: receives commands and sends responses"""
    while True:
        try:
            command = conn.recv()

            if command == "STOP":
                conn.send("ACK: Stopping")
                break
            elif command == "STATUS":
                conn.send("OK: Alive and processing")
            elif command.startswith("ECHO:"):
                message = command[5:]
                conn.send(f"ECHO BACK: {message}")
            else:
                conn.send(f"ERROR: Unknown command '{command}'")
        except EOFError:
            # Pipe was closed from the other end
            break


if __name__ == "__main__":
    parent_conn, child_conn = multiprocessing.Pipe()

    process = multiprocessing.Process(target=child_process, args=(child_conn,))
    process.start()

    commands = ["STATUS", "ECHO:Hello World", "INVALID_CMD", "STATUS", "STOP"]

    for cmd in commands:
        print(f"[PARENT] Sending: {cmd}")
        parent_conn.send(cmd)

        response = parent_conn.recv()
        print(f"[PARENT] Received: {response}")
        print("-" * 40)

    process.join()
    print("[PARENT] Done")