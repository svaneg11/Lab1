#!/usr/bin/env python3
"""Lab 1 TET - por Santiago Vanegas"""

import argparse
import re
import socket
import sys

from bs4 import BeautifulSoup


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

        self.request = f'{self.method} {self.subdirectory} HTTP/1.1\r\n' \
            f'Host: {self.domain}\r\n' \
            f'User-Agent: yacurl(svaneg11)\r\n' \
            f'Accept: */*\r\n' \
            f'Accept-Language: en-US\r\n' \
            f'Connection: keep-alive\r\n\r\n'

        self.request = bytes(self.request, encoding="'ISO-8859-1'")
        #explain_request(self.method, self.subdirectory, self.domain)

    def __repr__(self):
        return f"HttpRequest({self.method}, {self.domain}, {self.subdirectory}). ServerIP: {self.host} ,\n"\
            f"{self.request.decode('ISO-8859-1').encode('utf-8').decode('utf-8')}"

    def get(self):
        return self.host, self.request


def explain_request(method, subdirectory, domain):
    verbose_req = f'{method} {subdirectory} HTTP/1.1 --> Request Line - Método: {method}, Ubicación del recurso: {subdirectory}, Version del protocolo: HTTP/1.1\n' \
    f'Host: {domain} --> Especifica el nombre de dominio del servidor al que se hace la petición.\n' \
    f'User-Agent: yacurl(svaneg11) --> Especifica la aplicacion que hace la peticion, puede ademas contener version y sistema operativo.\n' \
    f'Accept: */* --> Tipo de archivo MIME que se espera como respuesta, */* indica cualquier tipo (paginas html, imagenes, videos audio, etc).\n' \
    f'Accept-Language: en-US --> Indica la preferencia de idioma y localidad para la respuesta.\n' \
    f'Connection: keep-alive --> Pide al servidor mantener la conexión para seguir enviando datos. Se usa un timeout para detectar cuando ha terminado la transferencia.' \
    f'\n --> Linea vacia.' \
    f'\n --> Linea vacia.'

    verbose_req = bytes(verbose_req, encoding="utf-8")
    print('Request:', verbose_req.decode("utf-8"), sep='\n', end='\n\n')


def separate_response(response):
    response = response.replace('\r', '')   # remove windows carriage return from response
    match = re.search('(.+?\n\n)(.*)', response, flags=re.DOTALL)   # retrieve the http headers and the body

    if match:
        http_headers = match.group(1)
        body = match.group(2)

        if body and 'Transfer-Encoding: chunked' in http_headers:
            body = re.sub('\n?(^[0-9a-z]+$)', '', body, flags=re.MULTILINE)  # Remove chunksize numbers from body

        match = re.search('Content-Type:\s*([^;\n]+)', http_headers)   # Get the Content-Type
        if match:
            content_type = match.group(1)

            if (content_type == 'text/html'):
                soup = BeautifulSoup(body, "html.parser")
                body = soup.prettify()
            return http_headers, body, content_type

def save_file(response_bytes, body, filename, content_type):
    print(content_type , len(content_type))
    if content_type == 'text/html':
        if '.html' not in filename:
            filename += '.html'
        file = open(filename, 'wt')
        file.write(body)
        file.close()
    if content_type == 'image/jpeg':
        if '.jpg' not in filename and'.jpeg' not in filename:
            filename += '.jpg'
    if content_type == 'image/gif':
        if '.gif' not in filename:
            filename += '.gif'
    if content_type == 'image/jpeg' or content_type == 'image/gif':
        sep = b''
        count = 0
        while sep != b'\r\n\r\n':   # find binary body
            sep = response_bytes[count:count + 4]
            print(sep, count)
            count += 1
        count += 3
        print(response_bytes[count:])
        img = open(filename, mode='wb')
        img.write(response_bytes[count:])


def send_request(url, port, filename):
    request = Request(url)
    #print(repr(request))
    HOST, http_request = request.get()
    PORT = port      # The port used by the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.settimeout(1)
        s.sendall(http_request)
        response_bytes = b''
        try:
            while True:
                data = s.recv(1024)
                if data == b'':
                    break
                response_bytes += data
        except Exception:
            pass
        print(response_bytes)
        s.close()
        response = response_bytes.decode('ISO-8859-1').encode('utf-8').decode('utf-8')
        http_headers, body, content_type = separate_response(response)
        print(http_headers, body, sep='\n\n')
        save_file(response_bytes, body, filename, content_type)
        sys.exit(0)


parser = argparse.ArgumentParser(description='HTTP requests using sockets')
parser.add_argument('url', help='The url where the request is going to be sent.')
parser.add_argument('--port', type=int, default=80,
                    help='Use the specified port number (default is port 80).')
parser.add_argument('--filename', default='file',
                    help='Name to use for the file in which the body(if any) will be saved')
args = parser.parse_args()
send_request(args.url, args.port, args.filename)
