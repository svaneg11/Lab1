"""Lab 1 TET - por Santiago Vanegas"""

import argparse
import re
import socket
import sys


class Request:
    def __init__(self, url, method="GET"):
        self.method = method
        if self.method.upper() != "GET":
            print("Method not supported (yet!)")
            sys.exit(1)

        regex = r"(?:\w+://)?([^/\r\n]+)(/[^\r\n]*)?"  # URL Regex

        try:
            match = re.fullmatch(regex, url)
            self.domain = match.group(1)
            self.subdirectory = match.group(2)
            if not self.subdirectory:
                self.subdirectory = '/'
        except AttributeError:
            print("Invalid url.")
            sys.exit(1)

        try:
            self.host = socket.gethostbyname(self.domain)
        except Exception as e:
            print(e)
            print('Failed to find server IP.')
            sys.exit(1)

        self.request = f'{self.method} {self.subdirectory} HTTP/1.1\n' \
            f'Host: {self.domain}\n' \
            f'Origin: ""\n' \
            f'User-Agent: yacurl(svaneg11)\n' \
            f'Accept: */*\n' \
            f'Accept-Language: en-US\n' \
            f'Connection: keep-alive\n\n'

        self.request = bytes(self.request, encoding="ascii")

    def __repr__(self):
        return f"HttpRequest({self.method}, {self.domain}, {self.subdirectory}). ServerIP: {self.host} ,\n"\
            f"{self.request.decode('ISO-8859-1').encode('utf-8').decode('utf-8')}"

    def get(self):
        return self.host, self.request


def send_request(url, port):
    request = Request(url)
    repr(request)
    HOST, http_request = request.get()
    PORT = port      # The port used by the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.settimeout(1)
        s.sendall(http_request)
        response = b''
        try:
            while True:
                data = s.recv(1024)
                response += data
        except Exception as e:
            s.close()
            response = response.decode('ISO-8859-1').encode('utf-8').decode('utf-8')
            print('Response:', response, sep='\n')
            sys.exit(0)


parser = argparse.ArgumentParser(description='HTTP requests using sockets')
parser.add_argument('url', help='The url where the request is going to be sent.')
parser.add_argument('--port', type=int, default=80,
                    help='Use the specified port number (default is port 80).')
args = parser.parse_args()
send_request(args.url, args.port)