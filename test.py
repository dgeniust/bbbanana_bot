from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import datetime
import schedule
import time
import threading

# Lưu danh sách công việc
tasks = []

# Hàm thêm công việc
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text("Vui lòng nhập đúng định dạng: /add <tiêu đề> <mô tả> <thời hạn (YYYY-MM-DD HH:MM)>")
        return
    
    title = context.args[0]
    description = context.args[1]
    try:
        deadline = datetime.datetime.strptime(" ".join(context.args[2:]), '%Y-%m-%d %H:%M')
    except ValueError:
        await update.message.reply_text("Thời hạn không hợp lệ. Định dạng: YYYY-MM-DD HH:MM")
        return

    tasks.append({"title": title, "description": description, "deadline": deadline, "chat_id": update.effective_chat.id})
    await update.message.reply_text(f"Đã thêm công việc: {title}\nMô tả: {description}\nThời hạn: {deadline.strftime('%Y-%m-%d %H:%M')}")

# Hàm hiển thị danh sách công việc
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tasks:
        await update.message.reply_text("Danh sách công việc trống!")
    else:
        message = "Danh sách công việc:\n"
        for i, task in enumerate(tasks, 1):
            message += f"{i}. {task['title']} - {task['description']} (Hạn: {task['deadline'].strftime('%Y-%m-%d %H:%M')})\n"
        await update.message.reply_text(message)

# Hàm xóa công việc
async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Vui lòng nhập số thứ tự công việc cần xóa: /delete <số>")
        return

    try:
        index = int(context.args[0]) - 1
        removed_task = tasks.pop(index)
        await update.message.reply_text(f"Đã xóa công việc: {removed_task['title']}")
    except (ValueError, IndexError):
        await update.message.reply_text("Số thứ tự không hợp lệ.")

# Hàm nhắc nhở
def send_reminders():
    now = datetime.datetime.now()
    for task in tasks:
        if task["deadline"] <= now:
            Application.current_app.bot.send_message(
                chat_id=task["chat_id"],
                text=f"🔔 Nhắc nhở: Công việc '{task['title']}' đã đến hạn!\nMô tả: {task['description']}"
            )
            tasks.remove(task)

# Lên lịch nhắc nhở
def schedule_reminders():
    schedule.every(1).minute.do(send_reminders)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Khởi chạy bot
if __name__ == "__main__":
    TOKEN = "YOUR_BOT_TOKEN"
    app = Application.builder().token(TOKEN).build()

    # Thêm lệnh
    app.add_handler(CommandHandler("add", add_task))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("delete", delete_task))

    # Chạy luồng nhắc nhở
    reminder_thread = threading.Thread(target=schedule_reminders, daemon=True)
    reminder_thread.start()

    print("Bot đang chạy...")
    app.run_polling()
