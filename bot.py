import os
import telebot
from telebot import types
import sqlite3
import random
import requests
from bs4 import BeautifulSoup
from flask import Flask

# Инициализация бота через переменную окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
#bot = telebot.TeleBot(BOT_TOKEN)
#bot = telebot.TeleBot("1458726905:AAGdb2BxeoFjQanpbWee0jn0z2SlVFHdH14")
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
# Flask приложение для веб-сервера (обязательно для Railway)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Ваш основной код бота (нужно немного адаптировать)

url = 'https://absurdopedia.net/wiki/Абсурдоцитатник:Цитаты_Джейсона_Стетхема'
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html')
#print(soup)
all_divs = soup.find_all('div')
quotes = []
for i, div in enumerate(all_divs):
        if div.get('style') and 'margin-left:2em' in div.get('style') and 'font-style: italic' in div.get('style'):
            quote_text = div.get_text(strip=True)
            if i + 1 < len(all_divs):
                next_div = all_divs[i + 1]
                if next_div.get('style') and 'margin-left: 3em' in next_div.get('style'):
                    signature = next_div.get_text(strip=True)
                    quotes.append({
                        'quote': quote_text,
                        'signature': signature
                    })
breath_practices_list = [
    "4-7-8 дыхание: вдох на 4 секунды, задержка на 7, выдох на 8. Повтори 5 раз.",
    "Квадратное дыхание: вдох 4 сек, задержка 4 сек, выдох 4 сек, пауза 4 сек. 5 циклов.",
    "Диафрагмальное дыхание: глубокий вдох через нос, живот надувается. Медленный выдох через рот. 10 раз.",
    "Огненное дыхание: быстрые короткие выдохи через нос, вдохи пассивные. 30 секунд.",
    "Альтернативное дыхание: закрой правую ноздрю, вдох левой. Закрой обе, выдох правой. 5 циклов.",
    "Расслабляющее дыхание: вдох на 5 секунд, выдох на 7 секунд. 10 раз."
]



###инициализация бдшки
def init_db(db_name = 'db_bot.db'):
  conn = sqlite3.connect(db_name)
  cursor = conn.cursor()
  #users
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        total_quotes INTEGER DEFAULT 0
        )
  ''')
  ##
  # аблица цитат
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quote_text TEXT NOT NULL,
        signature TEXT NOT NULL
    )
    ''')
  # аблица  дыхательных упражнений
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS breath_practic (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        practic_text TEXT NOT NULL
    )
    ''')
  # для статистики)
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        quote_id INTEGER,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

  conn.commit()
  conn.close()



def add_user(user_id):
  conn = sqlite3.connect('db_bot.db')
  cursor = conn.cursor()
  cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
  ex_user = cursor.fetchone()
  if not ex_user:
    cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
def incremetn_total_quotes(user_id):
  conn = sqlite3.connect('db_bot.db')
  cursor = conn.cursor()
  cursor.execute('UPDATE users SET total_quotes = total_quotes + 1 WHERE user_id = ?', (user_id,))
  conn.commit()
  conn.close()
  return True
def get_total_q(user_id):
  conn = sqlite3.connect('db_bot.db')
  cursor = conn.cursor()
  cursor.execute('SELECT  total_quotes FROM users WHERE user_id = ?', (user_id,))
  quote = cursor.fetchone()
  conn.close()
  return quote
def get_random_statham():
  conn = sqlite3.connect('db_bot.db')
  cursor = conn.cursor()
  cursor.execute('SELECT id, quote_text, signature FROM quotes ORDER BY RANDOM() LIMIT 1')
  quote = cursor.fetchone()
  conn.close()
  if quote:
    return {
                'quote_id':quote[0],
                'quote': quote[1],
                'signature': quote[2]
            }
###
def get_breath_practice():
    conn = sqlite3.connect('db_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, practic_text FROM breath_practic ORDER BY RANDOM() LIMIT 1')
    practice = cursor.fetchone()
    conn.close()
    if practice:
        return {
            'text': practice[1]
            }
    else:
        return None




def add_to_history(user_id, quote_id):
      conn = sqlite3.connect('db_bot.db')
      cursor = conn.cursor()

      cursor.execute('''
            INSERT INTO history (user_id, quote_id)
            VALUES (?, ?)
        ''', (user_id, quote_id))

      conn.commit()
      conn.close()
      return True



def add_stath(quotes_list):
  conn = sqlite3.connect('db_bot.db')
  cursor = conn.cursor()

  added_count = 0
  for quote_dict in quotes_list:
      quote_text = quote_dict['quote']
      signature = quote_dict['signature']
        # Проверяем, есть ли уже такая цитата
      cursor.execute('SELECT id FROM quotes WHERE quote_text = ?', (quote_text,))
      if cursor.fetchone() is None:
          cursor.execute('''
                INSERT INTO quotes (quote_text, signature)
                VALUES (?, ?)
            ''', (quote_text, signature))
          added_count += 1

  conn.commit()
  conn.close()
  return added_count
def add_all_breath_practices():
    conn = sqlite3.connect('db_bot.db')
    cursor = conn.cursor()

    added_count = 0
    for practice_text in breath_practices_list:
        # чек есть ли уже такая практика
        cursor.execute('SELECT id FROM breath_practic WHERE practic_text = ?', (practice_text,))
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO breath_practic (practic_text)
                VALUES (?)
            ''', (practice_text,))
            added_count += 1

    conn.commit()
    conn.close()
    return added_count
