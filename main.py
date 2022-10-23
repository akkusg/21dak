from datetime import datetime
import hashlib
import dateutil.parser
from dateutil.relativedelta import relativedelta
from pymongo import ReturnDocument

import initialize_checkout
import complete_checkout

from flask import Flask, render_template, request, redirect, session
import pymongo
from bson.objectid import ObjectId
from admin import admin

from classes.User import User

app = Flask(__name__)
app.secret_key = 'bizim cok zor gizli sozcugumuz'
# Blueprints
app.register_blueprint(admin)

myclient = pymongo.MongoClient("mongodb://mongouser:123321@localhost:27017/")
mydb = myclient["PersonalTrainer"]
users_table = mydb["Users"]
loginLogs = mydb["LoginLogs"]
subscriptions_table = mydb["Subscriptions"]
payment_logs = mydb["PaymentLogs"]
initialize_checkout = initialize_checkout
complete_checkout = complete_checkout
events_table = mydb["Events"]
classes_table = mydb["Classes"]
videos_table = mydb["Videos"]
trainers_table = mydb["Trainers"]

mesajlar_tablosu = mydb["mesajlar"]


def get_sequence(seq_name):
    return mydb.Counters.find_one_and_update(filter={"_id": seq_name},
                                             update={"$inc": {"seq": 1}},
                                             upsert=True)["seq"]


@app.context_processor
def utility_functions():
    def print_in_console(message):
        print(str(message))

    return dict(mdebug=print_in_console)


@app.route('/')
def homepage():
    trainer_list = list(trainers_table.find())
    class_list = list(classes_table.find())    
    user = None
    if 'user' in session:
        user_dict = session["user"]
        user_dict = users_table.find_one({"_id": user_dict["_id"]})
        del user_dict['password']
        session["user"] = user_dict
        user = User(user_dict)
        username = user.name + "" + user.surname
        print("username:", username)
        is_vip = user.isVip()
        print("isVip:", is_vip)        
    return render_template("homepage.html", user=user, trainer_list=trainer_list, class_list=class_list, active_page=1)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.pbkdf2_hmac(
            'sha256', # The hash digest algorithm for HMAC
            password.encode('utf-8'), # Convert the password to bytes
            username, # Provide the salt
            100000, # It is recommended to use at least 100,000 iterations of SHA-256 
            dklen=128 # Get a 128 byte key
        )
        user = users_table.find_one({"_id": username})
        if user:
            if hashed_password == user["password"]:
                del user['password']
                session["user"] = user
                update_last_login_time(user)
                loginLogs.insert_one({"username": username, "time": datetime.now()})
                return redirect("/", code=302)
            else:
                loginLogs.insert_one({"username": username, "errorMessage": "Wrong Password", "time": datetime.now()})
                return "Wrong Password"
        else:
            return "User Not Found"
    else:
        return render_template("login.html")


def update_last_login_time(user_dict):
    user_filter = {'_id': user_dict.get('_id')}
    newvalues = {"$set": {"lastLoginDate": datetime.now()}}
    users_table.update_one(user_filter, newvalues)


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/", code=302)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = dict(request.form)
        user["_id"] = user["email"]
        user["password"] = hashlib.pbkdf2_hmac(
            'sha256', # The hash digest algorithm for HMAC
            user["password"].encode('utf-8'), # Convert the password to bytes
            user["_id"], # Provide the salt
            100000, # It is recommended to use at least 100,000 iterations of SHA-256 
            dklen=128 # Get a 128 byte key
        )
        user["expireDate"] = datetime.now()
        if len(user["promo_code"]) > 0:
            promo = mydb["PromoCodes"].find_one({"_id": user["promo_code"]})
            if promo and promo["remaining_use"] > 0:
                user["expireDate"] = datetime.now() + relativedelta(days=+promo["promo_days"])
                mydb["PromoCodes"].update_one({"_id": promo["_id"]}, {"$inc": {"remaining_use": -1}})

        users_table.insert_one(user)
        return redirect("/login", code=302)
    else:
        return render_template("register.html")


