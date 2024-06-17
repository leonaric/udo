from flask import Flask, render_template, request, redirect
from vsldata import Database
import cv2
import time
import os
import threading
from imgbeddings import imgbeddings
from PIL import Image
from scipy.spatial.distance import cityblock
import socket
import math
import base64
import random


app = Flask(__name__)
db = Database("db\\db-user.db")
cascade = cv2.CascadeClassifier("static\haarcascade.xml")
bd = imgbeddings()
match_val = 0
user = ""
max_tries = 0
cropped = False
decryptFM = {"0":"gfTE","1":"JKbZ","2":"$RFe","3":"&Uii","4":"QW)(","5":"//We","6":"eeRT","7":"JKMf","8":"oo$$","9":"##Yt",".":"%#@!"}
ON_VPN = False
VPN_KEY = random.randint(5555, 99999)
vpn_port = 4444
auth_key = ""
n_size = 100
face_recognized = False
timer = 5
localhost = socket.gethostname()
global_ip = socket.gethostbyname(localhost)


def photo_write(base64_encoding, path):
    name_tt = 0
    for base in base64_encoding:
        if len(base) > 0:
            with open(f"db/FR_DB/{path}/{name_tt}.png", "wb") as wph:
                photo = base64.b64decode(base)
                wph.write(photo)
        name_tt += 1
    get_face = threading.Thread(target=gen_list, args=(f"db/FR_DB/{path}",))
    get_face.start()
    get_face.join()

def gen_list(path):
    global n_size

    for image in os.listdir(path):
        # walk through every image to find faces and crop

        img_path = path+"\\"+image
        cv_img = cv2.imread(img_path, 0)
        cv_bw = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)

        face = cascade.detectMultiScale(cv_bw, scaleFactor=1.05, minNeighbors=5, minSize=(50, 50))
        # cropping the images
        multiscaler = 0

        for x,y,w,h in face:

            crp_img = cv_img[y:(y+h), x+10:(x+w-10)]
            o_height , o_width = crp_img.shape
            n_height = o_height - (o_width - n_size)
            crp_img = cv2.resize(crp_img, (n_size, n_height))
            tar_file = path+"\\"+image[:image.find(".") - multiscaler] + ".png"
            multiscaler+=1

            # break

            cv2.imwrite(tar_file, crp_img)
            if True:
                time.sleep(1)
                print(f"succesfull: {multiscaler}")
                # os.rmdir(f"{path}\\{n_size}.png")


# def createAuth():
#     global auth_key
#     global IPAddress
#     for i in IPAddress:
#         for a, b in decryptFM.items():
#             if i == a:
#                 auth_key+= b
#                 break

def save_face():
    global match_val
    global cropped

    # cv2.imwrite("db/FR_DB/"+user+"/"+user+str(cap)+".jpg", frame)

    frame = cv2.imread("db/FR_DB/"+user+"/"+user+".png", 0)
    c_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    c_face = cascade.detectMultiScale(c_gray, scaleFactor=1.05,minNeighbors=2, minSize=(100, 100))

    for x, y, w, h in c_face:
        img_diff = 0
        img_total = 0

        c_cropped = c_gray[y:(y+h), x+20:(x+w-20)]
        o_height , o_width, _ = c_cropped.shape
        n_height = o_height - (o_width - 100)
        c_cropped = cv2.resize(c_cropped, (100, n_height))
        cv2.imwrite("db/FR_DB/"+user+"/"+user+".png", c_cropped)
        cropped = True

        time.sleep(1)
        c_cropped = Image.open("db/FR_DB/"+user+"/"+user+".png")
        c_bd = bd.to_embeddings(c_cropped)
        c_bd = c_bd.flatten()
        for db_images in os.listdir("db/FR_DB/"+user):
            if user not in db_images:
                db_path = os.path.join("db/FR_DB/"+user, db_images)
                db_img = Image.open(db_path)
                db_arr = bd.to_embeddings(db_img)
                db_arr = db_arr.flatten()
                dist = cityblock(db_arr, c_bd)
                img_diff += math.floor(dist)
                img_total += 1

        match_val = ((img_diff/img_total)/100) + 0.1
        print(match_val)
        match_val = math.ceil(match_val)
        # return match_val
        # match_val = (match_val/len(os.listdir("db/FR_DB/"+user)))
        # print(match_val, len(os.listdir("db/FR_DB/"+user)))


@app.route("/")
def index():
    # global IPAddress
    # IPAddress = request.remote_addr
    # createAuth()
    # print(IPAddress, auth_key)
    return render_template("index.html")

@app.route("/home")
def home():
        global face_recognized
        global ON_VPN
        if user == "admin" and ON_VPN and face_recognized:
            return render_template("admin.html")
        elif ON_VPN and user != "admin" and face_recognized:
            return render_template("LAN_index.html")
        else:
            return render_template("404page.html")

