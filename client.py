import socket
import os
import time
import tempfile
import threading

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

username = input('ユーザー名を入力してください：')

def generate_unique_address():
    # 一時ディレクトリ内にユニークなファイル名を生成
    temp_dir = tempfile.gettempdir()
    unique_filename = os.path.join(temp_dir, f'chat_messenger_socket_client_{username}')
    return unique_filename

# 動的にアドレスを生成
address = generate_unique_address()


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

message_history = []

def receive_messages(sock):
    while True:
        try:
            data, _ = sock.recvfrom(4096)
            message_history.append(data.decode())
            message_history.append('\n')
            print("".join(message_history))
            print("メッセージを入力してください（終了するには\"exit\"と入力）：", end="", flush=True)
        except socket.timeout:
            continue
        except Exception as e:
            print(f"受信エラー: {e}")
            break

try:
    # メッセージ受信用のスレッドを開始
    receive_thread = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    receive_thread.start()

    while True:
        message = input('メッセージを入力してください（終了するには"exit"と入力）：')
        if message.lower() == 'exit':
            break
        
        full_message = f'ユーザーネーム: {username}' + '\n' + f'{message}'
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