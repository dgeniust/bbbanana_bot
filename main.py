from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, CallbackQueryHandler
)
from list_tasks import (
    # list_tasks, add_task, delete_task, schedule_reminders
    list_tasks, add_task
)
import telebot
from play_audio import getResult 
from report_weather import weather
from play_quiz import ( question, answer, choose_difficult, 
                       difficult_choice, category_choose, category_choice )

from sql_connection import saveUser
import threading
from config import (TOKEN, BOT_USERNAME)
bot = telebot.TeleBot(TOKEN)

#Command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Thanks for chatting with me, I am a banana 🍌')
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'I am a banana! Please type something so I can respond to you 🍌\n'
        'Here are some commands you can use:\n\n'
        '/start - Start the Banana Bot\n'
        '/help - Get help 👷\n\n'
        'Play Music 🎧\n'
        '/play - Play music with the link you send from Youtube\n\n'
        'Tasks 📄\n'
        '/list_task - My tasks\n'
        '/add_task - Add a new task \n'
        '/delete_task - Delete a task\n\n'
        'Weather ☁️\n'
        '/weather - Get the weather today\n\n'
        'Quiz ❓\n'
        '/quiz_difficult - Choose difficult for the Quiz \n'
        '/quiz_category - Choose category for the Quiz \n'
        '/quiz - Play quiz\n'
    )

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command!')
    

# Responses
def handle_response(text: str):
    
    processed : str = text.lower()
    
    if 'hello' in processed:
        return 'Hello! I am a banana'
    if 'how are you' in processed:
        return 'I am a banana, I am always good'
    if 'bye' in processed or 'goodbye' in processed:
        return 'Goodbye! Have a great day'
    if 'diem quynh' in processed:
        return 'Remember to buy her a crosiant'
    
    else:
        return 'I do not understand what are you saying ...'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    
    print(f'User: ({update.message.chat.id}) in {message_type} said: {text}')

    if message_type == 'group':
        if BOT_USERNAME in text: 
            new_text : str  = text.replace(BOT_USERNAME, '').strip()
            response : str = handle_response(new_text)
        else: 
            return
    else: 
        response : str = handle_response(text)
    print('Bot:', response)
    await update.message.reply_text(response)
    
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
    
 
if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    
    # Conversation handler for /play command
    conv_handler = getResult()
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('list_task', list_tasks))
    app.add_handler(CommandHandler('add_task', add_task))
    #app.add_handler(CommandHandler('delete_task', delete_task))
    
    app.add_handler(CommandHandler('weather', weather))

    app.add_handler(CommandHandler('quiz_category', category_choose))
    app.add_handler(CallbackQueryHandler(category_choice, pattern="^(Linux|DevOps|Networking|Programming (PHP, JS, Pythong and etc.)|Cloud|Docker|Kubernetes)$"))
    
    app.add_handler(CommandHandler('quiz_difficult', choose_difficult))
    app.add_handler(CallbackQueryHandler(difficult_choice, pattern="^(easy|medium|hard)$"))
    
    app.add_handler(CommandHandler('quiz', question))
    app.add_handler(CallbackQueryHandler(answer, pattern=r"^answer_.*$"))
    
    app.add_handler(CommandHandler('sql', saveUser))
    
    #Run the reminder 
    # reminder_thread = threading.Thread(target=schedule_reminders, daemon=True)
    # reminder_thread.start()
    
    # Messages 
    app.add_handler(MessageHandler(filters.TEXT, handle_message)) 
    
    # Errors
    app.add_error_handler(error)
    
    print('Polling...')
    app.run_polling(poll_interval=3, timeout = 30)