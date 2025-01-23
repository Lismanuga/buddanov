from flask import Flask, request, jsonify
from telethon import TelegramClient
import os
import asyncio
from functools import partial
import re

# Initialize Flask app
app = Flask(__name__)

# Replace these with your own values from environment variables or directly
api_id = ''
api_hash = ''
phone_number = '+'

# Target chat/user (replace with the username or chat ID you want to send messages to)
TARGET_CHAT = '@prepotente_irreale'  # Replace with your target username/chat

# Create the client and connect
client = TelegramClient('session_name', api_id, api_hash)

# Create a new event loop for the Flask application
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def is_valid_hash(text):
    # Pattern for 32+ character alphanumeric string
    hash_pattern = r'[A-Za-z0-9]{32,}'
    return bool(re.search(hash_pattern, text))

def format_message(message_text):
    # Extract hash if present
    hash_match = re.search(r'[A-Za-z0-9]{32,}', message_text)
    if hash_match:
        hash_value = hash_match.group(0)
        return f'@bot_name analyze {hash_value}'
    return message_text

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message_text = data.get('message')

    if not message_text:
        return jsonify({'error': 'Message text is required'}), 400

    try:
        # Check if message contains a valid hash
        if is_valid_hash(message_text):
            # Format message for the second bot
            formatted_message = format_message(message_text)
            # Run the coroutine in the event loop
            loop.run_until_complete(client.send_message(TARGET_CHAT, formatted_message))
            return jsonify({
                'status': 'Message sent successfully',
                'formatted_message': formatted_message
            }), 200
        else:
            return jsonify({
                'error': 'Message does not contain a valid hash pattern'
            }), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def main():
    await client.start(phone=phone_number)
    print("Client is running...")
    
    # Verify that we can access the target chat
    try:
        chat = await client.get_input_entity(TARGET_CHAT)
        print(f"Successfully connected to target chat: {TARGET_CHAT}")
    except Exception as e:
        print(f"Error accessing target chat: {e}")

if __name__ == "__main__":
    # Start the Telegram client
    loop.run_until_complete(main())

    # Run the Flask app
    app.run(port=5000) 