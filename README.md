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
