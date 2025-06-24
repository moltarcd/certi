import paramiko
import time

hostname = "10.10.10.3"
port = 2222
username = "test.cert"
password = "Cert2506"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname, port, username, password)
    print("Conexión exitosa.")

    # Abrir canal interactivo (shell)
    channel = client.invoke_shell()

    # Esperar a que el prompt inicial cargue
    time.sleep(2)
    channel.recv(9999)  # Limpiar buffer

    # Ejecutar TACL y el comando
    channel.send("TACL\n")
    time.sleep(2)  # Espera a que TACL esté listo

    channel.send("fup info $duffy.xcomvval.CAFGLCA0\n")
    time.sleep(2)  # Espera a que el comando se ejecute

    # Leer salida
    output = channel.recv(9999).decode('utf-8')
    print("Salida del comando:")
    print(output)

finally:
    client.close()
