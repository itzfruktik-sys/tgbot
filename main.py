import random
import time
import telebot
from telebot import apihelper
from telebot.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

# Настройки подключения к приватному серверу Mechagram
TOKEN = "1780253734:RQi7Of7lVdVuriFfkMN02dxhnxExaijvVHS"
SERVER_URL = "http://177.3.213.27:8081"

apihelper.API_URL = f"{SERVER_URL}/bot{{0}}/{{1}}"
apihelper.FILE_URL = f"{SERVER_URL}/file/bot{{0}}/{{1}}"

bot = telebot.TeleBot(TOKEN)

# Юзернейм админа без символа @
ADMIN_USERNAME = "extera"

# Базы данных в памяти
user_balances = {}
user_inventory = {}
user_referrals = {}
user_states = {}  
user_bonus_time = {} 
user_pending_sell = {} 
user_usernames = {}
username_to_id = {}
pending_withdrawals = {}

CASES = {
    "bomzh": {"name": "📦 Бомж за 3", "price": 3},
    "bears": {"name": "🧸 Сердечки и Мишки", "price": 15},
    "holiday": {"name": "🍾 Праздничный", "price": 50},
    "autumn": {"name": "🍂 Осенний", "price": 100},
    "media": {"name": "🎬 Медиа", "price": 150},
    "ufc": {"name": "🥊 UFC & Street", "price": 75},
    "cyber": {"name": "⚡ Киберпанк & Артефакты", "price": 120},
    "vip": {"name": "💍 VIP Лухари", "price": 150},
    "ton": {"name": "💎 Ton Legacy NFT", "price": 500},
    "ludoman": {"name": "🎰 Кейс Лудомана", "price": 500},
}

MENU_BUTTONS = [
    "📦 Открыть кейс", "📦 Кейсы", "🎮 Мини-игры", "🎁 Ежедневный бонус", 
    "👥 Рефералы", "🎟 Ввести промокод", "🎒 Инвентарь", "В инвентарь", 
    "👤 Профиль", "🏆 Топы лидеров", "💳 Пополнить", "📤 Вывести"
]

def update_user_cache(user):
    user_id = user.id
    if user_id not in user_balances:
        user_balances[user_id] = 44
    if user_id not in user_inventory:
        user_inventory[user_id] = []
    if user_id not in user_referrals:
        user_referrals[user_id] = {"count": 0, "earned": 0, "invited": []}
    if user.username:
        un = user.username.lower().lstrip('@')
        user_usernames[user_id] = un
        username_to_id[un] = user_id
    return user_balances[user_id]

def get_user(user_id):
    if user_id not in user_balances:
        user_balances[user_id] = 44
    if user_id not in user_inventory:
        user_inventory[user_id] = []
    if user_id not in user_referrals:
        user_referrals[user_id] = {"count": 0, "earned": 0, "invited": []}
    return user_balances[user_id]

def get_name(user):
    update_user_cache(user)
    return f"@{user.username}" if user.username else user.first_name

def generate_drop(case_price):
    multiplier = random.choices(
        [0.3, 0.6, 0.9, 1.2, 2.0, 4.0, 10.0], 
        weights=[25, 30, 22, 15, 5, 2, 1]
    )[0]
    
    val = max(1, int(case_price * multiplier))
    
    if multiplier >= 10.0:
        name = f"💎 Ультра-элитный Подарок ({val} ⭐)"
    elif multiplier >= 4.0:
        name = f"🎉 Легендарный Подарок ({val} ⭐)"
    elif multiplier >= 2.0:
        name = f"🎁 Премиум Подарок ({val} ⭐)"
    elif multiplier >= 1.2:
        name = f"🛍 Отличный Подарок ({val} ⭐)"
    elif multiplier >= 0.9:
        name = f"🧸 Хороший Подарок ({val} ⭐)"
    elif multiplier >= 0.6:
        name = f"📦 Обычный Подарок ({val} ⭐)"
    else:
        name = f"📦 Утешительный Подарок ({val} ⭐)"
        
    return name, val

