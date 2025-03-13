import nest_asyncio 
nest_asyncio.apply()

import asyncio
import logging
import os
import threading
import random
import uuid
import json
from collections import defaultdict
from datetime import datetime, timedelta
from flask import Flask
import aiosqlite
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import MessageHandler, filters
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Configuration du logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Application Flask
app = Flask(__name__)

@app.route("/")
def home():
    return f"Bot actif depuis {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# Configuration
TOKEN = "7859942806:AAHy4pNgFunsgO4lA2wK8TLa89tSzZjvY58"
ADMIN_ID = 7392567951

# Ressources médias (inchangées)
MEDIA_RESOURCES = {
    "intro_video": "https://drive.google.com/uc?export=download&id=1NREjyyYDfdgGtx4r-Lna-sKgpCHIC1ia",
    "main_image": "https://i.postimg.cc/05CCgr53/photo-2025-02-17-09-41-43.jpg",
    "bottom_image": "https://aviator.com.in/wp-content/uploads/2024/04/Aviator-Predictor-in-India.png",
    "payment_proofs": [
        "https://i.postimg.cc/fRDSWT41/photo-2025-02-13-14-41-26-2.jpg",
        "https://i.postimg.cc/VNHJFqSc/photo-2025-02-13-14-41-25-2.jpg",
        "https://i.postimg.cc/RF6NpWfJ/photo-2025-02-13-14-41-25.jpg",
        "https://i.postimg.cc/MH1Xxg9W/photo-2025-02-13-14-41-26.jpg",
        "https://i.postimg.cc/zDkrZJjy/bandicam-2025-02-13-17-36-48-522.jpg"
    ],
    "info_images": [
        "https://i.postimg.cc/6QGXDnjK/bandicam-2025-02-13-17-33-14-929.jpg",
        "https://i.postimg.cc/zf3B3yx2/bandicam-2025-02-13-17-24-18-009.jpg",
        "https://i.postimg.cc/FHzmV207/bandicam-2025-02-13-17-32-31-633.jpg",
        "https://i.postimg.cc/mgn4X8SV/bandicam-2025-02-13-17-33-57-485.jpg",
        "https://media.licdn.com/dms/image/D5622AQGO3fuy3Xsi1w/feedshare-shrink_2048_1536/0/1717229135545?e=2147483647&v=beta&t=bj-cWzd74icpjK9Vb5mL6DhXXvdCz12alcJLQvqSg3s"
    ],
    "vip_images": [
        "https://i.postimg.cc/mgn4X8SV/bandicam-2025-02-13-17-33-57-485.jpg",
        "https://i.postimg.cc/zXtYv045/bandicam-2025-02-13-17-38-48-355.jpg"
    ]
}

def generate_random_coefficient():
    """Génère un coefficient aléatoire avec une forte probabilité entre 10 et 600"""
    if random.random() < 0.9:  # 90% de chance d'être entre 10 et 600
        return round(random.uniform(10, 600), 2)
    else:  # 10% de chance d'être entre 600 et 1702.03
        return round(random.uniform(600, 1702.03), 2)

