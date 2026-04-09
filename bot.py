import os
import logging
from html import escape
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Настройка логирования ---
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

# --- Фильтр для скрытия токена в логах (опционально) ---
class TokenFilter(logging.Filter):
    def filter(self, record):
        if BOT_TOKEN and hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = record.msg.replace(BOT_TOKEN, "[TOKEN_HIDDEN]")
        return True

for handler in logging.root.handlers:
    handler.addFilter(TokenFilter())

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type != "private":
        return
    await update.message.reply_text(
        "👋 Привет! Я бот для публикации заданий.\n\n"
        "Отправь мне задание в формате:\n"
        "Социальная сеть\n"
        "Ссылка (одна или несколько)\n"
        "Перечень актива\n\n"
        "Пример с одной ссылкой:\n"
        "Instagram\n"
        "https://instagram.com/example\n"
        "Лайк, Комментарий\n\n"
        "Пример с двумя ссылками:\n"
        "Telegram\n"
        "https://t.me/username\n"
        "https://t.me/channel\n"
        "Лайк, Репост"
    )

# --- Обработка сообщений ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type != "private":
        return

    text = update.message.text.strip()
    lines = text.split('\n')

    if len(lines) < 3:
        await update.message.reply_text(
            "⚠️ Неверный формат. Должно быть минимум 3 строки:\n"
            "1. Соцсеть\n"
            "2. Ссылка (минимум одна)\n"
            "3. Активности"
        )
        return

    # Первая строка — соцсеть
    social_network = lines[0].strip()
    # Последняя строка — активности
    activity = lines[-1].strip()
    # Всё между первой и последней — ссылки (может быть одна или несколько)
    links = [line.strip() for line in lines[1:-1] if line.strip()]

    if not links:
        await update.message.reply_text("⚠️ Не указана ни одна ссылка.")
        return

    # Экранирование HTML
    safe_social = escape(social_network)
    safe_activity = escape(activity)
    safe_links = [escape(link) for link in links]

    # Формируем сообщение
    if len(safe_links) == 1:
        links_text = f"<b>Ссылка:</b> {safe_links[0]}"
    else:
        links_text = "<b>Ссылки:</b>\n" + "\n".join(f"• {link}" for link in safe_links)

    message_to_send = (
        f"#{safe_social}\n"
        f"{links_text}\n"
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