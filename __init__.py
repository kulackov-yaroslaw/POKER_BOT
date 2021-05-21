import telebot

bot = None

COUNT_PLAYERS = 2
NAME = ''
SURNAME = ''
AGE = 0


def init_bot(token):
    global bot
    bot = telebot.TeleBot(token)

    from app import handlers