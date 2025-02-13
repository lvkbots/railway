import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Token Telegram
BOT_TOKEN = "7859942806:AAHy4pNgFunsgO4lA2wK8TLa89tSzZjvY58"

async def start(update: Update, context):
    """Répond avec un message de bienvenue et pose une question."""
    await update.message.reply_text("Bonjour! Comment vas-tu aujourd'hui?")

async def handle_message(update: Update, context):
    """Répond en fonction du message reçu."""
    user_message = update.message.text.lower()
    if "bien" in user_message:
        await update.message.reply_text("Content de l'entendre! Quel est ton passe-temps préféré?")
    else:
        await update.message.reply_text("Je suis là pour discuter! Parle-moi de toi.")

async def main():
    """Initialise et lance le bot."""
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Le bot est en cours d'exécution...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
