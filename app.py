from flask import Flask, request, jsonify, send_from_directory
import random
import re

app = Flask(__name__)

# ─────────────────────────────────────────
# KNOWLEDGE BASE
# ─────────────────────────────────────────

INFO = {
    "starlink_gen3_price": "K9,000",
    "starlink_mini_price": "K6,800",
    "monthly_price": "K800",
    "location": "Lusaka Woodlands and Ndola",
    "hours": "Monday to Sunday, 08:00 to 18:00",
    "phone": "+260 968 252 812",
    "email": "info@sovetlink.com",
    "website": "sovetlink.com"
}

# ─────────────────────────────────────────
# RESPONSE POOLS - VARIED, NATURAL
# ─────────────────────────────────────────

R = {
    "greeting": [
        "Hi! What can I help you with?",
        "Hey, what would you like to know?",
        "Hello! How can I assist you today?",
        "Hi there! Ask me anything."
    ],
    "thanks": [
        "Happy to help! Anything else?",
        "No problem at all. Let me know if you need anything else.",
        "Glad I could help! Feel free to ask more.",
        "Anytime! Is there something else I can help with?"
    ],
    "goodbye": [
        "Take care! Feel free to come back anytime.",
        "Goodbye! We're here whenever you need us.",
        "See you! Have a great day.",
        "Take care! Don't hesitate to reach out."
    ],
    "starlink_price": [
        "Starlink Gen 3 is K9,000 and the Mini is K6,800. Monthly internet is K800.",
        "Gen 3 goes for K9,000, Mini is K6,800. Monthly subscription is K800.",
        "Starlink prices: Gen 3 — K9,000 | Mini — K6,800 | Monthly internet — K800.",
        "The Gen 3 is K9,000 and the Mini K6,800. You also pay K800/month for the internet."
    ],
    "starlink_general": [
        "We install Starlink across Zambia — Gen 3 at K9,000, Mini at K6,800. Fast satellite internet for homes and businesses.",
        "We're Starlink installers in Zambia. Gen 3 is K9,000, Mini is K6,800. We handle everything from supply to setup.",
        "Yes, we do Starlink. Gen 3 at K9,000 and Mini at K6,800. Professional installation included.",
        "Starlink is one of our main services. Gen 3 — K9,000, Mini — K6,800. We cover Lusaka and Ndola."
    ],
    "monthly": [
        "Monthly unlimited internet is K800. No data caps.",
        "The monthly plan is K800 for unlimited Starlink internet.",
        "K800 a month gets you unlimited Starlink internet. Fast and reliable.",
        "Our monthly internet subscription is K800 — fully unlimited."
    ],
    "cctv": [
        "We do full CCTV installation — supply, setup and configuration. Want a quote?",
        "Yes, CCTV is one of our services. We handle everything from cameras to monitoring setup.",
        "We supply and install CCTV systems for homes, offices and businesses. What do you need?",
        "Our team handles full CCTV setup. Just let us know your location and what you need covered."
    ],
    "networking": [
        "We set up networks for offices, schools and businesses — LAN, WiFi, access points and more.",
        "Yes, networking is one of our core services. We handle full office and home network setups.",
        "From cable runs to wireless setups, we cover all networking needs. Want us to assess your space?",
        "We do structured networking — routers, switches, access points and full configurations."
    ],
    "it_support": [
        "We offer IT support for businesses and households — setup, troubleshooting and maintenance.",
        "Our IT team can help with computers, networks and general tech issues.",
        "Yes, IT support is something we cover. What are you dealing with?",
        "We provide IT support services. From software setup to hardware issues, our team handles it."
    ],
    "location": [
        "We're based in Lusaka Woodlands and Ndola, but we serve clients across Zambia.",
        "Our offices are in Lusaka Woodlands and Ndola. We travel for installations.",
        "Based in Lusaka Woodlands and Ndola. We can come to you.",
        "Lusaka Woodlands and Ndola are our main locations. We cover all of Zambia."
    ],
    "hours": [
        "We're open Monday to Sunday, 08:00 to 18:00.",
        "Our hours are 8am to 6pm, every day of the week.",
        "We operate 7 days a week from 08:00 to 18:00.",
        "Monday to Sunday, 08:00 to 18:00. Always available."
    ],
    "contact": [
        "You can reach us on WhatsApp at +260 968 252 812 or email info@sovetlink.com.",
        "Best way is WhatsApp — +260 968 252 812. We're also on sovetlink.com.",
        "Call or WhatsApp us on +260 968 252 812. Available Mon–Sun 08:00–18:00.",
        "Reach us on +260 968 252 812 via WhatsApp or email info@sovetlink.com."
    ],
    "services": [
        "We offer Starlink installation, CCTV systems, networking solutions and IT support. What do you need?",
        "Our services: Starlink internet, CCTV installation, networking and IT support. Anything specific?",
        "Sovet Link covers Starlink, CCTV, networking and IT support across Zambia. Which interests you?",
        "We do Starlink, CCTV, networking and IT support. Let me know what you're looking for."
    ],
    "price_general": [
        "Starlink Gen 3 — K9,000 | Mini — K6,800 | Monthly internet — K800. CCTV and networking are quoted based on your needs.",
        "Prices: Starlink Gen 3 K9,000, Mini K6,800, monthly internet K800. CCTV and networking — contact us for a quote.",
        "Starlink from K6,800, monthly internet K800. CCTV and networking pricing depends on your setup — want a quote?"
    ],
    "book": [
        "Our team will get you sorted. Tap below to chat with them directly.",
        "Let me connect you with the team — they'll handle everything from there.",
        "Our team is ready to help. Tap below to get started on WhatsApp."
    ],
    "fallback": [
        "Not sure about that one. Want me to connect you with the team?",
        "That's a bit outside what I know. Our team can help — want their WhatsApp?",
        "Good question! Our team would be better placed to answer that. Want to reach them?",
        "I don't have that info right now. Our team on WhatsApp can sort you out."
    ]
}

