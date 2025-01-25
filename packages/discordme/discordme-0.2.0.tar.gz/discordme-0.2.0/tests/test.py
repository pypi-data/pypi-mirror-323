import discordme
import requests

token = discordme.get_token("wathd_developement@proton.me", "QWERTYETOXEM@123")

def reply_mp(message, user_channel_id, message_id, token):
    url = f'https://discord.com/api/v9/channels/{user_channel_id}/messages'
    headers = {"authorization": token}
    data = {
        "content": message,
        "message_reference": {
            "channel_id": user_channel_id,
            "message_id": message_id
        }
    }
    response = requests.post(url, json=data, headers=headers)

reply_mp("this is a  reply", 1332372099154575446, 1332400031948607529, token)