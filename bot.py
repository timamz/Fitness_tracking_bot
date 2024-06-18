import os
import telebot
from telebot import types
from classes import TrainingProgram, Exercise, Workout
from enum import Enum, auto
import time

class UserState(Enum):
    IDLE = auto()
    CHOOSING_EDIT_FIELD = auto()
    AWAITING_NEW_VALUE = auto()

user_states = {}
TELEGRAM_ID = os.environ.get('TELEGRAM_ID')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
tp = TrainingProgram(['programs_test/chest.csv', 'programs_test/back.csv', 'programs_test/legs.csv'])

def get_user_state(user_id):
    return user_states.get(user_id, {'state': UserState.IDLE, 'edit_field': None})

def check_authorization(message):
    def is_authorized(user_id):
        return int(user_id) == int(TELEGRAM_ID)
    
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")
        return False
    return True

def add_keyboard_buttons(buttons: list[str]) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for button in buttons:
        markup.add(types.KeyboardButton(button))
    return markup
    
@bot.message_handler(commands=['start', 'help'])    
def send_welcome(message):
    authorized = check_authorization(message)
    if not authorized: return
    
    bot.send_message(message.chat.id, f"""
        /begin - starts the workout
        /end - ends the workout
        /time - shows the time passed and the expected time left
        /edit - edit the current exercise
        /help - shows the list of commands
        /clear_keyboard - removes the keyboard buttons
    """)
    
@bot.message_handler(commands=['begin'])
def start_workout(message):
    authorized = check_authorization(message)
    if not authorized: return
    
    tp.start_workout()
    # Starting the workout
    bot.send_message(message.chat.id, f"Starting {tp.workout.get_name()} workout")

    markup = add_keyboard_buttons(["Go to the first exercise"])
    bot.send_message(message.chat.id, "Make sure to warm up, then press 'Go to first exercise' when you're ready.", reply_markup=markup)
    
@bot.message_handler(commands=['clear_keyboard'])
def clear_keyboard(message):
    authorized = check_authorization(message)
    if not authorized: return
    
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, "Keyboard buttons have been removed", reply_markup=markup)
    
@bot.message_handler(commands=['time'])
def get_time(message):
    authorized = check_authorization(message)
    if not authorized: return
    
    bot.send_message(message.chat.id, f"You have trained for {tp.workout.get_passed_time()}")
    hours, minutes = tp.workout.calculate_passed_time()
    expected = tp.workout.calculate_expected_time()
    left = expected - minutes - hours * 60
    hours_rem, minutes_rem = divmod(left, 60)
    bot.send_message(message.chat.id, f"Expected time left: {int(hours_rem)} hours and {int(minutes_rem)} minutes")
        
@bot.message_handler(commands=['end'])
def end_workout(message):
    authorized = check_authorization(message)
    if not authorized: return
    
    try:
        reply = tp.workout.end()
        tp.workout.progress()
        tp.move_to_next_workout()
        bot.send_message(message.chat.id, reply)
    except AttributeError:
        bot.send_message(message.chat.id, "You have not started the workout yet. Please use the /begin command.")

@bot.message_handler(func=lambda message: message.text in ("Go to next exercise", "Go to the first exercise"))
def next_exercise(message):
    authorized = check_authorization(message)
    if not authorized: return
    
    reply = tp.workout.next_exercise()
    if reply == "Moving to the next exercise":
        markup = add_keyboard_buttons(["Go to next exercise", "Edit exercise", "Start rest"])
        bot.send_message(message.chat.id, f"{tp.workout.get_current_exercise()}", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"{reply}")

@bot.message_handler(func=lambda message: message.text == "Edit exercise")
def start_edit(message):
    authorized = check_authorization(message)
    if not authorized: return
    
    markup = add_keyboard_buttons(["setup", "sets", "reps", "weight", "rest_time", "increment"])
    bot.send_message(message.chat.id, "Please choose what to edit:", reply_markup=markup)
    user_states[message.chat.id] = {'state': UserState.CHOOSING_EDIT_FIELD, 'edit_field': None}
    
@bot.message_handler(func=lambda message: message.text == "Start rest")
def start_rest(message):
    authorized = check_authorization(message)
    if not authorized: return
    
    rest_time = tp.workout.current_exercise.rest_time
    rest_time_seconds = int(rest_time * 60)
    bot.send_message(message.chat.id, f"Starting {rest_time} minutes rest")
    time.sleep(rest_time_seconds - 30)
    bot.send_message(message.chat.id, "30 seconds left")
    time.sleep(30)
    
    markup = add_keyboard_buttons(["Go to next exercise", "Edit exercise", "Start rest"])
    bot.send_message(message.chat.id, "Rest time is up, start the next set!", reply_markup=markup)
    
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    authorized = check_authorization(message)
    if not authorized: return
    
    user_state = get_user_state(message.chat.id)
    
    if user_state['state'] == UserState.CHOOSING_EDIT_FIELD:
        user_states[message.chat.id] = {'state': UserState.AWAITING_NEW_VALUE, 'edit_field': message.text}
        bot.send_message(message.chat.id, f"Please enter new value for {message.text}")
    elif user_state['state'] == UserState.AWAITING_NEW_VALUE:
        new_value = message.text
        edit_field = user_state['edit_field']
        try:
            reply = tp.workout.edit_exercise(column_name=edit_field, exercise_name=tp.workout.current_exercise.name, new_value=new_value)
            bot.send_message(message.chat.id, reply)
            user_states[message.chat.id] = {'state': UserState.IDLE, 'edit_field': None}
            markup = add_keyboard_buttons(["Go to next exercise", "Edit exercise", "Start rest"])
            bot.send_message(message.chat.id, tp.workout.get_current_exercise(), reply_markup=markup)
        except BaseException as e:
            reply = f"An error occurred while updating the exercise: {e}"
            markup = add_keyboard_buttons(["Go to next exercise", "Edit exercise", "Start rest"])
            bot.send_message(message.chat.id, reply, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "To start editing, please use the /edit command.")

bot.infinity_polling()