class DatabaseManager:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY,
                    referral_code TEXT,
                    referred_by TEXT,
                    join_date TEXT,
                    vip_status INTEGER DEFAULT 0,
                    notification_settings TEXT,
                    stats TEXT
                )
            """)
            await db.commit()

    async def add_user(self, chat_id: int, referral_code=None):
        user_referral_code = str(uuid.uuid4())[:8]
        current_date = datetime.now().strftime('%Y-%m-%d')
        default_notifications = json.dumps({"signals": True, "promos": True, "marathons": True})
        default_stats = json.dumps({"predictions_received": 0, "correct_predictions": 0, "total_profit": 0})
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (chat_id, referral_code, referred_by, join_date, notification_settings, stats) VALUES (?, ?, ?, ?, ?, ?)", 
                (chat_id, user_referral_code, referral_code, current_date, default_notifications, default_stats)
            )
            await db.commit()
            
            if referral_code:
                # Vérifier si le code de parrainage existe
                async with db.execute("SELECT chat_id FROM users WHERE referral_code = ?", (referral_code,)) as cursor:
                    referrer = await cursor.fetchone()
                    if referrer:
                        return True, user_referral_code
            
            return False, user_referral_code

    async def get_all_users(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT chat_id FROM users") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def get_user_data(self, chat_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    columns = [column[0] for column in cursor.description]
                    return dict(zip(columns, row))
                return None

    async def update_user_stats(self, chat_id: int, key: str, value):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT stats FROM users WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    stats = json.loads(row[0])
                    if key in stats:
                        stats[key] += value
                    else:
                        stats[key] = value
                    
                    await db.execute("UPDATE users SET stats = ? WHERE chat_id = ?", (json.dumps(stats), chat_id))
                    await db.commit()

    async def update_notification_settings(self, chat_id: int, settings_dict):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT notification_settings FROM users WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    current_settings = json.loads(row[0])
                    current_settings.update(settings_dict)
                    
                    await db.execute("UPDATE users SET notification_settings = ? WHERE chat_id = ?", 
                                    (json.dumps(current_settings), chat_id))
                    await db.commit()

    async def update_vip_status(self, chat_id: int, is_vip: bool):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET vip_status = ? WHERE chat_id = ?", (1 if is_vip else 0, chat_id))
            await db.commit()

    async def get_user_referrals(self, referral_code: str):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT chat_id FROM users WHERE referred_by = ?", (referral_code,)) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

class KeyboardManager:
    @staticmethod
    def create_main_keyboard():
        keyboard = [
            [InlineKeyboardButton("🎯 COMMENT LE HACK FONCTIONNE", callback_data="info_bots")],
            [InlineKeyboardButton("💰 PREUVES DE RETRAIT", callback_data="casino_withdrawal")],
            [InlineKeyboardButton("❓ AIDE", callback_data="help_menu")],
            [InlineKeyboardButton("📱 Contacter l'expert", url="https://t.me/BILLGATESHACK")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_program_button():
        keyboard = [[InlineKeyboardButton("🚀 OBTENIR LE PROGRAMME MAINTENANT", url="https://t.me/BILLGATESHACK")]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_help_keyboard():
        keyboard = [
            [InlineKeyboardButton("📊 Mes Statistiques", callback_data="my_stats")],
            [InlineKeyboardButton("🔔 Notifications", callback_data="notifications")],
            [InlineKeyboardButton("👥 Programme de Parrainage", callback_data="referral")],
            [InlineKeyboardButton("💎 Mode VIP", callback_data="vip_info")],
            [InlineKeyboardButton("🔙 Retour", callback_data="back_to_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_notification_keyboard(settings):
        settings_dict = json.loads(settings) if isinstance(settings, str) else settings
        keyboard = [
            [InlineKeyboardButton(
                f"{'🔔' if settings_dict.get('signals', True) else '🔕'} Signaux Aviator",
                callback_data="toggle_signals"
            )],
            [InlineKeyboardButton(
                f"{'🔔' if settings_dict.get('promos', True) else '🔕'} Promotions",
                callback_data="toggle_promos"
            )],
            [InlineKeyboardButton(
                f"{'🔔' if settings_dict.get('marathons', True) else '🔕'} Marathons",
                callback_data="toggle_marathons"
            )],
            [InlineKeyboardButton("🔙 Retour", callback_data="back_to_help")]
        ]
        return InlineKeyboardMarkup(keyboard)

class MessageBroadcaster:
    def __init__(self, db_manager, delay_seconds):
        self.db_manager = db_manager
        self.delay = delay_seconds
        self.running = True

    async def send_message_with_photo(self, context, user_id, text, photo_url, max_retries=3):
        """Méthode commune pour envoyer un message avec photo"""
        for attempt in range(max_retries):
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode='Markdown'
                )
                if photo_url:
                    await asyncio.sleep(0.5)
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo_url
                    )
                return True
            except Exception as e:
                logger.error(f"Tentative {attempt + 1}/{max_retries} échouée pour {user_id}: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
        return False

    async def get_message(self, user_id=None, context=None):
        """Chaque classe doit implémenter sa propre logique de message"""
        pass

    def get_photo_url(self):
        """Chaque classe doit fournir son URL de photo"""
        pass

    async def broadcast(self, context):
        """Méthode commune de diffusion"""
        while self.running:
            try:
                logger.info(f"Début de la diffusion pour {self.__class__.__name__}")
                users = await self.db_manager.get_all_users()
                
                for user_id in users:
                    if not self.running:
                        break
                    
                    # Vérifier les paramètres de notification
                    user_data = await self.db_manager.get_user_data(user_id)
                    if user_data:
                        settings = json.loads(user_data.get('notification_settings', '{}'))
                        
                        # Déterminer le type de message et vérifier les paramètres
                        should_send = False
                        if isinstance(self, SignalBroadcaster) and settings.get('signals', True):
                            should_send = True
                        elif isinstance(self, MarathonBroadcaster) and settings.get('marathons', True):
                            should_send = True
                        elif (isinstance(self, PromoBroadcaster) or isinstance(self, InvitationBroadcaster)) and settings.get('promos', True):
                            should_send = True
                        elif isinstance(self, VIPSignalBroadcaster):
                            # Les messages VIP sont gérés différemment
                            should_send = False
                        
                        if should_send:
                            message = await self.get_message(user_id, context)
                            await self.send_message_with_photo(
                                context,
                                user_id,
                                message,
                                self.get_photo_url()
                            )
                            
                            # Mettre à jour les statistiques pour les signaux
                            if isinstance(self, SignalBroadcaster):
                                await self.db_manager.update_user_stats(user_id, "predictions_received", 1)
                                # Simuler une prédiction correcte avec 70% de chance
                                if random.random() < 0.7:
                                    await self.db_manager.update_user_stats(user_id, "correct_predictions", 1)
                                    profit = random.randint(2000, 8000)
                                    await self.db_manager.update_user_stats(user_id, "total_profit", profit)
                    
                    await asyncio.sleep(0.5)

                logger.info(f"Diffusion terminée pour {self.__class__.__name__}")
                await asyncio.sleep(self.delay)

            except Exception as e:
                logger.error(f"Erreur dans {self.__class__.__name__}: {str(e)}")
                await asyncio.sleep(5)

class SignalBroadcaster(MessageBroadcaster):
    def __init__(self, db_manager):
        super().__init__(db_manager, delay_seconds=10)

    def get_photo_url(self):
        return 'https://aviator.com.in/wp-content/uploads/2024/04/Aviator-Predictor-in-India.png'

    async def get_message(self, user_id=None, context=None):
        # Génération du coefficient avec distribution ciblée
        random_val = random.random()
        if random_val < 0.7:  # 70% entre 200 et 800
            coefficient = round(200 + (600 * random.random()), 2)
        elif random_val < 0.85:  # 15% entre 30.09 et 200
            coefficient = round(30.09 + (169.91 * random.random()), 2)
        else:  # 15% entre 800 et 1700.01
            coefficient = round(800 + (900.01 * random.random()), 2)
        
        mise = 3000
        gain = round(coefficient * mise, 2)

        return (
            f"🚀 **SIGNAL TOUR SUIVANT Aviator Prediction** 📈\n\n"
            f"🎯 Le coefficient pour ce tour est de **{coefficient}x**.\n\n"
            f"💸 Mise potentielle: **{mise} FCFA** → Gain: **{gain} FCFA** ! 💰\n"
            f"⚡️ Récupère le hack pour le **tour suivant** ! ⏱️\n\n"
            f"⏰ **Heure** : {datetime.now().strftime('%H:%M:%S')}\n\n"
            '💬 **Envoie "BOT" à @BILLGATESHACK** pour obtenir le bot gratuitement !'
        )

class MarathonBroadcaster(MessageBroadcaster):
    def __init__(self, db_manager):
        super().__init__(db_manager, delay_seconds=20)

    def get_photo_url(self):
        return "https://i.postimg.cc/zXtYv045/bandicam-2025-02-13-17-38-48-355.jpg"

    async def get_message(self, user_id=None, context=None):
        return (
            "🏆 **MARATHON GAGNANT-GAGNANT** 🏆\n\n"
            "🔥 **Objectif** : Faire gagner **50 000 FCFA** à chaque participant **AUJOURD'HUI** !\n\n"
            "⏳ **Durée** : 1 heure\n\n"
            "📹 **Guide personnel avec liaison vidéo !**\n\n"
            "💬 **Envoyez 'MARATHON'** pour participer !\n\n"
            "@BILLGATESHACK @BILLGATESHACK @BILLGATESHACK"
        )

class PromoBroadcaster(MessageBroadcaster):
    def __init__(self, db_manager):
        super().__init__(db_manager, delay_seconds=1527)

    def get_photo_url(self):
        return "https://i.postimg.cc/FHzmV207/bandicam-2025-02-13-17-32-31-633.jpg"

    async def get_message(self, user_id=None, context=None):
        first_name = "Ami"
        if context and user_id:
            try:
                chat = await context.bot.get_chat(user_id)
                first_name = chat.first_name if chat.first_name else "Ami"
            except:
                pass

        return (
            f"👋 Bonjour {first_name} !\n\n"
            "Vous avez besoin d'argent? Écrivez-moi @BILLGATESHACK pour comprendre le programme.\n\n"
            "Dépêchez-vous !!! Les places sont limitées !\n\n"
            "@BILLGATESHACK\n\n"
            "@BILLGATESHACK\n\n"
            "@BILLGATESHACK"
        )

class InvitationBroadcaster(MessageBroadcaster):
    def __init__(self, db_manager):
        super().__init__(db_manager, delay_seconds=1805)

    def get_photo_url(self):
        return "https://i.postimg.cc/yxn4FPdm/bandicam-2025-02-13-17-35-47-978.jpg"

    async def get_message(self, user_id=None, context=None):
        first_name = "Ami"
        if context and user_id:
            try:
                chat = await context.bot.get_chat(user_id)
                first_name = chat.first_name if chat.first_name else "Ami"
            except:
                pass

        return (
            f"👋 Bonjour {first_name} !\n\n"
            "💰 **Avez-vous gagné de l'argent aujourd'hui ?** 💭\n\n"
            "❌ Si la réponse est non, qu'attendez-vous ? 🤔\n\n"
            "🎯 Un signe particulier ? \n\n"
            "💵 Le voici $ 💫\n\n"
            "👨‍🏫 Je suis prêt à accueillir deux nouveaux élèves et à les amener à des résultats dès aujourd'hui !\n\n"
            "@BILLGATESHACK"
        )

class VIPSignalBroadcaster(MessageBroadcaster):
    def __init__(self, db_manager):
        super().__init__(db_manager, delay_seconds=30)  # Signaux VIP plus fréquents
        self.success_rate = 0.95  # Taux de réussite plus élevé pour les VIP

    def get_photo_url(self):
        return random.choice([
            'https://i.postimg.cc/mgn4X8SV/bandicam-2025-02-13-17-33-57-485.jpg',
            'https://aviator.com.in/wp-content/uploads/2024/04/Aviator-Predictor-in-India.png'
        ])

    async def get_message(self, user_id=None, context=None):
        # Plus haute probabilité de coefficients gagnants pour les VIP
        if random.random() < self.success_rate:
            coefficient = round(random.uniform(50, 500), 2)  # Coefficients plus modérés mais plus sûrs
        else:
            coefficient = round(random.uniform(5, 40), 2)
            
        mise = random.choice([5000, 7500, 10000])  # Mises plus élevées pour les VIP
        gain = round(coefficient * mise, 2)
        
        # Ajout de timing précis pour les VIP
        current_time = datetime.now()
        precise_time = (current_time + timedelta(minutes=random.randint(1, 3))).strftime('%H:%M:%S')

        return (
            f"🌟 **SIGNAL VIP EXCLUSIF** 🌟\n\n"
            f"✅ Coefficient attendu: **{coefficient}x**\n"
            f"💰 Mise recommandée: **{mise} FCFA**\n"
            f"💎 Gain potentiel: **{gain} FCFA**\n\n"
            f"⏱️ Heure optimale: **{precise_time}**\n"
            f"📊 Précision: **95%**\n\n"
            f"🔐 Ce signal est réservé aux membres VIP\n\n"
            f"📲 Pour plus d'informations, contactez @BILLGATESHACK"
        )

    async def broadcast(self, context):
        while self.running:
            try:
                users = await self.db_manager.get_all_users()
                
                for user_id in users:
                    if not self.running:
                        break
                    
                    # Vérifier si l'utilisateur est VIP
                    user_data = await self.db_manager.get_user_data(user_id)
                    if user_data and user_data.get('vip_status', 0) == 1:
                        # Vérifier les paramètres de notification
                        settings = json.loads(user_data.get('notification_settings', '{}'))
                        if settings.get('signals', True):
                            message = await self.get_message(user_id, context)
                            await self.send_message_with_photo(context, user_id, message, self.get_photo_url())
                            
                            # Mettre à jour les statistiques
                            await self.db_manager.update_user_stats(user_id, "predictions_received", 1)
                            # Simuler une prédiction correcte la plupart du temps
                            if random.random() < 0.9:
                                await self.db_manager.update_user_stats(user_id, "correct_predictions", 1)
                                profit = random.randint(5000, 20000)
                                await self.db_manager.update_user_stats(user_id, "total_profit", profit)
                    
                await asyncio.sleep(0.5)
                await asyncio.sleep(self.delay)

            except Exception as e:
                logger.error(f"Erreur dans VIPSignalBroadcaster: {str(e)}")
                await asyncio.sleep(5)

class BotHandler:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.signal_broadcaster = SignalBroadcaster(db_manager)
        self.marathon_broadcaster = MarathonBroadcaster(db_manager)
        self.promo_broadcaster = PromoBroadcaster(db_manager)
        self.invitation_broadcaster = InvitationBroadcaster(db_manager)
        self.vip_signal_broadcaster = VIPSignalBroadcaster(db_manager)
        self.running = True
        self.referral_rewards = defaultdict(int)  # Pour suivre les récompenses
        self.last_user_interaction = {}  # Pour suivre la dernière interaction

    async def handle_message(self, update, context):
        """Gestionnaire pour tous les messages texte"""
        user_id = update.effective_user.id
        
        message = (
            "❌ Désolé, ce bot ne peut pas répondre à votre message.\n\n"
            "💬 Écrivez-moi ici @BILLGATESHACK pour obtenir le hack gratuitement!"
        )
        
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Erreur dans handle_message pour {user_id}: {str(e)}")

    def register_handlers(self, application):
        """Enregistre les gestionnaires de messages"""
        # Handler pour la commande start
        application.add_handler(CommandHandler("start", self.start_command))
        
        # Handler pour la commande help
        application.add_handler(CommandHandler("help", self.help_command))
        
        # Handler pour la commande stats
        application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Handler pour les boutons
        application.add_handler(CallbackQueryHandler(self.handle_button))
        
        # Handler pour tous les messages texte (non commandes)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Handler pour tous les messages de l'admin
        application.add_handler(MessageHandler(
            filters.ALL & filters.Chat(ADMIN_ID),
            self.handle_admin_message
        ))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        first_name = update.effective_user.first_name
        
        # Vérifier si c'est un démarrage avec référence
        referral_code = None
        if context.args and len(context.args) > 0:
            referral_code = context.args[0]
        
        # Ajouter l'utilisateur à la base de données
        was_referred, user_code = await self.db_manager.add_user(chat_id, referral_code)
        
        try:
            if was_referred:
                # Informer le parrain qu'il a un nouveau filleul
                referrer_id = None
                async with aiosqlite.connect(self.db_manager.db_path) as db:
                    async with db.execute("SELECT chat_id FROM users WHERE referral_code = ?", (referral_code,)) as cursor:
                        row = await cursor.fetchone()
                        if row:
                            referrer_id = row[0]
                
                if referrer_id:
                    try:
                        await context.bot.send_message(
                            chat_id=referrer_id,
                            text=f"🎉 Félicitations! Un nouveau membre a rejoint grâce à votre lien de parrainage!\n\n"
                                 f"👤 {first_name} vient de rejoindre notre communauté.\n\n"
                                 f"💰 Vous recevrez des bonus pour chaque gain qu'il réalisera!",
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Erreur lors de la notification du parrain {referrer_id}: {e}")
            
            # Envoyer le message de bienvenue
            welcome_message = (
                f"👋 Bonjour {first_name} !\n\n"
                f"🎉 Bienvenue dans notre bot de signaux Aviator!\n\n"
                f"💫 Vous recevrez automatiquement nos signaux exclusifs.\n\n"
                f"🔗 Votre lien de parrainage personnel: t.me/{context.bot.username}?start={user_code}\n\n"
                f"🚀 Restez connecté pour ne manquer aucune opportunité !"
            )
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=welcome_message,
                parse_mode='Markdown'
            )
            
            # Continuer avec le processus de démarrage normal
            await context.bot.send_video(
                chat_id=chat_id,
                video=MEDIA_RESOURCES["intro_video"],
                caption="🎮 Découvrez notre méthode révolutionnaire ! 🎰"
            )
            
            message = f"""🎯 BONJOUR ❗️

