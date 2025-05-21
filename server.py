import socket
import threading
import json
import os
import mimetypes
from urllib.parse import unquote
import uuid

HOST = '127.0.0.1'
PORT = 8080
STATIC_DIR = './static'
UPLOAD_DIR = './uploads'
resources = {}
lock = threading.Lock()

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

status_messages = {
    200: 'OK',
    201: 'Created',
    204: 'No Content',
    400: 'Bad Request',
    404: 'Not Found',
    405: 'Method Not Allowed',
    500: 'Internal Server Error'
}

def parse_multipart_form_data(body, boundary, content_type):
    parts = body.split(b'--' + boundary.encode())
    data = {}
    files = {}
    
    for part in parts[1:-1]:
        if b'\r\n\r\n' not in part:
            continue
            
        headers, content = part.split(b'\r\n\r\n', 1)
        headers = headers.split(b'\r\n')
        
        disposition = None
        content_type_part = None
        
        for header in headers:
            if header.startswith(b'Content-Disposition:'):
                disposition = header[len(b'Content-Disposition:'):].strip().decode()
            elif header.startswith(b'Content-Type:'):
                content_type_part = header[len(b'Content-Type:'):].strip().decode()
        
        if disposition and 'name=' in disposition:
            name_start = disposition.find('name="') + 6
            name_end = disposition.find('"', name_start)
            name = disposition[name_start:name_end]
            
            if 'filename="' in disposition:
                filename_start = disposition.find('filename="') + 10
                filename_end = disposition.find('"', filename_start)
                filename = disposition[filename_start:filename_end]
                
                file_ext = os.path.splitext(filename)[1]
                unique_filename = f"{uuid.uuid4()}{file_ext}"
                filepath = os.path.join(UPLOAD_DIR, unique_filename)
                
                with open(filepath, 'wb') as f:
                    f.write(content[:-2])
                
                files[name] = {
                    'filename': filename,
                    'content_type': content_type_part,
                    'path': f'/uploads/{unique_filename}'
                }
            else:
                data[name] = content[:-2].decode()
    
    return data, files

def handle_client(conn, addr):
    try:
        data = conn.recv(4096)
        if not data:
            return

        decoded_data = data.decode('utf-8', errors='ignore')
        if '\r\n\r\n' not in decoded_data:
            send_error(conn, 400)
            return

        headers_part, body = decoded_data.split('\r\n\r\n', 1)
        lines = headers_part.split('\r\n')
        
        try:
            request_line = lines[0]
            method, path, version = request_line.split()
            path = unquote(path)
        except:
            send_error(conn, 400)
            return

        headers = {}
        for line in lines[1:]:
            if ': ' in line:
                key, value = line.split(': ', 1)
                headers[key.lower()] = value

        body = data.split(b'\r\n\r\n', 1)[1] if b'\r\n\r\n' in data else b''
        if 'content-length' in headers:
            content_length = int(headers['content-length'])
            while len(body) < content_length:
                body += conn.recv(4096)

        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }

        if method == 'OPTIONS':
            send_response(conn, 204, '', cors_headers)
            return

        if path.startswith('/static/'):
            serve_static(conn, path, cors_headers)
        elif path.startswith('/uploads/'):
            serve_uploaded_file(conn, path, cors_headers)
        elif path == '/resources':
            if method == 'GET':
                response_data = json.dumps(resources)
                send_response(conn, 200, response_data, cors_headers, 'application/json')
            elif method == 'POST':
                content_type = headers.get('content-type', '')
                if 'multipart/form-data' in content_type:
                    boundary = content_type.split('boundary=')[1]
                    form_data, files = parse_multipart_form_data(body, boundary, content_type)
                    
                    with lock:
                        res_id = str(len(resources) + 1)
                        resource = {
                            'name': form_data.get('name', ''),
                            'value': form_data.get('value', ''),
                            'image': files.get('file', {}).get('path', '')
                        }
                        resources[res_id] = resource
                    
                    response_data = json.dumps({res_id: resource})
                    send_response(conn, 201, response_data, cors_headers, 'application/json')
                else:
                    try:
                        payload = json.loads(body.decode('utf-8'))
                        with lock:
                            res_id = str(len(resources) + 1)
                            resources[res_id] = payload
                        response_data = json.dumps({res_id: payload})
                        send_response(conn, 201, response_data, cors_headers, 'application/json')
                    except json.JSONDecodeError:
                        send_error(conn, 400, cors_headers)
            else:
                send_error(conn, 405, cors_headers)
        elif path.startswith('/resources/'):
            res_id = path.split('/')[-1]
            if method == 'GET':
                if res_id in resources:
                    response_data = json.dumps(resources[res_id])
                    send_response(conn, 200, response_data, cors_headers, 'application/json')
                else:
                    send_error(conn, 404, cors_headers)
            elif method == 'PUT':
                if res_id in resources:
                    try:
                        payload = json.loads(body.decode('utf-8'))
                        with lock:
                            resources[res_id] = payload
                        response_data = json.dumps(payload)
                        send_response(conn, 200, response_data, cors_headers, 'application/json')
                    except json.JSONDecodeError:
                        send_error(conn, 400, cors_headers)
                else:
                    send_error(conn, 404, cors_headers)
            elif method == 'DELETE':
                if res_id in resources:
                    with lock:
                        del resources[res_id]
                    send_response(conn, 204, '', cors_headers)
                else:
                    send_error(conn, 404, cors_headers)
            else:
                send_error(conn, 405, cors_headers)
        else:
            send_error(conn, 404, cors_headers)
    except Exception as e:
        print(f"Error handling request: {e}")
        send_error(conn, 500, cors_headers)
    finally:
        conn.close()

def serve_static(conn, path, cors_headers):
    local_path = path[len('/static/'):]
    file_path = os.path.join(STATIC_DIR, local_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            content = f.read()
        content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        headers = {
            'Content-Type': content_type,
            'Content-Length': str(len(content))
        }
        headers.update(cors_headers)
        send_response(conn, 200, content, headers, content_type, is_binary=True)
    else:
        send_error(conn, 404, cors_headers)

def serve_uploaded_file(conn, path, cors_headers):
    local_path = path[len('/uploads/'):]
    file_path = os.path.join(UPLOAD_DIR, local_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            content = f.read()
        content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        headers = {
            'Content-Type': content_type,
            'Content-Length': str(len(content))
        }
        headers.update(cors_headers)
        send_response(conn, 200, content, headers, content_type, is_binary=True)
    else:
        send_error(conn, 404, cors_headers)

def send_response(conn, status, body, extra_headers=None, content_type='text/plain', is_binary=False):
    if extra_headers is None:
        extra_headers = {}
    
    status_line = f"HTTP/1.1 {status} {status_messages[status]}\r\n"
    headers = f"Content-Type: {content_type}\r\n"
    
    if not is_binary:
        body = body if isinstance(body, str) else body.decode('utf-8')
        headers += f"Content-Length: {len(body)}\r\n"
    else:
        headers += f"Content-Length: {len(body)}\r\n"
    
    for key, value in extra_headers.items():
        headers += f"{key}: {value}\r\n"
    
    response = status_line + headers + "\r\n"
    conn.sendall(response.encode('utf-8'))
    
    if is_binary:
        conn.sendall(body)
    else:
        conn.sendall(body.encode('utf-8'))

def send_error(conn, status, extra_headers=None):
    if extra_headers is None:
        extra_headers = {}
    body = status_messages[status]
    send_response(conn, status, body, extra_headers)

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server running on http://{HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == '__main__':
    start_server()