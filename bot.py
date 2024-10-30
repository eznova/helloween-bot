import os
import random
import requests
import time
import json
from config import TOKEN

API_URL = f"https://api.telegram.org/bot{TOKEN}/"
card_back_image_path = "card_back.png"  # Путь к локальному изображению
cards_directory = "cards"  # Папка с изображениями

def get_updates(offset=None):
    url = API_URL + "getUpdates"
    params = {"timeout": 100, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text, reply_markup=None):
    url = API_URL + "sendMessage"
    params = {"chat_id": chat_id, "text": text}
    if reply_markup:
        params['reply_markup'] = json.dumps(reply_markup)  # Сериализуем в JSON
    print(f'sending message {params} to {url}')
    response = requests.post(url, json=params)
    if not response.ok:
        print(f"Error sending message: {response.text}")

def send_photo(chat_id, photo_path, caption=None, reply_markup=None):
    url = API_URL + "sendPhoto"
    with open(photo_path, "rb") as photo:
        params = {"chat_id": chat_id, "caption": caption}
        if reply_markup:
            params['reply_markup'] = json.dumps(reply_markup)  # Сериализуем в JSON
        files = {"photo": photo}
        response = requests.post(url, data=params, files=files)
        print(response.json())

def send_photo_with_button(chat_id, caption):
    url = API_URL + "sendPhoto"
    print(f'sending photo to {url}')
    
    reply_markup = {
        "inline_keyboard": [
            [{"text": "Перевернуть карту", "callback_data": "flip_card"}]
        ]
    }
    
    with open(card_back_image_path, "rb") as photo:
        params = {
            "chat_id": chat_id,
            "caption": caption,
            "reply_markup": json.dumps(reply_markup)  # Сериализуем в JSON
        }
        files = {"photo": photo}
        response = requests.post(url, data=params, files=files)
        print(response.json())

def get_random_card_image():
    # Получаем список всех файлов в папке cards
    all_images = [f for f in os.listdir(cards_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]
    if not all_images:
        return None
    random_image = random.choice(all_images)  # Выбираем случайное изображение
    return os.path.join(cards_directory, random_image)  # Возвращаем полный путь

def main():
    print("Бот запущен...")
    offset = None

    while True:
        updates = get_updates(offset)
        if updates.get("ok"):
            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"].get("text", "").strip().lower()

                    if text == "/start":
                        print(f"{chat_id} requested welcome message")
                        welcome_message = ("О, приветствую тебя, искатель цифровых тайн! 🔮\n"
                                           "В моих таинственных руках карты IT-таро, готовые раскрыть тебе веления судьбы в мире технологий!\n"
                                           "Посмотри, что судьба приготовила для тебя... ✨\n"
                                           "Нажми на 'Перевернуть карту', и тайны IT-мира предстанут перед тобой!\n"
                                           "Но помни, что будущее непредсказуемо, и только от тебя зависит, как ты воспользуешься полученной мудростью! 😉")
                        send_photo_with_button(chat_id, welcome_message)

                    else:
                        send_message(chat_id, "Я пока знаю только команду 'Перевернуть карту'.")

                elif "callback_query" in update:
                    callback_data = update["callback_query"]["data"]
                    chat_id = update["callback_query"]["message"]["chat"]["id"]

                    if callback_data in ["flip_card", "get_another_card"]:
                        random_image_path = get_random_card_image()
                        if random_image_path:
                            caption = "Вот твоя карта!"
                            reply_markup = {
                                "inline_keyboard": [
                                    [{"text": "Получить еще одну", "callback_data": "get_another_card"}]
                                ]
                            }
                            send_photo(chat_id, random_image_path, caption, reply_markup)
                        else:
                            send_message(chat_id, "Извините, нет доступных изображений карт.")

        time.sleep(1)

if __name__ == "__main__":
    main()
