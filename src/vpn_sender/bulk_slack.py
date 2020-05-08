import json
import shutil
import slack
import requests
import os
import re
import subprocess
from dotenv import load_dotenv

MESSAGE_TEXT = """Привет!\nЭто — твой конфиг для настройки ВПНки. Она нужна для доступа
               к внутренним ресурсам Бестдоктора из дома (например, к админке).
               Если у тебя уже настроена ВПНка, то ничего делать не надо, а
               это сообщение можно проигнорировать."""
EXISTING_VPN_DIR = 'vpn_profiles'
NEW_VPN_DIR = 'bulk_creation'


def get_workspace_users(token):
    url = 'https://slack.com/api/users.list'
    params = {
        'token': token,
    }
    response = requests.get(url, params=params)
    all_users = response.json()['members']
    users_list = []

    for user in all_users:
        if (
            user['is_bot']
            or user['deleted']
            or user['is_restricted']
            or user['profile'].get('email') is None
            or not user['profile']['email'].endswith('@bestdoctor.ru')
            or user.get('is_invited_user')
            or user['name'] == 'slackbot'
        ):
            continue
        users_list.append({
            'name': re.sub('@.*$', '', user['profile']['email']),
            'email': user['profile']['email'],
            'id': user['id'],
        })
    return users_list


def get_old_configs(path=EXISTING_VPN_DIR):
    old_vpn_list = []
    for _, __, filenames in os.walk(path):
        for filename in filenames:
            old_vpn_list.append(filename.replace('.ovpn', ''))
    return old_vpn_list


def get_users_to_send(_slack_users, _old_configs):
    users_list = []
    for user in _slack_users:
        users_list.append(user['name'])
    users_list = set(users_list)
    _old_configs = set(_old_configs)
    _users_to_send = list(users_list - _old_configs)
    return _users_to_send


def make_config(user_list, playbook_path, _hosts):
    process = subprocess.Popen(
        [
            'ansible-playbook',
            '-i {0},'.format(_hosts),
            '-e',
            '{0}'.format(json.dumps({'users_to_create': user_list})),
            '{0}'.format(playbook_path),
            '-vvvv',
        ],
    )
    data = process.communicate()
    return data


def send_message(chat_id, path_to_file, text=MESSAGE_TEXT):
    client.files_upload(
        channels=chat_id,
        file=path_to_file,
        title=os.path.basename(path_to_file),
        filename=os.path.basename(path_to_file),
        initial_comment=text,
    )


def move_files():
    for dirpath, _, filenames in os.walk(NEW_VPN_DIR):
        for filename in filenames:
            filename = os.path.join(dirpath, filename)
            shutil.move(filename, EXISTING_VPN_DIR)


def start_sender(token, _hosts, _playbook):
    slack_users = get_workspace_users(token)
    old_configs = get_old_configs(EXISTING_VPN_DIR)
    users_to_send = get_users_to_send(slack_users, old_configs)
    make_config(users_to_send, _playbook, _hosts)
    for user_to_send in users_to_send:
        for slack_user in slack_users:
            if slack_user['name'] == user_to_send:
                path_file = os.path.join(NEW_VPN_DIR, (slack_user['name'] + '.ovpn'))
                send_message(slack_user['id'], path_to_file=path_file)
    move_files()


if __name__ == '__main__':
    load_dotenv()

    slack_token = os.getenv('SLACK_TOKEN')
    playbook = os.getenv('PLAYBOOK')
    hosts = os.getenv('HOSTS')
    client = slack.WebClient(token=slack_token)

    try:
        os.mkdir(EXISTING_VPN_DIR)
        os.mkdir(NEW_VPN_DIR)
    except FileExistsError:
        pass

    start_sender(slack_token, hosts, playbook)
