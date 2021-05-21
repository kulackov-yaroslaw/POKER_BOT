# -*- coding: utf-8 -*-
import telebot
import random
import copy
from app import bot, NAME, SURNAME, AGE, COUNT_PLAYERS

suits = ['S', 'C', 'D', 'H']
values = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
combinations = ['kicker', 'pair', 'two pairs', 'set', 'street', 'flash', 'full-house', 'caret', 'street-flash', 'flash-grand']
players = []


def get_emoji(code_suit):
    if code_suit == 'S':
        return "\u2660\ufe0f"
    elif code_suit == 'C':
        return "\u2663\ufe0f"
    elif code_suit == 'D':
        return "\u2666\ufe0f"
    else:
        return "\u2665\ufe0f"


class Card:
    def __init__(self, suit, value, player_hand=-1):
        self.suit = suit
        self.value = value
        self.player_hand = player_hand

    def print(self):
        print(self.suit, end='')
        print(self.value, end='')

    def print_bot(self, message):
        bot.send_message(message.chat.id, self.suit)
        bot.send_message(message.chat.id, self.value)


class Deck:
    def __init__(self):
        self.cards = []

    def init_full_deck(self):
        self.cards.clear()
        for suit_temp in suits:
            for value_temp in values:
                self.cards.append(Card(suit_temp, value_temp))

    def append(self, obj):
        self.cards.append(obj)

    def print(self):
        for card in self.cards:
            card.print()
            print(' ', end='')

    def print_bot(self, message):
        message_str = ''
        for card in self.cards:
            message_str += get_emoji(card.suit) + str(card.value) + '  '
        bot.send_message(message.chat.id, message_str)

    def __len__(self):
        return self.cards.__len__()


class Player:
    def __init__(self, idx_player):
        self.deck = Deck()
        self.idx_player = idx_player
        count_cards = 0
        while count_cards < 5:
            random_card = random.choice(main_deck.cards)
            if random_card.player_hand == -1:
                count_cards += 1
                random_card.player_hand = idx_player
                self.deck.append(random_card)


main_deck = Deck()


def choose_card():
    random_card = random.choice(main_deck.cards)
    while random_card.player_hand != -1:
        random_card = random.choice(main_deck.cards)
    return random_card


@bot.message_handler(commands=['start'])
def handle_start(message):
    print("START")
    bot.send_message(message.chat.id, 'Считается, что Дро-покер (Draw poker) является '
                                      'родоначальником всех популярных ныне видов покера.'
                                      'Предлагаем сыграть партеечку!\n'
                                      '(/play)\n'
                                      '(/rules)'
                     )


@bot.message_handler(commands=['rules'])
def rules(message):
    bot.send_message(message.chat.id, 'Игрокам раздается по 5 карт.'
                                      ' Цель игры - собрать самую сильную комбинацию.'
                                      ' Игроки могут поменять какие-то карты в надежде что им '
                                      'выпадет что-то получше.\n'
                                      'Комбинации\n\n'
                                      'Флэш-рояль\n'
                                      'Включает в себя десятку, валета, даму, короля и туза одной масти.\n\n'
                                      'Стрит-флэш\n'
                                      'Пять карт одной масти в последовательном порядке.\n\n'
                                      'Каре\n'
                                      'Любые четыре карты одного достоинства.\n\n'
                                      'Фулл хаус\n'
                                      'Три карты одного достоинства и две другого.\n\n'
                                      'Флэш\n'
                                      'Пять карт одной масти, в любом порядке.\n\n'
                                      'Стрит\n'
                                      'Пять карт разной масти, в последовательном порядке.\n\n'
                                      'Сет\n'
                                      'Три карты одного достоинства.\n\n'
                                      'Две пары\n'
                                      'Две разные пары карт.\n\n'
                                      'Пара\n'
                                      'Любые две карты совпадающие, по достоинству.\n\n'
                                      'Старшая карта\n'
                                      'Если у вас нет ни одной из вышеуказанных комбинаций, '
                                      'то у вас остается только самая большая карта в вашей руке по достоинству'
                                      ' - кикер(бьет только младшую по достоинству у соперника).\n'
                                      '(/play)')


@bot.message_handler(commands=['play'])
def handle_play(message):
    bot.send_message(message.chat.id, "Сколько играют? (2-5)")
    bot.register_next_step_handler(message, create_players)


def create_players(message):
    global COUNT_PLAYERS
    COUNT_PLAYERS = int(message.text)
    global players
    players.clear()
    main_deck.init_full_deck()
    for i in range(COUNT_PLAYERS):
        players.append(Player(i))
    for i in range(COUNT_PLAYERS):
        players[i].deck.print()
        print()
    bot.send_message(message.chat.id, "Ваши карты (артем лох)")
    players[0].deck.print_bot(message)
    bot.send_message(message.chat.id, "Номера карт, которые вы хотите поменять (через пробел,"
                                      " \"0\" - ничего не менять):")
    bot.register_next_step_handler(message, change_cards)


def change_cards(message):
    numbers_card = str(message.text).split(" ")
    print(numbers_card)
    if int(numbers_card[0]) != 0:
        for card in numbers_card:
            players[0].deck.cards[int(card) - 1].player_hand = -2
        new_player_hand = Deck()
        for card in players[0].deck.cards:
            if card.player_hand != -2:
                new_player_hand.append(card)
            else:
                card_new = choose_card()
                card_new.player_hand = 0
                new_player_hand.append(card_new)
        for card in numbers_card:
            players[0].deck.cards[int(card) - 1].player_hand = -1
        players[0].deck = copy.deepcopy(new_player_hand)
    bot.send_message(message.chat.id, "Ваши карты")
    players[0].deck.print_bot(message)
    for i in range(COUNT_PLAYERS):
        players[i].deck.print()
        print()
    print()
    understand_combinations(message)