def main_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("📦 Открыть кейс"), KeyboardButton("🎮 Мини-игры"))
    kb.row(KeyboardButton("🎁 Ежедневный бонус"), KeyboardButton("👥 Рефералы"))
    kb.row(KeyboardButton("🎟 Ввести промокод"), KeyboardButton("🎒 Инвентарь"))
    kb.row(KeyboardButton("👤 Профиль"), KeyboardButton("🏆 Топы лидеров"))
    kb.row(KeyboardButton("💳 Пополнить"), KeyboardButton("📤 Вывести"))
    return kb

@bot.message_handler(commands=["start"])
def cmd_start(message):
    user_id = message.from_user.id
    update_user_cache(message.from_user)
    username = get_name(message.from_user)

    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            inviter_id = int(args[1].split("_")[1])
            if inviter_id != user_id and user_id not in user_referrals[inviter_id]["invited"]:
                user_referrals[inviter_id]["invited"].append(user_id)
                user_referrals[inviter_id]["count"] += 1
                user_referrals[inviter_id]["earned"] += 50
                user_balances[inviter_id] += 50
                bot.send_message(inviter_id, "🎉 По вашей ссылке зарегистрировался игрок! +50 ⭐")
        except: pass

    bot.send_message(
        message.chat.id, 
        f"🦇 *FlowUp*\n\nоткрывай кейсы, играй и выводи NFT со склада!\n\n👤 Аккаунт: {username}\n💰 Баланс: {user_balances[user_id]} ⭐", 
        reply_markup=main_keyboard(), 
        parse_mode="Markdown"
    )

@bot.message_handler(commands=["give", "take"])
def admin_balance_control(message):
    if not message.from_user.username or message.from_user.username.lower() != ADMIN_USERNAME.lower():
        return
        
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, "⚙️ Формат: `/give [@юзернейм/ID] [сумма]` или `/take [@юзернейм/ID] [сумма]`", parse_mode="Markdown")
        return
        
    cmd = args[0][1:].lower()
    target_arg = args[1]
    
    try:
        amount = int(args[2])
        if amount <= 0: return
        
        target_id = None
        if target_arg.isdigit():
            target_id = int(target_arg)
        else:
            clean_name = target_arg.lower().lstrip('@')
            target_id = username_to_id.get(clean_name)
            if not target_id:
                for uid, un in user_usernames.items():
                    if un == clean_name:
                        target_id = uid
                        break
                        
        if not target_id:
            bot.send_message(message.chat.id, "❌ Пользователь не найден в базе.")
            return
            
        if target_id not in user_balances:
            get_user(target_id)
            
        if cmd == "give":
            user_balances[target_id] += amount
            bot.send_message(message.chat.id, f"✅ Выдано {amount} ⭐ пользователю `{target_id}`.\nНовый баланс: {user_balances[target_id]} ⭐", parse_mode="Markdown")
            try:
                bot.send_message(target_id, f"🎁 Администратор выдал вам {amount} ⭐!")
            except: pass
        elif cmd == "take":
            user_balances[target_id] = max(0, user_balances[target_id] - amount)
            bot.send_message(message.chat.id, f"✅ Списано {amount} ⭐ у пользователя `{target_id}`.\nНовый баланс: {user_balances[target_id]} ⭐", parse_mode="Markdown")
            try:
                bot.send_message(target_id, f"⚠️ Администратор списал у вас {amount} ⭐.")
            except: pass
    except ValueError: 
        bot.send_message(message.chat.id, "❌ Ошибка в аргументах команды.")

@bot.message_handler(commands=["withdrawals"])
def admin_withdrawals_list(message):
    if not message.from_user.username or message.from_user.username.lower() != ADMIN_USERNAME.lower():
        return
        
    if not pending_withdrawals:
        bot.send_message(message.chat.id, "📭 Активных заявок на вывод нет.")
        return
        
    text_out = "📋 *Активные заявки на вывод:*\n\n"
    for uid, reqs in pending_withdrawals.items():
        un = user_usernames.get(uid, f"id{uid}")
        for req in reqs:
            text_out += f"👤 @{un} (ID: `{uid}`)\n💰 Сумма: {req['amount']} ⭐\nКоманды:\n👉 Выплатить: `/pay_{uid}`\n👉 Отменить: `/cancel_{uid}`\n\n"
    bot.send_message(message.chat.id, text_out, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text and (msg.text.startswith("/pay_") or msg.text.startswith("/cancel_")))
