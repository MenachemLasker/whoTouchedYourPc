import os
import json
import socket
import hashlib


def hash_sha256(input_string):
    sha_signature = \
        hashlib.sha256(input_string.encode()).hexdigest()
    return sha_signature


def has_followrs(username):
    file_path = ('user_chat_ids.json')
    if os.path.isfile(file_path):
        with (open(file_path, 'r') as infile):
            user_chat_ids = json.load(infile)
            f = user_chat_ids.get(username) != 0 #שגיאה
            return f
    return False


def get_ids(username):
    with open('user_chat_ids.json', 'r') as file:
        user_chat_ids = json.load(file)
        list_chat_id = user_chat_ids[username]
        return list_chat_id


def has_file(name):
    return os.path.isfile(name)


def he_follow(chat_id, username):
    if has_followrs(username):
        for chat_ids in get_ids(username):
            if chat_ids == chat_id:
                return True
    return False


def has_user(username):
    file = "usersPass.json"
    if has_file(file):
        with open(file, 'r') as infile:
            users_pass = json.load(infile)
            return users_pass.get(username)
    return False


def rcv_username(client_socket):
    username = client_socket.recv(1024).decode()
    while has_user(username):
        client_socket.send("0".encode())
        username = client_socket.recv(1024).decode()
    client_socket.send("1".encode())
    return username


def new_user(id_a, username, hashed_pass):
    the_new_user = {
        str(id_a): str(username)
    }
    file = 'users.json'
    if has_file(file):
        with open(file, 'r') as infile:
            users = json.load(infile)
        users.update(the_new_user)
    else:
        users = the_new_user
    with open(file, 'w') as outfile:
        json.dump(users, outfile)
    new_user_and_pass = {
        str(username): str(hashed_pass)
    }
    file = 'usersPass.json'
    if has_file(file):
        with open(file, 'r') as infile:
            users_and_pass = json.load(infile)
        users_and_pass.update(new_user_and_pass)
    else:
        users_and_pass = new_user_and_pass
    with open(file, 'w') as outfile:
        json.dump(users_and_pass, outfile)
    print(f"Data added")


def get_username(id_a):
    with open("users.json", 'r') as infile:
        users = json.load(infile)
    username = users[str(id_a)]
    return username


def ensure_directory(directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)


def verify_user(username, password):
    file = 'usersPass.json'
    if has_file(file):
        with open(file, 'r') as infile:
            users_and_pass = json.load(infile)
            print(users_and_pass[username])
            return users_and_pass[username] == str(hash_sha256(password))
    return False
