import os
import socket
from scrapper import run_scrapper


HOST = os.getenv('LISTEN_HOST')
PORT = int(os.getenv('LISTEN_PORT'))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(3)

while True:
    conn, addr = s.accept()
    data = conn.recv(1024)
    if data == b"Start scrapper.":
        run_scrapper()
    conn.close()
    print("received data from sender: %s" % (data))
