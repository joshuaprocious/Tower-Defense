import socket
import threading
import pickle

def receive_messages(client_socket):
    """Thread function for handling incoming messages from the server."""
    while True:
        try:
            # Receive pickled message from the server
            message = client_socket.recv(1024)
            if not message:
                print("Disconnected from server. Exiting...")
                break  # Exit loop if no message is received (server closed)
            # Unpickle the message
            message = pickle.loads(message)
            print(f"Received: {message}")
        except Exception as e:
            print(f"An error occurred while receiving a message: {e}")
            client_socket.close()
            break

def send_messages(client_socket):
    """Sends messages to the server to be broadcasted."""
    try:
        while True:
            message = input("Enter message: ")  # Prompt for user input
            # Pickle the message before sending
            message = pickle.dumps(message)
            client_socket.send(message)
    except Exception as e:
        print(f"An error occurred while sending a message: {e}")
        client_socket.close()

if __name__ == "__main__":
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('127.0.0.1', 12345)
        client_socket.connect(server_address)  # Connect to the server
        print(f"Connected to server at {server_address}. You can start sending messages.")

        # Start receiving messages in a separate thread
        threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()
        
        # Main thread handles sending messages
        send_messages(client_socket)
    except Exception as e:
        print(f"Unable to connect to the server: {e}")
