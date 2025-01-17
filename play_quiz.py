from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
import requests
from config import (QUIZ_API_KEY, BASE_URL)


async def choose_difficult(update: Update, context: ContextTypes.DEFAULT_TYPE):
    header_text ='Chọn độ khó'
    keyboard = [
        [InlineKeyboardButton("Easy", callback_data='easy')],
        [InlineKeyboardButton("Medium", callback_data='medium')],
        [InlineKeyboardButton("Hard", callback_data='hard')]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(header_text, reply_markup = markup)
    
async def difficult_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    difficult = query.data
    await query.edit_message_text(text=f'Bạn đã chọn mức độ {difficult}')
    context.user_data['difficulty'] = difficult
    return ConversationHandler.END

async def category_choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    header_text = 'Chọn thể loại câu hỏi'
    keyboard = [
            [InlineKeyboardButton('Linux', callback_data='Linux')],
            [InlineKeyboardButton('DevOps', callback_data='DevOps')],
            [InlineKeyboardButton('Networking', callback_data='Networking')],
            [InlineKeyboardButton('Cloud', callback_data='Cloud')],
            [InlineKeyboardButton('Docker', callback_data='Docker')],
            [InlineKeyboardButton('Kubernetes', callback_data='Kubernetes')],
        ]
    markup = InlineKeyboardMarkup(keyboard)
    print(0)
    await update.message.reply_text(header_text, reply_markup = markup)
    print(1)

async def category_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(2)
    query = update.callback_query
    if not query.message:
        # If there's no message attached to the callback query, return early
        await query.answer(text="No message to edit.")
        return
    category = query.data
    try:
        await query.edit_message_text(text=f'Bạn đã chọn loại câu hỏi về {category}')
    except Exception as e:
        print(f"Error while editing message: {e}")
        await query.answer(text="An error occurred while processing your choice.")
    context.user_data['category'] = category
    return ConversationHandler.END
def get_quiz(difficulty, category):
    headers = {
        'X-Api-Key': QUIZ_API_KEY
    }
    if(difficulty == None):
        difficulty = 'easy'
    response = requests.get(BASE_URL, headers=headers, params={'difficulty': difficulty, 'limit': 5, 'category': category})
    if response.status_code == 200:
        cnt = 0
        data = response.json()
        for question_data in data:
            question = question_data.get('question')
            if question: 
                cnt+=1
                print('Câu hỏi thứ: '+ str(cnt))
                answers = question_data['answers']
                correct_answer = question_data['correct_answers']
                print('kiểu dữ liệu của correct_answer: '+ str(type(correct_answer)))
                
                correct_answer_key = None
                
                for key, value in correct_answer.items():
                    print("value: "+ str(value))
                    if value.lower() == "true":
                        correct_answer_key = key
                        print('correct_answer_key: '+ correct_answer_key)
                        break
                if correct_answer_key:
                    answer_key = correct_answer_key.split("_")[0] + "_" + correct_answer_key.split("_")[1] # Ví dụ "answer_d"
                    print('answer_key: ' + answer_key)
                    
                    correct_answer_text  = answers.get(f"{answer_key}", None)
                    print('correct_answer_text: ' + str(correct_answer_text))
                else: 
                    correct_answer_key = None
                print('độ khó: '+ difficulty)
                return question, answers, correct_answer_text
        print('No valid questions found.')
        return None, None, None 
    else:
        return None, None, None
    
async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Lấy độ khó từ context hoặc mặc định là 'easy'
    difficulty = context.user_data.get('difficulty', 'easy')
    category = context.user_data.get('category', 'Linux')
    print('category in question: '+ category)
    question_text, answers, correct_answer = get_quiz(difficulty,category)
    
    if question_text: 
        if correct_answer is None:
            await update.message.reply_text("Không thể xác định đáp án đúng. Vui lòng thử lại.")
            return
        markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(answer, callback_data=answer)]
                for answer in answers.values() if answer
            ]
        )
    
        await update.message.reply_text(question_text, reply_markup = markup)
        context.user_data['correct_answer_key'] = correct_answer
        context.user_data['question_key'] = question_text
            
    else:
        await update.message.reply_text("Lỗi khi lấy câu hỏi quiz. Vui lòng thử lại.")



async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    choice = query.data
    correct_answer_key = context.user_data.get('correct_answer_key')
    print("đáp án là: "+ correct_answer_key)
    question_key = context.user_data.get('question_key')
    if correct_answer_key is None:
        await query.edit_message_text(text="Có lỗi xảy ra trong quá trình lấy đáp án đúng.")
        return  # Dừng lại nếu không có đáp án đúng
    
    if choice == correct_answer_key:
        await query.edit_message_text(text='Đúng rồi!')
    else:
        await query.edit_message_text(text=f'Sai rồi! Đáp án đúng cho câu hỏi {question_key.upper()} \n => {correct_answer_key}.')
        ConversationHandler.END
    