@app.route('/createPromoCode', methods=['GET', 'POST'])
def createPromoCode():
    if request.method == 'POST':
        promo = dict(request.form)
        if len(list(mydb["PromoCodes"].find({"_id": promo["promo_code"]}))) > 0:
            return "Bu kod zaten kullanılmış. <button onclick='history.back()'>Geri</button>"
        m_promo = dict()
        m_promo["_id"] = promo["promo_code"]
        m_promo["max_number_of_use"] = int(promo["max_number_of_use"])
        m_promo["promo_days"] = int(promo["promo_days"])
        m_promo["remaining_use"] = int(promo["max_number_of_use"])
        mydb["PromoCodes"].insert_one(m_promo)

        return "OK"
    else:
        user_dict = session["user"]
        user = User(user_dict)
        return render_template("createPromoCode.html", user=user)


@app.route('/subscriptions', methods=['GET'])
def subscriptions():
    user = session["user"]
    subscriptionList = list(subscriptions_table.find())
    return render_template("subscriptions.html", user=user, subscriptions=subscriptionList)


@app.route('/initializeCheckout', methods=['GET', 'POST'])
def initializeCheckout():
    if 'user' in session:
        user = session["user"]
        args = request.args
        subscription_id = args["id"]
        subscription = subscriptions_table.find_one({"_id": subscription_id})
        if subscription:
            pricingPlanReferenceCode = subscription.get("referenceCode")

            shippingAddress = initialize_checkout.initialize_address(user.get("name"), user.get("city"),
                                                                     user.get("address"))
            customer = initialize_checkout.initialize_customer(user.get("name"), user.get("surname"),
                                                               user.get("email"), user.get("phone"), user.get("tckn"), shippingAddress,
                                                               shippingAddress)

            callbackUrl = "http://18.195.148.197:8000/completeCheckout?id=" + subscription_id

            responseDict = initialize_checkout.initialize_checkout_form(pricingPlanReferenceCode,
                                                                        customer,
                                                                        callbackUrl)
            checkoutFormContent = responseDict.get("checkoutFormContent")
            return checkoutFormContent

        else:
            return redirect("/")
    else:
        return render_template("login.html")


@app.route('/completeCheckout', methods=['POST'])
def completeCheckout():
    if 'user' in session:
        user_dict = session["user"]
        user = User(user_dict)
        args = request.args
        subscriptionId = args["id"]
        subscription = subscriptions_table.find_one({"_id": subscriptionId})
        if subscription:
            duration_month = subscription.get("durationMonth")
            responseForm = dict(request.form)
            token = responseForm.get("token")
            if token is not None:
                paymentLog = complete_checkout.complete_checkout_form(token)
                payment_logs.insert_one(paymentLog)
                if user.isVip():
                    user_dict["expireDate"] = user.expireDate + relativedelta(months=+duration_month)
                else:
                    user_dict["expireDate"] = datetime.now() + relativedelta(months=+duration_month)
                user_filter = {'_id': user.id}
                newvalues = {"$set": {"expireDate": user_dict.get('expireDate')}}
                users_table.update_one(user_filter, newvalues)
                session["user"] = user_dict
                return redirect("/")
            else:
                return redirect("/")


@app.route('/calendar')
def calendar():
    if 'user' not in session:
        return redirect("/login", code=302)
    else:
        user_dict = session["user"]
        user = User(user_dict)
        username = user.name + "" + user.surname
        print("username:", username)
        is_vip = user.isVip()
        print("isVip:", is_vip)
        videos = list(videos_table.find())
        classes = classes_table.find()
        return render_template("calendar.html", user=user, videos=videos, classes=classes, active_page=5)


@app.route('/insertEvent', methods=['POST'])
def insertEvent():
    if 'user' not in session:
        return redirect("/login", code=302)
    else:
        user_dict = session["user"]
        user = User(user_dict)
        event = request.get_json()
        print("Before:")
        print(event)
        start_date = dateutil.parser.parse(event.get('start'))
        event["start"] = start_date.isoformat()
        if 'end' not in event or event.get('end') is None:
            end_date = start_date + relativedelta(hours=+1)
        else:
            end_date = dateutil.parser.parse(event.get('end'))
        event["end"] = end_date.isoformat()
        event["_id"] = get_sequence("Event")
        print("After:")
        print(event)

        res = events_table.insert_one(event)
        print(str(res.inserted_id))
        return str(res.inserted_id)


