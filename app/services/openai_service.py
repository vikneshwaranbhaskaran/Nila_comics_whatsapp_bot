from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import logging

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize OpenAI client but point it to Groq
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

def get_system_prompt():
    try:
        with open("knowledge.md", "r", encoding="utf-8") as f:
            knowledge = f.read()
            return (
                "You are a helpful customer service assistant for Nila Comics. You must answer questions based ONLY on the following knowledge base. Be polite and concise.\n\n"
                "CRITICAL RULES:\n"
                "1. If a user asks about gift discounts, you MUST reply with the exact message from the Gift Discount section of the knowledge base.\n"
                "2. There is NO free shipping. Delivery charges are always calculated during checkout.\n"
                "3. If you don't know the answer based on the knowledge base, apologize and tell them to contact support at contact@nilacomics.com or +91 98848 06302.\n\n"
                f"KNOWLEDGE BASE:\n{knowledge}"
            )
    except Exception as e:
        logging.error(f"Failed to read knowledge base: {e}")
        return "You are a helpful customer service assistant for our bookstore."

def get_fallback_message():
    try:
        with open("knowledge.md", "r", encoding="utf-8") as f:
            knowledge = f.read()
            return f"I'm sorry, my AI brain is currently experiencing technical difficulties. However, here is our basic information:\n\n{knowledge}"
    except Exception:
        return "I'm sorry, I am currently experiencing technical difficulties. Please call us for assistance."

def get_chat_history(wa_id):
    with shelve.open("threads_db") as db:
        history = db.get(wa_id, [])
        # Only keep the last 10 messages to avoid context window limits
        return history[-10:]

def save_chat_history(wa_id, history):
    with shelve.open("threads_db", writeback=True) as db:
        db[wa_id] = history

def generate_response(message_body, wa_id, name):
    logging.info(f"Generating Groq response for {name} ({wa_id})")
    
    # 1. Get previous conversation history
    history = get_chat_history(wa_id)
    
    # 2. Add the new user message
    history.append({"role": "user", "content": message_body})
    
    # 3. Construct the messages array with the System Prompt first
    messages = [{"role": "system", "content": get_system_prompt()}] + history
    
    try:
        # 4. Call Groq API (using Llama 3.1 8B which is lightning fast)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=messages,
            temperature=0.2,
            max_tokens=500
        )
        
        # 5. Extract response text
        ai_message = response.choices[0].message.content
        
        # 6. Save back to history so it remembers next time
        history.append({"role": "assistant", "content": ai_message})
        save_chat_history(wa_id, history)
        
        logging.info(f"Generated message: {ai_message}")
        return ai_message
        
    except Exception as e:
        logging.error(f"Groq API Error: {e}")
        # robust fallback mechanism
        return get_fallback_message()
