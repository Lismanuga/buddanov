from flask import Flask, request, jsonify
from telethon import TelegramClient
import os
import asyncio
import re

# Initialize Flask app
app = Flask(__name__)

# Replace these with your own values from environment variables or directly
api_id = ''
api_hash = ''
phone_number = '+'

# Target chat and thread IDs
CHAT_ID = -1002393633389
THREAD_ID = 240737

# Create the client and connect
client = TelegramClient('session_name', api_id, api_hash)

# Create a new event loop for the Flask application
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Store the last sent message ID and response
last_sent_message_id = None

def is_valid_hash(text):
    # Pattern for 32+ character alphanumeric string
    hash_pattern = r'[A-Za-z0-9]{32,}'
    return bool(re.search(hash_pattern, text))

def format_message(message_text):
    # Extract hash if present
    hash_match = re.search(r'[A-Za-z0-9]{32,}', message_text)
    if hash_match:
        hash_value = hash_match.group(0)
        return f'@AgentScarlettBot analyze {hash_value}'
    return message_text

async def get_bot_response():
    # Wait a bit for the bot to respond
    await asyncio.sleep(5)
    
    # Get messages after our sent message
    messages = await client.get_messages(
        CHAT_ID,
        limit=10,  # Get last 10 messages to ensure we don't miss the response
        reverse=True
    )
    
    for message in messages:
        if (message.sender_id == 6377331006 and  # AgentScarlettBot's ID
            hasattr(message, 'id') and 
            message.id > last_sent_message_id):
            return message.text
    
    return None

@app.route('/send_message', methods=['POST'])
def send_message():
    global last_sent_message_id
    data = request.json
    message_text = data.get('message')

    if not message_text:
        return jsonify({'error': 'Message text is required'}), 400

    try:
        # Check if message contains a valid hash
        if is_valid_hash(message_text):
            # Format message for the second bot
            formatted_message = format_message(message_text)
            
            # Send message
            sent_message = loop.run_until_complete(
                client.send_message(
                    CHAT_ID,
                    formatted_message,
                    reply_to=THREAD_ID
                )
            )
            last_sent_message_id = sent_message.id
            print(f"Sent message ID: {last_sent_message_id}")

            # Wait and get response
            max_attempts = 20
            bot_response = None
            for attempt in range(max_attempts):
                bot_response = loop.run_until_complete(get_bot_response())
                if bot_response:
                    print(f"Got response on attempt {attempt + 1}: {bot_response}")
                    break
                print(f"No response on attempt {attempt + 1}, waiting...")
                loop.run_until_complete(asyncio.sleep(5))

            if bot_response:
                return jsonify({
                    'status': 'Message sent and response received',
                    'formatted_message': formatted_message,
                    'bot_response': bot_response
                }), 200
            else:
                return jsonify({
                    'status': 'Message sent but no response received',
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
        chat = await client.get_input_entity(CHAT_ID)
        print(f"Successfully connected to target chat: {CHAT_ID}")
    except Exception as e:
        print(f"Error accessing target chat: {e}")

if __name__ == "__main__":
    # Start the Telegram client
    loop.run_until_complete(main())

    # Run the Flask app on all interfaces
    app.run(host='0.0.0.0', port=5000) 