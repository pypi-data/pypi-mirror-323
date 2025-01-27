import requests
import discordme
import json

# Récupérer le token
token = discordme.get_token("skylookup.shop@proton.me", "QWERTYETOXEM@123")

def typing(user_channel_id, token):
    url = f'https://discord.com/api/v9/channels/{user_channel_id}/typing'
    headers = {"authorization": token}
    response = requests.post(url, headers=headers)

typing(1333073110802628659, token)
