from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys
import json
from urllib.parse import unquote
from threading import Thread
import socketserver
import cgi
import uuid

PORT = 8000
STATIC_DIR = 'static'
UPLOAD_DIR = os.path.join(STATIC_DIR, 'uploads')
RESOURCES = {}  # In-memory storage

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.path = unquote(self.path)

            if self.path == '/' or self.path.startswith('/static/'):
                self.handle_static()
            elif self.path == '/resources':
                self.list_resources()
            else:
                self.send_error(404, "Endpoint Not Found")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def do_POST(self):
        try:
            content_type = self.headers.get('Content-Type', '')

            if self.path == '/resources':
                if content_type.startswith('multipart/form-data'):
                    self.handle_multipart_resource()
                else:
                    length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(length)
                    self.create_resource(post_data)
            else:
                self.send_error(404, "Endpoint Not Found")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def do_PUT(self):
        try:
            if self.path.startswith('/resources/'):
                resource_id = self.path.split('/')[-1]
                length = int(self.headers.get('Content-Length', 0))
                put_data = self.rfile.read(length)
                self.update_resource(resource_id, put_data)
            else:
                self.send_error(404, "Endpoint Not Found")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def do_DELETE(self):
        try:
            if self.path.startswith('/resources/'):
                resource_id = self.path.split('/')[-1]
                self.delete_resource(resource_id)
            else:
                self.send_error(404, "Endpoint Not Found")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def handle_static(self):
        if self.path == '/':
            self.path = '/static/index.html'

        full_path = os.path.abspath(os.path.join('.', self.path.lstrip('/')))
        if not full_path.startswith(os.path.abspath(STATIC_DIR)):
            self.send_error(403, "Forbidden: Access outside root directory")
            return

        if not os.path.exists(full_path):
            self.send_error(404, "File Not Found")
            return

        self.send_response(200)
        self.send_header('Content-type', self.guess_type(full_path))
        self.end_headers()
        with open(full_path, 'rb') as f:
            self.wfile.write(f.read())

    def list_resources(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(RESOURCES).encode())

    def create_resource(self, data):
        try:
            resource = json.loads(data.decode())
            resource_id = str(len(RESOURCES) + 1)
            RESOURCES[resource_id] = resource
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.send_header('Location', f'/resources/{resource_id}')
            self.end_headers()
            self.wfile.write(json.dumps(resource).encode())
        except json.JSONDecodeError:
            self.send_error(400, "Bad Request: Invalid JSON")

    def handle_multipart_resource(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type']}
        )

        name = form.getvalue('name')
        value = form.getvalue('value')
        file_item = form['file'] if 'file' in form else None

        resource = {
            'name': name,
            'value': value,
            'image': None
        }

        if file_item and file_item.filename:
            ext = os.path.splitext(file_item.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)

            with open(filepath, 'wb') as f:
                f.write(file_item.file.read())

            resource['image'] = f'/static/uploads/{filename}'

        resource_id = str(len(RESOURCES) + 1)
        RESOURCES[resource_id] = resource

        self.send_response(201)
        self.send_header('Content-type', 'application/json')
        self.send_header('Location', f'/resources/{resource_id}')
        self.end_headers()
        self.wfile.write(json.dumps(resource).encode())

    def update_resource(self, resource_id, data):
        if resource_id not in RESOURCES:
            self.send_error(404, "Resource Not Found")
            return
        try:
            resource = json.loads(data.decode())
            RESOURCES[resource_id] = resource
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resource).encode())
        except json.JSONDecodeError:
            self.send_error(400, "Bad Request: Invalid JSON")

    def delete_resource(self, resource_id):
        if resource_id not in RESOURCES:
            self.send_error(404, "Resource Not Found")
            return
        del RESOURCES[resource_id]
        self.send_response(204)
        self.end_headers()

def run_server():
    server_address = ('', PORT)
    httpd = ThreadedHTTPServer(server_address, HTTPRequestHandler)
    print(f"\nServer running at http://localhost:{PORT}")
    print(f"Serving files from: {os.path.abspath(STATIC_DIR)}")
    print("Press Ctrl+C to stop\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        sys.exit(0)

if __name__ == '__main__':
    run_server()
