import socket
import logging
import datetime

host = ''
port = 8080

logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(message)s", 
)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(1)

print(f"Listening on port {port}...")
logging.info("Server started on port %s", port)

def apache_log(addr, request_line, status_code, size):
    """Write a log line in Apache Common Log Format."""
    ip = addr[0]
    now = datetime.datetime.utcnow().strftime("%d/%b/%Y:%H:%M:%S +0000")
    log_line = f'{ip} - - [{now}] "{request_line}" {status_code} {size}'
    logging.info(log_line)

while True:
    client, addr = s.accept()

    try:
        request = client.recv(1024).decode(errors="ignore")
        if not request:
            response = "HTTP/1.1 400 Bad Request\r\n\r\n<h1>400 Bad Request</h1>"
            client.sendall(response.encode())
            apache_log(addr, "-", 400, len(response.encode()))
            continue

        print("\n[REQUEST]\n", request)

        lines = request.splitlines()
        if not lines or len(lines[0].split()) != 3:
            response = "HTTP/1.1 400 Bad Request\r\n\r\n<h1>400 Bad Request</h1>"
            client.sendall(response.encode())
            apache_log(addr, lines[0] if lines else "-", 400, len(response.encode()))
            continue

        method, path, version = lines[0].split()

        if path == "/bad":
            response = "HTTP/1.1 400 Bad Request\r\n\r\n<h1>400 Bad Request (demo)</h1>"
            client.sendall(response.encode())
            apache_log(addr, lines[0], 400, len(response.encode()))
            continue

        if not version.startswith("HTTP/"):
            response = "HTTP/1.1 400 Bad Request\r\n\r\n<h1>400 Bad Request</h1>"
            client.sendall(response.encode())
            apache_log(addr, lines[0], 400, len(response.encode()))
            continue

        if path == '/':
            filename = 'index.html'
        else:
            filename = path.strip('/')

        try:
            with open(filename, 'r') as f:
                body = f.read()
            status = "200 OK"
            code = 200
        except FileNotFoundError:
            body = "<h1>404 Not Found</h1>"
            status = "404 Not Found"
            code = 404

        response = (
            f"HTTP/1.1 {status}\r\n"
            f"Content-Type: text/html\r\n"
            f"Content-Length: {len(body.encode())}\r\n"
            f"\r\n"
            f"{body}"
        )

        print("[RESPONSE]\n", response)
        client.sendall(response.encode())
        apache_log(addr, lines[0], code, len(body.encode()))

    except Exception as e:
        response = "HTTP/1.1 500 Internal Server Error\r\n\r\n<h1>500 Internal Server Error</h1>"
        client.sendall(response.encode())
        apache_log(addr, "-", 500, len(response.encode()))

    finally:
        client.close()

