# mini_telnet.py
import socket
import time

HOST = "10.10.10.3"
PORT = 2222

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

def recv():
    time.sleep(0.5)
    try:
        data = sock.recv(4096)
        print("RECIBIDO:", data.decode('ascii', errors='replace'))
        return data
    except:
        return b""

def send(cmd):
    sock.sendall((cmd + "\r\n").encode('ascii'))

# === Flujo ===
recv()
send("TACL")
recv()
send("test.cert")
recv()
send("Cert2506")
recv()
send("fup info $duffy.xcomvval.CAFGLCA0")
time.sleep(2)
output = sock.recv(4096)
print("RESULTADO:")
print(output.decode('ascii', errors='replace'))

sock.close()