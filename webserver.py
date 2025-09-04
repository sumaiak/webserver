import socket

# Create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = ''  # Listen on all interfaces
port = 8080
s.bind((host, port))
s.listen(1)
print(f"Listening on port {port}...")

while True:
    client, addr = s.accept()
    print("Connection from:", addr)

    try:
        # Receive request
        request = client.recv(1024).decode()
        print(request)

        # Parse HTTP request line
        request_line = request.splitlines()[0]  # e.g., "GET / HTTP/1.1"
        method, path, _ = request_line.split()
        print(f"Method: {method}, Path: {path}")

        # Determine file to serve
        if path == '/':
            filename = 'index.html'
        else:
            filename = path.strip('/')  # remove leading '/'

        # Try to open the file
        try:
            with open(filename, 'r') as f:
                body = f.read()
            status = "200 OK"
        except FileNotFoundError:
            body = "<h1>404 Not Found</h1><p>The file does not exist.</p>"
            status = "404 Not Found"
            print(f"File not found: {filename}")

        # Build full HTTP response
        response = (
            f"HTTP/1.1 {status}\r\n"
            f"Content-Type: text/html\r\n"
            f"Content-Length: {len(body.encode())}\r\n"
            f"\r\n"
            f"{body}"
        )

        client.sendall(response.encode())

    except Exception as e:
        print("Error handling request:", e)

    finally:
        client.close()
