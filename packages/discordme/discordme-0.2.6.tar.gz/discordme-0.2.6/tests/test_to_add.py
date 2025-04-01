import requests
import discordme
import json

# Récupérer le token
token = discordme.get_token("skylookup.shop@proton.me", "QWERTYETOXEM@123")

def join_server(invite, token):
    url = f'https://discord.com/api/v9/invites/{invite}'
    headers = {"authorization": token}
    response = requests.post(url, headers=headers)
    print(response.text)

join_server("dealify", token)
