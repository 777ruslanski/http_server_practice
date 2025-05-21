import socket
import json
import mimetypes

HOST = '127.0.0.1'
PORT = 8080

def send_request(method, path, body=None, headers={}):
    request_line = f"{method} {path} HTTP/1.1\r\n"
    headers["Host"] = f"{HOST}:{PORT}"
    headers["Content-Length"] = str(len(body)) if body else '0'
    request_headers = ''.join([f"{key}: {value}\r\n" for key, value in headers.items()])
    request = f"{request_line}{request_headers}\r\n{body if body else ''}"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(request.encode())

        response = s.recv(4096).decode()
        print(response)

def get(path):
    send_request("GET", path)

def post(path, body):
    send_request("POST", path, json.dumps(body), {"Content-Type": "application/json"})

def put(path, body):
    send_request("PUT", path, json.dumps(body), {"Content-Type": "application/json"})

def delete(path):
    send_request("DELETE", path)

def send_file(path, file_path):
    with open(file_path, 'rb') as file:
        file_data = file.read()
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{file_path}"\r\nContent-Type: {mimetypes.guess_type(file_path)[0]}\r\n\r\n'.encode() + file_data + f'\r\n--{boundary}--\r\n'.encode()
    send_request("POST", path, body, {"Content-Type": f"multipart/form-data; boundary={boundary}"})
