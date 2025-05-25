import requests
from supabase import create_client

# 配置参数
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"
QWEATHER_KEY = "YOUR_QWEATHER_KEY"
SERVERCHAN_SENDKEY = "YOUR_SENDKEY"

def get_weather(city):
    # 获取城市ID
    location_url = f"https://geoapi.qweather.com/v2/city/lookup?location={city}&key={QWEATHER_KEY}"
    location_data = requests.get(location_url).json()
    if not location_data.get('location'):
        return None
    location_id = location_data['location'][0]['id']
    
    # 获取天气数据
    weather_url = f"https://devapi.qweather.com/v7/weather/now?location={location_id}&key={QWEATHER_KEY}"
    weather_data = requests.get(weather_url).json()
    temp = weather_data['now']['temp']
    return temp

def push_to_user(openid, city, temp):
    # 生成穿衣建议
    if float(temp) >= 28:
        suggestion = "🔥 穿短袖+短裤"
    elif 10 <= float(temp) < 28:
        suggestion = "🌤 穿长袖+外套"
    else:
        suggestion = "❄️ 穿毛衣+羽绒服"
    # 推送消息
    requests.post(
        f"https://sctapi.ftqq.com/{SERVERCHAN_SENDKEY}.send",
        data={
            "title": f"{city}今日穿衣指南",
            "desp": f"当前温度：{temp}℃\n建议：{suggestion}",
            "openid": openid
        }
    )

def main():
    # 连接数据库
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    # 获取所有用户
    users = supabase.table('users').select('openid, city').execute().data
    # 遍历推送
    for user in users:
        city = user['city']
        temp = get_weather(city)
        if temp:
            push_to_user(user['openid'], city, temp)

if __name__ == "__main__":
    main()
