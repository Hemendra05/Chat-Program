import socket
import errno
import threading
import os

HEADER_LENGTH = 10

IP = input("Enter the Server's IP: ")
PORT = 1234
my_username = input("Enter Username: ")

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, 
# socket.SOCK_RAW - raw IP packets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception 
# we'll handle
client_socket.setblocking(False)

# Prepare username and header and send them
# We need to encode username to bytes, then count number of bytes and prepare header of fixed size,
# that we encode to bytes as well
username = my_username.encode()
username_header = f"{len(username):<{HEADER_LENGTH}}".encode()
client_socket.send(username_header + username)

# Create a function to handle the recieving messages
def recieve_message():

    while True:

            try:

                # Receive our "header" containing username length, it's size is defined and constant
                username_header = client_socket.recv(HEADER_LENGTH)

                # If we received no data, server gracefully closed a connection, for example using
                # socket.close() or socket.shutdown(socket.SHUT_RDWR)
                if not len(username_header):
                    print('Connection closed by the server')
                    os._exit(0)

                # Convert header to int value
                username_length = int(username_header.decode().strip())

                # Receive and decode username
                username = client_socket.recv(username_length).decode()

                # Now do the same for message (as we received username, we received whole message,
                # there's no need to check if it has any length)
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode().strip())
                message = client_socket.recv(message_length).decode()
                

                # Print message
                print(f'{username} > {message}')

                
            except IOError as e:
                # This is normal on non blocking connections - when there are no incoming data error is 
                # going to be raised. Some operating systems will indicate that using AGAIN, and some
                # using WOULDBLOCK error code. We are going to check for both - if one of them - that's
                # expected, means no incoming data, continue as normal. If we got different error code, 
                # then something happened
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    os._exit(0)

                # We just did not receive anything
                # continue
                
            except Exception as e:
                # Any other exception - something happened, exit
                print('Reading error: '.format(str(e)))
                os._exit(0)
                
            except:

                # If we are here, client closed connection violently, for example by pressing ctrl+c on his 
                # script or just lost his connection. socket.close() also invokes socket.shutdown(socket.SHUT_RDWR)
                # what sends information about closing the socket (shutdown read/write) and that's also a
                # cause when we receive an empty message
                return False

# Create a function to handle the messages that to be sended
def send_message():

    while True:

        # Wait for user to input a message
        send_message = input('type here...> ')
        
        # if we enter 'quit' here then it will exit the program and closed the connection
        if send_message == "quit":
            # Encode message to bytes, prepare header and convert to bytes, like for username above,
            # then send
            send_message = send_message.encode()
            send_message_header = f"{len(send_message):<{HEADER_LENGTH}}".encode()
            client_socket.send(send_message_header + send_message)
            os._exit(0)

        # If message is not empty - send it
        elif send_message:

            # Encode message to bytes, prepare header and convert to bytes, like for username above,
            # then send
            send_message = send_message.encode()
            send_message_header = f"{len(send_message):<{HEADER_LENGTH}}".encode()
            client_socket.send(send_message_header + send_message)  

        


# Multi-Threading: Creating threaads for both the functions so that they can work at same time to send or recieve the messages
recieve_threads = threading.Thread(target=recieve_message)
send_threads = threading.Thread(target=send_message)

# Starting the threads
recieve_threads.start()
send_threads.start()

    

    