def get_random_breath_practice():
  conn = sqlite3.connect('db_bot.db')
  cursor = conn.cursor()
  cursor.execute('SELECT id, practic_text FROM breath_practic ORDER BY RANDOM() LIMIT 1')
  result = cursor.fetchone()
  conn.close()
  if result:
      return {
          'id': result[0],
          'text': result[1]
        }
  return None



magic_ball_answers = [
    "Бесспорно",
    "Предрешено",
    "Никаких сомнений",
    "Определённо да",
    "Можешь быть уверен в этом",
    "Мне кажется — да",
    "Вероятнее всего",
    "Хорошие перспективы",
    "Знаки говорят — да",
    "Да",
    "Пока не ясно, попробуй снова",
    "Спроси позже",
    "Лучше не рассказывать",
    "Сейчас нельзя предсказать",
    "Сконцентрируйся и спроси опять",
    "Даже не думай",
    "Мой ответ — нет",
    "По моим данным — нет",
    "Перспективы не очень хорошие",
    "Весьма сомнительно"
]


init_db()

add_stath(quotes) ### доабвляет ток уникальные цитаты. так что можно в тот массив еще парсить
add_all_breath_practices()


@bot.message_handler(commands = ['start'])
def send_start_msg(message):
    add_user(message.from_user.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📈 Величайшая цитата стэтхэма")
    btn2 = types.KeyboardButton("⚙️ Статистика")
    btn3 = types.KeyboardButton("🎮 Бот угадывает")
    btn4 = types.KeyboardButton("🎮 Я угадываю")
    btn5 = types.KeyboardButton("🎱 Магический шар")
    btn6 = types.KeyboardButton("🌬️ Дыхательная практика")
    markup.add(btn1, btn2, btn3, btn4,btn5, btn6)
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! Теперь мы знаем твой id: {message.from_user.id} ))",
        reply_markup=markup
    )
user_secret_numbers = {}

