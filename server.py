import socket
import threading
import time
import datetime
import json
import ast

lock = threading.Lock()
tcp_clients = {} # list of TCP connected clients
udp_clients = {} # list of UDP clients connected
chat_history = {} # messages sent by each client, stored. (can get large if graphical interface introduced)
player_positions = {}  # Global dictionary to store player positions

# parse messages like this format: {'type': 'player_pos_update','payload': {'x': 100,'y': 200}}
def parse_message(decoded_message):
    try:
        client_id = decoded_message['client_id']
        message = decoded_message['message']
        #print('Message to be parsed: ' + str(message))
        
        # Check if the message is a string representation of a dictionary
        if isinstance(message, str):
            # Convert the string back to a dictionary
            # try ast.literal_eval deocding the string to dict
            try:
                message = ast.literal_eval(message)  # Handles Python dict format as a fallback
            except:
                #print('Cannot process string encoded in dict')
                pass
        
        # At this point, 'message' should be a dictionary
        message_type = decoded_message['type']
        print('decoded_message type: ' + str(message_type))
        print('message state before processing: ' + str(message))
        
        if message_type == 'player_pos_update':
            #print('player position object received')
            x , y = message
            print('x: ' + str(x) + ' y: ' + str(y))
            update_player_position(client_id, x, y)
    except Exception as e:
        #print(f'Not a valid object to parse: {e}')
        pass

def update_player_position(client_id, x, y):
    print('updating player positions')
    player_positions[client_id] = {'x': x, 'y': y}
    message = {'type': 'player_positions', 'message': player_positions}
    broadcast_message('server', message, is_udp=True)

# This is the server and listener for TCP and UDP messages. 
# Returns decoded_message which is the dictionary starting with "client_id"
def broadcast_message(sender_id, message, is_udp=False, sender_addr=None):
    with lock:
        # Prepare the message as a JSON string
        json_message = json.dumps({'client_id': sender_id, 'message': message})
        if is_udp == False:
            # Broadcast to TCP clients
            for client_id, conn in tcp_clients.items():
                if client_id != sender_id:  # Exclude the sender for TCP
                    try:
                        conn.sendall(json_message.encode())  # Encode JSON string to bytes before sending
                        print('sent tcp message: ' + str(json_message))
                    except Exception as e:
                        print(f"Error broadcasting to TCP client {client_id}: {e}")
        
        # Broadcast to UDP clients, if the message comes from a UDP client
        if is_udp:
            for addr in udp_clients.keys():
                if addr != sender_addr:  # Exclude the sender for UDP
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto(json_message.encode(), addr)  # Encode JSON string to bytes before sending
                        print('sent udp message: ' + str(json_message))
                        is_udp=False
                        sock.close()
                    except Exception as e:
                        print(f"Error broadcasting to UDP client {addr}: {e}")
        # add chat to chat_history dictionary
        protocol = "UDP" if is_udp else "TCP"
        client_key = sender_addr if is_udp else sender_id
        if client_key not in chat_history:
            chat_history[client_key] = []
        timestamp_ns = time.time_ns()
        chat_history[client_key].append((timestamp_ns, f"{protocol}: {message}"))

def handle_tcp_client(conn, addr):
    #client_id = conn.recv(1024).decode()
    try:
        # Wait for the initial message that includes the client_id
        initial_data = conn.recv(1024).decode()
        initial_message = json.loads(initial_data)
        client_id = initial_message.get('client_id')
        with lock:
            tcp_clients[client_id] = conn
        print(f"TCP Client {client_id} connected from {addr}")
        try:
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                # decode json message
                decoded_message = json.loads(data)  # Decode message from JSON
                #print('Message from TCP Client (JSON): ' + str(decoded_message))
                client_id = decoded_message['client_id']
                message = decoded_message['message']
                print(f"Message from TCP Client {client_id}: {decoded_message}")
                parse_message(decoded_message)
                broadcast_message(client_id, f"TCP: Client {client_id}: {message}")
        except:
            print('could not handle tcp client')
    finally:
        with lock:
            del tcp_clients[client_id]
        conn.close()

def udp_server(host, udp_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        udp_sock.bind((host, udp_port))
        print("UDP server listening...")
        while True:
            data, addr = udp_sock.recvfrom(1024)
            with lock:
                # Update or add the client with their last message timestamp
                udp_clients[addr] = {'last_message_time': datetime.datetime.now()}
            # decode json message
            decoded_message = json.loads(data.decode())  # Decode message from JSON
            #print('Message from UDP Client (JSON): ' + str(decoded_message))
            message = f"{decoded_message['client_id']}: {decoded_message['message']}"
            print(f"Message from UDP Client {addr}: {message}")
            parse_message(decoded_message)
            broadcast_message(None, f"UDP: {message}", is_udp=True, sender_addr=addr)

def tcp_server(host, tcp_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.bind((host, tcp_port))
        tcp_sock.listen()
        print("TCP server listening...")
        while True:
            conn, addr = tcp_sock.accept()
            threading.Thread(target=handle_tcp_client, args=(conn, addr)).start()

def server_commands():
    while True:
        cmd = input("Server command: ")
        if cmd == "print chat":
            with lock:
                for client, messages in chat_history.items():
                    print(f"Chat history for {client}:")
                    for timestamp_ns, message in messages:
                        time_str = datetime.datetime.fromtimestamp(timestamp_ns / 1e9).strftime('%Y-%m-%d %H:%M:%S.%f')
                        print(f"  {time_str} - {message}")
                    print("----------")
        elif cmd == "print player positions":
            for client_id, pos in player_positions.items():
                print(f"Client {client_id}: Position {pos}")
                print('raw play pos dictionary: ' + str(player_positions))
        elif cmd == "print tcp_clients":
            for client_id in tcp_clients.items():
                print(f"Client {client_id}")
        elif cmd == "print udp_clients":
            for client_id in udp_clients.items():
                print(f"Client {client_id}")

if __name__ == "__main__":
    HOST = '127.0.0.1'
    TCP_PORT = 12345
    UDP_PORT = 12346
    threading.Thread(target=tcp_server, args=(HOST, TCP_PORT)).start()
    threading.Thread(target=udp_server, args=(HOST, UDP_PORT)).start()
    threading.Thread(target=server_commands).start()

    # Simple wait mechanism to prevent the script from exiting
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server is shutting down...")
