# HTTP Server with CRUD and Multimedia Upload Support

This is a simple Python-based HTTP server that provides RESTful API endpoints for CRUD operations and supports uploading and serving multimedia content (e.g. images). It includes a web interface for interacting with the API.

## Features

- ✅ Serve static files from the `static/` directory
- ✅ RESTful API:
  - `GET /resources` - List all resources
  - `POST /resources` - Create a new resource (supports JSON and file upload)
  - `PUT /resources/{id}` - Update a resource
  - `DELETE /resources/{id}` - Delete a resource
- ✅ Upload multimedia files (PNG, JPEG, etc.)
- ✅ Automatically store and serve uploaded files
- ✅ Simple HTML frontend for testing requests

## Requirements

- Python 3.x

## Running the Server

```bash
python server.py
