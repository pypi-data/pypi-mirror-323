WEB/INTERNET utils: from Jeb import * or just import Jeb

### **1. `start_http_server`**

This function starts a simple HTTP server that listens on the specified IP and port. The default IP is `0.0.0.0` (listens on all available network interfaces), and the default port is `8000`.

**Example Usage:**
```python
start_http_server(ip="127.0.0.1", port=8080)  # Starts the server on localhost at port 8080
```

---

### **2. `stop_http_server`**

This function stops the running HTTP server by calling `exit(0)`, which will terminate the process.

**Example Usage:**
```python
stop_http_server()  # Stops the server
```

---

### **3. `get_server_status`**

This function checks the status of the server by sending a `GET` request to a specified URL (default is `http://localhost:8000`). It prints the server status based on the response code.

**Example Usage:**
```python
get_server_status(url="http://localhost:8000")  # Checks if the server is up and running
```

---

### **4. `set_server_timeout`**

This function sets a timeout for server connections using `socket.setdefaulttimeout()`. The default timeout is 10 seconds.

**Example Usage:**
```python
set_server_timeout(timeout=5)  # Sets the connection timeout to 5 seconds
```

---

### **5. `upload_file_to_server`**

This function uploads a file to the server via a POST request. The file path and server URL are required.

**Example Usage:**
```python
upload_file_to_server(file_path="example.txt", url="http://localhost:8000/upload")  # Uploads a file to the server
```

---

### **6. `download_file_from_server`**

This function downloads a file from the server at the given URL and saves it to the specified path.

**Example Usage:**
```python
download_file_from_server(file_url="http://localhost:8000/example.txt", save_path="downloaded_example.txt")  # Downloads the file
```

---

### **7. `CustomRequestHandler` (Class)**

A custom subclass of `SimpleHTTPRequestHandler` that provides specialized handling of GET requests. It serves custom responses for paths `/` and `/status`.

**Example Usage:**
```python
start_custom_http_server(ip="127.0.0.1", port=8080)  # Starts a custom HTTP server
```

---

### **8. `start_custom_http_server`**

This function starts a custom HTTP server that uses `CustomRequestHandler` to handle requests. It listens on the given IP and port.

**Example Usage:**
```python
start_custom_http_server(ip="0.0.0.0", port=8080)  # Starts a custom server that handles `/` and `/status`
```

---

### **9. `set_server_access_logs`**

This function enables server access logging to a specified log file. Logs are written with timestamps and message details.

**Example Usage:**
```python
set_server_access_logs(log_file="server_access.log")  # Starts logging server access
```

---

### **10. `get_server_logs`**

This function reads and prints the server logs from a specified log file.

**Example Usage:**
```python
get_server_logs(log_file="server_access.log")  # Prints logs from the server access log file
```

---

### **11. `restart_http_server`**

This function restarts the HTTP server by re-running the script using `os.execv`.

**Example Usage:**
```python
restart_http_server()  # Restarts the HTTP server
```

---

### **12. `open_url`**

This function opens a URL in the default web browser using the `subprocess.run()` method.

**Example Usage:**
```python
open_url("http://localhost:8000")  # Opens the specified URL in the browser
```

---

### **13. `download_image_from_url`**

This function downloads an image from a given URL and saves it to a specified path.

**Example Usage:**
```python
download_image_from_url(image_url="http://example.com/image.png", save_path="image.png")  # Downloads an image
```

---

### **14. `check_internet_connection`**

This function checks the system's internet connection by pinging `google.com`. It returns `True` if the connection is active, otherwise `False`.

**Example Usage:**
```python
is_connected = check_internet_connection()
print(is_connected)  # Prints True if connected, False if not
```

---

### **15. `create_web_server`**

This function creates a basic web server that serves files from a specified directory. It uses `SimpleHTTPRequestHandler` to serve static content.

**Example Usage:**
```python
create_web_server(directory="/path/to/directory", port=8080)  # Serves files from the specified directory
```

---

### **16. `create_custom_web_server`**

This function creates a custom web server that serves a specific HTML content at a given port.

**Example Usage:**
```python
html_content = "<html><body><h1>Hello, World!</h1></body></html>"
create_custom_web_server(html=html_content, port=8080)  # Serves the custom HTML content
```

---

### **17. `send_http_request`**

This function sends an HTTP request to a specified URL using either the `GET` or `POST` method. Optionally, you can send data with a POST request.

**Example Usage:**
```python
response = send_http_request("http://localhost:8000", method="GET")  # Sends a GET request
```