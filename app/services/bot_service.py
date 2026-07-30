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
        "options": ["Explore Collection", "Price", "Read Sample", "Delivery", "Buy Now", "Ask a Question", "Support"],
        "type": "list"
    },
    "explore": {
        "text": "Choose your preferred language.",
        "options": ["Tamil Edition", "English Edition", "Home", "Support"],
        "type": "list"
    },
    "edition": {
        "text": "✔ Beautiful Full Colour Artwork\n✔ Around 350 pages per volume\n✔ Available as individual books or complete collection",
        "options": ["Read Sample", "Price", "Buy Now", "Home", "Support"],
        "type": "list"
    },
    "price": {
        "text": "💰 Ponniyin Selvan Pricing\n\n📖 Single Volume\n₹750 per book\n\n📚 Complete Collection (5 Volumes)\n₹2,999 only\n\n🎉 Save ₹751 when you purchase the complete collection.\n\nThe complete collection is the best value and lets you enjoy the full story without interruption.",
        "options": ["Buy Single Volume", "Buy All 5 Volumes", "Delivery Charges", "Current Offers", "Home", "Support"],
        "type": "list"
    },
    "discount": {
        "text": "🎁 Discount Information\n\n✔ Single Book Price: ₹750 each\n✔ Buy any individual volume at ₹750.\n✔ Buy all 5 volumes together for only ₹2,999.\n✔ You save ₹751 compared to purchasing all five books separately.\n\nThe discount is automatically applied when purchasing the complete collection.",
        "options": ["Buy All 5 Volumes", "Price", "Home", "Support"],
        "type": "list"
    },
    "delivery": {
        "text": "🚚 Delivery Information\n\nDelivery available across India.\n✔ Estimated delivery time: 3–7 business days within India.\n✔ International shipping is available.\n✔ Delivery charges are applicable for all orders.\n✔ We do not offer free shipping.\n✔ Delivery charges are calculated based on your delivery location and order quantity.\n✔ The exact delivery charge will be displayed during checkout before payment.\n✔ There are no hidden charges after checkout.\n✔ Tracking details will be shared once your order is dispatched.",
        "options": ["Ship Abroad", "Buy Now", "Home", "Support"],
        "type": "list"
    },
    "sample": {
        "text": "Choose:",
        "options": ["Tamil Sample", "English Sample"],
        "type": "button"
    },
    "sample_preview": {
        "text": "Hope you enjoyed the preview images! Ready to continue your reading journey?",
        "options": ["Buy Single Volume", "Buy All 5 Volumes", "Home", "Support"],
        "type": "list"
    },
    "sample_more": {
        "text": "Would you like to see more sample images or go back to home?",
        "options": ["More Images", "Go back to Home", "Support"],
        "type": "button"
    },
    "product_details": {
        "text": "✔ Premium Maplitho Paper\n✔ Offset Printing\n✔ Full Colour\n✔ Approx. 350 Pages per Volume\n✔ Approx. 1,750 Pages Total\n✔ Tamil & English Editions",
        "options": ["Price", "Home", "Support"],
        "type": "button"
    },
    "support": {
        "text": "Contact our support team:\nWhatsApp: +91 98848 06302\nEmail: contact@nilacomics.com\nCall: +91 98848 06302",
        "options": ["Home"],
        "type": "button"
    },
    "buy": {
        "text": "Great! You can purchase from our website:\n\nSingle Volume (₹750): https://nilacomics.com/\nComplete Collection (₹2,999): https://nilacomics.com/",
        "options": ["Home", "Support"],
        "type": "button"
    },
    "smart_conversion": {
        "text": "It looks like you've explored the Ponniyin Selvan collection. Ready to own this timeless masterpiece?",
        "options": ["Buy Single Volume", "Buy All 5 Volumes", "Continue Browsing"],
        "type": "button"
    },
    "faq": {
        "text": "❓ FAQs\n\n*Is it available in English?*\nYes, available in English.\n\n*Is it available in Tamil?*\nYes, available in Tamil.\n\n*Can I buy a single book?*\nYes. Every volume can be purchased individually for ₹750.\n\n*Can I buy only two books?*\nYes. You may purchase any individual volumes you want.\n\n*What is the discount?*\nBuy all 5 volumes for ₹2,999 and save ₹751.\n\n*What are the delivery charges?*\nCalculated during checkout based on your location.\n\n*Hidden charges?*\nNo. Your final payable amount is shown before payment.\n\n*Suitable for children?*\nYes, the comic format is engaging for young readers.\n\n*Which volume to start with?*\nWe recommend starting with Volume 1.\n\n*Is there a gift discount?*\n🎁 The Ponniyin Selvan Comic Collection makes a wonderful gift for family, friends, and history lovers.\nOur Complete 5-Volume Collection is already offered at a special discounted price of ₹2,999, which includes a ₹750 discount from the original price.\nThere is no separate or additional discount for gift purchases.",
        "options": ["Contact Support", "Home"],
        "type": "button"
    },
    "unknown_first": {
        "text": "😊 Sorry, I couldn't quite understand that. I'm the Nila Comics assistant, and I'm happy to help you with:\n\n📚 Explore the Ponniyin Selvan Collection\n📖 Sample Pages\n💰 Pricing & Discounts\n🚚 Delivery Information\n❓ Frequently Asked Questions\n🛒 Buy the Collection\n\nPlease choose one of the options below.",
        "options": ["Explore Collection", "Read Sample", "Price", "Delivery", "FAQs", "Buy Now", "Home", "Support"],
        "type": "list"
    },
    "unknown_repeated": {
        "text": "😊 I'm sorry, I still couldn't understand your request.\n\nPlease select one of the options below, or contact our support team if you need further assistance.",
        "options": ["Contact Support", "Home"],
        "type": "button"
    }
}

