import asyncio
from telegram import Bot

# Remplacez par votre propre token et ID utilisateur
BOT_TOKEN = "8125835983:AAH3ytx14PPMqYB0hzXd-fPtb7SJGf5rRixa"
USER_ID = 7951781368

async def send_message(message: str):
    """Envoie un message à un utilisateur spécifique."""
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id=USER_ID, text=message)
        print("Message envoyé avec succès !")
    except Exception as e:
        print(f"Erreur lors de l'envoi du message : {e}")

async def main():
    message = "Hello from your Telegram Bot!"
    while True:
        await send_message(message)
        await asyncio.sleep(10)  # Attente de 10 secondes avant d'envoyer le prochain message

if __name__ == "__main__":
    asyncio.run(main())
