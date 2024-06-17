import os
import telebot
from telebot import types
from classes import TrainingProgram, Exercise, Workout
from enum import Enum, auto

class UserState(Enum):
    IDLE = auto()
    CHOOSING_EDIT_FIELD = auto()
    AWAITING_NEW_VALUE = auto()

user_states = {}
def get_user_state(user_id):
    return user_states.get(user_id, {'state': UserState.IDLE, 'edit_field': None})

TELEGRAM_ID = os.environ.get('TELEGRAM_ID')
def is_authorized(user_id):
    return int(user_id) == int(TELEGRAM_ID)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

tp = TrainingProgram(['programs_test/chest.csv', 'programs_test/back.csv', 'programs_test/legs.csv'])
what_to_edit = ""
    
@bot.message_handler(commands=['start', 'help'])    
def send_welcome(message):
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")
        return
    
    bot.send_message(message.chat.id, f"/begin - starts the workout\n/end - ends the workout\n/time - shows the time passed and the expected time left\n/edit - edit the current exercise\n/help - shows the list of commands\nclear_keyboard - removes the keyboard buttons")
    
@bot.message_handler(commands=['begin'])
def start_workout(message):
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")
        return
    
    tp.start_workout()
    # Starting the workout
    bot.send_message(message.chat.id, f"Starting {tp.workout.get_name()} workout")

    # Creating the button for the next exercise
    button = types.KeyboardButton("Go to next exercise")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(button) 

    # Sending the message with the keyboard for the next exercise
    bot.send_message(message.chat.id, "Make sure to warm up, then press 'Go to next exercise' when you're ready.", reply_markup=markup)
    
@bot.message_handler(commands=['clear_keyboard'])
def clear_keyboard(message):
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")
        return
    
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, "Keyboard buttons have been removed", reply_markup=markup)
    
@bot.message_handler(commands=['time'])
def get_time(message):
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")
        return
    
    bot.send_message(message.chat.id, f"You have trained for {tp.workout.get_passed_time()}")
    hours, minutes = tp.workout.calculate_passed_time()
    excepted_time_minutes = tp.workout.calculate_expected_time()
    left = excepted_time_minutes - minutes - hours * 60
    hours_rem, minutes_rem = divmod(left, 60)
    bot.send_message(message.chat.id, f"Expected time left: {int(hours_rem)} hours and {int(minutes_rem)} minutes")
        
@bot.message_handler(commands=['end'])
def end_workout(message):
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")
        return
    
    reply = tp.workout.end()
    tp.workout.progress()
    tp.move_to_next_workout()
    bot.send_message(message.chat.id, reply)

@bot.message_handler(func=lambda message: message.text == "Go to next exercise")
def next_exercise(message):
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")
        return
    
    reply = tp.workout.next_exercise()
    if reply == "Moving to the next exercise":
        # Create each button separately
        button1 = types.KeyboardButton("Go to next exercise")
        button2 = types.KeyboardButton("Edit exercise")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        # Add buttons to the markup
        markup.add(button1, button2)
        bot.send_message(message.chat.id, f"{tp.workout.get_current_exercise()}", reply_markup=markup)
    else:
        # TODO: Add the end workout button
        bot.send_message(message.chat.id, f"{reply}")

@bot.message_handler(func=lambda message: message.text == "Edit exercise")
def start_edit(message):
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    fields = ['setup', 'sets', 'reps', 'weight', 'rest_time', 'increment']
    for field in fields:
        markup.add(types.KeyboardButton(field))
    bot.send_message(message.chat.id, "Please choose what to edit:", reply_markup=markup)
    user_states[message.chat.id] = {'state': UserState.CHOOSING_EDIT_FIELD, 'edit_field': None}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not is_authorized(message.chat.id):
        bot.send_message(message.chat.id, "You are not authorized to use this bot.")
        return
    
    user_state = get_user_state(message.chat.id)
    
    if user_state['state'] == UserState.CHOOSING_EDIT_FIELD:
        user_states[message.chat.id] = {'state': UserState.AWAITING_NEW_VALUE, 'edit_field': message.text}
        bot.send_message(message.chat.id, f"Please enter new value for {message.text}")
    elif user_state['state'] == UserState.AWAITING_NEW_VALUE:
        new_value = message.text
        edit_field = user_state['edit_field']
        # Here, call the function to update the exercise with new_value for edit_field
        reply = tp.workout.edit_exercise(column_name=edit_field, exercise_name=tp.workout.current_exercise.name, new_value=new_value)
        bot.send_message(message.chat.id, reply)
        user_states[message.chat.id] = {'state': UserState.IDLE, 'edit_field': None}
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        fields = {'Go to next exercise', 'Edit exercise'}
        for field in fields:
            markup.add(types.KeyboardButton(field))
        bot.send_message(message.chat.id, tp.workout.get_current_exercise(), reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "To start editing, please use the /edit command.")
        
    
bot.infinity_polling()