def admin_process_withdrawal(message):
    if not message.from_user.username or message.from_user.username.lower() != ADMIN_USERNAME.lower():
        return
        
    parts = message.text.split("_")
    if len(parts) != 2: return
    action = parts[0][1:]
    try:
        target_id = int(parts[1])
    except ValueError: return
    
    if target_id not in pending_withdrawals or not pending_withdrawals[target_id]:
        bot.send_message(message.chat.id, "❌ Заявка не найдена.")
        return
        
    req = pending_withdrawals[target_id].pop(0)
    if not pending_withdrawals[target_id]:
        del pending_withdrawals[target_id]
        
    if action == "pay":
        bot.send_message(message.chat.id, f"✅ Вывод {req['amount']} ⭐ для `{target_id}` подтвержден.", parse_mode="Markdown")
        try:
            bot.send_message(target_id, f"🎉 Ваша заявка на вывод {req['amount']} ⭐ успешно выплачена!")
        except: pass
    elif action == "cancel":
        user_balances[target_id] = user_balances.get(target_id, 0) + req['amount']
        bot.send_message(message.chat.id, f"↩️ Вывод отменен, {req['amount']} ⭐ возвращены пользователю `{target_id}`.", parse_mode="Markdown")
        try:
            bot.send_message(target_id, f"⚠️ Ваша заявка на вывод отклонена, {req['amount']} ⭐ возвращены на баланс.")
        except: pass
