"""Lab 1 TET - por Santiago Vanegas"""

import re
import socket
import sys

template = b"""GET /~fdc/sample.html HTTP/1.1
    Host: www.columbia.edu
    Origin: ""
    User-Agent: yacurl(svaneg11)
    Accept: text/html, image/*, application/pdf, video/*
    Accept-Language: en-US
    Connection: keep-alive

    """


class HttpRequest():

    def __init__(self, url, method="GET"):
        self.method = method
        if self.method.upper() != "GET":
            print("Method not supported (yet!)")
            sys.exit(1)

        regex = r"(?:\w+\://)?([^/\r\n]+)(/[^\r\n]*)?"  # URL Regex

        try:
            match = re.fullmatch(regex, url)
            self.domain = match.group(1)
            self.subdirectory = match.group(2)
            if not self.subdirectory:
                self.subdirectory = '/'
        except AttributeError:
            print("Invalid url.")
            sys.exit(1)

        template = """%s %s HTTP/1.1
        Host: %s
        Origin: ""
        User-Agent: yacurl(svaneg11)
        Accept: text/html, image/*, application/pdf, video/*
        Accept-Language: en-US
        Connection: keep-alive

        """ % (self.method, self.subdirectory, self.domain)
        self.request = bytes(template, encoding="ascii")

        def __repr__(self):
            return f"HttpRequest({self.method}, {self.domain}, {self.subdirectory}"

        def get():
            return self.domain, self.request

host, request = HttpRequest("http://www.example.com/site/section1/VAR1/VAR2/").get()
HOST = 'www.columbia.edu'  # The server's hostname or IP address
PORT = 80        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.settimeout(2)
    s.sendall(request)
    response = b''
    try:
        while True:
            data = s.recv(1024)
            response += data
    except Exception as e:
        s.close()
        print('Response:', response, sep='\n')
        sys.exit(0)




