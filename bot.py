import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Настройка логирования ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Конфигурация ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TARGET_CHAT_ID = os.environ.get("TARGET_CHAT_ID")  # ID чата
# !!! НОВОЕ: ID темы (топика) в этом чате !!!
MESSAGE_THREAD_ID = int(os.environ.get("MESSAGE_THREAD_ID", "0"))

if not BOT_TOKEN or not TARGET_CHAT_ID or not MESSAGE_THREAD_ID:
    raise ValueError("Необходимо указать BOT_TOKEN, TARGET_CHAT_ID и MESSAGE_THREAD_ID в переменных окружения!")

# --- Команды бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ответ на команду /start."""
    await update.message.reply_text(
        "👋 Привет! Я бот для публикации заданий.\n\n"
        "Отправь мне задание в формате:\n"
        "1. Название социальной сети\n"
        "2. Ссылка\n"
        "3. Перечень актива\n\n"
        "Каждая часть — с новой строки."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка входящих сообщений от пользователей."""
    # Получаем текст сообщения и разбиваем его на строки
    text = update.message.text
    lines = text.strip().split('\n')
    
    if len(lines) < 3:
        await update.message.reply_text(
            "❌ Неверный формат. Пожалуйста, используй формат:\n\n"
            "Социальная сеть\n"
            "Ссылка\n"
            "Перечень актива"
        )
        return
    
    # Извлекаем данные
    social_network = lines[0].strip()
    link = lines[1].strip()
    activity = lines[2].strip()
    
    # Формируем красивое сообщение для публикации
    message_to_send = (
        f"#{social_network}\n"
        f"<b>Ссылка:</b> {link}\n"
        f"<b>Актив:</b> {activity}"
    )
    
    # Отправляем сообщение в целевой чат и тему
    try:
        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=message_to_send,
            message_thread_id=MESSAGE_THREAD_ID,  # <-- ВОТ ГЛАВНОЕ ИЗМЕНЕНИЕ
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        await update.message.reply_text("✅ Задание успешно опубликовано!")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в чат {TARGET_CHAT_ID}, тема {MESSAGE_THREAD_ID}: {e}")
        await update.message.reply_text("❌ Произошла ошибка при публикации задания. Попробуйте позже.")

def main() -> None:
    """Запуск бота."""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен и готов к работе...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