@bot.message_handler(func=lambda message: message.text == "🎮 Бот угадывает")
def bot_guesses(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    user_secret_numbers[user_id] = {
        'min': 1,
        'max': 100,
        'tries': 0,
        'chat_id': chat_id
    }

    guess = 50

    buttons = types.InlineKeyboardMarkup(row_width=3)
    btn_down = types.InlineKeyboardButton("🔽 Меньше", callback_data="bot_less")
    btn_yes = types.InlineKeyboardButton("🎯 Да, это оно!", callback_data="bot_yes")
    btn_up = types.InlineKeyboardButton("🔼 Больше", callback_data="bot_more")

    buttons.add(btn_down, btn_yes, btn_up)

    bot.send_message(
        chat_id,
        f"🎮 *Бот угадывает твое число*\n\n"
        f"Загадай число от 1 до 100 в уме.\n"
        f"Я буду пытаться угадать его!\n\n"
        f"*Мой первый вариант: {guess}*\n\n"
        f"Это твое число? Или оно меньше/больше?",
        parse_mode='Markdown',
        reply_markup=buttons
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('bot_'))
def handle_bot_guess(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    if user_id not in user_secret_numbers:
        bot.answer_callback_query(call.id, "Начни игру сначала!")
        return

    game = user_secret_numbers[user_id]
    game['tries'] += 1

    guess = (game['min'] + game['max']) // 2

    if call.data == "bot_yes":
        bot.answer_callback_query(call.id, f"🎉 Угадал за {game['tries']} попыток!")

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=f"🎉 *Угадал!*\n\n"
                 f"Твое число: *{guess}*\n"
                 f"Попыток: *{game['tries']}*\n\n"
                 f"Хочешь еще раз?",
            parse_mode='Markdown',
            reply_markup=None
        )

        del user_secret_numbers[user_id]

    elif call.data == "bot_less":
        game['max'] = guess - 1

        if game['min'] > game['max']:
            bot.answer_callback_query(call.id, "Ты где-то ошибся!")

            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text="❌ Ты где-то ошибся в ответах!",
                parse_mode='Markdown',
                reply_markup=None
            )
            del user_secret_numbers[user_id]
            return

        new_guess = (game['min'] + game['max']) // 2

        buttons = types.InlineKeyboardMarkup(row_width=3)
        btn_down = types.InlineKeyboardButton("🔽 Меньше", callback_data="bot_less")
        btn_yes = types.InlineKeyboardButton("🎯 Да, это оно!", callback_data="bot_yes")
        btn_up = types.InlineKeyboardButton("🔼 Больше", callback_data="bot_more")

        buttons.add(btn_down, btn_yes, btn_up)

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=f"🔽 *Меньше {guess}*\n\n"
                 f"*Мой следующий вариант: {new_guess}*\n\n"
                 f"Это твое число? Или оно меньше/больше?",
            parse_mode='Markdown',
            reply_markup=buttons
        )

        bot.answer_callback_query(call.id, "")

    elif call.data == "bot_more":
        game['min'] = guess + 1

        if game['min'] > game['max']:
            bot.answer_callback_query(call.id, "Ты где-то ошибся!")

            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text="❌ Ты где-то ошибся в ответах!",
                parse_mode='Markdown',
                reply_markup=None
            )
            del user_secret_numbers[user_id]
            return

        new_guess = (game['min'] + game['max']) // 2

        buttons = types.InlineKeyboardMarkup(row_width=3)
        btn_down = types.InlineKeyboardButton("🔽 Меньше", callback_data="bot_less")
        btn_yes = types.InlineKeyboardButton("🎯 Да, это оно!", callback_data="bot_yes")
        btn_up = types.InlineKeyboardButton("🔼 Больше", callback_data="bot_more")

        buttons.add(btn_down, btn_yes, btn_up)

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=f"🔼 *Больше {guess}*\n\n"
                 f"*Мой следующий вариант: {new_guess}*\n\n"
                 f"Это твое число? Или оно меньше/больше?",
            parse_mode='Markdown',
            reply_markup=buttons
        )

        bot.answer_callback_query(call.id, "")
bot_secret_numbers = {}

@bot.message_handler(func=lambda message: message.text == "🎮 Я угадываю")
def user_guesses(message):
    user_id = message.from_user.id

    secret = random.randint(1, 100)
    bot_secret_numbers[user_id] = {
        'secret': secret,
        'tries': 0,
        'max_tries': 10
    }

    bot.send_message(
        message.chat.id,
        f"🎮 *Угадай мое число!*\n\n"
        f"Я загадал число от 1 до 100.\n"
        f"У тебя есть {bot_secret_numbers[user_id]['max_tries']} попыток.\n\n"
        f"Введи свой вариант:",
        parse_mode='Markdown'
    )

    bot.register_next_step_handler(message, process_user_guess)

def process_user_guess(message):
    user_id = message.from_user.id

    if user_id not in bot_secret_numbers:
        return

    try:
        user_num = int(message.text)

        if user_num < 1 or user_num > 100:
            bot.send_message(message.chat.id, "Число должно быть от 1 до 100!")
            bot.register_next_step_handler(message, process_user_guess)
            return

        game = bot_secret_numbers[user_id]
        game['tries'] += 1

        if user_num == game['secret']:
            bot.send_message(
                message.chat.id,
                f"🎉 *Угадал!*\n\n"
                f"Загаданное число: *{game['secret']}*\n"
                f"Попыток: *{game['tries']}*",
                parse_mode='Markdown'
            )
            del bot_secret_numbers[user_id]

        elif game['tries'] >= game['max_tries']:
            bot.send_message(
                message.chat.id,
                f"❌ *Проиграл!*\n\n"
                f"Загаданное число: *{game['secret']}*\n"
                f"Твои попытки кончились.",
                parse_mode='Markdown'
            )
            del bot_secret_numbers[user_id]

        elif user_num < game['secret']:
            bot.send_message(
                message.chat.id,
                f"🔼 *Больше!*\n\n"
                f"Осталось попыток: *{game['max_tries'] - game['tries']}*\n"
                f"Попробуй еще:",
                parse_mode='Markdown'
            )
            bot.register_next_step_handler(message, process_user_guess)

        else:
            bot.send_message(
                message.chat.id,
                f"🔽 *Меньше!*\n\n"
                f"Осталось попыток: *{game['max_tries'] - game['tries']}*\n"
                f"Попробуй еще:",
                parse_mode='Markdown'
            )
            bot.register_next_step_handler(message, process_user_guess)

    except:
        bot.send_message(message.chat.id, "Введи нормальное число!")
        bot.register_next_step_handler(message, process_user_guess)

