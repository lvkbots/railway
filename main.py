import asyncio
from telegram import Bot

# Token Telegram
BOT_TOKEN = "7859942806:AAHy4pNgFunsgO4lA2wK8TLa89tSzZjvY58"

async def send_message():
    """Récupère les mises à jour du bot et affiche les nouveaux messages."""
    bot = Bot(token=BOT_TOKEN)
    try:
        updates = await bot.get_updates()
        for update in updates:
            if update.message:
                print(f"Message reçu de {update.message.chat.id}: {update.message.text}")
    except Exception as e:
        print(f"Erreur lors de la récupération des messages : {e}")

async def main():
    while True:
        await send_message()
        await asyncio.sleep(10)  # Vérifie les messages toutes les 10 secondes

if __name__ == "__main__":
    asyncio.run(main())
