import requests
from pprint import pprint
from .utils import convert_seconds_to_date
from db import queries as sql
import json

import config

def get_weather():
    data = []
    username = input('Enter username: ')
    is_exists, user_id = sql.check_user_exists('weather.db', username)
    if not is_exists:
        sql.add_user('weather.db', username)
        get_weather()
    else:


        while True:
            city = input("Напишите свой город: ")

            if city == "save":
                with open("weather.json", mode="w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4, ensuer_ascii=False)
                continue
            elif city == 'show':
                all_weather = sql.get_user_weather("weather.db", user_id)
                if not all_weather:
                    print('empty')
                    continue
                for item in all_weather:
                    name, _, sunrise, sunset, dt, description, speed, temp = item[1:-1]
                    print(f"""
================================
В городе {name} сейчас {description}
Температура: {temp}
Скорость ветра: {speed}
Восход солнца: {sunrise}
Закат солнца: {sunset}
Время отправки запроса: {dt}
================================
""")
                continue
            elif city == 'clear':
                sql.clear_user_weather("weather.db", user_id)
                print('История браузера очищена')
                continue

            config.parameters["q"] = city

            resp = requests.get(config.url, params=config.parameters).json()
            pprint(resp)
            timezone = resp["timezone"]
            name = resp["name"]
            sunrise = convert_seconds_to_date(seconds=resp["sys"]["sunrise"], timezone=timezone)
            sunset = convert_seconds_to_date(seconds=resp["sys"]["sunset"], timezone=timezone)
            dt = convert_seconds_to_date(seconds=resp["dt"], timezone=timezone)
            description = resp["weather"][0]["description"]
            speed = resp["wind"]["speed"]
            temp = resp["main"]["temp"]

            sql.add_weather("weather.db",
                            name=name,
                            tz=timezone,
                            sunset=sunset,
                            sunrise=sunrise,
                            description=description,
                            dt=dt,
                            speed=speed,
                            temp=temp,
                            user_id=user_id
                            )
            data.append(
                dict(
                    zip(
                        ['name', 'sunrise', 'sunset', 'description', 'speed'],
                        [name, sunrise, timezone, sunset, description, speed]
                    )
                )
            )
            print(f"""
================================
В городе {name} сейчас {description}
Температура: {temp}
Скорость ветра: {speed}
Восход солнца: {sunrise}
Закат солнца: {sunset}
Время отправки запроса: {dt}
================================
""")
