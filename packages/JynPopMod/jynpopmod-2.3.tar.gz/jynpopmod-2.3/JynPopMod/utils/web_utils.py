"""                                               PRIVATE USE AND DERIVATIVE LICENSE AGREEMENT 

        By using this software (the "Software"), you (the "User") agree to the following terms:  

1. Grant of License:  
    The Software is licensed to you for personal and non-commercial purposes, as well as for incorporation into your own projects, whether for private or public release.  

2. Permitted Use:  
    - You may use the Software as part of a larger project and publish your program, provided you include appropriate attribution to the original author (the "Licensor").  
    - You may modify the Software as needed for your project but must clearly indicate any changes made to the original work.  

3. Restrictions:  
     - You may not sell, lease, or sublicense the Software as a standalone product.  
     - If using the Software in a commercial project, prior written permission from the Licensor is required.(Credit,Cr)
     - You may not change or (copy a part of) the original form of the Software.  

4. Attribution Requirement:  
      Any published program or project that includes the Software, in whole or in part, must include the following notice:  
      *"This project includes software developed by [Jynoqtra], © 2025. Used with permission under the Private Use and Derivative License Agreement."*  

5. No Warranty:  
      The Software is provided "as is," without any express or implied warranties. The Licensor is not responsible for any damage or loss resulting from the use of the Software.  

6. Ownership:  
      All intellectual property rights, including but not limited to copyright and trademark rights, in the Software remain with the Licensor.  

7. Termination:  
     This license will terminate immediately if you breach any of the terms and conditions set forth in this agreement.  

8. Governing Law:  
      This agreement shall be governed by the laws of [the applicable jurisdiction, without regard to its conflict of law principles].  

9. Limitation of Liability:  
     In no event shall the Licensor be liable for any direct, indirect, incidental, special, consequential, or punitive damages, or any loss of profits, revenue, data, or use, incurred by you or any third party, whether in an action in contract, tort (including but not limited to negligence), or otherwise, even if the Licensor has been advised of the possibility of such damages.  

            Effective Date: [2025]  

            © 2025 [Jynoqtra]
"""

from http.server import SimpleHTTPRequestHandler, HTTPServer
import socketserver
import requests
import logging
import os
import sys
import subprocess
import socket
import http

def start_http_server(ip="0.0.0.0", port=8000):
    server_address = (ip, port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Server started on {ip}:{port}")
    httpd.serve_forever()

def stop_http_server():
    print("Stopping server...")
    exit(0)

def get_server_status(url="http://localhost:8000"):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Server is up and running.")
        else:
            print(f"Server is down. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")

def set_server_timeout(timeout=10):
    socket.setdefaulttimeout(timeout)
    print(f"Server connection timeout set to {timeout} seconds.")

def upload_file_to_server(file_path, url="http://localhost:8000/upload"):
    with open(file_path, 'rb') as file:
        response = requests.post(url, files={'file': file})
        if response.status_code == 200:
            print(f"File successfully uploaded: {file_path}")
        else:
            print(f"File upload failed. Status Code: {response.status_code}")

def download_file_from_server(file_url, save_path):
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded: {save_path}")
    else:
        print(f"File download failed. Status Code: {response.status_code}")

class CustomRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Welcome! Server is running.")
        elif self.path == "/status":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "online"}')
        else:
            self.send_response(404)
            self.end_headers()

def start_custom_http_server(ip="0.0.0.0", port=8000):
    server_address = (ip, port)
    httpd = HTTPServer(server_address, CustomRequestHandler)
    print(f"Custom server started on {ip}:{port}")
    httpd.serve_forever()

def set_server_access_logs(log_file="server_access.log"):
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
    print(f"Access logs are being saved to {log_file}")

def get_server_logs(log_file="server_access.log"):
    try:
        with open(log_file, 'r') as log:
            logs = log.readlines()
            print("".join(logs))
    except FileNotFoundError:
        print(f"{log_file} not found.")

def restart_http_server():
    print("Restarting server...")
    os.execv(sys.executable, ['python'] + sys.argv)

def open_url(url):
    subprocess.run(['open', url], check=True)

def download_image_from_url(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded to {save_path}")
    else:
        print(f"Failed to download image. Status Code: {response.status_code}")

def check_internet_connection():
    response = os.system("ping -c 1 google.com")
    return response == 0

def create_web_server(directory, port=8000):
    os.chdir(directory)
    handler = SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving {directory} at http://localhost:{port}")
        httpd.serve_forever()

def create_custom_web_server(html, port=8000):
    html_content = html

    class CustomHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))

    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        print(f"Serving custom HTML page at http://0.0.0.0:{port}")
        print("Anyone on the same network can access this. (if not work use this http://127.0.0.1:8000)")
        httpd.serve_forever()

def send_http_request(url, method='GET', data=None):
    if method == 'GET':
        response = requests.get(url)
    elif method == 'POST':
        response = requests.post(url, data=data)
    return response.text
