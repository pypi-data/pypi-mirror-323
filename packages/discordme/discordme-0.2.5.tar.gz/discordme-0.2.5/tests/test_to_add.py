import requests
import discordme
import json

# Récupérer le token
token = discordme.get_token("dealifygg@gmail.com", "QWERTYETOXEM@123")

def get_friends(token):
    url = f'https://discord.com/api/v9/users/@me/relationships'
    headers = {"authorization": token}
    response = requests.get(url, headers=headers)
    friends_data = json.loads(response.text)
    friends = [friend["id"] for friend in friends_data]
    print(friends)

get_friends(token)