SMART_CONVERSION_TRIGGERS = ["price", "discount", "delivery", "sample", "product_details"]

def get_state(wa_id):
    with shelve.open("threads_db") as db:
        if wa_id not in db:
            db[wa_id] = {"history": [], "viewed": [], "smart_conversion_triggered": False}
        
        user_data = db[wa_id]
        if isinstance(user_data, list):
            # Backward compatibility: old format was just a list of history
            user_data = {"history": user_data, "viewed": [], "smart_conversion_triggered": False}
            # We don't save it here without writeback, but we can return the defaults
        
        return user_data.get("viewed", []), user_data.get("smart_conversion_triggered", False)

def update_state(wa_id, viewed_section):
    with shelve.open("threads_db", writeback=True) as db:
        if wa_id not in db:
            db[wa_id] = {"history": [], "viewed": [], "smart_conversion_triggered": False}
        
        if isinstance(db[wa_id], list):
            # Upgrade old format to new format
            db[wa_id] = {"history": db[wa_id], "viewed": [], "smart_conversion_triggered": False}
            
        viewed_list = db[wa_id].get("viewed", [])
        if viewed_section not in viewed_list:
            viewed_list.append(viewed_section)
            db[wa_id]["viewed"] = viewed_list

def mark_smart_conversion_triggered(wa_id):
    with shelve.open("threads_db", writeback=True) as db:
        if wa_id in db:
            if isinstance(db[wa_id], list):
                db[wa_id] = {"history": db[wa_id], "viewed": [], "smart_conversion_triggered": False}
            db[wa_id]["smart_conversion_triggered"] = True

def get_unknown_count(wa_id):
    with shelve.open("threads_db") as db:
        user_data = db.get(wa_id, {})
        if isinstance(user_data, list):
            return 0
        return user_data.get("unknown_count", 0)

def set_unknown_count(wa_id, count):
    with shelve.open("threads_db", writeback=True) as db:
        if wa_id not in db or isinstance(db[wa_id], list):
            history = db[wa_id] if wa_id in db and isinstance(db[wa_id], list) else []
            db[wa_id] = {"history": history, "viewed": [], "smart_conversion_triggered": False}
        db[wa_id]["unknown_count"] = count

