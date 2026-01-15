import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# 1. Setup Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 2. Load Token from Environment Variable
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# 3. Product Data (Using your Cloudinary URL as a placeholder)
PRODUCTS = {
    'tigernut': [
        {'name': 'Tigernut Powder', 'price': 1500, 'description': 'Gluten Free, 500g pack', 'image_url': 'https://res.cloudinary.com/diym0l1y3/image/upload/v1767112155/4_eagbde.png'},
        {'name': 'Tigernut Milk', 'price': 1200, 'description': 'Natural and fresh', 'image_url': 'https://res.cloudinary.com/diym0l1y3/image/upload/v1767112155/4_eagbde.png'},
    ],
    'dates': [
        {'name': 'Dates Syrup', 'price': 2000, 'description': '250ml bottle', 'image_url': 'https://res.cloudinary.com/diym0l1y3/image/upload/v1767112155/4_eagbde.png'},
    ],
    'spices': [
        {'name': 'Maicors Powder', 'price': 800, 'description': 'Traditional seasoning', 'image_url': 'https://res.cloudinary.com/diym0l1y3/image/upload/v1767112155/4_eagbde.png'},
    ],
}

user_carts = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I'm KELS, your Mai Foods assistant. Use /shop to browse products or /cart to view your order.")

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Tigernut Products", callback_data='cat_tigernut')],
        [InlineKeyboardButton("Dates & Syrups", callback_data='cat_dates')],
        [InlineKeyboardButton("Spices", callback_data='cat_spices')],
    ]
    await update.message.reply_text("Please choose a category:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith('cat_'):
        cat = data.split('_')[1]
        products = PRODUCTS.get(cat, [])
        keyboard = [[InlineKeyboardButton(p['name'], callback_data=f"prod_{cat}_{i}")] for i, p in enumerate(products)]
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data='main_menu')])
        await query.edit_message_text("Select a product:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith('prod_'):
        _, cat, idx = data.split('_')
        product = PRODUCTS[cat][int(idx)]
        text = f"*{product['name']}*\nPrice: ₦{product['price']}\n{product['description']}"
        keyboard = [
            [InlineKeyboardButton("🛒 Add to Cart", callback_data=f"add_{cat}_{idx}")],
            [InlineKeyboardButton("⬅️ Back", callback_data=f"cat_{cat}")]
        ]
        # Sending image with product details
        await query.message.reply_photo(photo=product['image_url'], caption=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data.startswith('add_'):
        _, cat, idx = data.split('_')
        product = PRODUCTS[cat][int(idx)]
        if user_id not in user_carts: user_carts[user_id] = []
        user_carts[user_id].append(product)
        await query.message.reply_text(f"✅ {product['name']} added! Use /cart to view.")

    elif data == 'main_menu':
        keyboard = [[InlineKeyboardButton("Tigernut Products", callback_data='cat_tigernut')],
                    [InlineKeyboardButton("Dates & Syrups", callback_data='cat_dates')],
                    [InlineKeyboardButton("Spices", callback_data='cat_spices')]]
        await query.edit_message_text("Please choose a category:", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cart = user_carts.get(user_id, [])
    if not cart:
        await update.message.reply_text("Your cart is empty.")
        return
    msg = "🛒 *Your Cart:*\n"
    total = sum(item['price'] for item in cart)
    for i, item in enumerate(cart, 1):
        msg += f"{i}. {item['name']} - ₦{item['price']}\n"
    msg += f"\n*Total: ₦{total}*\n\nUse /checkout to finish."
    await update.message.reply_text(msg, parse_mode='Markdown')

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not user_carts.get(user_id):
        await update.message.reply_text("Cart is empty!")
        return
    await update.message.reply_text("Order received! Please pay via Paystack (Link Placeholder).\nReply 'paid' to confirm.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == 'paid':
        user_carts[update.effective_user.id] = []
        await update.message.reply_text("✅ Payment noted! We will process your order.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("shop", shop))
    app.add_handler(CommandHandler("cart", show_cart))
    app.add_handler(CommandHandler("checkout", checkout))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    print("KELS is running...")
    app.run_polling()
