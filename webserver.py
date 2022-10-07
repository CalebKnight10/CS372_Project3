# Caleb Knight
# Project to create a server that will actually serve files 
# when requesting a specific file in the browser

import socket
import sys
import os

# if the user inputs a port, use it
if len(sys.argv) >= 2:
	port = int(sys.argv[1])
else:
	port = 28333     # if not, use this one

s = socket.socket()

# bind to the port & listen
s.bind(('', port))
s.listen()

# MIME
map_ext = {'.gif': 'image/gif', '.txt': 'text/plain', '.html': 'text/HTML', '.jpeg': 'JPEG image', '.pdf': 'PDF file'}

# Parse request header
def get_request(message):

	# Read in full req header
	encoded = message.recv(4096)
	req = ""

	while True:

		# Accumulate data from all recv() into a var
		decoded = encoded.decode("ISO-8859-1")
		req = req + decoded

		# Search var (use .find()) to find "\r\n\r\n"
		if decoded.find('\r\n\r\n'):
			return(req)
			encoded = message.recv(4096)

# create connection
while True:
	new_connection = s.accept()
	new_sock = new_connection[0]
	request = get_request(new_sock)

	# .split() header data or "\r\n" to get individual lines
	# First line is GET
	get_line = request.split('\r\n')

	# .split() GET line into 3 parts: req (GET), path (/file.txt), and protocol (HTTP/1.1)
	get_req = get_line[0].split()[0]
	get_path = get_line[0].split()[1]
	get_protocol = get_line[0].split()[2]

# Strip Path for Security Reasons
	# os.path has .split() that pulls file name off path
	secure_path = os.path.split(get_path)

	# This returns a tuple where the second element is the filename ('/foo/bar', 'baz.txt')
	file = secure_path[1]

	get_file_type = os.path.splitext(file)
	file_type = get_file_type[1]

# Read data from named file
	# Use code snippet (in canvas) to read file and check for errors
	try:
		with open(file) as fp:
			data = fp.read()   # Read entire file

			# Encode data using ISO-8859-1 from .read() and use len() to compute # of bytes
			# The # of bytes go to Conetent-Length 
			payload = data.encode("ISO-8859-1")
			payload_length = len(payload)

			# OK response
			response = "HTTP/1.1 200 OK\r\n\
			Content-Type: {}\r\n\
			Content-Length: {}\r\n\r\n\
			{}".format(map_ext[file_type], payload_length, data).encode("ISO-8859-1")
			new_sock.sendall(response)		

	except:
    	# File not found or other error
		# Detect 404
		# HTTP/1.1 404 Not Found
		response = "HTTP/1.1 404 Not Found\r\n\
		Content-Type: text/plain\r\n\
		Content-Length: 13\r\n\
		Connection: close\r\n\r\n\
		404 not found".format(map_ext[file_type]).encode("ISO-8859-1")
		new_sock.sendall(response)

	new_sock.close()