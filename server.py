import datetime
import io
import random
import socket
import threading
from botTelegram import *
from PIL import Image
from usersManger import *


def handle_client_connection(client_socket):
    try:
        #create_keys()
        #public_key = load_key("public_key.pem")
        #send_public_key(client_socket, public_key)
        char_value = client_socket.recv(1)
        have_id = char_value.decode() == '1'
        if not have_id:
            id_a = bytes([random.randint(0, 255) for _ in range(1024)])
            client_socket.send(id_a)
            username = rcv_username(client_socket)
            hashed_pass = client_socket.recv(1024)
            hashed_pass = hashed_pass.decode('utf-8')
            new_user(str(id_a), username, str(hashed_pass))
        else:
            id_a = bytes(client_socket.recv(1024))
            username = get_username(id_a)
            print("hi " + username)
            image_stream = io.BytesIO()
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                image_stream.write(data)

            image_stream.seek(0)
            image = Image.open(image_stream)

            now = datetime.datetime.now()
            formatted_date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
            directory_name = f'images_{username}'
            ensure_directory(directory_name)
            image_path = os.path.join(directory_name, f'image_{formatted_date_time}.png')
            image.save(image_path)
            image.show()
            if has_followrs(username):
                for chat_id in get_ids(username):
                    bot.send_message(chat_id, f"המשתמש {username} נכנס לשרת.")
                    bot.send_photo(chat_id, image)

    except Exception as e:
        print(e)
        print("err")
    finally:
        client_socket.close()


def main():
    threading.Thread(target=start_bot).start()
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 5010))
    server_socket.listen(5)

    try:
        while True:
            client_sock, address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client_connection, args=(client_sock,))
            client_thread.start()
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
