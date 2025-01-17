import mysql.connector
from telegram import Update
from telegram.ext import (
    ContextTypes
)
import psycopg2
from mysql.connector.cursor import MySQLCursorDict


def connect_db():
    conn = mysql.connector.connect(
        host = '127.0.0.1',
        port = 3306,
        user = 'root',
        password = 'diemquynh2207',
        database = 'bbbanana_bot'
    )
    cursor = conn.cursor(dictionary=True)
    return conn, cursor

async def saveUser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    print("user: %s", str(user))
    user_id = user.id
    
    #Connect to database
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (user_id,))
    result = cursor.fetchone()
    print('result: %s', str(result))
    if result: 
        await update.message.reply_text(f'Hello, {result[2]}')
    else:
        cursor.execute("INSERT INTO users (telegram_id, first_name, last_name) VALUES (%s, %s, %s)", (user_id, user.first_name, user.last_name))
        conn.commit()
        await update.message.reply_text(f'Hello, {user.username}. Nice to meet you, I am Banana Bot')
    
    conn.close()

    