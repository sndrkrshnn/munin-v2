from http import HTTPStatus
from contextlib import asynccontextmanager
from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from text.chat import generate_chat_response
from fastapi import FastAPI, Request, Response
import uvicorn
from config import Config

WEBHOOK_URL = Config.WEBHOOK_URL
TELEGRAM_BOT_TOKEN = Config.TELEGRAM_BOT_TOKEN

# Global application instance
ptb_application: Application = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    response = await generate_chat_response("Introduce yourself!")
    await update.message.reply_html(
        rf"Hello there, {user.mention_html()}! {response}",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages."""
    response = await generate_chat_response(update.message.text)
    await update.message.reply_text(response)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager for FastAPI lifespan events.
    Handles startup and shutdown of the Telegram bot application.
    """
    global ptb_application
    
    # Build the Telegram application
    ptb_application = (
        Application.builder().token(TELEGRAM_BOT_TOKEN).updater(None).build()
    )

    # Register handlers
    ptb_application.add_handler(CommandHandler("start", start))
    ptb_application.add_handler(CommandHandler("help", help_command))

    # Handle all text messages
    ptb_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    # Set webhook
    await ptb_application.bot.set_webhook(
        url=f"{WEBHOOK_URL}", 
        allowed_updates=Update.ALL_TYPES
    )

    # Start the application
    await ptb_application.initialize()
    await ptb_application.start()
    
    yield
    
    # Shutdown
    await ptb_application.stop()
    await ptb_application.shutdown()


app = FastAPI(lifespan=lifespan)


@app.post("/")
async def telegram_webhook(request: Request) -> Response:
    """Handle incoming Telegram updates by putting them into the update_queue."""
    data = await request.json()
    update = Update.de_json(data=data, bot=ptb_application.bot)
    await ptb_application.update_queue.put(update)
    return Response(status_code=HTTPStatus.OK)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        use_colors=False,
    )
