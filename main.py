from aiogram.types import Message, BufferedInputFile
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
import requests
import asyncio
import base64
import io

API_TOKEN = "8121870262:AAHW3f17quznG4dTamMFVYwpYgnbukw0St4"

PROBIVAPI_KEY = "58ea8029-c366-4a2e-aaba-c87e335e65cd"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

print("!BOT STARTED!")

@dp.message(Command(commands=['start', 'help']))
async def send_welcome(message: Message):
    await message.reply("Osint Bot by Frenchmans")

@dp.message()
async def text(message: Message):
    nomer = message.text.strip()
    print(f"Запрос: {nomer}")
    
    url = f"https://probivapi.com/api/phone/info/{nomer}"
    pic_url = f"https://probivapi.com/api/phone/pic/{nomer}"
    head = {"X-Auth": PROBIVAPI_KEY}

    response = requests.get(url, headers=head)
    print(f"Ответ API: {response.text}")
    
    try:
        json_response = response.json()
    except Exception as e:
        print(f"Ошибка парсинга JSON: {e}")
        json_response = {}

    pic_response = requests.get(pic_url, headers=head)
    pic_data = None
    
    if pic_response.status_code == 200:
        try:
            if "error" in pic_response.text.lower():
                raise ValueError("API вернул ошибку вместо изображения")
            
            if pic_response.text.startswith("data:image"):
                pic_response.text = pic_response.text.split(",", 1)[-1]
            
            pic_data = base64.b64decode(pic_response.text)
        except (base64.binascii.Error, ValueError) as e:
            print(f"Ошибка при обработке изображения: {e}")
            pic_data = None

    dosie = f"""┏ ✅ Dosie for {nomer}
┣ 📱 ФИО (CallApp): {json_response.get('callapp', {}).get('name', 'Not found')}
┣ 📧 Emails (CallApp): {', '.join([e.get('email') for e in json_response.get('callapp', {}).get('emails', [])])}
┣ 🌐 Сайты (CallApp): {', '.join([s.get('websiteUrl') for s in json_response.get('callapp', {}).get('websites', [])])}
┣ 🏠 Адреса (CallApp): {', '.join([a.get('street') for a in json_response.get('callapp', {}).get('addresses', [])])}
┣ 📝 Описание (CallApp): {json_response.get('callapp', {}).get('description', 'Not found')}
┣ 🌐 ФИО (EyeCon): {json_response.get('eyecon', 'Not found')}
┣ 🔎 ФИО (ViewCaller): {', '.join([v.get('name', 'Not found') for v in json_response.get('viewcaller', [])])}
┗ 👇 Еще...

Пробив API: https://probivapi.com"""
    
    if pic_data and len(pic_data) > 0:
        pic_bytes = bytes(pic_data)
        await message.answer_photo(BufferedInputFile(pic_bytes, filename=f"{nomer}.jpg"), caption=dosie)
    else:
        await message.answer(dosie)

async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
