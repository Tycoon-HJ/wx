import random
from time import localtime
from requests import get, post
from datetime import datetime, date
from zhdate import ZhDate
import sys
import os


def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)


def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    return access_token


# 获取星座的信息
def get_constellation(key, consName):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    region_url = ("http://web.juhe.cn/constellation/getAll?consName={}&type=today&key={}").format(consName, key)
    response = get(region_url, headers=headers).json()
    name = "宝宝星座是：" + response["name"]
    QFriend = "速配星座是：" + response["QFriend"]
    color = "幸运色是：" + response["color"]
    health = "健康指数是：" + response["health"]
    love = "爱情指数是：" + response["love"]
    work = "工作指数是：" + response["work"]
    money = "财运指数是：" + response["money"]
    number = "幸运数字是：" + str(response["number"])
    summary = response["summary"]
    all = response["all"]
    return name, QFriend, color, health, love, work, money, number, summary, all


def get_weather(region):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    key = config["weather_key"]
    region_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}".format(region, key)
    response = get(region_url, headers=headers).json()
    if response["code"] == "404":
        print("推送消息失败，请检查地区名是否有误！")
        os.system("pause")
        sys.exit(1)
    elif response["code"] == "401":
        print("推送消息失败，请检查和风天气key是否正确！")
        os.system("pause")
        sys.exit(1)
    else:
        # 获取地区的location--id
        location_id = response["location"][0]["id"]
    weather_url = "https://devapi.qweather.com/v7/weather/now?location={}&key={}".format(location_id, key)
    response = get(weather_url, headers=headers).json()
    # 天气
    weather = "当前天气" + response["now"]["text"]
    # 当前温度
    temp = "当前温度" + response["now"]["temp"] + u"\N{DEGREE SIGN}" + "C"
    # 风向
    wind_dir = response["now"]["windDir"]
    otherInfo_url = "https://devapi.qweather.com/v7/weather/3d?location={}&key={}".format(location_id, key)
    response_info = get(otherInfo_url, headers=headers).json()
    infos = response_info["daily"][0]
    # 日出时间
    sunrise = "日出时间：" + infos["sunrise"]
    # 日落时间
    sunset = "日落时间：" + infos["sunset"]
    # 最低气温
    tempMin = "最低气温：" + infos["tempMin"] + u"\N{DEGREE SIGN}" + "C"
    # 最高气温
    tempMax = "最高气温：" + infos["tempMax"] + u"\N{DEGREE SIGN}" + "C"
    # 当前风向
    windDirDay = "当前风向：" + infos["windDirDay"]
    # 紫外线
    uvIndex = "紫外线：" + infos["uvIndex"] + "uw"
    # 湿度
    humidity = "湿度：" + infos["humidity"]
    # 可见度
    vis = "可见度：" + infos["vis"] + "公里"
    return weather, temp, wind_dir, sunrise, sunset, tempMin, tempMax, windDirDay, uvIndex, humidity, vis


def get_birthday(birthday, year, today):
    birthday_cp = birthday
    count = (datetime.now() - datetime.strptime(birthday_cp, "%Y-%m-%d")).days
    birthday_year = birthday.split("-")[0]
    # 判断是否为农历生日
    if birthday_year[0] == "r":
        r_mouth = int(birthday.split("-")[1])
        r_day = int(birthday.split("-")[2])
        # 获取农历生日的今年对应的月和日
        try:
            birthday = ZhDate(year, r_mouth, r_day).to_datetime().date()
        except TypeError:
            print("请检查生日的日子是否在今年存在")
            os.system("pause")
            sys.exit(1)
        birthday_month = birthday.month
        birthday_day = birthday.day
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)

    else:
        # 获取国历生日的今年对应月和日
        birthday_month = int(birthday.split("-")[1])
        birthday_day = int(birthday.split("-")[2])
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        if birthday_year[0] == "r":
            # 获取农历明年生日的月和日
            r_last_birthday = ZhDate((year + 1), r_mouth, r_day).to_datetime().date()
            birth_date = date((year + 1), r_last_birthday.month, r_last_birthday.day)
        else:
            birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    return birth_day, count


