import socket
import threading
import pickle

class ChatServer:
    def __init__(self, host, port):
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        print("Server running, waiting for connections...")

    def broadcast(self, message, sender):
        for client in self.clients:
            if client != sender:
                try:
                    client.send(message)
                except:
                    client.close()
                    self.remove(client)

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024)
                self.broadcast(message, client)
            except:
                self.remove(client)
                break

    def remove(self, client):
        if client in self.clients:
            self.clients.remove(client)

    def accept_connections(self):
        while True:
            client, address = self.server_socket.accept()
            print(f"Connection established with {address}")
            self.clients.append(client)
            threading.Thread(target=self.handle_client, args=(client,)).start()

if __name__ == "__main__":
    ChatServer('127.0.0.1', 12345).accept_connections()
