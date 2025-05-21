
# HTTP Server Practice

A basic HTTP server implementation in [Python/Node.js/Other] for learning web server fundamentals and the HTTP protocol.

## Features

- Handles `GET` and `POST` requests
- Serves static files (HTML, CSS, images, etc.)
- Customizable port and routes
- [Add other features like headers, cookies, query parsing if implemented]

## Prerequisites

- [Python 3.x/Node.js/etc.]
- [Any other dependencies]

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/777ruslanski/http_server_practice.git
   cd http_server_practice
Install dependencies (if applicable):

[pip install -r requirements.txt / npm install / etc.]

## Usage
Start the server:

[python server.py / node server.js / etc.]
Access in your browser:

http://localhost:[PORT]/
Default port is usually 8000 or 8080.

## Project Structure
```
http_server_practice/
├── server.py                # Main server implementation
├── public/                  # Static files directory
│   ├── index.html           # Example HTML file
│   ├── style.css            # Example CSS file
│   └── ...
├── README.md
└── [Other relevant files]
```

## API Reference (if applicable)
Endpoints
GET / - Serves index.html

GET /[filename] - Serves requested static file

POST /data - Example POST endpoint

Request Body:
```
{
  "key": "value"
}
```
## Examples
Making Requests
```
curl http://localhost:8000/

curl -X POST -H "Content-Type: application/json" -d '{"key":"value"}' http://localhost:8000/data
```
## Contributing
Contributions are welcome! Please follow these steps:

- Fork the project

- Create your feature branch (git checkout -b feature/AmazingFeature)
  
- Commit your changes (git commit -m 'Add some AmazingFeature')

- Push to the branch (git push origin feature/AmazingFeature)

- Open a Pull Request

## License
Distributed under the MIT License. See LICENSE for more information.

## Contact
ptudela04@gmail.com
