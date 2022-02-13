# TET - Lab1
por Santiago Vanegas / svaneg11@eafit.edu.co

## Pre-requisitos
Antes de poder correr el programa se deben instalar los requerimientos.

Desde la terminal se debe ir a la carpeta del proyecto y correr

> `pip install -r requirements.txt`

Esto instalará BeautifulSoup4


## Uso
> `python yacurl.py [-h] [--port PORT] [--filename FILENAME] url`

\
El uso basico del programa es corriendolo asi

> `python yacurl.py <url>`

Por ejemplo: `python yacurl.py www.google.com`

\
Por defecto el puerto que se usa es el 80, y el nombre que usa para los archivos es 'file'
pero se puede correr el programa especificando un puerto y nombre de archivo asi:

> `python yacurl.py www.google.com --port 443 --filename mypage`


El programa infiere la extension del header Content-Type y la agrega en caso de que
no se haya puesto en el nombre, asi que no es necesario añadir la extension del archivo en el argumento.



