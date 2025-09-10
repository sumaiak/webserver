import socket
import logging

host = ''
port = 8080

logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(1)

print(f"Listening on port {port}...")
logging.info("Server started on port %s", port)

while True:
    client, addr = s.accept()
    logging.info("Connection from %s:%s", addr[0], addr[1])

    try:
        request = client.recv(1024).decode(errors="ignore")
        if not request:
            response = "HTTP/1.1 400 Bad Request\r\n\r\n<h1>400 Bad Request</h1>"
            print("\n[REQUEST - EMPTY]")
            print("[RESPONSE]\n", response)
            logging.warning("Empty request → 400 Bad Request")
            logging.info("Response sent:\n%s", response)
            client.sendall(response.encode())
            continue

        logging.info("Raw request:\n%s", request)
        print("\n[REQUEST]\n", request)

        lines = request.splitlines()
        if not lines or len(lines[0].split()) != 3:
            response = "HTTP/1.1 400 Bad Request\r\n\r\n<h1>400 Bad Request</h1>"
            print("[RESPONSE]\n", response)
            logging.warning("Malformed request → 400 Bad Request")
            logging.info("Response sent:\n%s", response)
            client.sendall(response.encode())
            continue

        method, path, version = lines[0].split()
        logging.info("Method: %s, Path: %s", method, path)

        if path == "/bad":
            response = "HTTP/1.1 400 Bad Request\r\n\r\n<h1>400 Bad Request (demo)</h1>"
            print("[RESPONSE]\n", response)
            logging.warning("Demo endpoint → 400 Bad Request")
            logging.info("Response sent:\n%s", response)
            client.sendall(response.encode())
            continue

        if not version.startswith("HTTP/"):
            response = "HTTP/1.1 400 Bad Request\r\n\r\n<h1>400 Bad Request</h1>"
            print("[RESPONSE]\n", response)
            logging.warning("Bad HTTP version → 400 Bad Request")
            logging.info("Response sent:\n%s", response)
            client.sendall(response.encode())
            continue

        if path == '/':
            filename = 'index.html'
        else:
            filename = path.strip('/')

        try:
            with open(filename, 'r') as f:
                body = f.read()
            status = "200 OK"
            logging.info("Served file: %s → %s", filename, status)
        except FileNotFoundError:
            body = "<h1>404 Not Found</h1>"
            status = "404 Not Found"
            logging.warning("File not found: %s → %s", filename, status)

        response = (
            f"HTTP/1.1 {status}\r\n"
            f"Content-Type: text/html\r\n"
            f"Content-Length: {len(body.encode())}\r\n"
            f"\r\n"
            f"{body}"
        )

        print("[RESPONSE]\n", response)
        logging.info("Response sent:\n%s", response)
        client.sendall(response.encode())

    except Exception as e:
        logging.error("Unexpected error: %s", e)
        response = "HTTP/1.1 500 Internal Server Error\r\n\r\n<h1>500 Internal Server Error</h1>"
        print("[RESPONSE - ERROR]\n", response)
        logging.error("Response sent:\n%s", response)
        client.sendall(response.encode())

    finally:
        client.close()
