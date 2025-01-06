import re
import logging
import aiohttp
from playwright.async_api import async_playwright
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
import time

BOT_TOKEN = "7566387561:AAFxE7iIOBF5n6cl01zikhfAguSEXTM9JG8"  # Add your bot token here
API_ID = 24509589         # Add your API ID here
API_HASH = "717cf21d94c4934bcbe1eaa1ad86ae75"  # Add your API hash here

app = Client("my_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

class StripeCheckoutInfo:
    def __init__(self, url, pk, urlx, response_data, site_name, business_url, payment_mode):
        self.url = url
        self.pk = pk
        self.urlx = urlx
        self.response_data = response_data
        self.site_name = site_name
        self.business_url = business_url
        self.payment_mode = payment_mode

    @classmethod
    async def create(cls, url):
        pk, urlx, site_name, business_url, payment_mode = await cls.get_stripe_pk(url)
        if not pk or not urlx:
            logging.error("Failed to retrieve the Stripe Publishable Key.")
            response_data = {}
        else:
            response_data = await cls.get_response_data(pk, urlx)
        return cls(url, pk, urlx, response_data, site_name, business_url, payment_mode)

    @staticmethod
    async def get_stripe_pk(url):
        try:
            site_name = "Unknown Site"
            business_url = "Not Available"
            payment_mode = "Not Available"
            
            if "stripe" in url:
                site_name = "Stripe"
                business_url = "https://stripe.com"
                payment_mode = "subscription"  # You can modify this part based on the type of payment mode you want to identify

            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                pk = urlx = None

                async def handle_route(route):
                    nonlocal pk, urlx
                    if pk:
                        await route.continue_()
                        return
                    request = route.request
                    post_data = request.post_data
                    if post_data and 'pk' in post_data:
                        match = re.search(r'pk_live_[\w-]+', post_data)
                        if match:
                            pk = match.group(0)
                            urlx = request.url
                            logging.info(f"Stripe Publishable Key found: {pk}")
                    await route.continue_()

                await page.route("**/*", handle_route)
                await page.goto(url)
                await page.wait_for_timeout(5000)
                await browser.close()
                return pk, urlx, site_name, business_url, payment_mode
        except Exception as e:
            logging.error(f"Error retrieving Stripe Publishable Key: {e}")
            return None, None, "Unknown Site", "Not Available", "Not Available"

    @staticmethod
    async def get_response_data(pk, urlx):
        if not pk or not urlx:
            logging.warning("Missing Stripe Publishable Key or URL.")
            return {}
        try:
            base_url = urlx.split('#')[0]
            data = {
                'key': pk,
                'eid': 'NA',
                'browser_locale': 'en-US',
                'redirect_type': 'stripe_js'
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            async with aiohttp.ClientSession() as session:
                async with session.post(base_url, data=data, headers=headers) as response:
                    response.raise_for_status()
                    response_data = await response.json()
            return response_data
        except Exception as e:
            logging.error(f"HTTP request failed: {e}")
            return {}

    def get_customer_email(self):
        email = self.response_data.get('customer_email')
        if not email:
            line_item_group = self.response_data.get('line_item_group', {})
            line_items = line_item_group.get('line_items', [])
            if isinstance(line_items, list) and len(line_items) > 0:
                name = line_items[0].get('name', '')
                match = re.search(r'[\w\.-]+@[\w\.-]+', name)
                if match:
                    email = match.group(0)
        if not email:
            email = 'Email not found'
        return email

    def get_checkout_session(self):
        session_id = self.response_data.get('session_id', 'Not Available')
        return session_id

    def get_checkout_currency(self):
        currency = self.response_data.get('currency', 'Currency not found')
        return currency

    def get_amount_due(self):
        amount_due = None
        invoice = self.response_data.get('invoice')
        if invoice and isinstance(invoice, dict):
            amount_due = invoice.get('amount_due')
        if amount_due is None:
            payment_intent = self.response_data.get('payment_intent')
            if payment_intent and isinstance(payment_intent, dict):
                amount_due = payment_intent.get('amount')
        if amount_due is None:
            line_item_group = self.response_data.get('line_item_group')
            if line_item_group and isinstance(line_item_group, dict):
                amount_due = line_item_group.get('total')
        if isinstance(amount_due, int):
            amount_due /= 100.0
        else:
            amount_due = 'Not Available'
        return amount_due

    def get_client_secret(self):
        client_secret = 'Not Available'
        payment_intent = self.response_data.get('payment_intent')
        if payment_intent and isinstance(payment_intent, dict):
            client_secret = payment_intent.get('client_secret', 'Not Available')
        return client_secret

    def get_secure_type(self):
        secure_type = '2d secure'
        payment_intent = self.response_data.get('payment_intent')
        if payment_intent and isinstance(payment_intent, dict):
            last_payment_error = payment_intent.get('last_payment_error', {})
            payment_method = last_payment_error.get('payment_method', {})
            card = payment_method.get('card', {})
            three_d_secure = card.get('three_d_secure_usage', {}).get('supported', False)
            if three_d_secure:
                secure_type = '3d secure'
        return secure_type

@app.on_message(filters.command("start"))
async def start(client, message):
    welcome_text = (
        "👋 Hello! Welcome to the **Checkout Info Bot**!\n\n"
        "I can help you retrieve detailed information from Stripe and other payment gateways. Just send me a checkout URL, and I'll process it for you! 😎\n\n"
        "🔍 Supported Links: Stripe, PayPal, and more!\n"
        "Use `/cs <checkout_url>` to start checking a checkout URL.\n"
        "For any questions, feel free to ask! 💬"
    )
    await message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

@app.on_message(filters.text & filters.regex(r"^(http|https)://"))
async def handle_check_payment_gateways(client, message):

    processing_message = await message.reply_text("**Processing your request...**", disable_web_page_preview=True)

    start_time = time.time()

    url = message.text
    checkout_info = await StripeCheckoutInfo.create(url)

    if not checkout_info.pk or not checkout_info.urlx:
        return await processing_message.edit_text("⚠️ Failed to retrieve the Stripe Publishable Key.")

    session_id = checkout_info.get_checkout_session()
    if session_id == 'Not Available':
        reply_text = (
            "🚫 **Checkout Info Unavailable!** 🚫\n\n"
            f"🌐 **Business Name**: {checkout_info.site_name}\n"
            f"🔗 **Checkout Link**: [Here]({checkout_info.urlx})\n\n"
            "**Status**: Checkout Expired 🕒"
        )
        await processing_message.edit_text(reply_text, parse_mode=ParseMode.MARKDOWN)
        return

    amount_due = checkout_info.get_amount_due()
    if amount_due != 'Not Available':
        currency = checkout_info.get_checkout_currency()
        amount_info = f"{amount_due} {currency}"
    else:
        amount_info = "Not Available"

    checkout_url = checkout_info.urlx
    checkout_type = checkout_info.get_secure_type()
    checkout_session = session_id
    checkout_pk = checkout_info.pk
    checkout_secret = checkout_info.get_client_secret()
    checkout_amount = amount_info
    checkout_email = checkout_info.get_customer_email()
    business_url = checkout_info.business_url
    payment_mode = checkout_info.payment_mode

    elapsed_time = time.time() - start_time
    elapsed_time_str = f"{elapsed_time:.2f} seconds"

    reply_text = (
        "✅ **Stripe Checkout Info Retrieved!** ✅\n\n"
        f"🌐 **Business Name**: {checkout_info.site_name}\n"
        f"🔗 **Checkout Link**: [Here]({checkout_url})\n"
        f"🌍 **Business URL**: {business_url}\n\n"
        f"💳 **Payment Mode**: `{payment_mode}`\n"
        f"💳 **Checkout Type**: `{checkout_type}`\n"
        f"🆔 **Session ID**: `{checkout_session}`\n"
        f"🔑 **Publishable Key**: `{checkout_pk}`\n"
        f"🔐 **Client Secret**: `{checkout_secret}`\n"
        f"💰 **Amount Due**: `{checkout_amount}`\n"
        f"📧 **Customer Email**: `{checkout_email}`\n\n"
        f"⏱ **Response Time**: {elapsed_time_str}\n\n"
        "💡 If you need more info, just let me know!"
    )

    await processing_message.edit_text(
        reply_text, 
        disable_web_page_preview=True, 
        parse_mode=ParseMode.MARKDOWN
    )

app.run()
