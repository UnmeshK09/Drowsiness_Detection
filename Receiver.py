import socket

# Set up the socket connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', 12345))  # Change the IP address and port as needed
s.listen(5)
client_socket, addr = s.accept()
print(f"Connection from {addr} has been established!")


while True:
    flag = client_socket.recv(1024)  # Receive the flag over the socket
    received_flag = flag.decode('utf-8')  # Decode the received flag
    print("Received Flag:", received_flag)  # Debug print statement
    if received_flag == 'Drowsy':
        # Perform some action when the drowsy flag is received
        print("Driver is drowsy!")
    elif received_flag == 'Not drowsy':
        # Perform some action when the not drowsy flag is received
        print("Driver is not drowsy!")
    else:
        # Handle unexpected flags
        print("Received an unexpected flag:", received_flag)
