from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration
TOKEN = "7859942806:AAHy4pNgFunsgO4lA2wK8TLa89tSzZjvY58"
ADMIN_ID = 7392567951

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envoie un message lorsque la commande /start est émise."""
    await update.message.reply_text("Bienvenue ! Ce bot est activé.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envoie un message lorsque la commande /help est émise."""
    await update.message.reply_text("Utilisez /start pour démarrer le bot.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Répond à tous les messages directs avec le message spécifié."""
    response_message = "❌ Désolé, ce bot ne peut pas répondre à votre message.\n\n" \
                      "💬 Écrivez-moi ici @BILLGATESHACK pour obtenir le hack gratuitement!"
    
    # Vérifier si le message vient de l'admin
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("Message reçu, Admin.")
    else:
        await update.message.reply_text(response_message)

def main() -> None:
    """Démarre le bot."""
    # Créer l'application
    application = Application.builder().token(TOKEN).build()

    # Ajouter les handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Répondre à tous les messages texte
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Démarrer le bot
    print("Bot démarré...")
    application.run_polling()

if __name__ == "__main__":
    main()
