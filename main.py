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
from flask import Flask
import threading

app = Flask(__name__)


# @app.route('/')
# def home():
#     return "This is a telegram bot running on Cloud Run."


# Define a few command handlers. These usually take the two arguments update and
# context.
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
    # await update.message.reply_html(
    #     rf"Hi {user.mention_html()}!",
    #     reply_markup=ForceReply(selective=True),
    # )


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


@app.route("/", methods=["POST","GET"])
def main() -> None:
    """Start the bot."""
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("image", image))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    # Run the bot until the user presses Ctrl-C
    # application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    # Start background task in a separate thread
    # thread = threading.Thread(target=main)
    # thread.start()

    # # Run Flask server
    app.run(host="0.0.0.0", port=8080)
