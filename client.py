import socket
import os
import time

def create_socket():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock.settimeout(5)  # 5秒のタイムアウトを設定
    return sock


server_address = '/tmp/chat_messenger_socket'

def connect_to_server(sock):
    while True:
        try:
            sock.sendto(b'', server_address)
            print("サーバーに接続しました。")
            return True
        except (ConnectionRefusedError, FileNotFoundError):
            print("サーバーに接続できません。5秒後に再試行します...")
            time.sleep(5)

sock = create_socket()
address = '/tmp/chat_messenger_socket_client'

username = input('ユーザー名を入力してください：\n')

try:
    os.unlink(address)
except FileNotFoundError:
    pass

sock.bind(address)

connect_to_server(sock)

def send_message(sock, message):
    max_retries = 3
    retry_delay = 2
    for attempt in range(max_retries):
        try:
            sent = sock.sendto(message.encode(), server_address)
            return True
        except (ConnectionRefusedError, FileNotFoundError):
            if attempt < max_retries - 1:
                print(f"メッセージの送信に失敗しました。{retry_delay}秒後に再試行します...")
                time.sleep(retry_delay)
            else:
                print("メッセージの送信に失敗しました。サーバーに接続できません。")
                return False
        except Exception as e:
            print(f"送信エラー: {e}")
            return False

try:
    while True:
        message = input('メッセージを入力してください（終了するには"exit"と入力）：\n')
        if message.lower() == 'exit':
            break
        
        full_message = f'ユーザーネーム: {username}\n{message}'
        if send_message(sock, full_message):
            print("")
        else:
            print("メッセージの送信に失敗しました。サーバーとの接続を確認してください。")
            # ここで再接続を試みることもできます
            if connect_to_server(sock):
                print("サーバーに再接続しました。")
            else:
                print("サーバーへの再接続に失敗しました。プログラムを終了します。")
                break

        time.sleep(0.1)  # 短い遅延を追加して、受信スレッドが処理する時間を確保

finally:
    print('ソケットを閉じています')
    sock.close()