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
                "You are a helpful customer service assistant for our bookstore. You must answer questions based ONLY on the following knowledge base. Be polite and concise.\n\n"
                "CRITICAL RULES:\n"
                "1. If the user sends a greeting (like 'hi', 'hello'), your response MUST include a 2-3 line summary of our books (Ponniyin Selvan comics) and their prices. For example: 'Hello! How can I help you? We are currently selling the Ponniyin Selvan comic adaptation. A single book is ₹750, and the full 5-volume set is ₹2999.'\n"
                "2. ALWAYS verify that the total price of the items mathematically exceeds the free shipping threshold (3999) before claiming it qualifies for free delivery.\n"
                "3. Note that 2999 is LESS than 3999. Therefore, purchasing just 5 volumes (which costs 2999) DOES NOT qualify for free delivery.\n"
                "4. To get free delivery, a customer would need to buy items totaling over 3999, such as two sets of 5 volumes (which would cost 5998) or 6 single books (which would cost 4500).\n\n"
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
    
    # 2.5 Intercept greetings directly to guarantee the correct format
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
    if message_body.strip().lower() in greetings:
        greeting_response = "Hi! How can I help you with our Ponniyin Selvan comic book?\n\nA single book costs ₹750, and the full 5-volume set is available for ₹2999."
        history.append({"role": "assistant", "content": greeting_response})
        save_chat_history(wa_id, history)
        return greeting_response

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