@app.route("/face_recog", methods=["POST"])
def fralgo():
    global user
    global max_tries
    global face_recognized
    data = request.get_json()

    fr = base64.b64decode(data["data"])
    
    if os.path.exists("db/FR_DB/"+user):
        with open("db/FR_DB/"+user+"/"+user+".png", "wb") as wb:
            wb.write(fr)

        # for cap in range(0, 3, 1):
        #     vidCap = cv2.VideoCapture(0)
        #     val, frame = vidCap.read()
        #     vidCap.release()

        get_face = threading.Thread(target=save_face)
        get_face.start()
        get_face.join()

        # face_val = save_face()
        # time.sleep(3)

        #     if os.path.exists("db/FR_DB/"+user+"/"+user+str(cap)+".jpg"):
        #         os.remove("db/FR_DB/"+user+"/"+user+str(cap)+".jpg")
        #     print(match_val)

        if match_val <= 2 and match_val > 0 and cropped:
            print(f"MATCH : {match_val}")
            face_recognized = True
            with open("active_users.db", "r") as rdb:
                all_users = rdb.read()
                if f"...{user}\n" in all_users:
                    return "Error someone has already logged in with that username"
                else:
                    with open("active_users.db", "a") as rdb:
                        rdb.write(f"...{user}\n")
                    return "MATCH"
        elif match_val > 2:
            print(f"NO MATCH : {match_val}")
            max_tries += 1
            face_recognized = False
            return "NO MATCH"
        else:
            face_recognized = False
            return "Internal error please try again"

    else:
        return "NO DB"
        

@app.route("/get_pass", methods=["POST"])
def get_post():
    global user
    global max_tries
    data = request.get_json()
    print(data)

    username = data["user"]
    password = data["pass"]

    if db.isindb("name", username) and max_tries < 5:
        print(db.isindb("name", username), username, db.findrow(username, password))
        if db.findrow(username, password) and max_tries < 5:
            user = username

            return "confirmed"
        else:
            max_tries += 1
            return "password"
    elif max_tries >= 5:
        return render_template("404page.html")
    else:
        max_tries += 1
        return "unconfirmed"
    
@app.route("/get_auth", methods=["POST"])
def get_auth():
    global VPN_KEY
    if len(user) > 0:
        return str(VPN_KEY)
    else:
        return "2288889"

@app.route("/connect_vpn", methods=["POST"])
def get_conn():
    user_ip = request.remote_addr
    message = request.form.get("message")
    if message == user_ip:
        ON_VPN = True
        print("CONNECTED")
        return vpn_port
    else:
        ON_VPN = False
        return "Server not connected"
    
@app.route("/add_user", methods=["POST"])
def add_user():
    if ON_VPN:
        global db
        data = request.get_json()
        new_id = data["id"]
        new_pass = data["pass"]
        photo_db = data["photos"].split("$$$")

        print(new_id, new_pass, len(photo_db))
        if db.isindb("name", new_id):
            return "failed"
        else:
            db.append(new_id, new_pass)
            os.mkdir(f"db/FR_DB/{new_id}")
            photo_write(photo_db, new_id)

            return "success"
    
@app.route("/update", methods=["POST"])
def update():
    global OLD
    while True:
        time.sleep(0.5)
        with open("LAN_chat.coord" , "r") as readLan:
            LANDB = readLan.read()
            LANDB = LANDB.split("\n")
            NEW = LANDB[len(LANDB) - 1]
            if OLD != NEW:
                OLD = NEW
                VALUE = NEW.split("&&")
                if VALUE[0] != user:
                    return NEW
                else:
                    return f"name&&&{user}"
                
@app.route("/update_users", methods=["POST"])
def update_u():
    while True:
        time.sleep(2)
        with open("active_users.db", "r") as rdb:
            return rdb.read()

@app.route("/LAN_chat", methods=["POST"])
def func():
    text = request.get_json()["message"]
    with open("user_chats.db", "a") as adb:
        adb.write(f"{user}&&{text}\n")

@app.route("/api", methods=["POST"])
def returnValid():
    global VPN_KEY
    global timer
    global ON_VPN
    data = request.get_json()
    api_key = data["item"]
    # with open("keys.db", "r") as rdb:
    #     keys = rdb.read()
    if f"{user}{VPN_KEY}" == api_key :
        ON_VPN = True
        timer = 5
        return "Connected"
    elif api_key == "disc":
        ON_VPN = False
        return ""
    else:
        return ""

@app.route("/logout", methods=["POST"])
def logout():
    global match_val
    global user
    global max_tries
    global cropped
    global ON_VPN
    global n_size
    global timer
    global OLD
    global face_recognized

    match_val = 0
    user = ""
    max_tries = 0
    cropped = False
    face_recognized = False
    n_size = 100
    timer = 5
    OLD = ""

    with open("active_users.db", "r") as rdb:
        database = rdb.read()
    with open("active_users.db", "w") as wdb:
        if f"\n...{user}" in database:
            database = database.replace( f"\n...{user}", "")
            wdb.write(database)
        return "logged out"

if __name__ == "__main__":
    app.run(port=vpn_port, ssl_context=("cert.pem", "key.pem"),
            host=global_ip,
            debug=False)