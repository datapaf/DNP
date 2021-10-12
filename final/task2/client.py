from socket import *

BUFF_SIZE = 1024

addr = ("127.0.0.1", 50505)

if __name__ == "__main__":
  sock = socket(AF_INET, SOCK_STREAM)
  sock.connect(addr)
  
  while True:
    try:
      str_in = input("Enter string:\n")
      sock.send(str_in.encode())
      result = sock.recv(BUFF_SIZE)
      print("Hash: ", result.decode())
    except KeyboardInterrupt:
      sock.close()
      exit()
