import streamlit as st
import streamlit.components.v1 as components
import random
import time

# ==============================================================================
# 1. CONFIGURATION & ASSETS
# ==============================================================================
st.set_page_config(
    page_title="Quality Wars: Return of the ROI",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CUSTOM CSS: STARRY WARS THEME & ANIMATIONS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');

    /* COSMIC BACKGROUND ANIMATION */
    @keyframes move-twink-back {
        from {background-position:0 0;}
        to {background-position:-10000px 5000px;}
    }
    @keyframes twinkle {
        0% {opacity: 0.3;}
        50% {opacity: 1;}
        100% {opacity: 0.3;}
    }

    .stApp {
        background-color: #000;
        background-image: 
            radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 40px),
            radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 30px),
            radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 40px);
        background-size: 550px 550px, 350px 350px, 250px 250px;
        background-position: 0 0, 40px 60px, 130px 270px;
        font-family: 'Rajdhani', sans-serif;
        color: #e0e0e0;
    }

    /* TYPOGRAPHY */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    h1 {
        background: linear-gradient(180deg, #FFE81F 0%, #9B870C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 20px rgba(255, 232, 31, 0.5);
        text-align: center;
        font-weight: 900;
        font-size: 4rem !important;
        padding: 30px 0;
        margin-bottom: 0;
    }

    h2 { color: #00e5ff; text-shadow: 0 0 10px rgba(0, 229, 255, 0.5); }

    /* UI CARDS */
    .intel-viewer, .mission-card {
        background: rgba(16, 20, 24, 0.9);
        border: 1px solid #333;
        border-left: 5px solid #FFE81F;
        box-shadow: 0 0 30px rgba(0,0,0, 0.8);
        border-radius: 4px;
        padding: 30px;
        margin-bottom: 20px;
    }
    
    .mission-card:hover {
        border-color: #00e5ff;
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }

    /* BUTTONS */
    .stButton>button {
        font-family: 'Orbitron', sans-serif;
        background: transparent !important;
        color: #FFE81F !important;
        border: 2px solid #FFE81F !important;
        padding: 15px 25px;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        border-radius: 0px;
        clip-path: polygon(10% 0, 100% 0, 100% 70%, 90% 100%, 0 100%, 0 30%);
        width: 100%;
    }
    
    .stButton>button:hover {
        background: #FFE81F !important;
        color: #000 !important;
        box-shadow: 0 0 25px #FFE81F;
        transform: scale(1.05);
    }
    
    /* HUD METRICS */
    .hud-container {
        display: flex;
        justify-content: center;
        gap: 3rem;
        background: linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(0,229,255,0.1) 50%, rgba(0,0,0,0) 100%);
        border-top: 1px solid #00e5ff;
        border-bottom: 1px solid #00e5ff;
        padding: 10px;
        margin-bottom: 40px;
        margin-top: -20px;
    }
    
    .metric-box { text-align: center; }
    .metric-label { color: #00e5ff; font-size: 0.8rem; letter-spacing: 2px; font-family: 'Orbitron'; }
    .metric-value { color: #fff; font-size: 1.8rem; font-weight: bold; font-family: 'Orbitron'; text-shadow: 0 0 10px #00e5ff; }
    
    /* RADIO BUTTONS FOR QUIZ */
    .stRadio > div {
        background: rgba(255,255,255,0.05);
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CONTENT DATABASES (UPDATED)
# ==============================================================================

TRIVIA_DB = [
    # --- VIVE HISTORY & OPERATIONS ---
    {
        "id": 1,
        "q": "Vive Health operates how many strategic distribution centers across the US to ensure 1-2 day delivery?",
        "options": ["Four", "Two", "One", "Six"],
        "correct": "Four",
        "feedback": "Correct! Four centers allow 1-2 business day delivery across the US."
    },
    {
        "id": 2,
        "q": "What is the core advantage of Vive Health owning its own manufacturing facility?",
        "options": ["'Military Grade Standard' Quality Control", "Cheaper Labor", "Avoiding Tariffs", "Tax Loopholes"],
        "correct": "'Military Grade Standard' Quality Control",
        "feedback": "Correct. Owning manufacturing allows for superior QC standards."
    },
    {
        "id": 3,
        "q": "As of Oct 2025, the FBA Return Rate was slashed to what percentage (Goal < 7.50%)?",
        "options": ["5.54%", "10.2%", "2.1%", "0%"],
        "correct": "5.54%",
        "feedback": "Correct. This exceeded the goal significantly."
    },
    {
        "id": 4,
        "q": "Which regulatory marking is required to unlock the EU & UK markets?",
        "options": ["CE Mark", "ISO 13485", "FDA Clearance", "UL Listing"],
        "correct": "CE Mark",
        "feedback": "Correct. CE Mark is the requirement for market access, expanding TAM by +$150B."
    },
    
    # --- QUALITY TOOLS & STRATEGY ---
    {
        "id": 5,
        "q": "In FMEA (Failure Mode & Effects Analysis), what does RPN stand for?",
        "options": ["Risk Priority Number", "Rapid Prototype Number", "Real Problem Notification", "Return Percentage Net"],
        "correct": "Risk Priority Number",
        "feedback": "Correct. RPN helps prioritize which risks to fix first."
    },
    {
        "id": 6,
        "q": "What is the formula for calculating RPN?",
        "options": ["Severity x Occurrence x Detection", "Cost x Time x Scope", "Quality x Speed x Price", "Severity x Frequency x Budget"],
        "correct": "Severity x Occurrence x Detection",
        "feedback": "Correct. S x O x D = RPN."
    },
    {
        "id": 7,
        "q": "Which tool is used to trace a problem from 'What' is wrong to 'Why' it is happening (Root Cause)?",
        "options": ["Fishbone (Ishikawa) Diagram", "Pareto Chart", "Scatter Plot", "Control Chart"],
        "correct": "Fishbone (Ishikawa) Diagram",
        "feedback": "Correct. It analyzes Man, Machine, Material, Method, etc."
    },
    {
        "id": 8,
        "q": "In the RACI matrix, what does the 'A' stand for?",
        "options": ["Accountable", "Admin", "Action", "Advisor"],
        "correct": "Accountable",
        "feedback": "Correct. The person ultimately answerable for the task."
    },
    {
        "id": 9,
        "q": "According to the Kano Model, 'Delighters' are features that:",
        "options": ["Customers don't expect but love", "Customers demand as a baseline", "Increase cost but not value", "Are required by law"],
        "correct": "Customers don't expect but love",
        "feedback": "Correct. Like the 'Bluetooth speakers' example."
    },
    {
        "id": 10,
        "q": "What is the difference between Verification and Validation?",
        "options": ["Verification = Built it Right; Validation = Built the Right Thing", "Verification = User Testing; Validation = Lab Testing", "They are the same", "Validation is optional"],
        "correct": "Verification = Built it Right; Validation = Built the Right Thing",
        "feedback": "Correct. Verification checks specs. Validation checks user needs."
    },

    # --- TEAM & CULTURE ---
    {
        "id": 11,
        "q": "Who is the Retired PhD Chemist leading product testing at the Naples Office?",
        "options": ["Jim Ahearn", "Carolina Silva", "Annie", "Jason"],
        "correct": "Jim Ahearn",
        "feedback": "Correct. Jim leads research and testing."
    },
    {
        "id": 12,
        "q": "Which Core Value states: 'We take full responsibility... No excuses'?",
        "options": ["Extreme Ownership", "Growth Mindset", "Best Ideas Rise", "Data Driven"],
        "correct": "Extreme Ownership",
        "feedback": "Correct. We own the mission, not just the task."
    },
    
    # --- BUSINESS & ROI ---
    {
        "id": 13,
        "q": "Obtaining the CE Mark will unlock which major markets?",
        "options": ["EU & UK", "Asia Pacific", "South America", "Antarctica"],
        "correct": "EU & UK",
        "feedback": "Correct. This increases TAM by +$150B."
    },
    {
        "id": 14,
        "q": "In the TariffSight model, 'Landed Cost' includes:",
        "options": ["Production + Tariffs + Shipping + Storage + Fees", "MSRP - Profit", "Just Manufacturing Cost", "Shipping Cost only"],
        "correct": "Production + Tariffs + Shipping + Storage + Fees",
        "feedback": "Correct. Landed cost is the total cost to get product to the warehouse."
    },
    {
        "id": 15,
        "q": "What tool are we using to build custom analysis apps for free ('Vibe Coding')?",
        "options": ["Gemini / Claude", "ChatGPT / DALL-E", "Watson", "Siri"],
        "correct": "Gemini / Claude",
        "feedback": "Correct. AI is driving efficiency."
    },
    {
        "id": 16,
        "q": "The 'Post-Op Shoe' case study revealed that returns were high because:",
        "options": ["Shoes were 5-11% larger than competitors", "The fabric was tearing", "The velcro failed", "They were too expensive"],
        "correct": "Shoes were 5-11% larger than competitors",
        "feedback": "Correct. Data-driven resizing is now underway."
    },
    {
        "id": 17,
        "q": "What defines the 'B2B Return Rate' goal?",
        "options": ["< 2.00%", "< 5.00%", "< 1.00%", "0%"],
        "correct": "< 2.00%",
        "feedback": "Correct. We are currently around 2.29%, needing focus."
    },
    {
        "id": 18,
        "q": "What is a Project Charter used for?",
        "options": ["Defining problem, goal, scope, and team", "Calculating Taxes", "Ordering Pizza", " firing employees"],
        "correct": "Defining problem, goal, scope, and team",
        "feedback": "Correct. It is the 'Contract' for the project."
    },
    {
        "id": 19,
        "q": "What is 'Genchi Genbutsu'?",
        "options": ["Go and see (at the source)", "Continuous Improvement", "Respect for People", "Just in Time"],
        "correct": "Go and see (at the source)",
        "feedback": "Correct. We go to the factory or warehouse to understand the real problem."
    },
    {
        "id": 20,
        "q": "What is the main purpose of APQP (Advanced Product Quality Planning)?",
        "options": ["To build quality in from the start (Prevention)", "To inspect products at the end", "To negotiate prices", "To design logos"],
        "correct": "To build quality in from the start (Prevention)",
        "feedback": "Correct. Moving from reactive to proactive."
    }
]

SLIDE_DECKS = {
    "leadership": {
        "title": "Quality Leadership Presentation (Nov 2025)",
        "slides": [
            "**MISSION BRIEFING: QUALITY APPROVED**\n\n**THE SQUAD:**\n* **Carolina Silva:** Quality Analyst (Data/Biomedical).\n* **Annie:** QC Manager China (~25 Inspectors).\n* **Jim Ahearn:** Research & Testing (PhD Chemist).\n* **Luis Hidalgo:** CS Troubleshooting Specialist.\n* **Jason:** QC Lead at MPF (~7 Inspectors).\n* **Jessica Marshall:** Regulatory Affairs (ISO 13485).",
            "**THE OBJECTIVE: REVENUE GENERATION**\n\nQuality is not just a cost center. It is a revenue generator.\n\n* **Market Expansion:** CE Mark & ISO 13485 will >2x our TAM (Total Addressable Market) by unlocking EU & UK (+$150B market).\n* **Direct Revenue:** Developed memory foam seat cushion to offset costs.\n* **AI Efficiency:** Using Gemini/Claude ('Vibe Coding') to build custom apps for free.",
            "**STATUS REPORT: METRICS**\n\n* **FBA Return Rate:** 5.54% (Goal < 7.50%) - [EXCEEDING]\n* **B2B Return Rate:** 2.29% (Goal < 2.00%) - [NEEDS FOCUS]\n* **ISO 13485:** 42.5% Implementation Complete.\n* **VoC Health:** 77.61% Listings 'Good/Excellent'.",
            "**TACTICAL WIN: POST-OP SHOE**\n\n**Situation:** Returns were 20-40% due to 'size' complaints.\n**Action:** Analyzed competitors. Found our shoes were 5-11% larger than market leader.\n**Result:** Data-driven resizing initiated.\n\n*Lesson: Don't accept the status quo.*",
            "**CAUTIONARY TALE: THE PACKAGING MISTAKE**\n\n**Problem:** Switched to shrink wrap to save Amazon FBA fees.\n**Blowback:** Damaged B2B sales perception. Net negative for company.\n**Solution:** Cross-department sign-offs required. Don't optimize one metric at the expense of the whole."
        ]
    },
    "product_dev": {
        "title": "Product Dev Quality Strategies",
        "slides": [
            "**STRATEGY: START RIGHT**\n\n'How things start is how they'll go...'\n\n**The Toolkit:**\n1. Project Charter\n2. Risk Assessment\n3. Affinity Diagrams\n4. Kano Analysis\n5. FMEA",
            "**TOOL 1: PROJECT CHARTER**\n\nA living document. Defines:\n* **Problem Statement:** What is wrong (measured)?\n* **Business Case:** Why do we care?\n* **Goal:** What is the target?\n* **Scope:** What is IN and OUT?\n* **Team:** Who is fighting this battle?",
            "**TOOL 2: FMEA (Risk Analysis)**\n\n**Failure Mode & Effects Analysis**\n\nFormula: **Severity (S) x Occurrence (O) x Detection (D) = RPN**\n\n*Example:* Gel pad leak.\nS(9) x O(4) x D(7) = RPN 252.\n\n*Action:* Fix high RPNs on the whiteboard before you cut steel.",
            "**TOOL 3: KANO MODEL**\n\nPrioritize features:\n* **Basic Needs:** Must have (Breathable fabric).\n* **Performance:** More is better (Padding thickness).\n* **Delighters:** The 'Wow' factor (Bluetooth?).\n\n*Warning:* Don't waste budget on Delighters if Basic Needs aren't met.",
            "**VERIFICATION VS VALIDATION**\n\n* **Verification:** 'Did we build it RIGHT?' (Does it meet the specs? Lab Test).\n* **Validation:** 'Did we build the RIGHT THING?' (Does it solve the problem? User Test).\n\n*Goal:* Shift from Reactive Problem Solving to Proactive Prevention."
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
if 'questions_asked_ids' not in st.session_state:
    st.session_state.questions_asked_ids = []
if 'q_queue' not in st.session_state:
    st.session_state.q_queue = []
if 'mode' not in st.session_state:
    st.session_state.mode = 'CAMPAIGN' 
if 'slide_index' not in st.session_state:
    st.session_state.slide_index = 0
if 'current_deck' not in st.session_state:
    st.session_state.current_deck = 'leadership'
if 'mission_status' not in st.session_state:
    st.session_state.mission_status = 'ONGOING'
# SETTINGS
if 'game_duration_setting' not in st.session_state:
    st.session_state.game_duration_setting = 15 # Default to 15s for better gameplay

# --- SCORE SYNC LOGIC ---
if 'score' in st.query_params:
    try:
        incoming_score = int(st.query_params['score'])
        
        if st.session_state.game_state in ['GAME', 'BOXING_GAME']:
            # HANDLING DEATH / FAILURE
            if incoming_score == 0 and st.session_state.game_duration_setting != 9999:
                st.session_state.mission_status = 'FAILED'
                st.session_state.game_state = 'GAMEOVER'
            else:
                # SUCCESS or SURVIVAL END
                st.session_state.game_score += incoming_score
                st.session_state.game_state = 'TRIVIA'
                
                # Prepare questions (5 per round now)
                available = [q for q in TRIVIA_DB if q['id'] not in st.session_state.questions_asked_ids]
                
                # If we run out of unique questions, reset the pool but keep score
                if len(available) < 5:
                    st.session_state.questions_asked_ids = []
                    available = TRIVIA_DB
                
                st.session_state.q_queue = random.sample(available, min(5, len(available)))
                
    except Exception as e:
        pass
    finally:
        st.query_params.clear()

# ==============================================================================
# 4. GAME MODULES (OPTIMIZED JS)
# ==============================================================================
def get_space_shooter_html(round_num, duration):
    difficulty = round_num * 0.5
    is_survival = "true" if duration == 9999 else "false"
    time_label = "SURVIVAL" if duration == 9999 else str(duration)
    
    # JavaScript Game Engine
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; overflow: hidden; background: transparent; font-family: 'Courier New', monospace; }}
        canvas {{ display: block; margin: 0 auto; border: 2px solid #00e5ff; box-shadow: 0 0 20px rgba(0, 229, 255, 0.2); background: rgba(0,0,0,0.85); border-radius: 4px; }}
        #overlay {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #00e5ff; text-align: center; pointer-events: none; text-shadow: 0 0 10px #00e5ff; z-index: 10; width: 100%; }}
        h2 {{ font-size: 40px; margin: 0; letter-spacing: 5px; }}
        p {{ font-size: 18px; letter-spacing: 2px; }}
    </style>
    </head>
    <body>
    <div id="overlay">
        <h2>SECTOR {round_num}</h2>
        <p>MISSION: DEFEND QUALITY STANDARDS</p>
        <p style="color:#FFE81F; margin-top:20px; font-weight:bold; animation: blink 1s infinite;">CLICK TO ENGAGE</p>
    </div>
    <canvas id="gameCanvas" width="800" height="500"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const overlay = document.getElementById('overlay');
        
        let gameActive = false;
        let score = 0;
        let hull = 100;
        let timeLeft = {duration}; 
        let isSurvival = {is_survival};
        let lastTime = 0;
        let enemyTimer = 0;
        
        // Player
        const player = {{ x: 400, y: 450, width: 40, height: 40, color: '#00e5ff', speed: 5 }};
        
        // Entities
        let bullets = [];
        let enemies = [];
        let particles = [];
        let stars = [];

        // Initialize Stars
        for(let i=0; i<50; i++) {{
            stars.push({{ x: Math.random() * canvas.width, y: Math.random() * canvas.height, size: Math.random() * 2, speed: 0.5 + Math.random() * 2 }});
        }}
        
        // Input
        canvas.addEventListener('mousemove', (e) => {{
            const rect = canvas.getBoundingClientRect();
            player.x = e.clientX - rect.left;
        }});
        
        canvas.addEventListener('mousedown', () => {{
            if(!gameActive && hull > 0) {{
                gameActive = true;
                overlay.style.display = 'none';
                requestAnimationFrame(gameLoop);
                setInterval(() => {{ if(gameActive && !isSurvival) timeLeft--; }}, 1000);
            }}
            if(gameActive) bullets.push({{ x: player.x, y: player.y, speed: 10 }});
        }});

        function spawnEnemy() {{
            const rand = Math.random();
            // Increase difficulty by round
            let speedMulti = 1 + ({difficulty} * 0.2);
            
            if(rand > 0.70) {{
                enemies.push({{x: Math.random() * (canvas.width - 50), y: -50, width: 50, height: 50, speed: 2 * speedMulti, type: 'ASTEROID', hp: 3, color: '#888'}});
            }} else {{
                enemies.push({{x: Math.random() * (canvas.width - 30), y: -30, width: 30, height: 30, speed: 3 * speedMulti, type: 'DEFECT', hp: 1, color: '#ff0055'}});
            }}
        }}

        function gameLoop(timestamp) {{
            if(!gameActive) return;
            let dt = timestamp - lastTime;
            lastTime = timestamp;
            
            // Clear
            ctx.fillStyle = 'rgba(0, 0, 0, 0.3)'; 
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Stars
            ctx.fillStyle = '#fff';
            stars.forEach(s => {{ 
                s.y += s.speed; 
                if(s.y > canvas.height) s.y = 0; 
                ctx.globalAlpha = Math.random();
                ctx.fillRect(s.x, s.y, s.size, s.size);
                ctx.globalAlpha = 1.0;
            }});
            
            // Spawner
            enemyTimer += 16;
            if(enemyTimer > (800 - ({difficulty} * 100))) {{
                spawnEnemy();
                enemyTimer = 0;
            }}

            // Player
            ctx.save(); 
            ctx.translate(player.x, player.y); 
            ctx.fillStyle = player.color;
            ctx.beginPath(); 
            ctx.moveTo(0, -20); ctx.lineTo(-20, 20); ctx.lineTo(0, 10); ctx.lineTo(20, 20); 
            ctx.closePath(); ctx.fill();
            // Engine flame
            ctx.fillStyle = '#FFE81F';
            ctx.beginPath(); ctx.moveTo(-5, 15); ctx.lineTo(0, 30 + Math.random()*10); ctx.lineTo(5, 15); ctx.fill();
            ctx.restore();
            
            // Bullets
            ctx.fillStyle = '#FFE81F';
            for(let i = bullets.length - 1; i >= 0; i--) {{
                let b = bullets[i]; b.y -= b.speed; 
                ctx.fillRect(b.x - 2, b.y, 4, 15); 
                if(b.y < 0) bullets.splice(i, 1);
            }}
            
            // Enemies
            for(let i = enemies.length - 1; i >= 0; i--) {{
                let e = enemies[i]; e.y += e.speed;
                
                // Draw Enemy
                ctx.fillStyle = e.color;
                if(e.type === 'ASTEROID') {{ 
                    ctx.beginPath(); ctx.arc(e.x + e.width/2, e.y + e.height/2, e.width/2, 0, Math.PI*2); ctx.fill(); 
                }} else {{ 
                    ctx.fillRect(e.x, e.y, e.width, e.height); 
                }}
                
                // Collision Player
                let dx = player.x - (e.x + e.width/2);
                let dy = player.y - (e.y + e.height/2);
                let dist = Math.sqrt(dx*dx + dy*dy);
                
                if(dist < 30) {{
                    hull -= (e.type === 'ASTEROID' ? 30 : 15);
                    createExplosion(e.x, e.y, '#ffaa00', 20);
                    enemies.splice(i, 1);
                    if(hull <= 0) endGame(false);
                    continue;
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
                p.x += p.vx; p.y += p.vy; p.life--; 
                ctx.fillStyle = p.color; ctx.fillRect(p.x, p.y, 2, 2); 
                if(p.life <= 0) particles.splice(i, 1);
            }}
            
            // HUD
            ctx.fillStyle = '#00e5ff'; ctx.font = 'bold 20px monospace'; ctx.fillText('ROI: $' + score, 20, 30);
            
            // Hull Bar
            ctx.fillStyle = '#333'; ctx.fillRect(20, 45, 200, 15);
            ctx.fillStyle = hull < 30 ? '#ff0055' : '#00ff00'; ctx.fillRect(20, 45, hull * 2, 15);
            ctx.fillText('HULL', 230, 58);

            // Timer
            ctx.fillStyle = '#fff'; 
            let timerTxt = isSurvival ? "SURVIVAL" : timeLeft + "s";
            ctx.fillText(timerTxt, 700, 30);
            
            if(!isSurvival && timeLeft <= 0) endGame(true);

            requestAnimationFrame(gameLoop);
        }}

        function createExplosion(x, y, color, count) {{
            for(let i = 0; i < count; i++) {{ 
                particles.push({{ x: x, y: y, vx: (Math.random() - 0.5) * 10, vy: (Math.random() - 0.5) * 10, life: 10 + Math.random() * 10, color: color }}); 
            }}
        }}

        function endGame(success) {{
            gameActive = false;
            let finalScore = isSurvival ? score : (success ? score : 0);
            window.parent.location.search = '?score=' + finalScore; 
        }}
        
        // CSS for blinking text
        const style = document.createElement('style');
        style.innerHTML = `@keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}`;
        document.head.appendChild(style);
    </script>
    </body>
    </html>
    """

def get_boxing_html(round_num, duration):
    is_survival = "true" if duration == 9999 else "false"
    # FIX: Pre-calculate Python variables to avoid f-string syntax error
    cpu_start_hp = 9999 if duration == 9999 else 100 + (round_num * 25)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; overflow: hidden; background: #050505; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Courier New', monospace; }}
        canvas {{ border: 4px solid #FFE81F; box-shadow: 0 0 30px rgba(255, 232, 31, 0.2); background: linear-gradient(to bottom, #1a1a1a 0%, #000 100%); }}
        #overlay {{ position: absolute; color: #FFE81F; text-align: center; pointer-events: none; width: 100%; text-shadow: 2px 2px #000; }}
    </style>
    </head>
    <body>
    <div id="overlay">
        <h2 style="font-size:30px;">ROUND {round_num}</h2>
        <p style="font-size:14px; color:#ccc;">OPPONENT: THE AUDITOR</p>
        <p style="margin-top:10px; color:#00e5ff;">KEYS: [A] LEFT JAB | [S] RIGHT HOOK | [D] BLOCK</p>
        <p style="color:#FFE81F; font-weight:bold; margin-top:20px; animation: blink 1s infinite;">CLICK TO FIGHT</p>
    </div>
    <canvas id="gameCanvas" width="600" height="400"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const overlay = document.getElementById('overlay');
        
        let gameActive = false;
        let score = 0;
        let playerHP = 100;
        let cpuHP = {cpu_start_hp};
        let maxCpuHP = cpuHP;
        let stamina = 100;
        let timeLeft = {duration};
        let isSurvival = {is_survival};
        
        let action = 'IDLE';
        let cpuAction = 'IDLE';
        let message = '';
        let msgTimer = 0;
        let timerInterval;
        let cpuInterval;
        
        canvas.addEventListener('mousedown', () => {{
            if(!gameActive && playerHP > 0) {{
                gameActive = true;
                overlay.style.display = 'none';
                gameLoop();
                
                // Difficulty increases with rounds
                let thinkSpeed = Math.max(400, 1000 - ({round_num} * 100));
                
                cpuInterval = setInterval(cpuThink, thinkSpeed); 
                timerInterval = setInterval(updateTimer, 1000);
                window.addEventListener('keydown', handleInput);
            }}
        }});

        function handleInput(e) {{
            if(!gameActive || action !== 'IDLE') return; 
            
            let key = e.key.toLowerCase();
            if(key === 'a' && stamina >= 15) {{
                action = 'JAB'; stamina -= 15; checkHit(10 + ({round_num}*2), 0.8); 
                setTimeout(() => action = 'IDLE', 250);
            }} else if (key === 's' && stamina >= 35) {{
                action = 'HOOK'; stamina -= 35; checkHit(25 + ({round_num}*2), 0.5); 
                setTimeout(() => action = 'IDLE', 600);
            }} else if (key === 'd') {{
                action = 'BLOCK'; stamina = Math.min(100, stamina + 10); 
                setTimeout(() => action = 'IDLE', 400);
            }}
        }}

        function checkHit(dmg, accuracy) {{
            if(cpuAction === 'BLOCK') {{ 
                showMsg("BLOCKED!", '#ffff00'); 
                return; 
            }}
            if(Math.random() < accuracy) {{
                cpuHP -= dmg; score += dmg * 10; 
                showMsg("HIT!", '#00ff00');
                if(cpuHP <= 0) endGame(true);
            }} else {{ 
                showMsg("MISSED!", '#aaa'); 
            }}
        }}

        function showMsg(text, color) {{ message = text; msgTimer = 40; msgColor = color; }}
        let msgColor = '#fff';

        function cpuThink() {{
            if(!gameActive) return;
            const rand = Math.random();
            
            // AI Logic
            if(rand > 0.6) {{
                cpuAction = 'WINDUP';
                setTimeout(() => {{
                    if(!gameActive) return;
                    cpuAction = 'PUNCH';
                    // Damage calculation
                    if(action === 'BLOCK') {{ 
                        stamina = Math.min(100, stamina + 15); 
                        showMsg("BLOCKED!", '#00e5ff'); 
                    }} else {{ 
                        playerHP -= 10 + ({round_num} * 3); 
                        showMsg("OUCH!", '#ff0055'); 
                        if(playerHP <= 0) endGame(false); 
                    }}
                    setTimeout(() => cpuAction = 'IDLE', 400);
                }}, 400);
            }} else if (rand > 0.3) {{
                cpuAction = 'BLOCK'; 
                setTimeout(() => cpuAction = 'IDLE', 800);
            }}
        }}

        function updateTimer() {{
            if(!gameActive) return;
            stamina = Math.min(100, stamina + 5);
            if(!isSurvival) {{
                timeLeft--;
                if(timeLeft <= 0) endGame(true);
            }}
        }}

        function endGame(win) {{
            gameActive = false;
            clearInterval(timerInterval);
            clearInterval(cpuInterval);
            
            let finalScore = score;
            if (!isSurvival && !win) finalScore = 0;
            if (isSurvival) finalScore += 500; 
            else if (win) finalScore += 1000;
            
            window.parent.location.search = '?score=' + finalScore;
        }}

        function drawRect(x, y, w, h, color) {{ ctx.fillStyle = color; ctx.fillRect(x, y, w, h); }}

        function gameLoop() {{
            if(!gameActive) return;
            requestAnimationFrame(gameLoop);
            
            // BG
            drawRect(0, 0, 600, 400, '#111');
            
            // Floor
            var grd = ctx.createLinearGradient(0, 300, 0, 400);
            grd.addColorStop(0, "#222");
            grd.addColorStop(1, "#444");
            ctx.fillStyle = grd;
            ctx.fillRect(0, 300, 600, 100);
            
            // Ropes
            drawRect(0, 100, 600, 5, '#FFE81F');
            drawRect(0, 200, 600, 5, '#FFE81F');
            drawRect(0, 280, 600, 5, '#FFE81F');

            // CPU
            let cpuColor = '#ff00ff';
            if(cpuAction === 'BLOCK') cpuColor = '#666';
            if(cpuAction === 'WINDUP') cpuColor = '#ffa500';
            if(cpuAction === 'PUNCH') cpuColor = '#ff0000';
            
            // CPU Body
            drawRect(260, 120, 80, 180, cpuColor);
            // CPU Head
            drawRect(270, 70, 60, 50, cpuColor);
            
            // Player Hands
            if(action === 'JAB') drawRect(240, 160, 60, 40, '#00e5ff'); // Left extended
            else drawRect(200, 320, 50, 50, '#00e5ff'); // Left guard
            
            if(action === 'HOOK') drawRect(300, 150, 70, 60, '#00e5ff'); // Right huge
            else drawRect(350, 320, 50, 50, '#00e5ff'); // Right guard
            
            if(action === 'BLOCK') drawRect(220, 280, 160, 40, '#00e5ff');

            // UI
            ctx.font = 'bold 16px monospace'; ctx.fillStyle = '#fff';
            ctx.fillText("YOU: " + playerHP + "%", 20, 30);
            // Stamina Bar
            drawRect(20, 40, stamina * 1.5, 8, '#00e5ff');
            
            ctx.fillStyle = '#ff0055'; ctx.fillText("AUDITOR: " + cpuHP, 450, 30);

            ctx.fillStyle = '#FFE81F'; ctx.font = 'bold 40px monospace'; 
            let timeTxt = isSurvival ? "∞" : timeLeft;
            ctx.fillText(timeTxt, 280, 50);
            
            if(msgTimer > 0) {{
                ctx.font = 'bold 40px monospace'; ctx.fillStyle = msgColor; 
                ctx.fillText(message, 200, 200); 
                msgTimer--;
            }}
        }}
        
        // CSS for blinking text
        const style = document.createElement('style');
        style.innerHTML = `@keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}`;
        document.head.appendChild(style);
    </script>
    </body>
    </html>
    """

# ==============================================================================
# 6. UI COMPONENTS
# ==============================================================================

def show_sidebar():
    with st.sidebar:
        st.markdown("### 🛰️ MISSION CONTROL")
        
        # SETTINGS
        st.markdown("#### ⚙️ PROTOCOL SETTINGS")
        duration_mode = st.selectbox("GAME DURATION", 
                                    ["Quick Drill (15s)", "Standard (45s)", "Survival (Until Death)"],
                                    index=0)
        
        # Update state based on selection
        if "Quick" in duration_mode: st.session_state.game_duration_setting = 15
        elif "Standard" in duration_mode: st.session_state.game_duration_setting = 45
        else: st.session_state.game_duration_setting = 9999

        st.markdown("---")
        
        if st.button("🏠 MAIN MENU"):
            st.session_state.game_state = 'MENU'
            st.rerun()
        
        st.markdown("### MODULES")
        if st.button("🚀 SPACE CAMPAIGN"):
            st.session_state.mode = 'CAMPAIGN'
            st.session_state.game_state = 'INTEL'
            st.rerun()
            
        if st.button("🥊 BOXING GYM"):
            st.session_state.mode = 'BOXING'
            st.session_state.game_state = 'INTEL'
            st.rerun()
            
        if st.button("🎓 OFFICER EXAM"):
            st.session_state.mode = 'TRAINING'
            st.session_state.game_state = 'TRIVIA'
            # Reset trivia deck if empty
            if not st.session_state.q_queue:
                available = [q for q in TRIVIA_DB if q['id'] not in st.session_state.questions_asked_ids]
                st.session_state.q_queue = random.sample(available, min(5, len(available)))
            st.rerun()
            
        if st.button("📂 INTEL VIEWER"):
            st.session_state.game_state = 'VIEWER'
            st.rerun()
            
        st.markdown("---")
        st.caption("Quality Wars v5.0")

def show_menu():
    st.markdown("# QUALITY WARS")
    st.markdown("<h3 style='text-align:center; color:#00e5ff; margin-top:-20px; letter-spacing: 8px;'>RETURN OF THE ROI</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background:rgba(0,20,40,0.8); padding:30px; border:1px solid #00e5ff; border-top: 5px solid #FFE81F; border-radius:4px; margin-bottom:30px; text-align:center; box-shadow: 0 0 50px rgba(0,229,255,0.1);">
            <p style="color: #ccc; font-size: 1.2rem; line-height: 1.6;">
                The galaxy is plagued by <b>defects</b> and <b>inefficiency</b>. 
                <br><br>
                As a Quality Officer, you must master the archives of <b>ISO 13485</b>, 
                battle the <b>Audit Droids</b>, and secure the <b>Profit Margin</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 START CAMPAIGN", key="btn_camp"):
                st.session_state.mode = 'CAMPAIGN'
                st.session_state.game_state = 'INTEL'
                st.rerun()
        with c2:    
            if st.button("🥊 BOXING GYM", key="btn_box"):
                st.session_state.mode = 'BOXING'
                st.session_state.game_state = 'INTEL'
                st.rerun()
        
        if st.button("📂 REVIEW MISSION INTEL", key="btn_intel"):
            st.session_state.game_state = 'VIEWER'
            st.rerun()

def show_viewer():
    st.markdown("## 📂 CLASSIFIED INTEL VIEWER")
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
    
    st.markdown(f"""
    <div class="intel-viewer">
        <h3 style="border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 20px; color: #FFE81F;">{deck['title']} // PAGE {st.session_state.slide_index + 1}</h3>
        <div style="font-size: 1.3rem; line-height: 1.8; color: #ddd; white-space: pre-wrap;">{deck['slides'][st.session_state.slide_index]}</div>
    </div>
    """, unsafe_allow_html=True)
    
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

def show_intel_briefing():
    dur = st.session_state.game_duration_setting
    dur_txt = "UNTIL DEATH" if dur == 9999 else f"{dur} SECONDS"
    
    if st.session_state.mode == 'CAMPAIGN':
        title = f"SECTOR {st.session_state.current_round} BRIEFING"
        msg1 = f"**OBJECTIVE:** Survive the asteroid field for **{dur_txt}**."
        msg2 = "**THREAT:** Heavy Asteroids & Defects. 100% Hull Loss = Failure."
        btn = "INITIATE LAUNCH SEQUENCE"
    else:
        title = f"ROUND {st.session_state.current_round} WEIGH-IN"
        msg1 = f"**OBJECTIVE:** Defeat The Auditor in **{dur_txt}**."
        msg2 = "**CONTROLS:** [A] Left Jab, [S] Right Hook, [D] Block."
        btn = "STEP INTO THE RING"

    st.markdown(f"## {title}")
    
    st.markdown(f"""
    <div class="mission-card">
        <h3 style="color: #FFE81F;">COMMANDER'S NOTE:</h3>
        <p style="font-size: 1.2rem;">
            "We do not rise to the level of our expectations. We fall to the level of our training."
            <br><br>
            Review the Intel if you are unsure of the protocols. Knowledge is your best weapon.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1: 
        st.info(msg1)
    with col2: 
        st.warning(msg2)
    
    st.write("")
    if st.button(btn, type="primary"):
        st.session_state.game_state = 'GAME' if st.session_state.mode == 'CAMPAIGN' else 'BOXING_GAME'
        st.rerun()

def show_trivia_round():
    st.markdown(f"## KNOWLEDGE CHECKPOINT: ROUND {st.session_state.current_round}")
    
    # Ensure queue is populated
    if not st.session_state.q_queue:
        available = [q for q in TRIVIA_DB if q['id'] not in st.session_state.questions_asked_ids]
        if len(available) < 5: 
            st.session_state.questions_asked_ids = [] # Reshuffle deck
            available = TRIVIA_DB
        st.session_state.q_queue = random.sample(available, min(5, len(available)))

    # Display Score so far
    st.progress(st.session_state.trivia_score / (st.session_state.total_rounds * 5) if st.session_state.total_rounds > 0 else 0)

    with st.form("quiz_form"):
        score_delta = 0
        for i, q in enumerate(st.session_state.q_queue):
            st.markdown(f"##### {i+1}. {q['q']}")
            
            # Randomized options logic (stable per render)
            opts = q['options'].copy()
            # Simple shuffle based on Q text to keep it consistent during interaction
            random.seed(q['q']) 
            random.shuffle(opts)
            random.seed() # Reset seed
            
            choice = st.radio(f"Select Answer:", opts, key=f"q_{st.session_state.current_round}_{i}", label_visibility="collapsed")
            
            # Check answer logic happens AFTER submit in the logic block below, 
            # but we need to store the choice to check it.
            
            st.markdown("---")
        
        if st.form_submit_button("SUBMIT ANSWERS"):
            # Calculate score
            correct_count = 0
            for i, q in enumerate(st.session_state.q_queue):
                user_choice = st.session_state.get(f"q_{st.session_state.current_round}_{i}")
                if user_choice == q['correct']:
                    correct_count += 1
                    st.toast(f"✅ Q{i+1} Correct!", icon="🎉")
                else:
                    st.toast(f"❌ Q{i+1} Wrong. Answer: {q['correct']}", icon="⚠️")
                
                # Mark question as asked
                if q['id'] not in st.session_state.questions_asked_ids:
                    st.session_state.questions_asked_ids.append(q['id'])

            st.session_state.trivia_score += correct_count
            
            time.sleep(2) # Give user time to read toasts
            
            if st.session_state.current_round < st.session_state.total_rounds:
                st.session_state.current_round += 1
                # Next state logic
                next_state = 'TRIVIA' if st.session_state.mode == 'TRAINING' else 'INTEL'
                st.session_state.game_state = next_state
                # Clear queue for next round to force re-roll
                st.session_state.q_queue = []
                st.rerun()
            else:
                st.session_state.mission_status = 'SUCCESS'
                st.session_state.game_state = 'GAMEOVER'
                st.rerun()

def show_gameover():
    # Handling Mission Failed (Death) vs Mission Complete
    if st.session_state.mission_status == 'FAILED':
        st.markdown("# 💀 MISSION FAILED")
        st.markdown("""
        <div style="text-align:center; padding:40px; border:2px solid #ff0055; border-radius:4px; background:rgba(50,0,0,0.5);">
            <h1 style="color:#ff0055; font-size:40px !important; margin:0;">CRITICAL FAILURE</h1>
            <p style="font-size: 1.2rem; margin-top: 20px;">Your department has been shut down due to excessive defects.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("RESET SIMULATION", type="primary"):
            for k in ['current_round', 'trivia_score', 'game_score']: st.session_state[k] = 0
            st.session_state.questions_asked_ids = []
            st.session_state.mission_status = 'ONGOING'
            st.session_state.game_state = 'MENU'
            st.rerun()
        return

    # Standard Scoring
    st.markdown("# MISSION DEBRIEF")
    max_trivia = st.session_state.total_rounds * 5 # 5 qs per round
    trivia_pct = (st.session_state.trivia_score / max_trivia) * 100 if max_trivia > 0 else 0
    
    if st.session_state.game_duration_setting == 9999:
         game_text = f"{st.session_state.game_score} (SURVIVAL)"
    else:
         game_text = f"{st.session_state.game_score}"

    if st.session_state.mode == 'TRAINING':
        final_score = trivia_pct
    else:
        # Weighted score
        game_pct = min((st.session_state.game_score / 3000) * 100, 100)
        final_score = (trivia_pct * 0.60) + (game_pct * 0.40)
    
    # Rank
    if final_score >= 90: rank, color = "JEDI MASTER", "#00ff00"
    elif final_score >= 70: rank, color = "QUALITY KNIGHT", "#00e5ff"
    elif final_score >= 50: rank, color = "PADAWAN", "#FFE81F"
    else: rank, color = "JAR JAR BINKS", "#ff0055"
    
    st.markdown(f"""
    <div style="text-align:center; padding:40px; border:2px solid {color}; border-radius:10px; background:rgba(0,0,0,0.8); box-shadow: 0 0 50px {color}40;">
        <h1 style="color:{color}; font-size:80px !important; margin:0;">{final_score:.1f}%</h1>
        <h2 style="color:{color}; letter-spacing:5px; font-family:'Orbitron';">{rank}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### KNOWLEDGE")
        st.write(f"**Score:** {st.session_state.trivia_score}/{max_trivia}")
        st.progress(trivia_pct/100)
    with c2:
        if st.session_state.mode != 'TRAINING':
            st.markdown("### SKILLS")
            st.write(f"**Combat Score:** {game_text}")

    st.markdown("---")
    if st.button("START NEW CAMPAIGN", type="primary"):
        for k in ['current_round', 'trivia_score', 'game_score']: st.session_state[k] = 0
        st.session_state.current_round = 1
        st.session_state.questions_asked_ids = []
        st.session_state.mission_status = 'ONGOING'
        st.session_state.game_state = 'MENU'
        st.rerun()

# ==============================================================================
# 7. MAIN CONTROLLER
# ==============================================================================

show_sidebar()

# HUD (Skip on Menu/Gameover/Viewer)
if st.session_state.game_state not in ['MENU', 'GAMEOVER', 'VIEWER']:
    st.markdown(f"""
    <div class="hud-container">
        <div class="metric-box"><div class="metric-label">ROUND</div><div class="metric-value">{st.session_state.current_round}/{st.session_state.total_rounds}</div></div>
        <div class="metric-box"><div class="metric-label">ROI SCORE</div><div class="metric-value">${st.session_state.game_score}</div></div>
        <div class="metric-box"><div class="metric-label">INTEL</div><div class="metric-value">{st.session_state.trivia_score}</div></div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.game_state == 'MENU':
    show_menu()
elif st.session_state.game_state == 'VIEWER':
    show_viewer()
elif st.session_state.game_state == 'INTEL':
    show_intel_briefing()
elif st.session_state.game_state == 'GAME':
    # Space Shooter
    html_code = get_space_shooter_html(st.session_state.current_round, st.session_state.game_duration_setting)
    components.html(html_code, height=550)
elif st.session_state.game_state == 'BOXING_GAME':
    # Boxing
    html_code = get_boxing_html(st.session_state.current_round, st.session_state.game_duration_setting)
    components.html(html_code, height=450)
elif st.session_state.game_state == 'TRIVIA':
    show_trivia_round()
elif st.session_state.game_state == 'GAMEOVER':
    show_gameover()
