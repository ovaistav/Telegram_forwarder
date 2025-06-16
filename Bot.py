import logging
from telegram.ext import Updater, MessageHandler, Filters
from telegram import Update
import os
from threading import Thread
import time

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# دریافت تنظیمات از متغیرهای محیطی
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SOURCE_CHANNEL_ID = os.getenv('SOURCE_CHANNEL_ID')
DESTINATION_CHANNEL_ID = os.getenv('DESTINATION_CHANNEL_ID')

# دیکشنری برای ذخیره آخرین پیام پردازش شده
last_processed_message = {}

def forward_messages(context):
    try:
        # دریافت آخرین پیام‌های کانال مبدا
        messages = context.bot.get_chat_history(int(SOURCE_CHANNEL_ID), limit=10)
        
        for message in messages:
            # بررسی اینکه آیا پیام قبلاً پردازش شده یا نه
            if message.message_id not in last_processed_message:
                # فوروارد پیام به کانال مقصد
                context.bot.forward_message(
                    chat_id=int(DESTINATION_CHANNEL_ID),
                    from_chat_id=int(SOURCE_CHANNEL_ID),
                    message_id=message.message_id
                )
                last_processed_message[message.message_id] = True
                logger.info(f"پیام با ID {message.message_id} فوروارد شد.")
                
        # پاکسازی دیکشنری برای جلوگیری از رشد بی‌رویه
        if len(last_processed_message) > 100:
            oldest_id = min(last_processed_message.keys())
            del last_processed_message[oldest_id]
            
    except Exception as e:
        logger.error(f"خطا در فوروارد پیام: {e}")

def start_bot():
    # ایجاد آپدیت و دیسپچر
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # تنظیم جاب برای اجرای هر 15 دقیقه
    job_queue = updater.job_queue
    job_queue.run_repeating(forward_messages, interval=900, first=0)
    
    # شروع ربات
    updater.start_polling()
    logger.info("ربات شروع به کار کرد...")
    updater.idle()

if __name__ == '__main__':
    start_bot()
