from telethon import TelegramClient, events, Button
import json
import os

# === CONFIGURATION ===
BOT_TOKEN = '7921657103:AAFx5EsIw3THsYZ76_EKuLPhTk7TKOtim64'
OWNER_ID = 5998835324  # Your Telegram numeric user ID (admin)
DATA_FILE = 'users_data.json'  # Local message store

# === INIT CLIENT FOR BOT TOKEN ===
bot = TelegramClient('rakkun_bot', api_id=0, api_hash='none').start(bot_token=BOT_TOKEN)

# === LOAD/SAVE DATA ===
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

user_data = load_data()

# === HANDLE /start ===
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user = await event.get_sender()
    uid = str(user.id)

    if uid not in user_data:
        user_data[uid] = {
            'username': user.username or '',
            'name': user.first_name or '',
            'messages': []
        }
        save_data(user_data)

    welcome_text = "👋 *This is Rakkun Chatbot*\n\nClick the button below to start chatting."
    await event.respond(welcome_text, buttons=[
        [Button.inline("✉️ Start Chatting", data=b'start_chat')]
    ])

# === STORE USER MESSAGES & FORWARD TO ADMIN ===
@bot.on(events.NewMessage(incoming=True))
async def handle_user_messages(event):
    user = await event.get_sender()
    uid = str(user.id)

    if uid == str(OWNER_ID):  # Skip admin's own messages
        return

    if uid not in user_data:
        user_data[uid] = {
            'username': user.username or '',
            'name': user.first_name or '',
            'messages': []
        }

    user_data[uid]['messages'].append(event.text)
    user_data[uid]['messages'] = user_data[uid]['messages'][-20:]
    save_data(user_data)

    uname = user.username or user.first_name
    await bot.send_message(OWNER_ID, f"📥 Message from @{uname} ({uid}):\n{event.text}")

# === INLINE BUTTON TO ENABLE CHAT ===
@bot.on(events.CallbackQuery(data=b'start_chat'))
async def start_chat_callback(event):
    await event.edit("😊 You can now start messaging. Just type below:")

# === ADMIN PANEL ===
@bot.on(events.NewMessage(from_users=OWNER_ID, pattern='/panel'))
async def admin_panel(event):
    buttons = []
    for uid in user_data:
        uname = user_data[uid]['username'] or user_data[uid]['name']
        label = f"@{uname}" if user_data[uid]['username'] else user_data[uid]['name']
        buttons.append([Button.inline(label, data=f'user_{uid}'.encode())])

    if not buttons:
        await event.respond("⚠️ No users yet.")
        return

    await event.respond("📊 *User List:*", buttons=buttons)

# === SHOW LAST 3 MESSAGES FROM SELECTED USER ===
@bot.on(events.CallbackQuery(pattern=b'user_'))
async def show_user_history(event):
    uid = event.data.decode().split('_')[1]
    if uid in user_data:
        msgs = user_data[uid]['messages'][-3:]
        uname = user_data[uid]['username'] or user_data[uid]['name']
        text = f"👤 *Last 3 messages from @{uname}:*\n\n"
        for m in msgs:
            text += f"- {m}\n"
        await event.answer()
        await event.respond(text)
    else:
        await event.answer("User not found.", alert=True)

# === START THE BOT ===
print("🤖 Rakkun Chatbot is running...")
bot.run_until_disconnected()