Je suis un programmeur Africain et je travaille avec des Russes, je connais la combine pour retirer l'argent des jeux casinos.

✅ 1800 personnes ont déjà gagné avec moi. Et je peux vous garantir en toute confiance que vous gagnerez.

💫 Vous pouvez gagner de l'argent sans rien faire, car j'ai déjà fait tout le programme pour vous.

🔥 Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y')}"""

            await update.message.reply_photo(
                photo=MEDIA_RESOURCES["main_image"],
                caption=message,
                reply_markup=KeyboardManager.create_main_keyboard()
            )
            
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=MEDIA_RESOURCES["bottom_image"],
                caption="🏆 Rejoignez les gagnants dès aujourd'hui !"
            )
            
        except Exception as e:
            logger.error(f"Erreur start: {chat_id}: {e}")

    async def handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        chat_id = update.effective_chat.id
        
        try:
            if query.data == "casino_withdrawal":
                await self._handle_withdrawal(context, chat_id)
            elif query.data == "info_bots":
                await self._handle_info(context, chat_id)
                
        except Exception as e:
            logger.error(f"Erreur bouton {chat_id}: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="Une erreur est survenue. Réessayez."
            )

    async def _handle_withdrawal(self, context, chat_id):
        await context.bot.send_message(
            chat_id=chat_id,
            text="""🎰 PREUVES DE PAIEMENT RÉCENTES 🎰

💎 Ces retraits ont été effectués dans les dernières 24 heures
✨ Nos utilisateurs gagnent en moyenne 50.000 FCFA par jour
⚡️ Méthode 100% automatisée et garantie
🔒 Aucun risque de perte

👇 Voici les preuves en images 👇"""
        )
        media_group = [InputMediaPhoto(media=url) for url in MEDIA_RESOURCES["payment_proofs"]]
        await context.bot.send_media_group(chat_id=chat_id, media=media_group)
        await context.bot.send_message(
            chat_id=chat_id,
            text="🌟 Prêt à commencer votre succès ?",
            reply_markup=KeyboardManager.create_program_button()
        )

    async def _handle_info(self, context, chat_id):
        await context.bot.send_message(
            chat_id=chat_id,
            text="""🤖 COMMENT LE HACK FONCTIONNE 🤖

✅ Intelligence artificielle avancée
🎯 Taux de réussite de 98.7%
💫 Mise à jour quotidienne des algorithmes
⚡️ Plus de 1800 utilisateurs satisfaits

👇 Découvrez notre système en images 👇"""
        )
        media_group = [InputMediaPhoto(media=url) for url in MEDIA_RESOURCES["info_images"]]
        await context.bot.send_media_group(chat_id=chat_id, media=media_group)
        await context.bot.send_message(
            chat_id=chat_id,
            text="🚀 Prêt à révolutionner vos gains ?",
            reply_markup=KeyboardManager.create_program_button()
        )

def keep_alive():
    def run():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    thread = threading.Thread(target=run)
    thread.start()

async def main():
    try:
        db_manager = DatabaseManager()
        await db_manager.init_db()
        
        bot_handler = BotHandler(db_manager)
        
        application = Application.builder().token(TOKEN).build()
        
        # Handler pour la commande start
        application.add_handler(CommandHandler("start", bot_handler.start_command))
        
        # Handler pour les boutons
        application.add_handler(CallbackQueryHandler(bot_handler.handle_button))
        
        # Handler pour tous les messages de l'admin
        application.add_handler(MessageHandler(
            filters.ALL & filters.Chat(ADMIN_ID),
            bot_handler.handle_admin_message
        ))
        
        # Démarrer la diffusion automatique
        asyncio.create_task(bot_handler.auto_broadcast_signal(application))
        
        keep_alive()
        logger.info("Bot démarré!")
        await application.run_polling()
        
    except Exception as e:
        logger.critical(f"Erreur fatale: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
