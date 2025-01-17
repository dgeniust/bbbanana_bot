from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from config import (WEATHER_API_KEY)
import requests
def get_weather(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no&lang=vi"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Trích xuất thông tin thời tiết
        weather = data['current']['condition']['text']
        temp = data['current']['temp_c']
        feels_like = data['current']['feelslike_c']
        humidity = data['current']['humidity']
        wind_speed = data['current']['wind_kph']

        return (f"Thời tiết tại {city} 🏙️:\n"
                f"- Mô tả: {weather} ☁️\n"
                f"- Nhiệt độ: {temp}°C (Cảm giác: {feels_like}°C) 🔥\n"
                f"- Độ ẩm: {humidity}% 💧\n"
                f"- Tốc độ gió: {wind_speed} km/h 💨")
    else:
        return "Không tìm thấy thông tin thời tiết cho địa điểm này."

# Hàm xử lý lệnh /weather
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Vui lòng nhập tên thành phố. Ví dụ: /weather Hanoi")
        return

    city = " ".join(context.args)  # Lấy tên thành phố từ lệnh người dùng
    weather_info = get_weather(city)
    await update.message.reply_text(weather_info)

