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
        explain_request(self.method, self.subdirectory, self.domain)

    def __repr__(self):
        return f"HttpRequest({self.method}, {self.domain}, {self.subdirectory}). ServerIP: {self.host} ,\n"\
            f"{self.request.decode('ISO-8859-1').encode('utf-8').decode('utf-8')}"

    def get(self):
        return self.host, self.request


def explain_request(method, subdirectory, domain):
    verbose_req = f'{method} {subdirectory} HTTP/1.1 --> Request Line - Método: {method}, Ubicación del recurso: {subdirectory}, Version del protocolo: HTTP/1.1\n' \
    f'Host: {domain} --> Especifica el nombre de dominio del servidor al que se hace la petición.\n' \
    f'User-Agent: yacurl(svaneg11) --> Especifica la aplicacion que hace la peticion, puede ademas contener version y sistema operativo.\n' \
    f'Accept: */* --> Tipo de archivo MIME que se espera como respuesta en el cuerpo del mensaje, */* indica cualquier tipo (paginas html, imagenes, videos audio, etc).\n' \
    f'Accept-Language: en-US --> Indica la preferencia de idioma y localidad para la respuesta.\n' \
    f'Connection: keep-alive --> Pide al servidor mantener la conexión para seguir enviando datos. Se usa un timeout para detectar cuando ha terminado la transferencia.\n' \
    f'--> Linea vacia.\n'

    verbose_req = bytes(verbose_req, encoding="utf-8")
    print('Request:', verbose_req.decode("utf-8"), sep='\n', end='\n\n')


def explain_response(response_headers):
    lines = response_headers.splitlines()
    response_line = lines[0]
    match = re.match('([^ ]+) ([^ ]+) (.*)', response_line)
    version, status_code, status = match.group(1), match.group(2), match.group(3),
    headers = dict()
    for line in lines[1:-1]:    # Parse headers
        index = line.index(':')
        key = line[:index]
        value = line[index+1:]
        headers[key] = value

    explain_headers = dict()
    explain_headers['Date'] = 'Fecha en que se originó la respuesta, en GMT.'
    explain_headers['Server'] = 'Nombre del software que atendió la petición.'
    explain_headers['Content-Length'] = 'Indica el tamaño del cuerpo de la respuesta en bytes.'
    explain_headers['Content-Type'] = 'El tipo MIME del archivo que se envía como respuesta en el cuerpo del mensaje y opcionalmente el charset si es texto.'

    print('Response:')
    print(response_line, f'--> Response Line - Version del protocolo: {version}, Código de estado: {status_code}, Mensaje de estado: {status}')
    for k, v in headers.items():
        if k in explain_headers.keys():
            print(f'{k}:{v} --> {explain_headers[k]}')
        else:
            print(f'{k}:{v} -->')
    print('')


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

            if content_type == 'text/html':
                soup = BeautifulSoup(body, "html.parser")
                body = soup.prettify()
            return http_headers, body, content_type


def save_file(response_bytes, body, filename, content_type):
    if content_type == 'text/html':
        if '.html' not in filename:
            filename += '.html'
        file = open(filename, 'wt', encoding='utf-8')
        file.write(body)
        file.close()
    elif content_type == 'image/jpeg':
        if '.jpg' not in filename and '.jpeg' not in filename:
            filename += '.jpg'
    else:
        extension = '.' + content_type[content_type.index('/')+1:]
        if extension not in filename:
            filename += extension

    if content_type is not None and content_type != 'text/html':
        sep = b''
        count = 0
        while sep != b'\r\n\r\n':   # find binary body
            sep = response_bytes[count:count + 4]
            count += 1
        count += 3
        print('Body:')
        print(response_bytes[count:])
        img = open(filename, mode='wb')
        img.write(response_bytes[count:])


def send_request(url, port, filename):
    request = Request(url)
    host, http_request = request.get()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
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

        s.close()
        response = response_bytes.decode('ISO-8859-1').encode('utf-8').decode('utf-8')
        tup = separate_response(response)
        if tup:
            http_headers, body, content_type = tup
        else:
            http_headers = response
            body = None
            content_type = None

        explain_response(http_headers)

        if content_type == 'text/html':
            print('Body:', body, sep='\n')
            soup = BeautifulSoup(body, "html.parser")
            images = soup.findAll('img')
            links = []
            for image_tag in images:
                if image_tag['src'] not in links:
                    links.append(image_tag['src'])

            print('Recursos estáticos:')
            for l in links:
                if l.startswith('/'):
                    print('http://', request.domain, l, sep='')
                else:
                    print(l)
        save_file(response_bytes, body, filename, content_type)


parser = argparse.ArgumentParser(description='HTTP requests using sockets')
parser.add_argument('url', help='The url where the request is going to be sent.')
parser.add_argument('--port', type=int, default=80,
                    help='Use the specified port number (default is port 80).')
parser.add_argument('--filename', default='file',
                    help='Name to use for the file in which the body(if any) will be saved')
args = parser.parse_args()
send_request(args.url, args.port, args.filename)
