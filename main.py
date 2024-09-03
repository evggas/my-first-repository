import telebot
import requests

api_key = "3a5cf8827821449abe2210021240109"

bot = telebot.TeleBot("7234672072:AAFjumc3cBF00aI2PIwBX41987Xb3awmLF4")

weather_translations = {
    "Partly cloudy": "Малооблачно",
    "Clear": "Ясно",
    "Patchy rain nearby": "Местами дождь",
    "Sunny": "Солнечно",
    "Light rain": "Легкий дождь",
    "Heavy rain": "Сильный дождь",
    "Overcast": "Пасмурно",
    "Mist": "Туман",
    "Snow": "Снег",
    "Moderate rain": "Умеренный дождь",
    "Moderate or heavy rain with thunder": "Умеренный или сильный дождь с грозой",
}


# Функция для перевода описания погоды
def translate_weather(description):
    return weather_translations.get(description, description)


# Функция для получения текущей погоды через WeatherAPI
def fetch_weather(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        weather_description = translate_weather(data['current']['condition']['text'])
        temperature = data['current']['temp_c']
        return weather_description, temperature
    else:
        return None


# Функция для получения прогноза погоды на 3 дня через WeatherAPI
def fetch_forecast(city):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=3&aqi=no&alerts=no"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        forecast_message = f"Прогноз погоды для {city} на 3 дня:\n"

        for day in data['forecast']['forecastday']:
            date = day['date']
            condition = translate_weather(day['day']['condition']['text'])
            max_temp = day['day']['maxtemp_c']
            min_temp = day['day']['mintemp_c']
            forecast_message += f"{date}: {condition}, макс. температура: {max_temp}°C, мин. температура: {min_temp}°C\n"

        return forecast_message
    else:
        return None


# Обработка команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Привет! Я помогу тебе узнать погоду.\n\n" +
                 "Просто напиши название города, и я расскажу, какая там погода сейчас.\n\n" +
                 "Чтобы узнать прогноз на 3 дня, введи: прогноз <город>.\n\n" +
                 "Чтобы узнать погоду сразу в нескольких городах, введи: города <город1, город2,...>.")


# Обработка команды на получение прогноза на 3 дня
@bot.message_handler(func=lambda message: message.text.lower().startswith('прогноз'))
def forecast_message(message):
    city = message.text.replace('прогноз ', '').strip()
    forecast_data = fetch_forecast(city)

    if forecast_data:
        bot.reply_to(message, forecast_data)
    else:
        bot.reply_to(message, "Не удалось получить прогноз. Пожалуйста, проверьте название города и попробуйте снова.")


# Обработка команды на получение погоды в нескольких городах
@bot.message_handler(func=lambda message: message.text.lower().startswith('города'))
def multiple_cities_weather(message):
    cities = message.text.replace('города ', '').split(',')
    response_message = ""

    for city in cities:
        weather_data = fetch_weather(city.strip())

        if weather_data:
            weather_description, temperature = weather_data
            response_message += f"Погода в {city.strip()}: {weather_description}, температура: {temperature}°C\n"
        else:
            response_message += f"Не удалось получить данные о погоде для {city.strip()}.\n"

    bot.reply_to(message, response_message)


# Обработка всех остальных текстовых сообщений (для запросов погоды)
@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def get_weather(message):
    city = message.text
    weather_data = fetch_weather(city)

    if weather_data:
        weather_description, temperature = weather_data
        response = f"Погода в {city}: {weather_description}, температура: {temperature}°C"
    else:
        response = "Не удалось получить данные о погоде. Пожалуйста, проверьте название города и попробуйте снова."

    bot.reply_to(message, response)


# Запуск бота
bot.polling()
