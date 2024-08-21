
from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from image.generate_image import generate_image
from text.chat import generate_chat_response
from flask import Flask, request

app = Flask(__name__)

WEBHOOK_URL = 'https://munin-v2-732lhukoma-nw.a.run.app/'  # Replace with your actual domain

# Define a few command handlers. These usually take the two arguments update and context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    response = await generate_chat_response("Introduce yourself!")
    await update.message.reply_html(
        rf"Hello there, {user.mention_html()}! {response}",
        reply_markup=ForceReply(selective=True),
    )

async def image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /image is issued."""
    image = await generate_image(update.message.text)
    await update.message.reply_photo(image)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = await generate_chat_response(update.message.text)
    await update.message.reply_text(response)

application = (
    Application.builder()
    .token("1921970606:AAFvOb2DLn58gQqaBGXy2R4a5PFewMcP5NE")
    .build()
)

# Webhook route to receive updates from Telegram
@app.route("/", methods=["POST"])
async def webhook() -> None:
    """Webhook route to handle incoming Telegram updates."""
    # Decode the incoming request
    update = Update.de_json(request.get_json(), application.bot)
    # Dispatch the update to the appropriate handler
    await application.process_update(update)
    
    return "ok"

if __name__ == "__main__":
    # Add handlers for different commands
    try:
        webhook_set = application.bot.set_webhook(url=WEBHOOK_URL)
    except:
        print('Failed to set webhook')
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("image", image))

    # Handle all text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    # Start the Flask server to handle webhooks
    app.run(host="0.0.0.0", port=8080)