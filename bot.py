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

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

tp = TrainingProgram(['programs_test/legs.csv'])

what_to_edit = ""

@bot.message_handler(commands=['start'])
def greet(message):
    # Create keyboard buttons
    button = types.KeyboardButton("Start current workout")
    
    # Create the keyboard markup and add the button
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(button) 
    
    bot.send_message(message.chat.id, f"To start current workout, press the button", reply_markup=markup)
    
@bot.message_handler(func=lambda message: message.text == "Start current workout")
def start_workout(message):
    tp.start_workout()
    # Starting the workout
    bot.send_message(message.chat.id, f"Starting {tp.workout.get_name()} workout")

    # Creating the button for the next exercise
    button = types.KeyboardButton("Go to next exercise")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(button) 

    # Sending the message with the keyboard for the next exercise
    bot.send_message(message.chat.id, "Make sure to warm up, then press 'Go to next exercise' when you're ready.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Go to next exercise")
def next_exercise(message):
    reply = tp.workout.next_exercise()
    if reply == "Moving to the next exercise":
        # Create each button separately
        button1 = types.KeyboardButton("Go to next exercise")
        button2 = types.KeyboardButton("Edit exercise")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        # Add buttons to the markup
        markup.add(button1, button2)
        bot.send_message(message.chat.id, f"{tp.workout.get_current_exercise()}", reply_markup=markup)
    elif reply == "There are no more exercises for today, please finish the workout":
        # TODO: Add the end workout button
        bot.send_message(message.chat.id, f"{reply}")
         
def get_user_state(user_id):
    return user_states.get(user_id, {'state': UserState.IDLE, 'edit_field': None})

@bot.message_handler(func=lambda message: message.text == "Edit exercise")
def start_edit(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    fields = ['setup', 'sets', 'reps', 'weight', 'rest_time', 'increment']
    for field in fields:
        markup.add(types.KeyboardButton(field))
    bot.send_message(message.chat.id, "Please choose what to edit:", reply_markup=markup)
    user_states[message.chat.id] = {'state': UserState.CHOOSING_EDIT_FIELD, 'edit_field': None}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
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