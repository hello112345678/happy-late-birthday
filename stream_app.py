import streamlit as st
import random
from time import sleep
from PIL import Image
import base64
import io

# ==================== GAME DATA ====================
BIOCARDS = {
    "♣️": ["Light Energy", "Chlorophyll", "H₂O", "CO₂", "Photosynthase"],
    "♥️": ["ATP", "Glucose", "Mitochondria", "Oxygen", "Lactic Acid"],
    "♦️": ["DNA", "RNA", "Chromosome", "Mutation", "Telomere"],
    "♠️": ["Amino Acid", "Protein", "Enzyme", "Ribosome", "Prion"],
    "☢️": ["Super Mutation", "Caffeine", "Dark Circles", "Homework Pass", "Nobel Medal"]
}

RECIPES = {
    ("Glucose", "Enzyme"): ("Alcohol", "Fermentation successful! Lab smells like beer", "🫗", "#FFD700"),
    ("DNA", "Amino Acid"): ("mRNA", "Transcription initiated! Ribosomes on their way", "📜", "#9370DB"),
    ("ATP", "Mitochondria"): ("Energy Storm", "Mitochondria overload! All cards blown away", "🌪️", "#FF6347"),
    ("Light Energy", "CO₂"): ("Starch", "Photosynthesis achieved! Gain 3 new cards", "🍚", "#32CD32")
}

BAD_COMBOS = {
    ("Mutation", "DNA"): ("Genetic Collapse", "🧬", "#FF0000"),
    ("Prion", "Protein"): ("Protein Denaturation", "☠️", "#8B0000")
}

# Hidden birthday awards for Mr. Weitzel
HIDDEN_AWARDS = {
    "YAY Mr.weitzel": {
        "name": "Weitzel's Wisdom",
        "image": "https://cdn.pixabay.com/photo/2017/01/31/15/33/biology-2025821_960_720.png",
        "description": "For making biology unforgettable",
        "found": False
    },
    "happybirthday": {
        "name": "Birthday Nobel",
        "image": "https://cdn.pixabay.com/photo/2012/04/24/13/49/medal-40383_960_720.png",
        "description": "Special birthday achievement",
        "found": False
    },
    "bestbio": {
        "name": "Best Bio Teacher",
        "image": "https://cdn.pixabay.com/photo/2016/11/22/19/08/award-1850042_960_720.png",
        "description": "The DNA of great teaching",
        "found": False
    }
}

# ==================== GAME STATE ====================
if "game" not in st.session_state:
    st.session_state.game = {
        "deck": [],
        "discard_pile": [],
        "inventory": [],
        "boss_hp": 0,
        "boss_active": False,
        "recipes_unlocked": 0,
        "game_status": "playing",
        "last_action": "Game started!",
        "birthday_seen": False,
        "hidden_awards": HIDDEN_AWARDS.copy(),
        "player_name": "Mr. Weitzel"
    }

# ==================== CORE FUNCTIONS ====================
def create_deck():
    deck = []
    for suit, items in BIOCARDS.items():
        for rank, name in enumerate(items, 1):
            deck.append({
                "suit": suit,
                "rank": rank,
                "name": name,
                "selected": False,
                "color": "#2E8B57" if suit == "♣️" else
                         "#DC143C" if suit == "♥️" else
                         "#4169E1" if suit == "♦️" else
                         "#4B0082" if suit == "♠️" else
                         "#FF8C00"
            })
    random.shuffle(deck)
    return deck

def draw_card():
    if not st.session_state.game["deck"]:
        st.session_state.game["deck"] = create_deck()
    card = st.session_state.game["deck"].pop()
    st.session_state.game["discard_pile"].append(card)
    
    # Activate boss after 20 draws
    if len(st.session_state.game["discard_pile"]) > 20 and not st.session_state.game["boss_active"]:
        st.session_state.game["boss_active"] = True
        st.session_state.game["boss_hp"] = 100
        st.session_state.game["discard_pile"].append({
            "suit": "☢️", 
            "name": "All-Nighter Professor", 
            "rank": 99,
            "selected": False,
            "color": "#FF8C00"
        })
        st.session_state.game["last_action"] = "⚠️ BOSS APPEARED! Mr. Weitzel's Evil Twin!"
    else:
        st.session_state.game["last_action"] = f"Drew: {card['suit']} {card['name']}"
    return card

