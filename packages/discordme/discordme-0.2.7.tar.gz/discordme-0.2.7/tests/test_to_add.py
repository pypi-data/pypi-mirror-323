import requests
import discordme
import json

# Récupérer le token
token = discordme.get_token("wathd_developement@proton.me", "QWERTYETOXEM@123")

def unblock_user(user_id, token):
    url = f'https://discord.com/api/v9/users/@me/relationships/{user_id}'
    headers = {"authorization": token}
    response = requests.delete(url, headers=headers)
    print(response.text)


unblock_user(1301295022892646486, token)
