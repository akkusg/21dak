import datetime
import pytz


class User:
    def __init__(self, user_dict):
        self.id = user_dict.get('_id')
        self.name = user_dict.get('name')
        self.surname = user_dict.get('surname')
        self.email = user_dict.get('email')
        self.password = user_dict.get('password')
        self.address = user_dict.get('address')
        self.phone = user_dict.get('phone')
        self.tckn = user_dict.get('tckn')
        self.expireDate = user_dict.get('expireDate')
        self.isAdmin = user_dict.get('isAdmin') if user_dict.get('isAdmin') is not None else False
        self.isTrainer = user_dict.get('isTrainer') if user_dict.get('isTrainer') is not None else False

    def isVip(self):
        utc = pytz.UTC
        expire = self.expireDate
        if expire is not None:
            if expire.tzinfo is None or expire.tzinfo.utcoffset(expire) is None:
                expire = utc.localize(expire)
            now = utc.localize(datetime.datetime.now())
            return expire > now
        return False
