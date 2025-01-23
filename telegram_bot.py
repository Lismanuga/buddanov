from flask import Flask, request, jsonify
from telethon import TelegramClient
import os
import asyncio
from functools import partial
import re

# Initialize Flask app
app = Flask(name)

# Replace these with your own values from environment variables or directly
api_id = "24344346"
api_hash = "0ae609349ce85cf9f39c8af6c3e35c60"
phone_number = "+380732976199"

# Target chat and thread IDs
CHAT_ID = -1002393633389
THREAD_ID = 240737

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
        return f'@AgentScarlettBot analyze {hash_value}'
    return message_text

async def get_scarlett_response(client, chat_id, thread_id, timeout=30):
    """Wait for and return Scarlett's response in the thread."""
    # Add initial delay before checking for response
    await asyncio.sleep(10)  # 10 second delay
    
    start_time = asyncio.get_event_loop().time()
    
    while (asyncio.get_event_loop().time() - start_time) < timeout:
        # Get recent messages in the thread
        async for message in client.iter_messages(
            chat_id,
            reply_to=thread_id,
            limit=5  # Check last 5 messages
        ):
            # Check if message is from Scarlett and newer than our request
            if (message.sender and 
                hasattr(message.sender, 'username') and 
                message.sender.username == 'AgentScarlettBot' and
                message.date.timestamp() > start_time):
                return message.text
        
        # Wait a bit before checking again
        await asyncio.sleep(1)
    
    return None

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
            
            async def send_and_get_response():
                # Send message
                await client.send_message(
                    CHAT_ID,
                    formatted_message,
                    reply_to=THREAD_ID
                )
                # Wait for Scarlett's response
                response = await get_scarlett_response(client, CHAT_ID, THREAD_ID)
                return response

            # Run the coroutine in the event loop
            scarlett_response = loop.run_until_complete(send_and_get_response())
            
            if scarlett_response:
                return jsonify({
                    'status': 'Message sent successfully',
                    'formatted_message': formatted_message,
                    'scarlett_response': scarlett_response
                }), 200
            else:
                return jsonify({
                    'status': 'Message sent but no response received',
                    'formatted_message': formatted_message
                }), 202

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

if name == "main":
    # Start the Telegram client
    loop.run_until_complete(main())

    # Run the Flask app on all interfaces
    app.run(host='0.0.0.0', port=5000)