def understand_combinations(message):
    players_combinations = []
    for i in range(COUNT_PLAYERS):
        players_combinations.append(find_combination(players[i].deck))
        print(players_combinations[i])
    win_combination = max(players_combinations)
    type_win = type_combination(win_combination)
    bot.send_message(message.chat.id, "Победа \"" + type_win + "\" у....")
    for i in range(COUNT_PLAYERS):
        if players_combinations[i] == win_combination:
            if i == 0:
                bot.send_message(message.chat.id, "Вас:")
            else:
                bot.send_message(message.chat.id, str("Игрока " + str(i) + ":"))
            players[i].deck.print_bot(message)


def type_combination(win_combination):
    if win_combination < 9:
        return combinations[0]
    else:
        return combinations[win_combination - 8]


def find_combination(deck):
    if is_flesh_royal(deck):
        return 17
    elif is_street_flesh(deck):
        return 16
    elif is_kare(deck):
        return 15
    elif is_full_house(deck):
        return 14
    elif is_flesh(deck):
        return 13
    elif is_street(deck):
        return 12
    elif is_set(deck):
        return 11
    elif is_two_pairs(deck):
        return 10
    elif is_pair(deck):
        return 9
    else:
        for value in values[::-1]:
            if value in [card.value for card in deck.cards]:
                return values.index(value)


def is_flesh_royal(deck):
    suit_first = deck.cards[0].suit
    for card in deck.cards:
        if suit_first != card.suit:
            return False
    for value in values[-5:-1]:
        if value not in [card.value for card in deck.cards]:
            return False
    return True


def is_street_flesh(deck):
    suit_first = deck.cards[0].suit
    for card in deck.cards:
        if suit_first != card.suit:
            return False
    values_card = [card.value for card in deck.cards]
    values_card = sorted(values_card)
    temp_value_idx = values.index(values_card[0])
    for i in range(1, 5):
        if values.index(values_card[i]) != temp_value_idx + 1:
            return False
        temp_value_idx += 1
    return True


def is_kare(deck):
    values_card = [card.value for card in deck.cards]
    for value in values_card:
        if values_card.count(value) == 4:
            return True
    return False


def is_full_house(deck):
    values_card = [card.value for card in deck.cards]
    values_card = sorted(values_card)
    if values_card[0] == values_card[1] and values_card[0] == values_card[2] and values_card[3] == values_card[4]:
        return True
    return False


def is_flesh(deck):
    suit_all_card = deck.cards[0].suit
    for card in deck.cards:
        if card.suit != suit_all_card:
            return False
    return True


def is_street(deck):
    values_card = [card.value for card in deck.cards]
    values_card = sorted(values_card)
    temp_value_idx = values.index(values_card[0])
    for i in range(1, 5):
        if values.index(values_card[i]) != temp_value_idx + 1:
            return False
        temp_value_idx += 1
    return True


def is_set(deck):
    values_card = [card.value for card in deck.cards]
    for value in values_card:
        if values_card.count(value) == 3:
            return True
    return False


def is_two_pairs(deck):
    values_card = [card.value for card in deck.cards]
    count_cards_in_pairs = 0
    for value in values_card:
        if values_card.count(value) == 2:
            count_cards_in_pairs += 1
        if count_cards_in_pairs == 3:
            return True
    return False


def is_pair(deck):
    values_card = [card.value for card in deck.cards]
    for value in values_card:
        if values_card.count(value) == 2:
            return True
    return False


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, 'Напиши /reg')


@bot.message_handler(commands=['reg'])
def handle_reg(message):
    bot.send_message(message.chat.id, "Как тебя зовут?")
    bot.register_next_step_handler(message, get_name)  # следующий шаг – функция get_name


# Handles all text messages that match the regular expression
@bot.message_handler(content_types=['text'], regexp="python")
def handle_python_message(message):
    bot.send_message(message.chat.id, "Я обожаю python!")


@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    if message.text == "ярик":
        bot.send_message(message.chat.id, "люблю тоби\u2665\ufe0f")
    else:
        bot.send_message(message.chat.id, message.text)


def get_name(message):
    global NAME
    NAME = message.text
    bot.send_message(message.chat.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    global SURNAME
    SURNAME = message.text
    bot.send_message(message.chat.id, 'Сколько тебе лет?')
    bot.register_next_step_handler(message, get_age)


def get_age(message):
    global AGE
    try:
        AGE = int(message.text)  # проверяем, что возраст введен корректно
    except (TypeError, ValueError):
        bot.send_message(message.chat.id, 'Цифрами, пожалуйста')
    keyboard = telebot.types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    question = 'Тебе {age} лет, тебя зовут {name} {surname}?'.format(age=AGE, name=NAME, surname=SURNAME)
    bot.send_message(message.chat.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
        bot.send_message(call.message.chat.id, 'Запомню : )')
    elif call.data == "no":
        bot.send_message(call.message.chat.id, "Попробуем начать сначала. Как тебя зовут?")
        bot.register_next_step_handler(call.message, get_name)
