import streamlit as st
import streamlit.components.v1 as components
import random
import time
import re

# ==============================================================================
# 1. CONFIGURATION & ASSETS
# ==============================================================================
st.set_page_config(
    page_title="Quality Wars: The ROI Strikes Back",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CUSTOM CSS: NEON/SPACE THEME & ANIMATIONS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto:wght@300;400;700&display=swap');

    /* MAIN THEME */
    .stApp {
        background-color: #050505;
        background-image: 
            radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 40px),
            radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 30px),
            radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 40px);
        background-size: 550px 550px, 350px 350px, 250px 250px;
        background-position: 0 0, 40px 60px, 130px 270px;
        font-family: 'Roboto', sans-serif;
        color: #e0e0e0;
    }

    /* TYPOGRAPHY */
    h1, h2, h3, h4 {
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    h1 {
        background: -webkit-linear-gradient(#FFE81F, #D4AF37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 20px rgba(255, 232, 31, 0.5);
        text-align: center;
        font-weight: 900;
        font-size: 3.5rem !important;
        margin-bottom: 0px;
    }

    /* INTEL/SLIDE CARDS */
    .intel-viewer {
        background: rgba(16, 20, 24, 0.98);
        border: 2px solid #00e5ff;
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.15);
        border-radius: 12px;
        padding: 40px;
        min-height: 600px;
        position: relative;
    }

    .slide-content {
        font-size: 1.1rem;
        line-height: 1.8;
        white-space: pre-wrap; 
    }

    .slide-nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 20px;
        border-top: 1px solid #333;
        padding-top: 20px;
    }

    /* BUTTONS */
    .stButton>button {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(45deg, #00e5ff, #2979ff) !important;
        color: #000 !important;
        border: none;
        padding: 15px 25px;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
        text-transform: uppercase;
        border-radius: 4px;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.3);
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 0 30px rgba(0, 229, 255, 0.8);
        color: white !important;
    }

    /* HUD */
    .hud-container {
        display: flex;
        justify-content: space-around;
        background: rgba(0,0,0,0.9);
        border-bottom: 2px solid #FFE81F;
        padding: 15px;
        position: sticky;
        top: 0;
        z-index: 999;
        backdrop-filter: blur(5px);
        margin-bottom: 30px;
    }
    
    .metric-box {
        text-align: center;
        font-family: 'Orbitron', sans-serif;
    }
    .metric-label { color: #888; font-size: 0.7rem; letter-spacing: 2px; }
    .metric-value { color: #FFE81F; font-size: 1.5rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CONTENT DATABASES (Expanded & Specific)
# ==============================================================================

TRIVIA_DB = [
    # VIVE HISTORY & STRATEGY
    {
        "q": "Vive Health was founded in 2014. How many distribution centers does it strategically operate across the US?",
        "options": ["Four", "Two", "One", "Six"],
        "correct": "Four",
        "feedback": "Correct! Four centers allow 1-2 business day delivery across the entire US."
    },
    {
        "q": "Which of the following is a core 'Strategic Advantage' of Vive Health regarding manufacturing?",
        "options": ["Owns its own Manufacturing Facility", "Outsources to random bidders", "Dropshipping only", "3D Prints everything in-house"],
        "correct": "Owns its own Manufacturing Facility",
        "feedback": "Correct. Owning manufacturing allows for 'Military Grade Standard' quality control."
    },
    {
        "q": "Vive Health's goal for Amazon FBA Return Rate is </= 7.50%. In Oct 2025, the rate was slashed to:",
        "options": ["5.54%", "10.2%", "2.1%", "0%"],
        "correct": "5.54%",
        "feedback": "Correct. The FBA return rate was slashed to 5.54%, exceeding the goal."
    },
    
    # TEAM & CULTURE
    {
        "q": "Who leads Product Testing at the Naples Office and is a retired PhD Chemist?",
        "options": ["Jim Ahearn", "Carolina Silva", "Annie", "Jason"],
        "correct": "Jim Ahearn",
        "feedback": "Correct. Jim leads research and testing."
    },
    {
        "q": "Who is the QC Manager in China managing ~25 inspectors?",
        "options": ["Annie", "Jessica", "Luis", "Tom"],
        "correct": "Annie",
        "feedback": "Correct. Annie contracts inspectors and reviews data in China."
    },
    {
        "q": "Which Core Value states: 'We take full responsibility for our actions, results, and success. No excuses'?",
        "options": ["Extreme Ownership", "Growth Mindset", "Best Ideas Rise", "Data & System Driven"],
        "correct": "Extreme Ownership",
        "feedback": "Correct. 'External obstacles are just hurdles, not roadblocks.'"
    },

    # QUALITY TOOLS & CONCEPTS
    {
        "q": "In the context of Strategic Planning, what is 'The Comfort Trap'?",
        "options": ["Focusing on activities you control (hiring, timelines) instead of competitive outcomes.", "Buying too many office chairs.", "Staying in old markets.", "Ignoring safety regulations."],
        "correct": "Focusing on activities you control (hiring, timelines) instead of competitive outcomes.",
        "feedback": "Correct. Real strategy requires specifying a competitive outcome you don't control."
    },
    {
        "q": "What does 'Genchi Genbutsu' mean in our quality philosophy?",
        "options": ["Go and See (to the source)", "Continuous Improvement", "Respect for People", "Just in Time"],
        "correct": "Go and See (to the source)",
        "feedback": "Correct. We visit the warehouse or factory to understand problems deeply."
    },
    {
        "q": "In a RACI Matrix, what does the 'R' stand for?",
        "options": ["Responsible (The person who does the task)", "Reviewer", "Random", "Regulator"],
        "correct": "Responsible (The person who does the task)",
        "feedback": "Correct. 'A' is Accountable (the one who answers for it)."
    },
    {
        "q": "What is the estimated Total Addressable Market (TAM) increase by obtaining the CE Mark for EU/UK expansion?",
        "options": ["> 2x (More than double)", "10%", "50%", "No change"],
        "correct": "> 2x (More than double)",
        "feedback": "Correct. Accessing the EU/UK adds +520M people and ~$150B in accessible device market."
    }
]

# FULL SLIDE CONTENT RECONSTRUCTED FROM UPLOADS
SLIDE_DECKS = {
    "leadership": {
        "title": "Quality Leadership Presentation (11/2025)",
        "slides": [
            "**TITLE:** QUALITY APPROVED\nVive Health - November 2025\n\n---",
            "**VIVE'S QUALITY TEAM**\n\n* **Carolina Silva (Quality Analyst):** Analyzes trends, Biomedical Engineer.\n* **Annie (QC Manager China):** Contracts ~25 inspectors, reviews data.\n* **Jim Ahearn (Research & Testing):** Retired PhD Chemist, leads testing in Naples.\n* **Jason (QC at MPF):** Leads MPF inspection team.\n* **Jessica Marshall (Regulatory Affairs):** Leads ISO 13485 & EU Market Access.",
            "**AGENDA**\n\n1.  **Why we do what we do:** Strategic Value.\n2.  **How we are doing:** Performance Review.\n3.  **What we are doing:** Process & Proactivity.",
            "**STRATEGIC WINS**\n\n* **Market Expansion:** CE Mark (Nov 2025) & ISO 13485 will >2x our TAM (Total Addressable Market).\n* **Revenue:** Developed memory foam seat cushion to generate revenue/offset costs.\n* **AI Efficiency:** Used Gemini/Claude ('Vibe Coding') to build custom analytics apps with $0 software budget.",
            "**PERFORMANCE METRICS (NOV 2025)**\n\n* **FBA Return Rate:** 5.54% (Target < 7.50%) - EXCEEDING GOAL.\n* **B2B Return Rate:** 2.29% (Target < 2.00%) - NEEDS FOCUS.\n* **ISO 13485 Implementation:** 42.5% Complete - ON TRACK.\n* **VoC Listing Health:** 77.61% Good/Excellent.",
            "**CASE STUDY: POST-OP SHOE**\n\n* **Situation:** High return rate due to 'fit/size' complaints.\n* **Action:** Deep analysis against competitors.\n* **Finding:** Our shoes were 5-11% larger than top market brand.\n* **Result:** Data-driven resizing in progress to slash returns.",
            "**LESSONS LEARNED: PACKAGING**\n\n* **The Mistake:** Changed packaging to Shrink Wrap to save Amazon FBA fees.\n* **The Cost:** It hurt B2B sales perception.\n* **The Fix:** Cross-department sign-offs. We now ask 'Will it be a net positive for the company?' not just one department.",
            "**PHILOSOPHY & STRATEGY**\n\n* **Philosophy:** 'Ounce of prevention > Pound of cure.'\n* **Strategy:** Shift from Reactive Quality Control (Detecting defects) to Proactive Quality Assurance (Preventing defects).\n* **Military Leadership Model:** Moving from 'Command by Directive' (Micromanagement) to 'Command by Intent' (Autonomy).",
        ]
    },
    "product_dev": {
        "title": "Product Dev Quality Strategies",
        "slides": [
            "**INTRODUCTION**\n\n'How things start is how they'll go...' - FDA Postmarket Branch.\n\nSmall changes with big impacts:\n* Project Charter\n* Risk Assessment\n* Affinity Diagrams",
            "**PROJECT CHARTER**\n\nA living document outlining:\n* **Problem Statement:** The problem in measurement form.\n* **Business Case:** Why are we doing this?\n* **Scope:** What is IN and OUT.\n* **Timeline & Team:** Who and When.",
            "**VOICE OF CUSTOMER (VoC)**\n\nWe must move from 'What' to 'Why'.\n\n* **Fishbone Diagram:** Trace problems (e.g., 'discomfort') to sources (Materials, Methods, Environment).\n* **Kano Analysis:** Separate 'Basic Needs' (Breathable fabric) from 'Delighters' (Bluetooth speakers). Don't waste money on features customers don't care about.",
            "**FMEA (FAILURE MODE & EFFECTS ANALYSIS)**\n\nFormula: **Severity (S) x Occurrence (O) x Detection (D) = RPN (Risk Priority Number)**.\n\n1.  Identify Failure Modes (e.g., Gel pad leaks).\n2.  Score S, O, D (1-10).\n3.  Prioritize highest RPNs for mitigation.\n\n*Goal: Solve problems on the whiteboard, not via costly returns.*",
            "**HOUSE OF QUALITY (LITE)**\n\nA translation map connecting:\n* **Customer 'Whats':** 'Brace must be comfortable.'\n* **Engineering 'Hows':** 'Fabric Air Permeability > 100 CFM.'\n\nPrevents the 'Lost in Translation' gap between Marketing and Engineering.",
            "**VERIFICATION VS VALIDATION**\n\n* **Verification:** 'Did we build it RIGHT?' (Does it meet specs? Lab testing).\n* **Validation:** 'Did we build the RIGHT THING?' (Does it solve the user's problem? User testing).\n\n*Remember: Reactive = Problem Solving. Proactive = Problem Prevention.*"
        ]
    }
}

# ==============================================================================
# 3. STATE MANAGEMENT
# ==============================================================================
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'MENU'
if 'current_round' not in st.session_state:
    st.session_state.current_round = 1
if 'trivia_score' not in st.session_state:
    st.session_state.trivia_score = 0
if 'game_score' not in st.session_state:
    st.session_state.game_score = 0
if 'total_rounds' not in st.session_state:
    st.session_state.total_rounds = 3
if 'questions_asked' not in st.session_state:
    st.session_state.questions_asked = []
if 'q_queue' not in st.session_state:
    st.session_state.q_queue = []
if 'mode' not in st.session_state:
    st.session_state.mode = 'CAMPAIGN'
if 'slide_index' not in st.session_state:
    st.session_state.slide_index = 0
if 'current_deck' not in st.session_state:
    st.session_state.current_deck = 'leadership'

# HANDLE AUTOMATIC SCORE SYNC FROM JS GAME
if 'score' in st.query_params:
    try:
        incoming_score = int(st.query_params['score'])
        # Only process if score > 0 or we specifically expect a game end
        if st.session_state.game_state == 'GAME':
            st.session_state.game_score += incoming_score
            st.session_state.game_state = 'TRIVIA'
            
            # Prepare questions
            available = [q for q in TRIVIA_DB if q not in st.session_state.questions_asked]
            if len(available) < 3:
                st.session_state.questions_asked = [] 
                available = TRIVIA_DB
            st.session_state.q_queue = random.sample(available, 3)
            for q in st.session_state.q_queue:
                st.session_state.questions_asked.append(q)
    except:
        pass
    finally:
        st.query_params.clear()

# ==============================================================================
# 4. HTML5 GAME ENGINE (Permadeath & Asteroids)
# ==============================================================================
def get_game_html(round_num):
    difficulty = round_num * 0.5
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; overflow: hidden; background: transparent; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Orbitron', monospace; }}
        canvas {{ border: 2px solid #00e5ff; box-shadow: 0 0 30px #00e5ff; background: rgba(0,0,0,0.9); cursor: none; }}
        #overlay {{ position: absolute; color: #00e5ff; text-align: center; font-size: 24px; pointer-events: none; text-shadow: 0 0 10px #00e5ff; }}
    </style>
    </head>
    <body>
    <div id="overlay">
        <h2>SECTOR {round_num}</h2>
        <p>WARN: ASTEROID FIELD DETECTED</p>
        <p style="color:#ff0055">HULL INTEGRITY CRITICAL</p>
        <p style="font-size: 16px; color: #FFE81F; margin-top:20px;">CLICK TO ENGAGE</p>
    </div>
    <canvas id="gameCanvas" width="800" height="500"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const overlay = document.getElementById('overlay');
        
        let gameActive = false;
        let score = 0;
        let hull = 100;
        let timeLeft = 30; 
        
        const player = {{ x: 400, y: 450, width: 40, height: 40, color: '#00e5ff' }};
        let bullets = [];
        let enemies = [];
        let particles = [];
        let stars = [];

        // Starfield
        for(let i=0; i<100; i++) {{
            stars.push({{ x: Math.random() * canvas.width, y: Math.random() * canvas.height, size: Math.random() * 2, speed: Math.random() * 3 }});
        }}
        
        canvas.addEventListener('mousemove', (e) => {{
            const rect = canvas.getBoundingClientRect();
            player.x = e.clientX - rect.left;
            if(player.x < 0) player.x = 0;
            if(player.x > canvas.width) player.x = canvas.width;
        }});
        
        canvas.addEventListener('mousedown', () => {{
            if(!gameActive && hull > 0) {{
                gameActive = true;
                overlay.style.display = 'none';
                gameLoop();
                setInterval(spawnEnemy, 800 - ({difficulty} * 100)); 
                setInterval(updateTimer, 1000);
            }}
            if(gameActive) bullets.push({{ x: player.x, y: player.y, speed: 15 }});
        }});

        function spawnEnemy() {{
            if(!gameActive) return;
            const rand = Math.random();
            
            if(rand > 0.8) {{
                // ASTEROID (High Damage, Slow)
                enemies.push({{
                    x: Math.random() * (canvas.width - 50),
                    y: -50,
                    width: 50,
                    height: 50,
                    speed: 2,
                    type: 'ASTEROID',
                    hp: 3,
                    color: '#888888'
                }});
            }} else {{
                // DEFECT (Standard)
                enemies.push({{
                    x: Math.random() * (canvas.width - 30),
                    y: -30,
                    width: 30,
                    height: 30,
                    speed: 4 + ({difficulty}),
                    type: 'DEFECT',
                    hp: 1,
                    color: '#ff0055'
                }});
            }}
        }}

        function updateTimer() {{
            if(!gameActive) return;
            timeLeft--;
            if(timeLeft <= 0) endGame();
        }}

        function endGame() {{
            gameActive = false;
            window.parent.location.search = '?score=' + score;
        }}

        function gameLoop() {{
            if(!gameActive) return;
            requestAnimationFrame(gameLoop);
            
            // Draw BG
            ctx.fillStyle = 'rgba(0, 0, 0, 0.4)'; 
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Stars
            ctx.fillStyle = '#fff';
            stars.forEach(s => {{
                s.y += s.speed;
                if(s.y > canvas.height) s.y = 0;
                ctx.fillRect(s.x, s.y, s.size, s.size);
            }});
            
            // Player
            ctx.fillStyle = player.color;
            ctx.beginPath();
            ctx.moveTo(player.x, player.y);
            ctx.lineTo(player.x - 15, player.y + 40);
            ctx.lineTo(player.x + 15, player.y + 40);
            ctx.fill();
            
            // Bullets
            ctx.fillStyle = '#FFE81F';
            for(let i = bullets.length - 1; i >= 0; i--) {{
                let b = bullets[i];
                b.y -= b.speed;
                ctx.fillRect(b.x - 2, b.y, 4, 15);
                if(b.y < 0) bullets.splice(i, 1);
            }}
            
            // Enemies
            for(let i = enemies.length - 1; i >= 0; i--) {{
                let e = enemies[i];
                e.y += e.speed;
                
                ctx.fillStyle = e.color;
                if(e.type === 'ASTEROID') {{
                    ctx.beginPath();
                    ctx.arc(e.x + e.width/2, e.y + e.height/2, e.width/2, 0, Math.PI*2);
                    ctx.fill();
                }} else {{
                    ctx.fillRect(e.x, e.y, e.width, e.height);
                }}
                
                // Collision Player (Damage)
                if(Math.abs(player.x - (e.x + e.width/2)) < 30 && Math.abs(player.y - e.y) < 30) {{
                    hull -= (e.type === 'ASTEROID' ? 50 : 20);
                    createExplosion(e.x, e.y, '#ffaa00', 20);
                    enemies.splice(i, 1);
                    
                    if(hull <= 0) {{
                        gameActive = false;
                        // Reset logic handled by UI overlay usually, but here we auto-submit 0
                        alert("HULL BREACHED. MISSION FAILED.");
                        window.parent.location.search = '?score=0'; 
                    }}
                }}
                
                // Collision Bullet
                for(let j = bullets.length - 1; j >= 0; j--) {{
                    let b = bullets[j];
                    if(b.x > e.x && b.x < e.x + e.width && b.y < e.y + e.height && b.y > e.y) {{
                        e.hp--;
                        bullets.splice(j, 1);
                        createExplosion(b.x, b.y, '#fff', 5);
                        
                        if(e.hp <= 0) {{
                            score += (e.type === 'ASTEROID' ? 250 : 100);
                            createExplosion(e.x, e.y, e.color, 15);
                            enemies.splice(i, 1);
                        }}
                        break;
                    }}
                }}
                
                if(e.y > canvas.height) enemies.splice(i, 1);
            }}
            
            // Particles
            for(let i = particles.length - 1; i >= 0; i--) {{
                let p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.life--;
                ctx.fillStyle = p.color;
                ctx.fillRect(p.x, p.y, 2, 2);
                if(p.life <= 0) particles.splice(i, 1);
            }}
            
            // HUD
            ctx.fillStyle = '#00e5ff';
            ctx.font = '20px Orbitron';
            ctx.fillText('SCORE: ' + score, 20, 30);
            ctx.fillStyle = hull < 30 ? '#ff0055' : '#00ff00';
            ctx.fillText('HULL: ' + hull + '%', 20, 60);
            ctx.fillStyle = '#fff';
            ctx.fillText('TIME: ' + timeLeft, 700, 30);
        }}

        function createExplosion(x, y, color, count) {{
            for(let i = 0; i < count; i++) {{
                particles.push({{
                    x: x, y: y,
                    vx: (Math.random() - 0.5) * 10,
                    vy: (Math.random() - 0.5) * 10,
                    life: 20, color: color
                }});
            }}
        }}
    </script>
    </body>
    </html>
    """

# ==============================================================================
# 5. UI COMPONENTS
# ==============================================================================

def show_hud():
    st.markdown(f"""
    <div class="hud-container">
        <div class="metric-box">
            <div class="metric-label">SECTOR</div>
            <div class="metric-value">{st.session_state.current_round}/{st.session_state.total_rounds}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">XP (BATTLE)</div>
            <div class="metric-value">{st.session_state.game_score}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">INTEL (TRIVIA)</div>
            <div class="metric-value">{st.session_state.trivia_score}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_menu():
    st.markdown("# QUALITY WARS")
    st.markdown("<h4 style='text-align:center; color:#FFE81F; margin-top:-15px'>THE ROI STRIKES BACK</h4>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background:rgba(0,0,0,0.5); padding:20px; border:1px solid #333; border-radius:10px; margin-bottom:20px; text-align:center;">
            <p><strong>INCOMING TRANSMISSION:</strong></p>
            <p>Quality Control is not enough. We need Quality Assurance. Your mission is to master the strategy and eliminate defects.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚔️ START CAMPAIGN (GAME + QUIZ)"):
            st.session_state.mode = 'CAMPAIGN'
            st.session_state.game_state = 'INTEL'
            st.rerun()
            
        if st.button("🎓 OFFICER EXAM (QUIZ ONLY)"):
            st.session_state.mode = 'TRAINING'
            st.session_state.game_state = 'TRIVIA'
            # Load up queue immediately
            available = TRIVIA_DB.copy()
            st.session_state.q_queue = random.sample(available, 3)
            st.rerun()
            
        if st.button("📂 MISSION INTEL (PRESENTATIONS)"):
            st.session_state.game_state = 'VIEWER'
            st.rerun()

def show_viewer():
    """Interactive Slide Viewer"""
    st.markdown("## 📂 MISSION INTEL VIEWER")
    
    c1, c2 = st.columns([3, 1])
    with c1:
        deck_choice = st.selectbox("SELECT DATA TAPE:", 
                                 options=list(SLIDE_DECKS.keys()),
                                 format_func=lambda x: SLIDE_DECKS[x]['title'])
    
    if deck_choice != st.session_state.current_deck:
        st.session_state.current_deck = deck_choice
        st.session_state.slide_index = 0
        st.rerun()
        
    deck = SLIDE_DECKS[st.session_state.current_deck]
    total_slides = len(deck['slides'])
    
    # Slide Display
    st.markdown(f"""
    <div class="intel-viewer">
        <div class="intel-header">{deck['title']} | SLIDE {st.session_state.slide_index + 1}/{total_slides}</div>
        <div class="slide-content">{deck['slides'][st.session_state.slide_index]}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        if st.button("◀ PREV"):
            if st.session_state.slide_index > 0:
                st.session_state.slide_index -= 1
                st.rerun()
    with c3:
        if st.button("NEXT ▶"):
            if st.session_state.slide_index < total_slides - 1:
                st.session_state.slide_index += 1
                st.rerun()
                
    st.markdown("---")
    if st.button("RETURN TO MAIN MENU"):
        st.session_state.game_state = 'MENU'
        st.rerun()

def show_intel_briefing():
    st.markdown(f"## SECTOR {st.session_state.current_round}: BRIEFING")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("MISSION OBJECTIVE: Survive the asteroid field and eliminate non-conforming units. Prepare for knowledge check immediately following combat.")
    with col2:
        st.warning("HAZARD WARNING: Asteroids detected. Heavy damage upon impact. Dodge or destroy.")
        
    if st.button("INITIATE LAUNCH SEQUENCE"):
        st.session_state.game_state = 'GAME'
        st.rerun()

def show_trivia_round():
    st.markdown(f"## KNOWLEDGE CHECKPOINT: ROUND {st.session_state.current_round}")
    
    # Queue check
    if not st.session_state.q_queue:
        available = [q for q in TRIVIA_DB if q not in st.session_state.questions_asked]
        if len(available) < 3:
            available = TRIVIA_DB # Reset
        st.session_state.q_queue = random.sample(available, 3)

    with st.form("quiz_form"):
        score_delta = 0
        for i, q in enumerate(st.session_state.q_queue):
            st.markdown(f"**{i+1}. {q['q']}**")
            choice = st.radio(f"Options for {i}", q['options'], key=f"q{i}", label_visibility="collapsed")
            st.markdown("---")
            if choice == q['correct']:
                score_delta += 1
        
        if st.form_submit_button("SUBMIT ANSWERS"):
            st.session_state.trivia_score += score_delta
            
            # Show results briefly
            if score_delta == 3:
                st.balloons()
                st.success("PERFECT SCORE! INTEL SECURED.")
            else:
                st.info(f"RESULTS: {score_delta}/3 CORRECT.")
            
            time.sleep(2)
            
            # Advance
            if st.session_state.current_round < st.session_state.total_rounds:
                st.session_state.current_round += 1
                st.session_state.game_state = 'INTEL' if st.session_state.mode == 'CAMPAIGN' else 'TRIVIA'
                # Re-roll queue
                available = [q for q in TRIVIA_DB if q not in st.session_state.questions_asked]
                if len(available) < 3: available = TRIVIA_DB
                st.session_state.q_queue = random.sample(available, 3)
                st.rerun()
            else:
                st.session_state.game_state = 'GAMEOVER'
                st.rerun()

def show_gameover():
    st.markdown("# MISSION DEBRIEF")
    
    # Calc Score
    max_trivia = st.session_state.total_rounds * 3
    trivia_pct = (st.session_state.trivia_score / max_trivia) * 100
    game_pct = min((st.session_state.game_score / 3000) * 100, 100)
    
    if st.session_state.mode == 'TRAINING':
        final_score = trivia_pct
    else:
        final_score = (trivia_pct * 0.90) + (game_pct * 0.10)
    
    # Rank
    if final_score >= 90: rank, color = "JEDI MASTER", "#00ff00"
    elif final_score >= 70: rank, color = "QUALITY KNIGHT", "#00e5ff"
    else: rank, color = "PADAWAN LEARNER", "#ff0055"
    
    st.markdown(f"""
    <div style="text-align:center; padding:40px; border:2px solid {color}; border-radius:10px; background:rgba(0,0,0,0.8);">
        <h1 style="color:{color}; font-size:80px !important; margin:0;">{final_score:.1f}%</h1>
        <h2 style="color:{color}; letter-spacing:5px;">{rank}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**KNOWLEDGE:** {st.session_state.trivia_score}/{max_trivia}")
        st.progress(trivia_pct/100)
    with c2:
        if st.session_state.mode == 'CAMPAIGN':
            st.write(f"**COMBAT:** {st.session_state.game_score} PTS")
            st.progress(game_pct/100)

    st.markdown("---")
    if st.button("RESTART MISSION"):
        for k in ['current_round', 'trivia_score', 'game_score']: st.session_state[k] = 0
        st.session_state.current_round = 1
        st.session_state.questions_asked = []
        st.session_state.game_state = 'MENU'
        st.rerun()

# ==============================================================================
# 6. MAIN CONTROLLER
# ==============================================================================

show_hud()

if st.session_state.game_state == 'MENU':
    show_menu()
elif st.session_state.game_state == 'VIEWER':
    show_viewer()
elif st.session_state.game_state == 'INTEL':
    show_intel_briefing()
elif st.session_state.game_state == 'GAME':
    components.html(get_game_html(st.session_state.current_round), height=550)
elif st.session_state.game_state == 'TRIVIA':
    show_trivia_round()
elif st.session_state.game_state == 'GAMEOVER':
    show_gameover()
