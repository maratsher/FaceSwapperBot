
import logging
import db_api as db
from swapper import swap
import configparser

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read("config.ini")

RES_IMG = range(1)

TOKEN = config.get("telegram_bot", "token")

IMG_TARGET = "img_target"
IMG_RES = "img_res"
IMG_RESULT = "img_result"

PREFIX = config.get("files", "prefix")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start знакомит пользовтеля с функционалом бота"""
    
    db.add_user(str(update.message.chat_id))

    keyboard = [
        [
            KeyboardButton("/start", callback_data="1"),
            KeyboardButton("/cancel", callback_data="2"),
        ],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    await update.message.reply_text(

        "Просто пришли мне фото, откуда мы будем вырезать лицо.",
        reply_markup=reply_markup
    )


async def target_img(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохронить присланное целевое изображение и запросить ресурсное изоюражение"""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    chat_id = update.message.chat_id

    img_url = PREFIX+"target_"+str(update.message.chat_id)+".jpg"
    await photo_file.download(img_url)
    db.update_img(str(chat_id), IMG_TARGET, img_url)

    await update.message.reply_text(
        "Отлично! Теперь пришли мне фото, где нужно заменить лицо."
    )

    return RES_IMG

async def res_img(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохронить присланное ресурсное изображение и отправить резльтут"""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    chat_id = update.message.chat_id

    img_url = PREFIX+"res_"+str(update.message.chat_id)+".jpg"
    await photo_file.download(img_url)
    db.update_img(str(chat_id), IMG_RES, img_url)

    await update.message.reply_text(
        "Готово! Вот Результат:"
    )

    print(db.get_target_img(str(chat_id)))
    img_url = swap(db.get_target_img(str(chat_id)), img_url, str(chat_id))

    await context.bot.send_photo(chat_id, photo=open(PREFIX+"result_"+str(chat_id)+".jpg", 'rb'))

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Закончить диолог"""
    user = update.message.from_user
    await update.message.reply_text(
        "Отменено..."
    )

    return ConversationHandler.END

def main() -> None:
    """Запустить бота"""
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.PHOTO, target_img)],
        states={
            RES_IMG: [MessageHandler(filters.PHOTO, res_img)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )

    start_handler = CommandHandler("start", start)

    application.add_handler(conv_handler)
    application.add_handler(start_handler)

    application.run_polling()


if __name__ == "__main__":
    main()