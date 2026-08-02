# Nila Comics Knowledge Base

**About Nila Comics:**
Nila Comics presents a comic book adaptation of the classic Tamil novel "Ponniyin Selvan" by Kalki. This epic novel brings to life the love, valor, and piety of the Tamil kings. Every panel is crafted to capture the grandeur, history, and emotions of Kalki's masterpiece in an engaging visual style for all ages.

**1. Price & Offers:** 
- ₹750 per single book.
- ₹2,999 for the complete collection (5 Volumes).
- Save ₹751 when purchasing the complete collection.

**2. Product Details:**
- Premium Maplitho Paper
- Offset Printing
- Full Colour artwork
- Approx. 350 Pages per Volume
- Approx. 1,750 Pages Total
- Available in Tamil & English Editions

**3. Delivery Information:**
- Delivery available across India.
- Estimated delivery time: 3–7 business days within India.
- International shipping is available.
- Delivery charges are applicable for all orders (No free shipping).
- Delivery charges are calculated based on your delivery location and order quantity.
- The exact delivery charge will be displayed during checkout before payment.
- There are no hidden charges after checkout.
- Tracking details will be shared once your order is dispatched.

**4. FAQs (Mandatory):**
- **Is it available in English?** Yes, available in English.
- **Is it available in Tamil?** Yes, available in Tamil.
- **Can I buy a single book?** Yes. Every volume can be purchased individually for ₹750.
- **Can I buy only two books?** Yes. You may purchase any individual volumes you want.
- **What is the discount?** Buy all 5 volumes for ₹2,999 and save ₹751.
- **What are the delivery charges?** Delivery charges are calculated during checkout based on your location.
- **Are there any hidden charges?** No. Your final payable amount is shown before payment.
- **Is this suitable for children?** Yes, the comic format is engaging for young readers while preserving the historical story.
- **Which volume should I start with?** We recommend starting with Volume 1.
- **Is there a gift discount?**
🎁 The Ponniyin Selvan Comic Collection makes a wonderful gift for family, friends, and history lovers.
Our Complete 5-Volume Collection is already offered at a special discounted price of ₹2,999, which includes a ₹750 discount from the original price.
There is no separate or additional discount for gift purchases.

**5. Contact Information & Support:**
- WhatsApp: +91 98848 06302
- Email: contact@nilacomics.com
- Call: +91 98848 06302
- W-100, 4th floor, 2nd Avenue, Anna Nagar, Chennai -600 040

**6. Important Links:**
- Website: https://nilacomics.com/
- FAQs: https://nilacomics.com/
- Contact Us: https://nilacomics.com/

**7. Conversational Flows & Bot Responses:**

This section is the single source of truth for every screen the bot can show, and must be
kept in sync with the `SCREENS` dict in `app/services/bot_service.py`. Do not duplicate a
screen here with different wording/buttons than the code — the two have drifted apart before
and it made the AI describe menus incorrectly.

**Welcome (Home):**
👋 Vanakkam! Welcome to Nila Comics

Experience Kalki's legendary Ponniyin Selvan through beautifully illustrated full-colour comics.

📚 Available in Tamil and English

Need help choosing? I'm here to guide you.

How can I help you today?

Buttons: Price, Read Sample, Delivery, Buy Now, Ask a Question, Support

**Tamil Edition / English Edition (shared template):**
✔ Beautiful Full Colour Artwork
✔ Around 350 pages per volume
✔ Available as individual books or complete collection

Buttons: Read Sample, Price, Buy Now, Home, Support

**Sample Pages:**
User picks Tamil Sample or English Sample; the bot sends 4 sample images at a time, then asks
if they want more images or want to return home.

**After reading Sample Pages (Follow-up message):**
Hope you enjoyed the preview images! Ready to continue your reading journey?

Buttons: Buy Single Volume, Buy All 5 Volumes, Home, Support

**Price:**
💰 Ponniyin Selvan Pricing

📖 Single Volume
₹750 per book

📚 Complete Collection (5 Volumes)
₹2,999 only

🎉 Save ₹751 when you purchase the complete collection.

Buttons: Buy Single Volume, Buy All 5 Volumes, Delivery Charges, Current Offers, Home, Support

**Discount:**
🎁 Discount Information

✔ Single Book Price: ₹750 each
✔ Buy all 5 volumes together for only ₹2,999.
✔ You save ₹751 compared to purchasing all five books separately.

Buttons: Buy All 5 Volumes, Price, Home, Support

**Delivery:**
🚚 Delivery Information

Delivery available across India, 3–7 business days domestically, international shipping
available, no free shipping, charges shown at checkout, no hidden charges after checkout.

Buttons: Ship Abroad, Buy Now, Home, Support

**Product Details:**
✔ Premium Maplitho Paper
✔ Offset Printing
✔ Full Colour
✔ Approx. 350 Pages per Volume
✔ Approx. 1,750 Pages Total
✔ Tamil & English Editions

Buttons: Price, Home, Support

**FAQs:**
Reachable by tapping the "FAQs" button (shown on the unknown-message fallback screen) or by
typing "faq"/"faqs" directly. Renders the full FAQ list from section 4 above (including the
Gift Discount answer) as one message.

Buttons: Contact Support, Home

**Support:**
Contact our support team:
WhatsApp: +91 98848 06302
Email: contact@nilacomics.com
Call: +91 98848 06302

Buttons: Home

**Buy:**
Great! You can purchase from our website:
Single Volume (₹750) / Complete Collection (₹2,999): https://nilacomics.com/

Buttons: Home, Support

**Smart Conversion:**
Fires once, the first time a user has viewed any 2 of {Price, Discount, Delivery, Sample
Pages, Product Details}, right after whatever screen they just requested:

It looks like you've explored the Ponniyin Selvan collection. Ready to own this timeless masterpiece?

Buttons: Buy Single Volume, Buy All 5 Volumes, Continue Browsing

**Unknown/random input (1st or 2nd consecutive miss):**
😊 Sorry, I couldn't quite understand that. I'm the Nila Comics assistant, and I'm happy to help you with:

📚 Explore the Ponniyin Selvan Collection
📖 Sample Pages
💰 Pricing & Discounts
🚚 Delivery Information
❓ Frequently Asked Questions
🛒 Buy the Collection

Please choose one of the options below.

Buttons: Read Sample, Price, Delivery, FAQs, Buy Now, Home, Support

**Unknown/random input (3rd+ consecutive miss):**
😊 I'm sorry, I still couldn't understand your request.

Please select one of the options below, or contact our support team if you need further assistance.

Buttons: Contact Support, Home

**How "unknown" is decided:** free text that doesn't match a button is sent to the AI, which
first judges whether the message is actually about Nila Comics / Ponniyin Selvan / pricing /
delivery / orders. If it is, the AI answers normally from this knowledge base. If it is not
(small talk, unrelated trivia, gibberish), the bot does NOT let the AI free-associate a reply —
it shows the sweet on-brand redirect screen above instead, and a per-user streak counter
decides whether to show the 1st/2nd version or escalate to the 3rd+ "contact support" version.
The streak resets to zero the moment the user taps any real menu button or asks something the
AI can answer on-topic.