@bot.message_handler(func=lambda msg: True)
def handle_text(message):
    update_user_cache(message.from_user)
    user_id = message.from_user.id
    text = message.text
    balance = get_user(user_id)
    username = get_name(message.from_user)

    if text in MENU_BUTTONS:
        user_states[user_id] = None
    else:
        state = user_states.get(user_id)
        state_name = state if isinstance(state, str) else (state.get("name") if isinstance(state, dict) else None)
        
        if state_name == "waiting_promo":
            user_states[user_id] = None
            if text.upper() in ["EXTERA", "FLOWUP"]:
                user_balances[user_id] += 100
                bot.send_message(message.chat.id, f"🎟 Промокод активирован! Баланс: {user_balances[user_id]} ⭐")
            else:
                bot.send_message(message.chat.id, "❌ Неверный или использованный промокод.")
            return

        elif state_name == "waiting_deposit":
            user_states[user_id] = None
            try:
                amount = int(text)
                if amount > 0:
                    bot.send_message(
                        message.chat.id,
                        f"💳 *Заявка на пополнение*\n\n"
                        f"Сумма: {amount} ⭐\n"
                        f"Получатель подарков: @{ADMIN_USERNAME}\n\n"
                        f"❗️ Отправьте подарки на сумму **{amount} ⭐** пользователю **@{ADMIN_USERNAME}**, после чего отправьте скриншот или подтверждение администратору для зачисления.",
                        parse_mode="Markdown"
                    )
            except ValueError: 
                bot.send_message(message.chat.id, "❌ Введите число.")
            return

        elif state_name == "waiting_withdrawal":
            user_states[user_id] = None
            try:
                amount = int(text)
                if amount < 400:
                    bot.send_message(message.chat.id, f"⚠️ Минимум для вывода — 400 ⭐. Вы ввели: {amount} ⭐")
                elif amount > balance:
                    bot.send_message(message.chat.id, f"❌ Недостаточно средств. У вас: {balance} ⭐")
                else:
                    user_balances[user_id] -= amount
                    if user_id not in pending_withdrawals:
                        pending_withdrawals[user_id] = []
                    pending_withdrawals[user_id].append({"amount": amount, "time": time.time()})

                    bot.send_message(
                        message.chat.id, 
                        f"📤 Заявка на вывод {amount} ⭐ успешно создана!\n👤 {username}\n\n❗️ Администратор проверит заявку и выплатит средства.",
                        parse_mode="Markdown"
                    )
                    try:
                        admin_id = username_to_id.get(ADMIN_USERNAME.lower(), 0)
                        if admin_id:
                            bot.send_message(admin_id, f"🔔 *Новая заявка на вывод!*\nОт: {username} (ID: `{user_id}`)\nСумма: {amount} ⭐\n\nИспользуйте `/withdrawals`", parse_mode="Markdown")
                    except: pass
            except ValueError: bot.send_message(message.chat.id, "❌ Введите число.")
            return
            
        elif state_name == "waiting_dice_bet":
            user_states[user_id] = None
            try:
                bet = int(text)
                if bet > balance or bet <= 0: return bot.send_message(message.chat.id, "❌ Некорректная ставка.")
                
                user_balances[user_id] -= bet
                if random.randint(1, 100) > 52:
                    win = int(bet * 1.8)
                    user_balances[user_id] += win
                    bot.send_message(message.chat.id, f"🎲 Вы выиграли {win} ⭐!\nБаланс: {user_balances[user_id]} ⭐")
                else:
                    bot.send_message(message.chat.id, f"🎲 Вы проиграли {bet} ⭐.\nБаланс: {user_balances[user_id]} ⭐")
            except ValueError: bot.send_message(message.chat.id, "❌ Введите число.")
            return

        elif state_name == "waiting_crash_bet":
            try:
                bet = int(text)
                if bet > balance or bet <= 0: 
                    return bot.send_message(message.chat.id, "❌ Некорректная ставка.")
                
                user_states[user_id] = {"name": "selecting_crash_multi", "bet": bet}
                
                markup = InlineKeyboardMarkup(row_width=3)
                markup.add(
                    InlineKeyboardButton("1.2x", callback_data="crash_pick_1.2"),
                    InlineKeyboardButton("1.5x", callback_data="crash_pick_1.5"),
                    InlineKeyboardButton("2.0x", callback_data="crash_pick_2.0"),
                    InlineKeyboardButton("3.0x", callback_data="crash_pick_3.0"),
                    InlineKeyboardButton("5.0x", callback_data="crash_pick_5.0"),
                    InlineKeyboardButton("10.0x", callback_data="crash_pick_10.0")
                )
                markup.add(InlineKeyboardButton("🔙 Отмена", callback_data="back_games"))
                bot.send_message(message.chat.id, f"🚀 Ставка принята: {bet} ⭐\n\nВыберите желаемый коэффициент вывода кнопкой ниже:", reply_markup=markup)
            except ValueError: 
                bot.send_message(message.chat.id, "❌ Введите число.")
            return

        elif state_name == "waiting_roulette_bet":
            user_states[user_id] = None
            try:
                bet = int(text)
                color = state["color"]
                if bet > balance or bet <= 0: return bot.send_message(message.chat.id, "❌ Некорректная ставка.")

                user_balances[user_id] -= bet
                spin = random.choices(["red", "black", "green"], weights=[48, 48, 4])[0]
                color_emoji = "🔴 Красное" if spin == "red" else "⚫ Чёрное" if spin == "black" else "🟢 Зелёное"

                if spin == color:
                    multiplier = 14 if color == "green" else 2
                    win = bet * multiplier
                    user_balances[user_id] += win
                    bot.send_message(message.chat.id, f"🎰 Выпало {color_emoji}!\n✅ Вы выиграли {win} ⭐!\nБаланс: {user_balances[user_id]} ⭐")
                else:
                    bot.send_message(message.chat.id, f"🎰 Выпало {color_emoji}...\n❌ Вы проиграли {bet} ⭐.\nБаланс: {user_balances[user_id]} ⭐")
            except ValueError: bot.send_message(message.chat.id, "❌ Введите число.")
            return

    if text in ["📦 Открыть кейс", "📦 Кейсы"]:
        markup = InlineKeyboardMarkup(row_width=1)
        for key, case in CASES.items():
            markup.add(InlineKeyboardButton(f"{case['name']} — {case['price']} ⭐", callback_data=f"case_{key}"))
        bot.send_message(message.chat.id, "📦 *Выбирай кейс в FlowUp:*", reply_markup=markup, parse_mode="Markdown")

    elif text == "🎮 Мини-игры":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("🚀 Краш", callback_data="game_crash"),
            InlineKeyboardButton("🎰 Рулетка", callback_data="game_roulette"),
            InlineKeyboardButton("🎲 Кости (50/50)", callback_data="game_dice"),
            InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")
        )
        bot.send_message(message.chat.id, f"🎮 *Мини-игры FlowUp*\nБаланс: {balance} ⭐", reply_markup=markup, parse_mode="Markdown")

    elif text == "🎁 Ежедневный бонус":
        last_claim = user_bonus_time.get(user_id, 0)
        current_time = time.time()
        
        if current_time - last_claim < 86400:
            left = int(86400 - (current_time - last_claim))
            h, m = left // 3600, (left % 3600) // 60
            bot.send_message(message.chat.id, f"⏳ Вы уже забирали бонус. Следующий через {h} ч. {m} мин.")
        else:
            user_balances[user_id] += 50
            user_bonus_time[user_id] = current_time
            bot.send_message(message.chat.id, f"🎁 Ежедневный бонус +50 ⭐ получен!\n💰 Баланс: {user_balances[user_id]} ⭐")

    elif text == "👥 Рефералы":
        ref = user_referrals[user_id]
        bot.send_message(message.chat.id, f"👥 Приглашено: {ref['count']} чел.\n🎁 Заработано: {ref['earned']} ⭐\n🔗 Ссылка: `https://t.me/flowupbot?start=ref_{user_id}`", parse_mode="Markdown")

    elif text == "🎟 Ввести промокод":
        user_states[user_id] = "waiting_promo"
        bot.send_message(message.chat.id, "🎟 Отправьте промокод:")

    elif text in ["🎒 Инвентарь", "В инвентарь"]:
        inv = user_inventory[user_id]
        if not inv:
            bot.send_message(message.chat.id, "🎒 *Твой инвентарь пуст.*", parse_mode="Markdown")
        else:
            items_list = "\n".join([f"• {item}" for item in inv[-15:]])
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("💰 Продать весь инвентарь", callback_data="sell_all_inv"))
            bot.send_message(message.chat.id, f"🎒 *Твой инвентарь (последние 15 из {len(inv)}):*\n\n{items_list}", reply_markup=markup, parse_mode="Markdown")

    elif text == "👤 Профиль":
        bot.send_message(message.chat.id, f"👤 *Профиль {username}*\n\nID: `{user_id}`\nБаланс: {balance} ⭐\nСклад: {len(user_inventory[user_id])} шт.", parse_mode="Markdown")

    elif text == "🏆 Топы лидеров":
        sorted_users = sorted(user_balances.items(), key=lambda x: x[1], reverse=True)[:10]
        top_text = "🏆 *Топ-10 игроков по балансу:*\n\n"
        for i, (uid, bal) in enumerate(sorted_users, 1):
            un = user_usernames.get(uid, f"id{uid}")
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            name_display = f"@{un}" if not un.startswith("id") else f"ID {uid}"
            top_text += f"{medal} {name_display} — {bal} ⭐\n"
        bot.send_message(message.chat.id, top_text, parse_mode="Markdown")

    elif text == "💳 Пополнить":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("⭐ Звёздами", callback_data="dep_stars"),
            InlineKeyboardButton("💎 NFT подарком", callback_data="dep_nft")
        )
        bot.send_message(message.chat.id, "💳 Выберите способ:", reply_markup=markup)

    elif text == "📤 Вывести":
        user_states[user_id] = "waiting_withdrawal"
        bot.send_message(message.chat.id, f"📤 *Вывод*\nНа балансе: {balance} ⭐\nМинимум: 400 ⭐\n\nВведите сумму для вывода:", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    update_user_cache(call.from_user)
    user_id = call.from_user.id
    balance = get_user(user_id)
    username = get_name(call.from_user)

    if call.data == "main_menu":
        bot.edit_message_text(f"Главное меню FlowUp.\n👤 {username}\n💰 Баланс: {balance} ⭐", call.message.chat.id, call.message.message_id)

    elif call.data == "back_games":
        user_states[user_id] = None
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("🚀 Краш", callback_data="game_crash"),
            InlineKeyboardButton("🎰 Рулетка", callback_data="game_roulette"),
            InlineKeyboardButton("🎲 Кости (50/50)", callback_data="game_dice"),
            InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")
        )
        try:
            bot.edit_message_text(f"🎮 *Мини-игры FlowUp*\nБаланс: {balance} ⭐", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            bot.send_message(call.message.chat.id, f"🎮 *Мини-игры FlowUp*\nБаланс: {balance} ⭐", reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("case_"):
        c_key = call.data.split("_")[1]
        case = CASES[c_key]
        if balance < case["price"]:
            bot.answer_callback_query(call.id, "❌ Недостаточно звезд!", show_alert=True)
            return

        user_balances[user_id] -= case["price"]

        prize, drop_val = generate_drop(case["price"])
        
        user_inventory[user_id].append(prize)
        user_pending_sell[user_id] = {"value": drop_val, "items": [prize]}

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(f"🔄 Крутить ещё ({case['price']} ⭐)", callback_data=f"case_{c_key}"),
            InlineKeyboardButton(f"💰 Продать дроп (+{drop_val} ⭐)", callback_data="sell_drop"),
            InlineKeyboardButton("📦 К кейсам", callback_data="back_cases")
        )

        diff = drop_val - case['price']
        profit_text = f"🔥 Окуп! +{diff} ⭐" if diff >= 0 else f"📉 Убыток: {diff} ⭐"

        text_res = (
            f"📦 *{case['name']}*\n\n"
            f"Выпало:\n• {prize}\n\n"
            f"{profit_text}\n"
            f"Предмет добавлен в инвентарь!\nБаланс: {user_balances[user_id]} ⭐"
        )
        bot.edit_message_text(text_res, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "sell_drop":
        sell_data = user_pending_sell.get(user_id)
        if not sell_data:
            bot.answer_callback_query(call.id, "❌ Этот дроп уже продан или недоступен!", show_alert=True)
            return
            
        user_balances[user_id] += sell_data["value"]
        
        for item in sell_data["items"]:
            if item in user_inventory[user_id]:
                user_inventory[user_id].remove(item)
                
        user_pending_sell[user_id] = None
        
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("📦 Кейсы", callback_data="back_cases"),
            InlineKeyboardButton("🏠 Меню", callback_data="main_menu")
        )
        bot.edit_message_text(f"✅ Дроп успешно продан за {sell_data['value']} ⭐!\nБаланс: {user_balances[user_id]} ⭐", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "sell_all_inv":
        inv = user_inventory[user_id]
        if not inv:
            bot.answer_callback_query(call.id, "❌ Инвентарь пуст!", show_alert=True)
            return
            
        total_sell_val = 0
        for item in inv:
            if "(" in item and "⭐" in item:
                try:
                    val_part = item.split("(")[1].split("⭐")[0].strip()
                    total_sell_val += int(val_part)
                except:
                    total_sell_val += 3
            else:
                total_sell_val += 3

        user_balances[user_id] += total_sell_val
        user_inventory[user_id] = []
        user_pending_sell[user_id] = None
        
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("📦 Кейсы", callback_data="back_cases"),
            InlineKeyboardButton("🏠 Меню", callback_data="main_menu")
        )
        bot.edit_message_text(f"✅ Весь инвентарь успешно продан за {total_sell_val} ⭐!\nБаланс: {user_balances[user_id]} ⭐", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "back_cases":
        markup = InlineKeyboardMarkup(row_width=1)
        for key, case in CASES.items():
            markup.add(InlineKeyboardButton(f"{case['name']} — {case['price']} ⭐", callback_data=f"case_{key}"))
        bot.edit_message_text("📦 *Кейсы:*", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "dep_stars":
        user_states[user_id] = "waiting_deposit"
        bot.send_message(call.message.chat.id, "⭐ Введи числом сумму пополнения:")

    elif call.data == "dep_nft":
        bot.send_message(call.message.chat.id, f"💎 Открой диалог для передачи NFT подарка на аккаунт @{ADMIN_USERNAME}.")

    elif call.data == "game_dice":
        user_states[user_id] = "waiting_dice_bet"
        bot.send_message(call.message.chat.id, "🎲 *Игра Кости*\nШанс выигрыша ~48%, коэффициент x1.8.\n\nВведите сумму ставки:", parse_mode="Markdown")

    elif call.data == "game_crash":
        user_states[user_id] = "waiting_crash_bet"
        bot.send_message(call.message.chat.id, "🚀 *Краш*\nВведите сумму ставки для ракеты:")

    elif call.data.startswith("crash_pick_"):
        try:
            target_multi = float(call.data.split("_")[2])
        except:
            return

        state = user_states.get(user_id)
        if not isinstance(state, dict) or state.get("name") != "selecting_crash_multi":
            bot.answer_callback_query(call.id, "❌ Сессия устарела. Начните заново.", show_alert=True)
            return

        bet = state["bet"]
        current_balance = get_user(user_id)
        if bet > current_balance:
            bot.answer_callback_query(call.id, "❌ Недостаточно средств!", show_alert=True)
            return

        user_balances[user_id] -= bet
        user_states[user_id] = None

        roll = random.random()
        if roll < 0.45:
            crash_point = round(random.uniform(1.00, 1.15), 2)
        elif roll < 0.70:
            crash_point = round(random.uniform(1.16, 1.50), 2)
        elif roll < 0.88:
            crash_point = round(random.uniform(1.51, 2.20), 2)
        elif roll < 0.96:
            crash_point = round(random.uniform(2.21, 3.50), 2)
        else:
            crash_point = round(random.uniform(3.51, 6.00), 2)

        if target_multi <= crash_point:
            win = int(bet * target_multi)
            user_balances[user_id] += win
            res_text = f"🚀 Ракета долетела до x{crash_point}!\n✅ Вы выбрали x{target_multi} и выиграли {win} ⭐!\nБаланс: {user_balances[user_id]} ⭐"
        else:
            res_text = f"💥 Ракета взорвалась на x{crash_point}...\n❌ Вы выбрали x{target_multi} и проиграли ставку {bet} ⭐.\nБаланс: {user_balances[user_id]} ⭐"

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("🎮 К мини-играм", callback_data="back_games"))
        try:
            bot.edit_message_text(res_text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            bot.send_message(call.message.chat.id, res_text, reply_markup=markup)

    elif call.data == "game_roulette":
        markup = InlineKeyboardMarkup(row_width=3)
        markup.add(
            InlineKeyboardButton("🔴 (x2)", callback_data="roulette_red"),
            InlineKeyboardButton("⚫ (x2)", callback_data="roulette_black"),
            InlineKeyboardButton("🟢 (x14)", callback_data="roulette_green")
        )
        markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back_games"))
        bot.edit_message_text("🎰 *Рулетка*\n\nВыберите цвет для ставки:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("roulette_"):
        color = call.data.split("_")[1]
        user_states[user_id] = {"name": "waiting_roulette_bet", "color": color}
        emoji = "🔴 Красное" if color == "red" else "⚫ Чёрное" if color == "black" else "🟢 Зелёное"
        bot.send_message(call.message.chat.id, f"🎰 Вы выбрали {emoji}.\n\nВведите сумму ставки:")

if __name__ == "__main__":
    print("🚀 Бот FlowUp запущен на приватке Mechagram...")
    bot.infinity_polling()