# ─────────────────────────────────────────
# TYPO / FUZZY NORMALIZER
# ─────────────────────────────────────────

TYPO_MAP = {
    r'starlnk|starlinck|starlinkk|starlik|strlink|starlonk|starlimk': 'starlink',
    r'ccctv|cctvi|cctv|camara|camra|camrea|secuirty|securty|surveilance': 'cctv',
    r'netowrk|netwrok|networkng|nwtwork|netwerk': 'network',
    r'instalation|instal|intallation|installtion': 'installation',
    r'prise|prce|pric|priec|priice|coust|cots|hoe much|hw much': 'price',
    r'woring|wroking|workin|opn|openn|wrking': 'working',
    r'bookng|bokk|bok|boook': 'book',
    r'watsapp|whtsapp|whatsap|whasapp|watsap': 'whatsapp',
    r'loaction|lacation|locaton|locatin': 'location',
    r'supprot|suport|suupport|IT suport': 'it support',
    r'ministarlink|starlink mini|mni': 'mini',
}

def normalize(text):
    text = text.lower().strip()
    for pattern, replacement in TYPO_MAP.items():
        text = re.sub(pattern, replacement, text)
    return text

# ─────────────────────────────────────────
# INTENT DETECTOR
# ─────────────────────────────────────────

def detect(msg, history):
    m = normalize(msg)
    h = ' '.join(history).lower()

    # Greeting
    if re.search(r'\b(hi|hey|hello|good morning|good afternoon|good evening|hie|howdy|sup|yo)\b', m):
        return 'greeting'

    # Thanks
    if re.search(r'\b(thanks|thank you|thx|cheers|appreciated|thank)\b', m):
        return 'thanks'

    # Goodbye
    if re.search(r'\b(bye|goodbye|see you|later|cya|take care|done|ok bye|kk bye)\b', m):
        return 'goodbye'

    # Book / ready to proceed
    if re.search(r'\b(book|order|buy|purchase|get one|install|want one|interested|proceed|sign up|ready|how do i start|set up|set it up|i want|id like|i need)\b', m):
        return 'book'

    # Starlink price
    if re.search(r'starlink', m) and re.search(r'(price|cost|how much|rate|charge|fee|kwacha|zmw|k\d)', m):
        return 'starlink_price'

    # Monthly internet
    if re.search(r'(monthly|subscription|per month|internet plan|unlimited|data plan|month)', m):
        return 'monthly'

    # Starlink general
    if re.search(r'starlink', m):
        return 'starlink_general'

    # CCTV
    if re.search(r'(cctv|camera|security camera|surveillance|cams|footage|monitor)', m):
        return 'cctv'

    # Networking
    if re.search(r'(network|networking|lan|wifi|wireless|router|cable|access point|wiring|local area)', m):
        return 'networking'

    # IT support
    if re.search(r'(it support|tech support|computer|laptop|repair|fix|troubleshoot|configure|software)', m):
        return 'it_support'

    # Location
    if re.search(r'(where|location|address|based|lusaka|ndola|find you|office|area|operate)', m):
        return 'location'

    # Hours
    if re.search(r'(hours|open|close|working hours|when|what time|available|operate)', m):
        return 'hours'

    # Contact
    if re.search(r'(contact|call|phone|number|whatsapp|email|reach|talk|speak)', m):
        return 'contact'

    # Services
    if re.search(r'(services|what do you|offer|provide|do you do|what can you|help with|what you offer)', m):
        return 'services'

    # Price general
    if re.search(r'(price|cost|how much|charge|fee|rate|kwacha|zmw|affordable|pricing)', m):
        return 'price_general'

    # Context from history
    if re.search(r'starlink', h) and re.search(r'(price|cost|how much|more)', m):
        return 'starlink_price'

    if re.search(r'cctv', h) and re.search(r'(price|cost|how much|more|install)', m):
        return 'cctv'

    return 'fallback'

