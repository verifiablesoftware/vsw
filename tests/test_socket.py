import socket

def test_socket():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('3.142.235.22', 1234))

    client.sendall(str.encode("Hello"))
    data = client.recv(1024)
    client.close()

    print('Received', repr(data))