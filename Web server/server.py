import os
import cgi
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit

# Ensure the uploads directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/files":
            # List all files in the uploads directory as a JSON response
            files = os.listdir(UPLOAD_DIR)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(files).encode('utf-8'))

        elif self.path == "/gallery.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            # Generate the gallery page dynamically
            files = os.listdir(UPLOAD_DIR)
            self.wfile.write(b"<html><head><title>Gallery</title></head><body>")
            self.wfile.write(b"<h1>Gallery</h1><ul>")
            for file in files:
                self.wfile.write(
                    f'<li><a href="{file}" download>{file}</a> <button onclick="deleteFile(\'{file}\')">Delete</button></li>'.encode("utf-8")
                )
            self.wfile.write(b"</ul>")
            self.wfile.write(b"""
                <script>
                    function deleteFile(file) {
                        fetch('/delete/' + file, { method: 'DELETE' })
                        .then(response => {
                            if (response.ok) {
                                alert('File deleted successfully.');
                                window.location.reload();
                            } else {
                                alert('Failed to delete the file.');
                            }
                        });
                    }
                </script>
            """)
            self.wfile.write(b"</body></html>")
        
        else:
            super().do_GET()

    def do_DELETE(self):
        if self.path.startswith('/delete/'):
            filename = self.path.split('/')[-1]
            file_path = os.path.join(UPLOAD_DIR, filename)
            try:
                os.remove(file_path)
                self.send_response(200)
                self.end_headers()
            except FileNotFoundError:
                self.send_response(404)  # Not found
                self.end_headers()
            except Exception as e:
                self.send_response(500)  # Server error
                self.end_headers()
                print(f"Error deleting file: {e}")
        else:
            self.send_response(404)
            self.end_headers()

    # The existing do_POST method from your previous implementation...

# Start the server and bind to all network interfaces
server_address = ("0.0.0.0", 8000)  # Bind to all interfaces (or use your local IP address)
httpd = HTTPServer(server_address, CustomHandler)
print("Server running on http://localhost:8000")
httpd.serve_forever()
