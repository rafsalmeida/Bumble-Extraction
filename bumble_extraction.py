
import sqlite3 as sql
from flask import Flask, render_template
import argparse
import json
import os

parser=argparse.ArgumentParser(description='Bumble Script')
parser.add_argument("-d", "--directory", required=True,  help="Path to Bumble's private directory")
args=parser.parse_args()

pathBumble = args.directory+"/files/c2V0dGluZ3M="
print(pathBumble)

if(os.path.exists(pathBumble)):
   with open(pathBumble,encoding="UTF-8", errors="ignore") as lst:
      datafile = lst.readlines()
      for line in datafile:
         if 'user_media@' in line:
            nameUser=line[16:len(line)] 
         if 'server_get_user' in line:
            index=line.find("https")
            Finalindex=line.find("t=");  
            avatar=line[index:Finalindex+12]
            imageUser=avatar
else:
   print("Error! The path was not found. Example of a valid path: /home/user/com.bumble.app. If you're using Windows, please use "" in the directory path.")
   exit();

database=args.directory+"/databases/ChatComDatabase"
connection = sql.connect(database)

# cursor
crsr = connection.cursor()
crsr.execute("SELECT id, conversation_id, sender_name, created_timestamp, payload, sender_avatar_url, is_incoming, payload_type FROM message ORDER BY conversation_id, created_timestamp")
msgs = crsr.fetchall()


all_msgs=[]
for msg in msgs:

   username=""
   image_url=""
   if msg[6]==0:
      username=nameUser.strip()
      image_url=imageUser
   
   crsr.execute("SELECT user_id , gender, user_name, user_image_url, age FROM conversation_info ORDER BY user_id")

   info = crsr.fetchall()
   for inf in info:
      if(msg[1] == inf[0] and msg[6]==1):
         image_url = inf[3]
         username = inf[2]

   payload_type = msg[7]
   if username == "":
      username = "Unknown"
   if image_url == "":
      image_url = "Unknown"

   if payload_type == "TEXT":
      all_msgs.append({"id": msg[0], "conversation_id": msg[1], "sender_name": username, "created_timestamp":msg[3], "text":json.loads(msg[4])['text'], "sender_avatar_url":image_url, "is_incoming":msg[6], "payload_type":msg[7]})
      dict_obj = json.loads(msg[4])
   elif payload_type == "QUESTION_GAME":
      all_msgs.append({"id": msg[0], "conversation_id": msg[1], "sender_name": username, "created_timestamp":msg[3], 
      "text":"Question: "+json.loads(msg[4])['text']+". Own answer: "+ json.loads(msg[4])['answer_own'] + ". Answer: " + json.loads(msg[4])['answer_other'] + "."
      , "sender_avatar_url":image_url, "is_incoming":msg[6], "payload_type":msg[7]})

   elif(payload_type == "IMAGE"):
      all_msgs.append({"id": msg[0], "conversation_id": msg[1], "sender_name": username, "created_timestamp":msg[3], 
      "text":"No access to the picture sent." , "sender_avatar_url":image_url, "is_incoming":msg[6], "payload_type":msg[7]})
   elif(payload_type == "AUDIO"):
      all_msgs.append({"id": msg[0], "conversation_id": msg[1], "sender_name": username, "created_timestamp":msg[3], 
      "text":"No access to the audio sent.", "sender_avatar_url":image_url, "is_incoming":msg[6], "payload_type":msg[7]})
   elif(payload_type == "GIF"):
      all_msgs.append({"id": msg[0], "conversation_id": msg[1], "sender_name": username, "created_timestamp":msg[3], "text":json.loads(msg[4])['url'], "sender_avatar_url":image_url, "is_incoming":msg[6], "payload_type":msg[7]})
   
   elif(payload_type == "VIDEO_CALL"):
      all_msgs.append({"id": msg[0], "conversation_id": msg[1], "sender_name": username, "created_timestamp":msg[3], "text":"Duration of videocall: " + str(json.loads(msg[4])['duration']) + " seconds.", "sender_avatar_url":image_url, "is_incoming":msg[6], "payload_type":str(msg[7])})
   

connection.close()

app = Flask(__name__)
jsonmsg2=json.dumps(all_msgs)
@app.route("/")
def hello_world():
   return render_template('index.html', entries=jsonmsg2)

if __name__ == "__main__":
    app.run()



