import gspread
import pandas as pd
import telebot
from telebot import types

bot = telebot.TeleBot('8396948402:AAHd_Bgw9lyZkKHVJTTP_4H1OPBkG1fNR0c')
gc = gspread.service_account("C:/Users/pinto/AppData/Local/Programs/Python/Python313/Lib/site-packages/google/auth/service_account.json")
sh = gc.open("Kladenec")

# Простой словарь для хранения временных данных
temp_data = {}

bot.delete_webhook()


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Новая продажа"))
    bot.send_message(message.chat.id, "Для добавления новой продажи нажми на кнопку 'Новая продажа'.", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Новая продажа')
def new_sell(message):
    chat_id = message.chat.id
    temp_data[chat_id] = {'step': 1}
    bot.send_message(chat_id, "Введите фамилию мастера:")


@bot.message_handler(func=lambda message: True)
def handle_all(message):
    chat_id = message.chat.id

    if chat_id not in temp_data:
        bot.reply_to(message, "Начните с команды 'Новая продажа'")
        return

    step = temp_data[chat_id]['step']

    if step == 1:
        temp_data[chat_id]['master'] = message.text
        temp_data[chat_id]['step'] = 2
        bot.send_message(chat_id, "Введите дату (дд.мм.гггг):")
        print(temp_data[chat_id]['master'])

    elif step == 2:
        temp_data[chat_id]['date'] = message.text
        temp_data[chat_id]['step'] = 3
        bot.send_message(chat_id, "Введите название продукта:")
        print(temp_data[chat_id]['date'])

    elif step == 3:
        temp_data[chat_id]['product'] = message.text
        temp_data[chat_id]['step'] = 4
        bot.send_message(chat_id, "Введите цену:")
        print(temp_data[chat_id]['product'])

    elif step == 4:
        try:
            temp_data[chat_id]['cost'] = float(message.text)
            print(temp_data[chat_id]['cost'])

            # Сохраняем в Google Sheets
            worksheet = sh.worksheet("Январь")
            df = pd.DataFrame(worksheet.get_all_records())

            new_row = pd.DataFrame([{
                'Фио мастера': temp_data[chat_id]['master'],
                'дата': temp_data[chat_id]['date'],
                'изделие': temp_data[chat_id]['product'],
                'сумма': temp_data[chat_id]['cost']
            }])

            df = pd.concat([df, new_row], ignore_index=True)
            df = df.fillna(' ')
            worksheet.update([df.columns.tolist()] + df.values.tolist())

            bot.send_message(chat_id, "✅ Продажа добавлена!")
            del temp_data[chat_id]

        except Exception as e:
            bot.send_message(chat_id, f"Ошибка: {e}")


bot.infinity_polling()
