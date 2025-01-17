from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
import yt_dlp
import os

# Define states for ConversationHandler
WAITING_FOR_LINK = 1

async def play_audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Please send me the audio link 🎵🎵🎵')
    return WAITING_FOR_LINK
def download_audio(url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': 'D:/ffmpeg-7.1-essentials_build/ffmpeg-7.1-essentials_build/bin',
        'outtmpl': 'song.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if url.startswith("http"):
            # If url is a URL
            ydl.download([url])
        else:
            # If url is a search term
            search_result = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]
            ydl.download([search_result['webpage_url']])
        
async def play_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text # Get the query aftert /play 
    await update.message.reply_text('Downloading audio...Please wait')
    try: 
        download_audio(url)
        await update.message.reply_text('Upload audio')
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open('song.mp3', 'rb'))
        os.remove('song.mp3')
    
    except Exception as e:
        print(e)
        await update.message.reply_text(f"An error occurred: {e}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END


def getResult() :
    result = ConversationHandler(
        entry_points=[CommandHandler('play', play_audio_command)],
        states={
            WAITING_FOR_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, play_audio)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],  # Fallback for interruptions
    )
    return result