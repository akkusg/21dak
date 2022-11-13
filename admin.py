from flask import Blueprint, render_template, redirect, session, request
import pymongo
from classes.User import User
from datetime import datetime
import dateutil.parser
import pytz

admin = Blueprint('admin', __name__, url_prefix='/admin', static_folder='admin/static')
# myclient = pymongo.MongoClient("mongodb://mongouser:123321@localhost:27017/")
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["PersonalTrainer"]
users_table = mydb["Users"]
videos_table = mydb["Videos"]
promo_codes_table = mydb["PromoCodes"]


@admin.route('/')
@admin.route('/dashboard')
def dashboard():
    print("Static Folder:", admin.static_folder)
    print("Static Url Path:", admin.static_url_path)
    print("Root Url Path:", admin.root_path)
    if 'user' in session:
        user_dict = session["user"]
        user_dict = users_table.find_one({"_id": user_dict["_id"]})
        del user_dict['password']
        session["user"] = user_dict
        user = User(user_dict)
        if user.isAdmin:
            user_list = list(users_table.find())
            normal_user_list = list(filter(lambda current_user: is_user_dict_vip(current_user) is False, user_list))
            vip_user_list = list(filter(lambda current_user: is_user_dict_vip(current_user) is True, user_list))
            return render_template("admin/dashboard.html", user=user, user_list=user_list,
                                   vip_user_count=len(vip_user_list),
                                   normal_user_count=len(normal_user_list), active_page=1)
        else:
            return redirect("/login", code=302)
    else:
        return redirect("/login", code=302)


def is_user_dict_vip(user_dict):
    user = User(user_dict)
    return user.isVip()


@admin.route('/users')
def admin_user_list():
    if 'user' in session:
        user_dict = session["user"]
        user_dict = users_table.find_one({"_id": user_dict["_id"]})
        del user_dict['password']
        session["user"] = user_dict
        user = User(user_dict)
        if user.isAdmin:
            user_list = list(users_table.find())
            return render_template("admin/users.html", user=user, user_list=user_list, active_page=1)
        else:
            return redirect("/login", code=302)
    else:
        return redirect("/login", code=302)


@admin.route('/add-video', methods=['GET', 'POST'])
def add_video():
    if 'user' not in session:
        return redirect("/login", code=302)
    else:
        user_dict = session["user"]
        user_dict = users_table.find_one({"_id": user_dict["_id"]})
        del user_dict['password']
        session["user"] = user_dict
        user = User(user_dict)
        if user.isAdmin:
            if request.method == 'GET':
                video_list = list(videos_table.find())
                return render_template("admin/addVideo.html", user=user, videos=video_list, active_page=4)
            else:
                video_title = request.form['videoTitle']
                video_url = request.form['videoUrl']

                premierStartDate = dateutil.parser.parse(request.form['premierStartDate'])
                premierEndDate = dateutil.parser.parse(request.form['premierEndDate'])

                turkey = pytz.timezone('Europe/Istanbul')
                if premierStartDate.tzinfo is None or premierStartDate.tzinfo.utcoffset(premierStartDate) is None:
                    premierStartDate = turkey.localize(premierStartDate)

                if premierEndDate.tzinfo is None or premierEndDate.tzinfo.utcoffset(premierStartDate) is None:
                    premierEndDate = turkey.localize(premierEndDate)

                video_url = video_url.replace("https://www.youtube.com/watch?v=", "https://www.youtube.com/embed/")
                video_url += "?rel=0"
                video = {"title": video_title, "url": video_url, "date": datetime.now(),
                         "premierStartDate": premierStartDate, "premierEndDate": premierEndDate}
                videos_table.insert_one(video)
            return redirect("/admin/add-video")
        else:
            return redirect("/")


@admin.route('/create-promo-code', methods=['GET', 'POST'])
def create_promo_code():
    if request.method == 'POST':
        promo = dict(request.form)
        if len(list(promo_codes_table.find({"_id": promo["promo_code"]}))) > 0:
            return "Bu kod zaten kullanılmış. <button onclick='history.back()'>Geri</button>"
        m_promo = dict()
        m_promo["_id"] = promo["promo_code"]
        m_promo["max_number_of_use"] = int(promo["max_number_of_use"])
        m_promo["promo_days"] = int(promo["promo_days"])
        m_promo["remaining_use"] = int(promo["max_number_of_use"])
        promo_codes_table.insert_one(m_promo)

        return redirect("/admin/create-promo-code")
    else:
        user_dict = session["user"]
        user = User(user_dict)
        promo_codes = list(promo_codes_table.find())
        return render_template("admin/createPromoCode.html", user=user, promo_codes=promo_codes)