def check_combos():
    names = [card["name"] for card in st.session_state.game["discard_pile"] if card.get("selected")]
    
    # Check recipes
    for (item1, item2), (product, msg, icon, color) in RECIPES.items():
        if item1 in names and item2 in names:
            st.session_state.game["inventory"].append(product)
            st.session_state.game["recipes_unlocked"] += 1
            st.session_state.game["discard_pile"] = [
                card for card in st.session_state.game["discard_pile"] 
                if not (card["name"] == item1 or card["name"] == item2)
            ]
            st.session_state.game["last_action"] = f"{icon} {msg} Got [{product}]!"
            return True
    
    # Check bad combos
    for (item1, item2), (effect, icon, color) in BAD_COMBOS.items():
        if item1 in names and item2 in names:
            st.session_state.game["game_status"] = "game_over"
            st.session_state.game["last_action"] = f"{icon} {effect}! Game Over"
            return True
    return False

def attack_boss():
    atp_cards = [card for card in st.session_state.game["discard_pile"] 
                if card["name"] == "ATP" and card.get("selected")]
    if atp_cards:
        st.session_state.game["boss_hp"] -= 20 * len(atp_cards)
        st.session_state.game["discard_pile"] = [
            card for card in st.session_state.game["discard_pile"] 
            if card["name"] != "ATP" or not card.get("selected")
        ]
        st.session_state.game["last_action"] = f"💥 Used {len(atp_cards)} ATP cards | Boss HP: {st.session_state.game['boss_hp']}"
        if st.session_state.game["boss_hp"] <= 0:
            st.session_state.game["inventory"].append("Homework Pass")
            st.session_state.game["last_action"] = "🎉 DEFEATED BOSS! Got [Homework Pass]"
            return True
    return False

# ==================== BIRTHDAY FEATURES ====================
def show_birthday_message():
    with st.expander(f"🎂 SPECIAL MESSAGE FOR {st.session_state.game['player_name'].upper()}", expanded=True):
        st.balloons()
        st.markdown(f"""
        <div style="background:linear-gradient(to right, #FFD700, #FF8C00); 
                    padding:20px; border-radius:10px; text-align:center;">
            <h2 style="color:white;">Happy Birthday, {st.session_state.game['player_name']}!</h2>
            <p style="font-size:18px;">Thank you for making biology such an intresting class!</p>
            <p style="font-size:24px;">🎁 Your special gift is hidden in the game!</p>
        </div>
        """, unsafe_allow_html=True)

def check_secret_code(code):
    code = code.lower()
    if code in st.session_state.game["hidden_awards"]:
        if not st.session_state.game["hidden_awards"][code]["found"]:
            st.session_state.game["hidden_awards"][code]["found"] = True
            st.session_state.game["inventory"].append(
                st.session_state.game["hidden_awards"][code]["name"]
            )
            st.session_state.game["last_action"] = f"✨ Discovered: {st.session_state.game['hidden_awards'][code]['name']}"
            st.balloons()
            st.rerun()
            
# ==================== CUSTOM COMPONENTS ====================
def render_card(card, key):
    emoji = "🔘" if card.get("selected") else "⚪"
    card_html = f"""
    <div style="
        background: {card['color']};
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: all 0.3s;
        transform: {'scale(1.05)' if card.get('selected') else 'scale(1)'};
    ">
        <div style="font-size: 24px;">{card['suit']}</div>
        <div style="font-size: 18px; font-weight: bold;">{card['name']}</div>
        <div style="font-size: 14px;">Level: {card['rank']}/5</div>
    </div>
    """
    if st.button(emoji, key=key):
        card["selected"] = not card.get("selected", False)
        st.rerun()
    st.markdown(card_html, unsafe_allow_html=True)

def render_award_card(award_name, award_data):
    col1, col2 = st.columns([1, 3])
    with col1:
        if award_data["found"]:
            st.image(award_data["image"], width=100)
        else:
            st.markdown("""
            <div style="
                background: #DDDDDD;
                color: #666666;
                border-radius: 10px;
                width: 100px;
                height: 100px;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 5px;
            ">
                <span style="font-size: 24px;">?</span>
            </div>
            """, unsafe_allow_html=True)
    with col2:
        if award_data["found"]:
            st.subheader(award_name)
            st.caption(award_data["description"])
        else:
            st.subheader("???")
            st.caption("Hidden award")

