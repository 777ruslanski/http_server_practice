# Lightweight HTTP Server and Client in Python

## Overview
This project implements a lightweight HTTP server and client system developed in Python. The server is capable of handling basic RESTful API requests (GET, POST, PUT, DELETE), serving static files, and supporting file uploads (e.g., images) using the `multipart/form-data` MIME type. The client interacts with the server through customizable HTTP requests, displaying responses in a user-friendly manner.

## Features
- **HTTP Server**:
  - Supports multiple HTTP methods (GET, POST, PUT, DELETE)
  - Static file serving (HTML, CSS, images)
  - In-memory resource management
  - Support for file uploads (e.g., PNG, JPG images)
  - Multi-threaded handling of client requests
  - Returns appropriate HTTP status codes
  - Error handling for incorrect requests
- **HTTP Client**:
  - Send HTTP requests (GET, POST, PUT, DELETE)
  - Attach custom headers
  - Submit data with requests, including file uploads
  - Display responses and handle errors
  - Continuous request handling without restarting the client

## Project Structure
├── server.py # Python HTTP server implementation
├── client.py # Python HTTP client implementation
├── static/ # Folder for static files (HTML, CSS, images)
│ ├── index.html # HTML page for the web interface
│ ├── style.css # CSS file for styling
│ └── uploads/ # Directory for storing uploaded files
└── README.md # This file

bash
Copiar
Editar

## Setup and Installation

### Prerequisites
- Python 3.6 or higher

### Installation Steps
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
Run the server:

bash
Copiar
Editar
python server.py
Open the client in your browser by navigating to http://127.0.0.1:8080/static/index.html. You will be able to interact with the server using the provided interface.

Running the Client
To send requests directly from the terminal using the client:

bash
Copiar
Editar
python client.py
The client will allow you to interact with the server and test the CRUD operations, including file uploads.

Usage
HTTP Server
GET /resources: Retrieves the list of all resources.

POST /resources: Adds a new resource (supports multipart/form-data for file uploads).

GET /resources/{id}: Retrieves a specific resource by its ID.

PUT /resources/{id}: Updates an existing resource.

DELETE /resources/{id}: Deletes a specific resource.

HTTP Client
Sending Requests: You can choose the HTTP method (GET, POST, PUT, DELETE) and the URL to which the request will be sent. The client will also allow you to add headers and specify the body of the request (in JSON format or file upload).

View the Responses: After submitting a request, the client will display the response status and body, including any errors encountered.

Testing
The server and client have been tested using functional manual tests:

GET and POST requests are correctly processed.

Static files (e.g., index.html, style.css) are served correctly.

File uploads (e.g., PNG, JPG) are handled as expected, and images are displayed in the gallery.

Example Requests
To test the server with curl:

GET request:

bash
Copiar
Editar
curl -X GET http://127.0.0.1:8080/resources
POST request with data and file:

bash
Copiar
Editar
curl -X POST -F "name=Example" -F "value=123" -F "file=@path_to_image.png" http://127.0.0.1:8080/resources
Screenshots

Challenges and Solutions
Concurrency Handling: The server uses multi-threading to handle multiple client requests concurrently.

File Uploads: We implemented multipart/form-data parsing to handle file uploads, ensuring that the server saves images in the correct directory and associates them with the corresponding resource.

Future Improvements
Add database support for persistent resource storage.

Implement HTTPS and authentication mechanisms.

Add advanced file validation (e.g., check file size and type before accepting uploads).
