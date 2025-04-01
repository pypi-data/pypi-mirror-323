import discordme
import time

user_id = 1234567891012 #User id
token = discordme.get_token("wathd_developement@proton.me", "QWERTYETOXEM@123") #Or put your token directly

discordme.block_user(user_id, token)
time.sleep(3600) #1 hour
discordme.unblock_user(user_id, token)