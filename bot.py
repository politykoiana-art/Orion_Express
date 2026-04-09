import os
import logging
from html import escape
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Логирование ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Переменные окружения ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TARGET_CHAT_ID = os.environ.get("TARGET_CHAT_ID")
TARGET_THREAD_ID = os.environ.get("TARGET_THREAD_ID")

if not BOT_TOKEN:
    raise ValueError("❌ Не указан BOT_TOKEN в переменных окружения!")
if not TARGET_CHAT_ID:
    raise ValueError("❌ Не указан TARGET_CHAT_ID в переменных окружения!")
if not TARGET_THREAD_ID:
    raise ValueError("❌ Не указан TARGET_THREAD_ID в переменных окружения!")

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Отвечаем только в личных сообщениях
    if update.effective_chat.type != "private":
        return
    await update.message.reply_text(
        "👋 Привет! Я бот для публикации заданий.\n\n"
        "Отправь мне задание в формате:\n"
        "Социальная сеть\n"
        "Ссылка\n"
        "Перечень актива\n\n"
        "Пример:\n"
        "Instagram\n"
        "https://instagram.com/example\n"
        "Лайк, Комментарий"
    )

# --- Обработка сообщений ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Игнорируем сообщения из групп и каналов
    if update.effective_chat.type != "private":
        return

    text = update.message.text
    lines = text.strip().split('\n')

    if len(lines) < 3:
        await update.message.reply_text(
            "⚠️ Неверный формат. Используй:\n\n"
            "Социальная сеть\n"
            "Ссылка\n"
            "Перечень актива"
        )
        return

    social_network = lines[0].strip()
    link = lines[1].strip()
    activity = lines[2].strip()

    safe_social = escape(social_network)
    safe_link = escape(link)
    safe_activity = escape(activity)

    message_to_send = (
        f"#{safe_social}\n"
        f"<b>Ссылка:</b> {safe_link}\n"
        f"<b>Актив:</b> {safe_activity}"
    )

    try:
        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            message_thread_id=int(TARGET_THREAD_ID),
            text=message_to_send,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        await update.message.reply_text("✅ Задание успешно опубликовано!")
    except Exception as e:
        logger.error(f"Ошибка при отправке: {e}")
        await update.message.reply_text(f"❌ Ошибка публикации: {e}")

# --- Запуск ---
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен и готов к работе (только ЛС)...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