# ─────────────────────────────────────────
# MIXED QUESTION HANDLER
# ─────────────────────────────────────────

def handle_mixed(m, history):
    parts = []
    wa = False

    has_starlink = bool(re.search(r'starlink', m))
    has_price = bool(re.search(r'(price|cost|how much|kwacha)', m))
    has_cctv = bool(re.search(r'(cctv|camera|security)', m))
    has_network = bool(re.search(r'(network|wifi|lan|internet)', m))
    has_location = bool(re.search(r'(where|location|lusaka|ndola)', m))
    has_hours = bool(re.search(r'(hours|open|time|when)', m))
    has_monthly = bool(re.search(r'(monthly|subscription|per month)', m))

    topics = sum([has_starlink, has_cctv, has_network, has_location, has_hours, has_monthly])

    if topics < 2:
        return None, False

    if has_starlink and has_price:
        parts.append("Starlink Gen 3 is K9,000, Mini is K6,800")
        wa = True
    elif has_starlink:
        parts.append("we install Starlink across Zambia")
        wa = True

    if has_monthly:
        parts.append("monthly internet is K800")
        wa = True

    if has_cctv:
        parts.append("CCTV installation is also available")
        wa = True

    if has_network:
        parts.append("we handle networking setups too")

    if has_location:
        parts.append("we're based in Lusaka Woodlands and Ndola")

    if has_hours:
        parts.append("open Mon–Sun 08:00–18:00")

    if parts:
        reply = ", ".join(parts).capitalize() + ". Anything else you'd like to know?"
        return reply, wa

    return None, False

# ─────────────────────────────────────────
# WHATSAPP TRIGGER LOGIC
# ─────────────────────────────────────────

WA_INTENTS = {'book', 'starlink_price', 'starlink_general', 'monthly', 'cctv', 'price_general', 'contact', 'fallback'}

def needs_whatsapp(intent, msg):
    m = normalize(msg)
    # Only send to WhatsApp when they want to proceed or need more specific help
    if intent == 'book':
        return True
    if intent == 'fallback':
        return True
    if intent in {'starlink_price', 'starlink_general', 'monthly', 'cctv', 'price_general'}:
        # Only if they show buying signals
        if re.search(r'(want|interested|book|buy|proceed|ready|get one|install|set up|yes|yeah|yep|sure)', m):
            return True
    if intent == 'contact':
        return True
    return False

# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get('message', '').strip()
    history = data.get('history', [])

    if not msg:
        return jsonify({'reply': 'Please send a message.', 'whatsapp': False})

    m = normalize(msg)

    # Try mixed question handler
    mixed_reply, mixed_wa = handle_mixed(m, history)
    if mixed_reply:
        return jsonify({'reply': mixed_reply, 'whatsapp': mixed_wa})

    # Single intent
    intent = detect(msg, history)
    reply = random.choice(R.get(intent, R['fallback']))
    whatsapp = needs_whatsapp(intent, msg)

    return jsonify({'reply': reply, 'whatsapp': whatsapp})

# ─────────────────────────────────────────

if __name__ == '__main__':
    print("\n Sovet Link Assistant running on http://localhost:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False)