def get_sample_state(wa_id):
    with shelve.open("threads_db") as db:
        user_data = db.get(wa_id, {})
        if isinstance(user_data, list):
            return "tamil", 0
        return user_data.get("sample_language", "tamil"), user_data.get("sample_page", 0)

def update_sample_state(wa_id, language, page):
    with shelve.open("threads_db", writeback=True) as db:
        if wa_id not in db or isinstance(db[wa_id], list):
            db[wa_id] = {"history": [], "viewed": [], "smart_conversion_triggered": False}
        db[wa_id]["sample_language"] = language
        db[wa_id]["sample_page"] = page

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

def check_and_mark_processed(msg_id):
    if not msg_id:
        return False
    with shelve.open("threads_db", writeback=True) as db:
        processed = db.get("processed_messages", [])
        if msg_id in processed:
            return True
        processed.append(msg_id)
        if len(processed) > 1000:
            processed = processed[-1000:]
        db["processed_messages"] = processed
        return False

def process_incoming_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    msg_id = message.get("id")
    
    if check_and_mark_processed(msg_id):
        logging.info(f"Message {msg_id} already processed. Ignoring duplicate.")
        return

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

    if cmd in ["home", "hi", "hello", "hey", "vanakkam", "go back to home"]:
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
    elif cmd in ["tamil sample", "english sample", "more images"]:
        from flask import request
        import os
        base_url = request.url_root
        
        # Ensure https for media links if behind a proxy
        if base_url.startswith("http://") and "localhost" not in base_url and "127.0.0.1" not in base_url:
            base_url = base_url.replace("http://", "https://")
            
        from app.utils.whatsapp_utils import get_image_message_input
        
        if cmd == "more images":
            lang, page = get_sample_state(wa_id)
        else:
            lang = "tamil" if cmd == "tamil sample" else "english"
            page = 0
            
        samples_dir = os.path.join("app", "static", "samples", lang)
        
        has_more = False
        if os.path.exists(samples_dir):
            images = [img for img in sorted(os.listdir(samples_dir)) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
            start_idx = page * 4
            end_idx = start_idx + 4
            current_images = images[start_idx:end_idx]
            
            for img in current_images:
                img_url = f"{base_url}static/samples/{lang}/{img}"
                send_message(get_image_message_input(wa_id, img_url))
                
            has_more = len(images) > end_idx
            
        if has_more:
            update_sample_state(wa_id, lang, page + 1)
            next_screen = "sample_more"
        else:
            # reset page if they want to view samples again later
            update_sample_state(wa_id, lang, 0)
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
    elif cmd in ["buy now", "buy single volume", "buy complete collection", "buy all 5 volumes"]:
        next_screen = "buy"
    elif cmd == "ship abroad":
        next_screen = "support"
    elif cmd in ["faqs", "faq"]:
        next_screen = "faq"
    elif cmd in ["contact support", "support"]:
        next_screen = "support"
    elif cmd == "ask a question":
        # Send a prompt to ask the question
        set_unknown_count(wa_id, 0)
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
        # A recognized command means the user is no longer "stuck" -> reset the streak
        set_unknown_count(wa_id, 0)

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

    # If fallback to AI: let the model decide whether this is an on-topic question it
    # can answer from the knowledge base, or off-topic/random text that should get the
    # branded redirect + menu instead of a free-form AI reply.
    if fallback_to_ai:
        is_on_topic, response = generate_response(message_text, wa_id, name)

        if is_on_topic:
            set_unknown_count(wa_id, 0)
            response = process_text_for_whatsapp(response)
            data = get_text_message_input(wa_id, response)
            send_message(data)
        else:
            unknown_count = get_unknown_count(wa_id) + 1
            set_unknown_count(wa_id, unknown_count)

            if unknown_count >= 3:
                send_screen(wa_id, "unknown_repeated")
            else:
                send_screen(wa_id, "unknown_first")
