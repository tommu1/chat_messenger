import socket
import os

sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

server_address = '/tmp/chat_messenger_socket'

try:
    os.unlink(server_address)
except FileNotFoundError:
    pass

print('Staring up on {}.'.format(server_address))

sock.bind(server_address)

while True:
    try:
        data, address = sock.recvfrom(4096)
        
        if data and address:
            print(data.decode('utf-8'))
            response = "メッセージを受信しました：".encode('utf-8') + data
            sent = sock.sendto(response, address)
        else:
            print("無効なデータまたはアドレスを受信しました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")