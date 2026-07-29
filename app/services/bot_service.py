import logging
import json
import shelve
from app.services.openai_service import generate_response
from app.utils.whatsapp_utils import (
    get_text_message_input,
    get_interactive_button_message,
    get_interactive_list_message,
    send_message,
    process_text_for_whatsapp
)

# Screen configurations based on the spec
SCREENS = {
    "welcome": {
        "text": "👋 Vanakkam! Welcome to Nila Comics\n\nExperience Kalki's legendary Ponniyin Selvan through beautifully illustrated full-colour comics.\n\n📚 Available in Tamil and English\n\nNeed help choosing? I'm here to guide you.\n\nHow can I help you today?",
        "options": ["Explore Collection", "Price", "Read Sample", "Delivery", "Buy Now", "Ask a Question"],
        "type": "list"
    },
    "explore": {
        "text": "Choose your preferred language.",
        "options": ["Tamil Edition", "English Edition", "Home"],
        "type": "button"
    },
    "edition": {
        "text": "✔ Beautiful Full Colour Artwork\n✔ Around 350 pages per volume\n✔ Available as individual books or complete collection",
        "options": ["Read Sample", "Price", "Buy Now", "Home"],
        "type": "list"
    },
    "price": {
        "text": "💰 Ponniyin Selvan Pricing\n\n📖 Single Volume\n₹750 per book\n\n📚 Complete Collection (5 Volumes)\n₹2,999 only\n\n🎉 Save ₹751 when you purchase the complete collection.\n\nThe complete collection is the best value and lets you enjoy the full story without interruption.",
        "options": ["Buy Single Volume", "Buy Complete Collection", "Delivery Charges", "Current Offers", "Home"],
        "type": "list"
    },
    "discount": {
        "text": "🎁 Discount Information\n\n✔ Single Book Price: ₹750 each\n✔ Buy any individual volume at ₹750.\n✔ Buy all 5 volumes together for only ₹2,999.\n✔ You save ₹751 compared to purchasing all five books separately.\n\nThe discount is automatically applied when purchasing the complete collection.",
        "options": ["Buy Complete Collection", "Price", "Home"],
        "type": "button"
    },
    "delivery": {
        "text": "🚚 Delivery Information\n\nDelivery available across India.\n✔ Estimated delivery time: 3–7 business days within India.\n✔ International shipping is available.\n✔ Delivery charges are applicable for all orders.\n✔ We do not offer free shipping.\n✔ Delivery charges are calculated based on your delivery location and order quantity.\n✔ The exact delivery charge will be displayed during checkout before payment.\n✔ There are no hidden charges after checkout.\n✔ Tracking details will be shared once your order is dispatched.",
        "options": ["International Orders", "Buy Now", "Home"],
        "type": "button"
    },
    "sample": {
        "text": "Choose:",
        "options": ["Tamil Sample", "English Sample"],
        "type": "button"
    },
    "sample_preview": {
        "text": "Here is your sample link: https://nilacomics.com/\n\nHope you enjoyed the preview. Ready to continue your reading journey?",
        "options": ["Buy Single Volume", "Buy Complete Collection", "Home"],
        "type": "button"
    },
    "product_details": {
        "text": "✔ Premium Maplitho Paper\n✔ Offset Printing\n✔ Full Colour\n✔ Approx. 350 Pages per Volume\n✔ Approx. 1,750 Pages Total\n✔ Tamil & English Editions",
        "options": ["Price", "Home"],
        "type": "button"
    },
    "support": {
        "text": "Contact our support team:\nWhatsApp: +91 98848 06302\nEmail: contact@nilacomics.com\nCall: +91 98848 06302",
        "options": ["Home"],
        "type": "button"
    },
    "buy": {
        "text": "Great! You can purchase from our website:\n\nSingle Volume (₹750): https://nilacomics.com/\nComplete Collection (₹2,999): https://nilacomics.com/",
        "options": ["Home"],
        "type": "button"
    },
    "smart_conversion": {
        "text": "It looks like you've explored the Ponniyin Selvan collection. Ready to own this timeless masterpiece?",
        "options": ["Buy Single Volume", "Buy Complete Collection", "Continue Browsing"],
        "type": "button"
    }
}

SMART_CONVERSION_TRIGGERS = ["price", "discount", "delivery", "sample", "product_details"]