# ==================== MAIN GAME UI ====================
def main():
    st.set_page_config(
        page_title=f"🎁 Bio Game for {st.session_state.game['player_name']}",
        page_icon="🔬",
        layout="wide"
    )

    # Birthday message on first run
    if not st.session_state.game["birthday_seen"]:
        show_birthday_message()
        st.session_state.game["birthday_seen"] = True

    st.title(f"🧪 Bio Card Lab: Special Edition for {st.session_state.game['player_name']}")
    st.caption("A birthday gift from your favorite student!")

    # Awards display
    st.subheader("🏆 Mr. Weitzel's Hidden Awards")
    award_cols = st.columns(len(st.session_state.game["hidden_awards"]))
    for i, (award_key, award_data) in enumerate(st.session_state.game["hidden_awards"].items()):
        with award_cols[i]:
            render_award_card(award_data["name"], award_data)

    # Secret code input
    with st.expander("🔐 Enter Birthday Code (hint: try 'YAY Mr.weitzel')", expanded=False):
        code = st.text_input("Secret code...", type="password")
        if st.button("Submit Special Code"):
            check_secret_code(code)

    # Status bar
    cols = st.columns(3)
    with cols[0]:
        st.metric("🔧 Combos Made", st.session_state.game["recipes_unlocked"])
    with cols[1]:
        st.metric("👾 Boss HP", 
                 f"{st.session_state.game['boss_hp']}/100" if st.session_state.game["boss_active"] else "Not activated",
                 delta=-20 if st.session_state.game["boss_active"] else None)
    with cols[2]:
        if "Homework Pass" in st.session_state.game["inventory"]:
            st.success("📝 Homework Pass Available!")
        elif any(award["found"] for award in st.session_state.game["hidden_awards"].values()):
            st.success("🎖️ Award Unlocked!")

    # Action area
    tab1, tab2 = st.tabs(["🃏 Card Zone", "⚗️ Lab Bench"])
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎴 Draw Card", help="Draw a new card", use_container_width=True):
                draw_card()
                st.rerun()
        with col2:
            if st.button("🔄 Clear Selection", type="secondary", use_container_width=True):
                for card in st.session_state.game["discard_pile"]:
                    card["selected"] = False
                st.session_state.game["last_action"] = "Cleared all selections"
                st.rerun()

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚗️ Try Combo", 
                        disabled=len([c for c in st.session_state.game["discard_pile"] if c["selected"]]) != 2,
                        help="Combine 2 selected cards",
                        use_container_width=True):
                if check_combos():
                    st.rerun()
        with col2:
            if st.session_state.game["boss_active"] and st.button("💣 Attack with ATP", 
                                                                use_container_width=True,
                                                                help="Use selected ATP cards as ammo"):
                if attack_boss():
                    st.balloons()
                st.rerun()

    # Card display
    st.subheader(f"📜 Card Pool (Selected: {len([c for c in st.session_state.game['discard_pile'] if c['selected']])}/2)")
    card_cols = st.columns(5)
    for i, card in enumerate(st.session_state.game["discard_pile"]):
        with card_cols[i % 5]:
            render_card(card, f"card_{i}")

    # Inventory
    if st.session_state.game["inventory"]:
        st.subheader("🎒 Inventory")
        inv_cols = st.columns(5)
        for i, item in enumerate(st.session_state.game["inventory"]):
            with inv_cols[i % 5]:
                st.markdown(f"""
                <div style="
                    background: #444;
                    color: white;
                    padding: 10px;
                    border-radius: 10px;
                    text-align: center;
                ">
                    {item}
                </div>
                """, unsafe_allow_html=True)

    # Last action log
    st.markdown(f"**Last Action:** {st.session_state.game['last_action']}")

    # Game over checks
    if st.session_state.game["game_status"] != "playing":
        if st.session_state.game["game_status"] == "victory":
            st.balloons()
            st.success("""
            🎉 **CONGRATULATIONS!**  
            You've mastered biological card science!  
            Mr. Weitzel would be proud!
            """)
        else:
            st.error("""
            💀 **LAB ACCIDENT!**  
            The experiment failed...  
            Better luck next time!
            """)
        
        if st.button("🔄 Start New Experiment", type="primary"):
            st.session_state.clear()
            st.rerun()

    # Custom styling
    st.markdown("""
    <style>
        /* Title styling */
        h1 {
            color: #4B0082;
            border-bottom: 2px solid #9370DB;
            padding-bottom: 10px;
        }
        
        /* Card hover effects */
        div[data-testid="stButton"] button {
            transition: transform 0.2s;
        }
        div[data-testid="stButton"] button:hover {
            transform: scale(1.1);
        }
        
        /* Metric styling */
        [data-testid="stMetricValue"] {
            font-size: 24px;
        }
        
        /* Tab styling */
        button[data-baseweb="tab"] {
            font-size: 16px !important;
            padding: 8px 16px !important;
        }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