@bot.message_handler(commands = ['start'])
def send_start_msg(message):
    add_user(message.from_user.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📈 Цитата Стетхема")
    btn2 = types.KeyboardButton("⚙️ Статистика")
    btn3 = types.KeyboardButton("🎮 Бот угадывает")
    btn4 = types.KeyboardButton("🎮 Я угадываю")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)

    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! Выбери игру:",
        reply_markup=markup
    )
@bot.message_handler(commands=['game1'])
def start_game1(message):
    bot_guesses(message)

@bot.message_handler(commands=['game2'])
def start_game2(message):
    user_guesses(message)
@bot.message_handler(func=lambda message: message.text == "📈 Величайшая цитата стэтхэма")
def statham(message):
  citatca = get_random_statham()
  incremetn_total_quotes(message.from_user.id)
  bot.send_message(message.chat.id, f"Задумайся ~~~ \n {citatca['quote']} \n {citatca['signature']}")
@bot.message_handler(func=lambda message: message.text == "⚙️ Статистика")
def static(message):
  citatca = get_total_q(message.from_user.id)
  bot.send_message(message.chat.id, f"Всего ты просмотрел \n {citatca} цитат, это на {citatca} больше чем 0 )")
@bot.message_handler(func=lambda message: message.text == "🎱 Магический шар")
def taro_for_scam(message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn = types.KeyboardButton("🔮 Задать вопрос")
  markup.add(btn)

  bot.send_message(
        message.chat.id,
        "🎱 *Магический шар 8-Ball*\n\n"
        "Задай любой вопрос, на который можно ответить Да/Нет.\n\n"
        "*Не является индивидуальной инвестиционной стратегией*\n"
        "Нажми кнопку ниже чтобы спросить:",
        parse_mode='Markdown',
        reply_markup=markup
    )
@bot.message_handler(func=lambda message: message.text == "🔮 Задать вопрос")
def ask_question(message):
    bot.send_message(
        message.chat.id,
        "📝 Напиши свой вопрос:"
    )
    bot.register_next_step_handler(message, get_question)

def get_question(message):
    question = message.text

    if len(question) < 3:
        bot.send_message(message.chat.id, "❌ Вопрос должен быть длиннее!")
        return

    answer = random.choice(magic_ball_answers)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📈 Величайшая цитата стэтхэма")
    btn2 = types.KeyboardButton("⚙️ Статистика")
    btn3 = types.KeyboardButton("🎮 Бот угадывает")
    btn4 = types.KeyboardButton("🎮 Я угадываю")
    btn5 = types.KeyboardButton("🎱 Магический шар")
    btn6 = types.KeyboardButton("🌬️ Дыхательная практика")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

    bot.send_message(
        message.chat.id,
        f"🎱 *Вопрос:* {question}\n\n"
        f"✨ *Ответ:* {answer}",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(commands=['ball'])
def ball_command(message):
    taro_for_scam(message)
@bot.message_handler(func=lambda message: message.text == "🌬️ Дыхательная практика")
def send_breath_practice(message):
    practice = get_random_breath_practice()

    if practice:
        bot.send_message(
            message.chat.id,
            f"🧘 *Дыхательная практика:*\n\n{practice['text']}\n\n"
            f"Выполни это упражнение для расслабления.",
            parse_mode='Markdown'
        )
    else:
        bot.send_message(
            message.chat.id,
            "Практики пока не загружены. Используй /fill_practices"
        )
# Запуск через веб-сервер
if __name__ == '__main__':
    # Запускаем поллинг бота в отдельном потоке
    import threading
    threading.Thread(target=bot.polling, kwargs={'none_stop': True}).start()
    
    # Запускаем Flask сервер
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)