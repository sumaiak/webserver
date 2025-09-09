import socket, os

host = ''
port = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(1)

print(f"Listening on port {port}...")

while True:
    client, addr = s.accept()
    print("Connection from:", addr)

    try:
        request = client.recv(1024).decode()
        print(request)

        request_line = request.splitlines()[0]
        method, path, version = request_line.split()
        print(f"Method: {method}, Path: {path}")

        if path == '/':
            filename = 'index.html'
        else:
            filename = path.strip('/')

        try:
            with open(filename, 'r') as f:
                body = f.read()
            status = "200 OK"
        except FileNotFoundError:
            body = "<h1>404 Not Found</h1>"
            status = "404 Not Found"

        response = (
            f"HTTP/1.1 {status}\r\n"
            f"Content-Type: text/html\r\n"
            f"Content-Length: {len(body.encode())}\r\n"
            f"\r\n"
            f"{body}"
        )

        client.sendall(response.encode())

    except Exception as e:
        print("Error:", e)

    finally:
        client.close()
