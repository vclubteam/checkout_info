# Stripe Checkout Info Bot

This is a Python-based bot that uses Playwright, Pyrogram, and Stripe API to extract detailed information from Stripe checkout links. The bot retrieves and displays information such as session IDs, amounts due, customer email, payment modes, and more. It's a great tool for monitoring and retrieving checkout data from Stripe.

## Features

- Extract Stripe checkout session details from URL.
- Fetch payment-related information such as session ID, publishable key, client secret, and more.
- Includes Stripe API integration to create payment intents and retrieve checkout data.
- Supports automatic response formatting for quick viewing.

## Requirements

- Python 3.7+
- `playwright`
- `stripe` Python package
- `pyrogram` Python package
- `aiohttp` for making HTTP requests

## Installation

Follow the steps below to install and run the bot:

### 1. Clone the Repository

```bash
git clone https://github.com/vclubteam/checkout_info
cd checkout_info

```

## Example Response
```
✅ **Stripe Checkout Info Retrieved!** ✅

🌐 **Business Name**: Stripe
🔗 **Checkout Link**: [Here](https://checkout.stripe.com/c/pay/...)
🌍 **Business URL**: https://stripe.com

💳 **Payment Mode**: `Subscription`
💳 **Checkout Type**: `2d secure`
🆔 **Session ID**: `cs_live_a1raW7gwYNf1WLgggXOhQulJICsllSH0uZAa7v3oMNYJJUwqN4dzFtB2fy`
🔑 **Publishable Key**: `pk_live_51HOrSwC6h1nxGoI3lTAgRjYVrz4dU3fVOabyCcKR3pbEJguCVAlqCxdxCUvoRh1XWwRacViovU3kLKvpkjh7IqkW00iXQsjo3n`
🔐 **Client Secret**: `pi_1IYQkH2eZv6eRe42lfHqYmEd_secret_DdrPoK7QnddF2LaShz87r8l9g`
💰 **Amount Due**: `50.00 USD`
📧 **Customer Email**: `example@domain.com`

💡 If you need more info, just let me know!

```
