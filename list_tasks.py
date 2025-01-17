from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
import subprocess
import datetime
import schedule
import time
import threading
import shlex
from sql_connection import connect_db

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: 
        conn, cursor = connect_db()
        cursor.execute("SELECT * FROM tasks WHERE telegram_id_task =%s", (update.effective_chat.id,))
        tasks = cursor.fetchall()
        print("tasks type: " + str(type(tasks)))
        print("tasks: " + str(tasks))
        if not tasks:
            await update.message.reply_text("Danh sách công việc trống!")
        else:
            message = f"Danh sách công việc của ID {update.effective_chat.id}:\n" 
            for task in tasks:
                message += f"{task['stt']}. {task['header']} - {task['descriptions']} (Deadline: {task['deadline']})\n"
            await update.message.reply_text(message)
    except Exception as e:
        print(f"Lỗi: {str(e)}")
    
    
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn, cursor = connect_db()
        # Sử dụng shlex để phân tích cú pháp đúng
        args = shlex.split(update.message.text)
        print(args)
        # Xác minh cú pháp
        if len(args) < 4:
            await update.message.reply_text(
                "Sai cú pháp. Vui lòng nhập lệnh đúng định dạng: /addtask <tiêu đề> <mô tả> <thời hạn (YYYY-MM-DD HH:MM)>"
            )
            return

        # Lấy tiêu đề, mô tả và thời hạn
        title = args[1]  # Tiêu đề
        description = args[2]  # Mô tả
        deadline_input = " ".join(args[3:])  # Thời hạn (ngày giờ) #TYPE: <class 'str'>
        deadline = parse_deadline(deadline_input) #TYPE: <class 'datetime.datetime'>
        cursor.execute("SELECT * FROM tasks WHERE telegram_id_task= %s AND header = %s AND deadline =%s", (update.effective_chat.id, title, deadline_input))
        result = cursor.fetchone()
        print('result: ' + str(result))
        if result: 
            await update.message.reply_text(f'Công việc đã tồn tại')
            return
        else:
            cursor.execute("INSERT INTO tasks (telegram_id_task, header, descriptions, deadline) VALUES (%s, %s, %s, %s)", (update.effective_chat.id, title, description, deadline_input))
            conn.commit()
            await update.message.reply_text(
            f"✅ Đã thêm công việc:\n"
            f"- Tiêu đề: {title}\n"
            f"- Mô tả: {description}\n"
            f"- Thời hạn: {deadline.strftime('%Y-%m-%d %H:%M')}"
            )
        
        # Thêm công việc vào danh sách
        # tasks.append({
        #     "title": title,
        #     "description": description,
        #     "deadline": deadline,
        #     "chat_id": update.effective_chat.id,
        # })
        # print('tasks: ' + str(tasks))
        
    except ValueError as ve:
        await update.message.reply_text(
            f"Thời hạn không hợp lệ: {deadline_input}\nHỗ trợ các định dạng:\n"
            f"- YYYY-MM-DD HH:MM\n- YYYY/MM/DD HH:MM\n- DD-MM-YYYY HH:MM\n- YYYY-MM-DD 12-hour (AM/PM)"
        )
    except Exception as e:
        print(f"Lỗi: {e}")
def parse_deadline(deadline_input):
    supported_formats = [
        '%Y-%m-%d %H:%M',  # YYYY-MM-DD HH:MM
        '%Y/%m/%d %H:%M',  # YYYY/MM/DD HH:MM
        '%d-%m-%Y %H:%M',  # DD-MM-YYYY HH:MM
        '%Y-%m-%d %I:%M %p',  # YYYY-MM-DD 12-hour (AM/PM)
    ]
    for fmt in supported_formats:
        try:
            return datetime.datetime.strptime(deadline_input, fmt)
        except ValueError:
            continue
    raise ValueError(f"Thời hạn không hợp lệ: {deadline_input}")

# Hàm xóa công việc
# async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not context.args:
#         await update.message.reply_text("Vui lòng nhập số thứ tự công việc cần xóa: /delete <số>")
#         return

#     try:
#         index = int(context.args[0]) - 1
#         removed_task = tasks.pop(index)
#         await update.message.reply_text(f"Đã xóa công việc: {removed_task['title']}")
#     except (ValueError, IndexError):
#         await update.message.reply_text("Số thứ tự không hợp lệ.")

# # Hàm nhắc nhở
# def send_reminders():
#     now = datetime.datetime.now()
#     for task in tasks:
#         if task["deadline"] <= now:
#             Application.current_app.bot.send_message(
#                 chat_id=task["chat_id"],
#                 text=f"🔔 Nhắc nhở: Công việc '{task['title']}' đã đến hạn!\nMô tả: {task['description']}"
#             )
#             tasks.remove(task)

# Lên lịch nhắc nhở
# def schedule_reminders():
#     schedule.every(1).minute.do(send_reminders)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
