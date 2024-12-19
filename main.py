from http import HTTPStatus
from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from asgiref.wsgi import WsgiToAsgi

from image.generate_image import generate_image
from text.chat import generate_chat_response
from flask import Flask, request, Response, abort, make_response, request
import asyncio
import uvicorn

app = Flask(__name__)

WEBHOOK_URL = 'https://munin-odinsraven.azurewebsites.net/'  # Replace with your actual domain

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

# application = (
#     Application.builder()
#     .token("1921970606:AAFvOb2DLn58gQqaBGXy2R4a5PFewMcP5NE")
#     .build()
# )

async def main() -> None:
    """Set up PTB application and a web application for handling the incoming requests."""
    # Here we set updater to None because we want our custom webhook server to handle the updates
    # and hence we don't need an Updater instance
    application = (
        Application.builder().token("1921970606:AAFvOb2DLn58gQqaBGXy2R4a5PFewMcP5NE").updater(None).build()
    )

    # register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("image", image))

    # Handle all text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    
    # Pass webhook settings to telegram
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}", allowed_updates=Update.ALL_TYPES)

    @app.route("/", methods=["POST"])  # type: ignore[misc]
    async def telegram() -> Response:
        """Handle incoming Telegram updates by putting them into the `update_queue`"""
        await application.update_queue.put(Update.de_json(data=request.json, bot=application.bot))
        return Response(status=HTTPStatus.OK)
    
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=WsgiToAsgi(app),
            port=8080,
            use_colors=False,
            host="0.0.0.0",
        )
    )

    # Run application and webserver together
    async with application:
        await application.start()
        await webserver.serve()
        await application.stop()


if __name__ == "__main__":
    asyncio.run(main())