@app.route('/updateEvent', methods=['POST'])
def updateEvent():
    if 'user' not in session:
        return redirect("/login", code=302)
    else:
        user_dict = session["user"]
        user = User(user_dict)
        event = request.get_json()
        start_date = dateutil.parser.parse(event.get('start'))
        event["start"] = start_date.isoformat()
        if 'end' not in event or event.get('end') is None:
            end_date = start_date + relativedelta(hours=+1)
        else:
            end_date = dateutil.parser.parse(event.get('end'))
        event["end"] = end_date.isoformat()
        filter = {'_id': int(event["_id"])}
        newvalues = {"$set": {'start': event.get('start'), 'end': event.get('end')}}
        print("newvalues", newvalues)
        res = events_table.update_one(filter, newvalues)
        print(res.modified_count)
        return "OK"


@app.route('/all-users', methods=['GET'])
def all_users():
    if 'user' not in session:
        return redirect("/login", code=302)
    else:
        user_dict = session["user"]
        user = User(user_dict)
        if user.isAdmin:
            user_list = list(users_table.find())
            return render_template("allUsers.html", user=user, user_list=user_list)
        else:
            return redirect("/")


@app.route('/users-week-old', methods=['GET'])
def users_week_old():
    if 'user' not in session:
        return redirect("/login", code=302)
    else:
        user_dict = session["user"]
        user = User(user_dict)
        if user.isAdmin:
            week_ago = datetime.now() + relativedelta(days=-7)
            user_list = list(users_table.find({"lastLoginDate": {"$lt": week_ago}}).sort("lastLoginDate"))
            return render_template("allUsers.html", user=user, user_list=user_list)
        else:
            return redirect("/")


@app.route('/profil/<profilno>')
def profil_goster(profilno):
    if 'user' not in session:
        return redirect("/login", code=302)
    else:
        if profilno == "1":
            adsoyad = "Jane Doe"
        else:
            adsoyad = "John Doe"
        return render_template("profil.html", adsoyad=adsoyad)


@app.route('/mesajkaydet', methods=['POST'])
def mesaj_kaydet():
    adsoyad = request.form.get('adsoyad')
    email = request.form.get('email')
    konu = request.form.get('konu')
    mesaj = request.form.get('mesaj')

    kayit = {"adsoyad": adsoyad, "email": email, "konu": konu, "mesaj": mesaj}
    kaydedilmis = mesajlar_tablosu.insert_one(kayit)
    print(kaydedilmis.inserted_id)
    #return redirect("/mesajlar", code=302)
    return "OK" # "Sayın " + adsoyad + ". Mesajınız için teşekkürler. Tüm mesajlar için tıklayın."


@app.route('/mesajlar')
def mesajlar():
    if 'user' not in session:
        return redirect("/login", code=302)
    else:
        user_dict = session["user"]
        user = User(user_dict)

    mesaj_listesi = list(mesajlar_tablosu.find())
    return render_template("mesajlar.html", mesaj_listesi=mesaj_listesi, user=user, active_page=6)


@app.route('/classes')
def classes():
    if 'user' not in session:
        return redirect("/login", code=302)
    else:
        user_dict = session["user"]
        user = User(user_dict)
        username = user.name + "" + user.surname
        print("username:", username)
        is_vip = user.isVip()
        print("isVip:", is_vip)
        return render_template("classes.html", user=user, active_page=2)


@app.route('/trainers')
def trainers():
    if 'user' not in session:
        return redirect("/login", code=302)
    else:
        user_dict = session["user"]
        user = User(user_dict)
        username = user.name + "" + user.surname
        print("username:", username)
        is_vip = user.isVip()
        print("isVip:", is_vip)
        return render_template("trainers.html", user=user, active_page=3)


@app.route('/videos')
def videos():
    if 'user' not in session:
        return redirect("/login", code=302)
    else:
        user_dict = session["user"]
        user = User(user_dict)
        is_vip = user.isVip()
        video_list = list(videos_table.find())
        now_time = datetime.now()
        if 'id' in request.args:
            videoId = request.args.get('id')
            objId = ObjectId(videoId)
            selected_video = videos_table.find_one({"_id": objId})
            if selected_video:
                return render_template("videos.html", user=user, videos=video_list,
                                       now_time=now_time, selected_video=selected_video)

        return render_template("videos.html", user=user, videos=video_list, now_time=now_time, active_page=4)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
