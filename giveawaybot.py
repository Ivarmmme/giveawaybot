import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Initialize your bot
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

bot = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Get chat links and required chat IDs from environment variables
chat_links = os.getenv("CHAT_LINKS").split(',')
required_chat_ids = [int(chat_id) for chat_id in os.getenv("REQUIRED_CHAT_IDS").split(',')]

# Dictionary to store referral links for each user
referral_links = {}

# Function to check if a user is a member of a chat
def is_member(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except Exception as e:
        print(f"Error checking membership for user {user_id} in chat {chat_id}: {e}")
    return False

# Function to generate a unique referral link for a user
def generate_referral_link(user_id):
    # Generate the referral link using user-specific information
    username = bot.get_me().username
    referral_link = f"https://t.me/{username}?start={user_id}"
    return referral_link

# Define the /start command handler
@bot.on_message(filters.command("start"))
def start(bot, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Send the initial message with the "Joined All" button and chat links
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("Joined All", callback_data="joined_all")]])
    chat_links_str = "\n".join(f"Join Chat {i+1}: {chat_link}" for i, chat_link in enumerate(chat_links))
    bot.send_message(chat_id, f"🎉 Welcome to the giveaway bot! 🎉\n\nTo get started, please join all the channels and groups listed below:\n\n{chat_links_str}", reply_markup=markup)

# Define the "Joined All" button handler
@bot.on_callback_query(filters.regex("^joined_all$"))
def joined_all(bot, query):
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    is_joined_all = True

    # Check if user is a member of all required channels and groups
    for required_chat_id in required_chat_ids:
        if not is_member(required_chat_id, user_id):
            is_joined_all = False
            break

    # If user is a member of all required chats, allow participation
    if is_joined_all:
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Referral System", callback_data="referral_system"),
             InlineKeyboardButton("Contact Support", callback_data="contact_support"),
             InlineKeyboardButton("Help", callback_data="help")]
        ])
        bot.send_message(chat_id, "🚀 Congratulations! You're all set! 🚀\n\nYou've successfully joined all the required channels and groups! Thank you for taking this step! 🙌\n\nYou're now eligible to participate in the giveaway. 🎁\n\nPlease select one of the options below for further actions:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "⚠️ Oops! It seems you haven't joined all the required channels/groups yet. Please make sure to join them all to participate in the giveaway. 📢")

# Define the Referral System button handler
@bot.on_callback_query(filters.regex("^referral_system$"))
def referral_system(bot, query):
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    # Generate or retrieve user's referral link
    if user_id in referral_links:
        referral_link = referral_links[user_id]
    else:
        referral_link = generate_referral_link(user_id)
        referral_links[user_id] = referral_link

    # Send the referral message to the user
    bot.send_message(chat_id, f"By referring others, you increase your chances of winning! Invite your friends using your unique referral link below:\n\n🔗 Referral Link: {referral_link}\n\nYou can also check the top referrers at: @toprefferralchannel")

# Define the Contact Support button handler
@bot.on_callback_query(filters.regex("^contact_support$"))
def contact_support(bot, query):
    chat_id = query.message.chat.id
    bot.send_message(chat_id, "🤝 Need help or assistance? Feel free to contact our support team! They're here to help you! Just reach out to [SUPPORT_USERNAME]. 📞")

# Define the Help button handler
@bot.on_callback_query(filters.regex("^help$"))
def help(bot, query):
    chat_id = query.message.chat.id
    bot.send_message(chat_id, "📘 Welcome to the Help section! Here you'll find all the guidance and support you need to use the bot and participate in the giveaway. Let's make this experience smooth and fun for you! 🎉")

# Run the bot
bot.run()
