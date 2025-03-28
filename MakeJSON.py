import json


def write_to_json():
    dict_to_write = { "email_address": "example@example.com",
    "email_password": "password",
    "default_to_email": 'example@example.com',
    "default_subject": 'Subject',
    "smtp_server": "server address",
    "smtp_port": 587}
    json_dict = json.dumps(dict_to_write)

    with open('email_info.json', 'w', encoding='utf-8') as f:
        json.dump(json_dict, f, ensure_ascii=False, indent=4)

def read_json():

    with open('email_info.json') as f:
        json_string = json.load(f)
    new_dict = json.loads(json_string)
    print(new_dict)

write_to_json()
