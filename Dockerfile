FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY telegram_bot.py .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "telegram_bot.py"] 