def get_state(wa_id):
    with shelve.open("threads_db") as db:
        if wa_id not in db:
            db[wa_id] = {"history": [], "viewed": [], "smart_conversion_triggered": False}
        return db[wa_id].get("viewed", []), db[wa_id].get("smart_conversion_triggered", False)

def update_state(wa_id, viewed_section):
    with shelve.open("threads_db", writeback=True) as db:
        if wa_id not in db:
            db[wa_id] = {"history": [], "viewed": [], "smart_conversion_triggered": False}
        
        viewed_list = db[wa_id].get("viewed", [])
        if viewed_section not in viewed_list:
            viewed_list.append(viewed_section)
            db[wa_id]["viewed"] = viewed_list

def mark_smart_conversion_triggered(wa_id):
    with shelve.open("threads_db", writeback=True) as db:
        if wa_id in db:
            db[wa_id]["smart_conversion_triggered"] = True

def send_screen(wa_id, screen_id):
    screen = SCREENS.get(screen_id)
    if not screen:
        return
    
    if screen["type"] == "button":
        data = get_interactive_button_message(wa_id, screen["text"], screen["options"])
    else:
        # For list type
        data = get_interactive_list_message(wa_id, screen["text"], "Choose an option", screen["options"])
    
    send_message(data)


def process_incoming_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    msg_type = message.get("type", "text")
    
    message_text = ""
    if msg_type == "text":
        message_text = message["text"]["body"]
    elif msg_type == "interactive":
        interactive = message["interactive"]
        if interactive["type"] == "button_reply":
            message_text = interactive["button_reply"]["title"]
        elif interactive["type"] == "list_reply":
            message_text = interactive["list_reply"]["title"]
            
    logging.info(f"Incoming message from wa_id={wa_id} name={name}: {message_text}")
    
    # Normalizing message for routing
    cmd = message_text.strip().lower()
    
    # State tracking & routing logic
    viewed, conversion_triggered = get_state(wa_id)
    next_screen = None
    fallback_to_ai = False

    if cmd in ["home", "hi", "hello", "hey", "vanakkam"]:
        next_screen = "welcome"
    elif cmd == "explore collection":
        next_screen = "explore"
    elif cmd in ["tamil edition", "english edition"]:
        next_screen = "edition"
    elif cmd == "price":
        update_state(wa_id, "price")
        next_screen = "price"
    elif cmd == "read sample":
        update_state(wa_id, "sample")
        next_screen = "sample"
    elif cmd in ["tamil sample", "english sample"]:
        next_screen = "sample_preview"
    elif cmd in ["delivery", "delivery charges"]:
        update_state(wa_id, "delivery")
        next_screen = "delivery"
    elif cmd in ["current offers", "discount"]:
        update_state(wa_id, "discount")
        next_screen = "discount"
    elif cmd == "product details":
        update_state(wa_id, "product_details")
        next_screen = "product_details"
    elif cmd in ["buy now", "buy single volume", "buy complete collection"]:
        next_screen = "buy"
    elif cmd == "international orders":
        next_screen = "support"
    elif cmd == "ask a question":
        # Send a prompt to ask the question
        data = get_text_message_input(wa_id, "Please type your question below:")
        send_message(data)
        return
    elif cmd == "continue browsing":
        next_screen = "welcome"
    else:
        # Unrecognized command -> pass to AI
        fallback_to_ai = True

    # Smart Conversion Logic check
    if not fallback_to_ai:
        # Refetch state to see if updated
        viewed, conversion_triggered = get_state(wa_id)
        # Count how many smart conversion triggers the user has viewed
        trigger_count = sum(1 for section in viewed if section in SMART_CONVERSION_TRIGGERS)
        
        if trigger_count >= 2 and not conversion_triggered:
            # Send the screen first, then the smart conversion message
            if next_screen:
                send_screen(wa_id, next_screen)
            
            mark_smart_conversion_triggered(wa_id)
            send_screen(wa_id, "smart_conversion")
            return
            
        if next_screen:
            send_screen(wa_id, next_screen)
            return

    # If fallback to AI
    if fallback_to_ai:
        response = generate_response(message_text, wa_id, name)
        response = process_text_for_whatsapp(response)
        data = get_text_message_input(wa_id, response)
        send_message(data)