def send_message(to_user, access_token, region, weather, temp, wind_dir, sunrise, sunset, tempMin, tempMax, windDirDay,
                 uvIndex, humidity, vis, name, QFriend, color, health, love, work,
                 money, number, summary, all, note_ch, note_en):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    # 获取在一起的日子的日期格式
    love_year = int(config["love_date"].split("-")[0])
    love_month = int(config["love_date"].split("-")[1])
    love_day = int(config["love_date"].split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    # 获取所有生日数据
    birthdays = {}
    for k, v in config.items():
        if k[0:5] == "birth":
            birthdays[k] = v
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": get_color()
            },
            "region": {
                "value": region,
                "color": get_color()
            },
            "weather": {
                "value": weather,
                "color": get_color()
            },
            "temp": {
                "value": temp,
                "color": get_color()
            },
            "wind_dir": {
                "value": wind_dir,
                "color": get_color()
            },
            "love_day": {
                "value": love_days,
                "color": get_color()
            },
            "name": {
                "value": name,
                "color": get_color()
            },
            "QFriend": {
                "value": QFriend,
                "color": get_color()
            },
            "color": {
                "value": color,
                "color": get_color()
            },
            "health": {
                "value": health,
                "color": get_color()
            },
            "love": {
                "value": love,
                "color": get_color()
            },
            "work": {
                "value": work,
                "color": get_color()
            },
            "money": {
                "value": money,
                "color": get_color()
            },
            "number": {
                "value": number,
                "color": get_color()
            },
            "summary": {
                "value": summary,
                "color": get_color()
            },
            "all": {
                "value": all,
                "color": get_color()
            },
            "sunrise": {
                "value": sunrise,
                "color": get_color()
            },
            "sunset": {
                "value": sunset,
                "color": get_color()
            },
            "tempMin": {
                "value": tempMin,
                "color": get_color()
            },
            "tempMax": {
                "value": tempMax,
                "color": get_color()
            },
            "windDirDay": {
                "value": windDirDay,
                "color": get_color()
            },
            "uvIndex": {
                "value": uvIndex,
                "color": get_color()
            },
            "humidity": {
                "value": humidity,
                "color": get_color()
            },
            "vis": {
                "value": vis,
                "color": get_color()
            },
            "note_ch": {
                "value": note_ch,
                "color": get_color()
            },
            "note_en": {
                "value": note_en,
                "color": get_color()
            }
        }
    }
    index = 0
    for key, value in birthdays.items():
        # 获取距离下次生日的时间
        birth_day, count = get_birthday(value["birthday"], year, today)
        if birth_day == 0:
            birthday_data = "今天{}生日哦，祝{}生日快乐！".format(value["name"], value["name"])
        else:
            birthday_data = "距离{}的生日还有{}天".format(value["name"], birth_day)
        # 将生日数据插入data
        data["data"][key] = {"value": birthday_data, "color": get_color()}
        index = count
    data["data"]["index"] = {"value": index, "color": get_color()}
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)


def get_ciba():
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    return note_ch, note_en


if __name__ == "__main__":
    try:
        with open("config.txt", encoding="utf-8") as f:
            config = eval(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except SyntaxError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)

    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入地区获取天气信息
    region = config["region"]

    # 获取星座的信息
    key = config["key"]
    consName = config["consName"]

    note_ch = config["note_ch"]
    note_en = config["note_en"]
    if note_ch == "" and note_en == "":
        # 获取词霸每日金句
        note_ch, note_en = get_ciba()

    weather, temp, wind_dir, sunrise, sunset, tempMin, tempMax, windDirDay, uvIndex, humidity, vis = get_weather(region)
    name, QFriend, color, health, love, work, money, number, summary, all = get_constellation(key, consName)
    # 公众号推送消息
    for user in users:
        send_message(user, accessToken, region, weather, temp, wind_dir, sunrise, sunset, tempMin, tempMax, windDirDay,
                     uvIndex, humidity, vis, name, QFriend, color, health, love, work,
                     money, number, summary, all, note_ch, note_en)
    os.system("pause")
