#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys
import daemon

# Set the server information
SERVER = 'irc.libera.chat'
PORT = 6667
CHANNEL = '#gentoo-kernelci'
NICKNAME = 'MyBot'

def connect_to_irc():
    # Connect to the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER, PORT))

    # Send login information
    sock.send(f'NICK {NICKNAME}\r\n'.encode())
    sock.send(f'USER {NICKNAME} {NICKNAME} {NICKNAME} :Python IRC\r\n'.encode())

    # Join the channel
    sock.send(f'JOIN {CHANNEL}\r\n'.encode())

    return sock

def send_messages(sock, messages):
    # Send messages passed as arguments
    for message in messages:
        sock.send(f'PRIVMSG {CHANNEL} :{message}\r\n'.encode())

def listen_for_messages(sock):
    # Listen for messages
    while True:
        response = sock.recv(2048).decode()
        if 'PING' in response:
            sock.send('PONG :pingis\n'.encode())
        if response.strip().split(' ')[1] == 'PRIVMSG':
            sender = response.split('!')[0][1:]
            message = response.split('PRIVMSG')[1].split(':')[1].strip()
            print(f'{sender}: {message}')

def main():
    # Get messages from command line arguments
    messages = sys.argv[1:]

    # Connect to IRC server
    sock = connect_to_irc()

    # Send messages to IRC channel
    send_messages(sock, messages)

    # Listen for incoming messages
    listen_for_messages(sock)

if __name__ == '__main__':
    with daemon.DaemonContext():
        main()
