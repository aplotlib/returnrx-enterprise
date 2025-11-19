import streamlit as st
import streamlit.components.v1 as components
import random
import time

# ==============================================================================
# 1. CONFIGURATION & ASSETS
# ==============================================================================
st.set_page_config(
    page_title="Quality Wars: The ROI Strikes Back",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS: NEON/SPACE THEME
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto:wght@300;400;700&family=Press+Start+2P&display=swap');

    /* MAIN THEME */
    .stApp {
        background-color: #050505;
        background-image: 
            linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)),
            url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
        font-family: 'Roboto', sans-serif;
        color: #e0e0e0;
    }

    /* TYPOGRAPHY */
    h1, h2, h3, h4 {
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: #00e5ff;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
    }
    
    h1 {
        background: -webkit-linear-gradient(#FFE81F, #D4AF37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 20px rgba(255, 232, 31, 0.3);
        text-align: center;
        font-weight: 900;
        font-size: 3.5rem !important;
        padding-bottom: 20px;
    }

    /* BUTTONS */
    .stButton>button {
        font-family: 'Orbitron', sans-serif;
        background: rgba(0, 20, 40, 0.8) !important;
        color: #00e5ff !important;
        border: 1px solid #00e5ff !important;
        padding: 15px 25px;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
        text-transform: uppercase;
        border-radius: 4px;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.2);
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.02);
        background: #00e5ff !important;
        color: #000 !important;
        box-shadow: 0 0 30px rgba(0, 229, 255, 0.6);
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: rgba(5, 5, 10, 0.95);
        border-right: 1px solid #333;
    }

    /* HUD */
    .hud-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        background: rgba(0,0,0,0.8);
        border: 1px solid #333;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 30px;
        backdrop-filter: blur(10px);
    }
    
    .metric-box {
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        min-width: 120px;
    }
    .metric-label { color: #888; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }
    .metric-value { color: #FFE81F; font-size: 1.8rem; font-weight: bold; text-shadow: 0 0 10px rgba(255, 232, 31, 0.5); }
    
    /* INTEL VIEWER */
    .intel-viewer {
        background: rgba(16, 20, 24, 0.95);
        border: 1px solid #00e5ff;
        box-shadow: inset 0 0 50px rgba(0, 229, 255, 0.1);
        border-radius: 4px;
        padding: 40px;
        min-height: 500px;
        position: relative;
    }
    
    .intel-viewer::before {
        content: "TOP SECRET // VIVE HEALTH // QUALITY DIV";
        position: absolute;
        top: 10px;
        left: 20px;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.7rem;
        color: rgba(0, 229, 255, 0.5);
    }

    .slide-content {
        font-size: 1.1rem;
        line-height: 1.8;
        white-space: pre-wrap; 
        font-family: 'Roboto', sans-serif;
        color: #ccc;
    }
    
    .slide-content strong {
        color: #fff;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CONTENT DATABASES
# ==============================================================================

TRIVIA_DB = [
    # --- VIVE HISTORY & STRATEGY ---
    {
        "q": "Vive Health operates how many strategic distribution centers across the US to ensure 1-2 day delivery?",
        "options": ["Four", "Two", "One", "Six"],
        "correct": "Four",
        "feedback": "Correct! This infrastructure allows for rapid replacement of defects."
    },
    {
        "q": "What is the core advantage of Vive Health owning its own manufacturing facility?",
        "options": ["'Military Grade Standard' Quality Control", "Cheaper Labor", "Avoiding Tariffs", "None of the above"],
        "correct": "'Military Grade Standard' Quality Control",
        "feedback": "Correct. Ownership allows for direct oversight and 'Military Grade' standards."
    },
    {
        "q": "In Oct 2025, the FBA Return Rate was slashed to what percentage, exceeding the 7.50% goal?",
        "options": ["5.54%", "10.2%", "2.1%", "0%"],
        "correct": "5.54%",
        "feedback": "Correct. A massive win for the quality team, down from higher averages."
    },
    # --- TEAM & CULTURE ---
    {
        "q": "Who is the Retired PhD Chemist leading product testing at the Naples Office?",
        "options": ["Jim Ahearn", "Carolina Silva", "Annie", "Jason"],
        "correct": "Jim Ahearn",
        "feedback": "Correct. Jim leads research and testing."
    },
    {
        "q": "Who manages the team of ~25 QC Inspectors on the ground in China?",
        "options": ["Annie", "Jessica", "Luis", "Tom"],
        "correct": "Annie",
        "feedback": "Correct. Annie is the QC Manager in China."
    },
    {
        "q": "Which Core Value states: 'We take full responsibility... No excuses'?",
        "options": ["Extreme Ownership", "Growth Mindset", "Best Ideas Rise", "Data Driven"],
        "correct": "Extreme Ownership",
        "feedback": "Correct. We own the mission, not just the task."
    },
    # --- QUALITY TOOLS ---
    {
        "q": "In a Project Charter, what section captures the issue in the form of a measurement?",
        "options": ["Problem Statement", "Business Case", "Goal Statement", "Timeline"],
        "correct": "Problem Statement",
        "feedback": "Correct. You can't fix what you can't measure."
    },
    {
        "q": "According to the Kano Model, features that customers don't expect but love are called:",
        "options": ["Delighters/Excitement Attributes", "Basic Needs", "Performance Attributes", "Threshold Attributes"],
        "correct": "Delighters/Excitement Attributes",
        "feedback": "Correct. Like the 'Bluetooth speakers' example (though check if they add value!)."
    },
    {
        "q": "Which tool helps move from 'What' is wrong to 'Why' it is happening (Root Cause)?",
        "options": ["Fishbone Diagram (Ishikawa)", "Pareto Chart", "Scatter Plot", "Control Chart"],
        "correct": "Fishbone Diagram (Ishikawa)",
        "feedback": "Correct. It traces problems to Man, Machine, Material, Method, etc."
    },
    {
        "q": "In FMEA, what is the formula for the Risk Priority Number (RPN)?",
        "options": ["Severity x Occurrence x Detection", "Cost x Time x Scope", "Quality x Speed x Price", "Severity x Frequency x Budget"],
        "correct": "Severity x Occurrence x Detection",
        "feedback": "Correct. S x O x D = RPN. High RPNs get fixed first."
    },
    # --- TARIFFS & COSTS ---
    {
        "q": "In the TariffSight model, what defines the 'Landed Cost'?",
        "options": ["Production + Tariffs + Shipping + Storage + Fees", "MSRP - Profit", "Just Manufacturing Cost", "Shipping Cost only"],
        "correct": "Production + Tariffs + Shipping + Storage + Fees",
        "feedback": "Correct. Landed cost includes every expense to get the product to the warehouse."
    },
    {
        "q": "What is 'Verification' vs 'Validation'?",
        "options": ["Verification = Built it Right; Validation = Built the Right Thing", "Verification = User Testing; Validation = Lab Testing", "They are the same", "Verification is optional"],
        "correct": "Verification = Built it Right; Validation = Built the Right Thing",
        "feedback": "Correct. Verification checks specs. Validation checks user needs."
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
if 'mission_status' not in st.session_state:
    st.session_state.mission_status = 'ONGOING'

# --- ROBUST SCORE SYNC LOGIC ---
# This captures the score passed from the JS games via URL parameters
if 'score' in st.query_params:
    try:
        incoming_score = int(st.query_params['score'])
        
        # Handle Game Loop Logic
        if st.session_state.game_state in ['GAME', 'BOXING_GAME']:
            if incoming_score == 0:
                # Death Condition
                st.session_state.mission_status = 'FAILED'
                st.session_state.game_state = 'GAMEOVER'
            else:
                # Success Condition
                st.session_state.game_score += incoming_score
                st.session_state.game_state = 'TRIVIA'
                
                # Prepare questions for the upcoming trivia round
                available = [q for q in TRIVIA_DB if q not in st.session_state.questions_asked]
                if len(available) < 3: 
                    st.session_state.questions_asked = [] 
                    available = TRIVIA_DB
                st.session_state.q_queue = random.sample(available, 3)
                
    except Exception as e:
        st.error(f"Comms Error: {e}")
    finally:
        # Clear params to prevent state loops
        st.query_params.clear()

# ==============================================================================
# 4. GAME MODULES (HTML/JS)
# ==============================================================================
def get_space_shooter_html(round_num):
    difficulty = round_num * 0.8
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; overflow: hidden; background: transparent; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Orbitron', monospace; }}
        canvas {{ border: 2px solid #00e5ff; box-shadow: 0 0 20px rgba(0, 229, 255, 0.4); background: rgba(0,0,0,0.85); cursor: none; border-radius: 8px; }}
        #overlay {{ position: absolute; color: #00e5ff; text-align: center; font-size: 24px; pointer-events: none; text-shadow: 0 0 10px #00e5ff; z-index: 10; }}
    </style>
    </head>
    <body>
    <div id="overlay">
        <h2 style="margin:0; font-size: 40px;">SECTOR {round_num}</h2>
        <p style="letter-spacing: 2px;">PROTECT THE SUPPLY CHAIN</p>
        <p style="color:#ff0055; font-weight:bold;">CLICK TO ENGAGE</p>
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
        
        // Input Handling
        canvas.addEventListener('mousemove', (e) => {{
            const rect = canvas.getBoundingClientRect();
            player.x = e.clientX - rect.left;
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
            if(rand > 0.70) {{
                // Asteroid (Process Failure)
                enemies.push({{x: Math.random() * (canvas.width - 50), y: -50, width: 50, height: 50, speed: 2 + ({difficulty}*0.5), type: 'ASTEROID', hp: 3, color: '#888888', label: 'RISK'}});
            }} else {{
                // Defect (Fast)
                enemies.push({{x: Math.random() * (canvas.width - 30), y: -30, width: 30, height: 30, speed: 4 + ({difficulty}), type: 'DEFECT', hp: 1, color: '#ff0055', label: 'DEFECT'}});
            }}
        }}

        function updateTimer() {{
            if(!gameActive) return;
            timeLeft--;
            if(timeLeft <= 0) endGame();
        }}

        function endGame() {{
            gameActive = false;
            // Send score back to Streamlit
            window.parent.location.search = '?score=' + score;
        }}

        function gameLoop() {{
            if(!gameActive) return;
            requestAnimationFrame(gameLoop);
            
            // Clear
            ctx.fillStyle = 'rgba(0, 0, 0, 0.3)'; 
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Player
            ctx.fillStyle = player.color;
            ctx.beginPath(); ctx.moveTo(player.x, player.y); ctx.lineTo(player.x - 15, player.y + 40); ctx.lineTo(player.x + 15, player.y + 40); ctx.fill();
            
            // Bullets
            ctx.fillStyle = '#FFE81F';
            for(let i = bullets.length - 1; i >= 0; i--) {{
                let b = bullets[i]; b.y -= b.speed; ctx.fillRect(b.x - 2, b.y, 4, 15); 
                if(b.y < 0) bullets.splice(i, 1);
            }}
            
            // Enemies
            for(let i = enemies.length - 1; i >= 0; i--) {{
                let e = enemies[i]; e.y += e.speed;
                ctx.fillStyle = e.color;
                if(e.type === 'ASTEROID') {{ 
                    ctx.beginPath(); ctx.arc(e.x + e.width/2, e.y + e.height/2, e.width/2, 0, Math.PI*2); ctx.fill(); 
                }} else {{ 
                    ctx.fillRect(e.x, e.y, e.width, e.height); 
                }}
                
                // Collision with Player
                if(Math.abs(player.x - (e.x + e.width/2)) < 30 && Math.abs(player.y - e.y) < 30) {{
                    hull -= (e.type === 'ASTEROID' ? 40 : 20);
                    createExplosion(e.x, e.y, '#ffaa00', 20);
                    enemies.splice(i, 1);
                    if(hull <= 0) {{
                        gameActive = false;
                        window.parent.location.search = '?score=0'; 
                    }}
                }}
                
                // Collision with Bullets
                for(let j = bullets.length - 1; j >= 0; j--) {{
                    let b = bullets[j];
                    if(b.x > e.x - 10 && b.x < e.x + e.width + 10 && b.y < e.y + e.height && b.y > e.y) {{
                        e.hp--; bullets.splice(j, 1); 
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
                let p = particles[i]; p.x += p.vx; p.y += p.vy; p.life--; ctx.fillStyle = p.color; ctx.fillRect(p.x, p.y, 2, 2); 
                if(p.life <= 0) particles.splice(i, 1);
            }}
            
            // HUD
            ctx.fillStyle = '#00e5ff'; ctx.font = '20px Orbitron'; ctx.fillText('ROI: $' + score, 20, 30);
            ctx.fillStyle = hull < 30 ? '#ff0055' : '#00ff00'; ctx.fillText('HULL: ' + hull + '%', 20, 60);
            ctx.fillStyle = '#fff'; ctx.fillText('T-MINUS: ' + timeLeft, 650, 30);
        }}

        function createExplosion(x, y, color, count) {{
            for(let i = 0; i < count; i++) {{ 
                particles.push({{ x: x, y: y, vx: (Math.random() - 0.5) * 10, vy: (Math.random() - 0.5) * 10, life: 10 + Math.random() * 10, color: color }}); 
            }}
        }}
    </script>
    </body>
    </html>
    """

def get_boxing_html(round_num):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; overflow: hidden; background: #111; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Press Start 2P', cursive; }}
        canvas {{ border: 4px solid #FFD700; box-shadow: 0 0 30px #FFD700; background: linear-gradient(to bottom, #202020 0%, #000 100%); }}
        #overlay {{ position: absolute; color: #FFD700; text-align: center; font-size: 20px; pointer-events: none; text-shadow: 2px 2px #000; width: 100%; }}
    </style>
    </head>
    <body>
    <div id="overlay">
        <h2>ROUND {round_num}</h2>
        <p>OPPONENT: THE AUDITOR</p>
        <p style="font-size:12px; color:#aaa; margin-top:20px;">KEYS: [A] JAB | [S] HAYMAKER | [D] BLOCK</p>
        <p style="color:#00e5ff; margin-top:20px;">CLICK TO FIGHT</p>
    </div>
    <canvas id="gameCanvas" width="600" height="400"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const overlay = document.getElementById('overlay');
        
        let gameActive = false;
        let score = 0;
        let playerHP = 100;
        let cpuHP = 100 + ({round_num} * 20);
        let stamina = 100;
        let timeLeft = 60;
        let action = 'IDLE';
        let cpuAction = 'IDLE';
        let message = '';
        
        canvas.addEventListener('mousedown', () => {{
            if(!gameActive && playerHP > 0) {{
                gameActive = true;
                overlay.style.display = 'none';
                gameLoop();
                setInterval(cpuThink, 1000 - ({round_num} * 50)); 
                setInterval(updateTimer, 1000);
                window.addEventListener('keydown', handleInput);
            }}
        }});

        function handleInput(e) {{
            if(!gameActive) return;
            if(action !== 'IDLE') return; 
            
            if(e.key.toLowerCase() === 'a' && stamina >= 10) {{
                action = 'JAB'; stamina -= 10; checkHit(10, 0.8);
                setTimeout(() => action = 'IDLE', 200);
            }} else if (e.key.toLowerCase() === 's' && stamina >= 30) {{
                action = 'HAYMAKER'; stamina -= 30; checkHit(30, 0.4);
                setTimeout(() => action = 'IDLE', 600);
            }} else if (e.key.toLowerCase() === 'd') {{
                action = 'BLOCK'; stamina = Math.min(100, stamina + 5);
                setTimeout(() => action = 'IDLE', 300);
            }}
        }}

        function checkHit(dmg, accuracy) {{
            if(cpuAction === 'BLOCK') {{ message = "BLOCKED!"; return; }}
            if(Math.random() < accuracy) {{
                cpuHP -= dmg; score += dmg * 10; message = "HIT!";
                if(cpuHP <= 0) endGame(true);
            }} else {{ message = "MISSED!"; }}
        }}

        function cpuThink() {{
            if(!gameActive) return;
            const rand = Math.random();
            if(rand > 0.6) {{
                cpuAction = 'PUNCH';
                if(action === 'BLOCK') {{
                    stamina = Math.min(100, stamina + 10); message = "YOU BLOCKED!";
                }} else {{
                    playerHP -= 10 + ({round_num} * 2); message = "OUCH!";
                    if(playerHP <= 0) endGame(false);
                }}
                setTimeout(() => cpuAction = 'IDLE', 400);
            }} else if (rand > 0.3) {{
                cpuAction = 'BLOCK'; setTimeout(() => cpuAction = 'IDLE', 600);
            }}
        }}

        function updateTimer() {{
            if(!gameActive) return;
            timeLeft--; stamina = Math.min(100, stamina + 5);
            if(timeLeft <= 0) endGame(true);
        }}

        function endGame(win) {{
            gameActive = false;
            const finalScore = win ? score + 1000 : 0;
            window.parent.location.search = '?score=' + finalScore;
        }}

        function drawRect(x, y, w, h, color) {{ ctx.fillStyle = color; ctx.fillRect(x, y, w, h); }}

        function gameLoop() {{
            if(!gameActive) return;
            requestAnimationFrame(gameLoop);
            drawRect(0, 0, 600, 400, '#222');
            
            // Draw Ring Floor
            drawRect(0, 300, 600, 100, '#333');
            
            // CPU
            let cpuColor = cpuAction === 'BLOCK' ? '#555' : (cpuAction === 'PUNCH' ? '#ff0000' : '#ff00ff');
            drawRect(250, 100, 100, 200, cpuColor); // Body
            drawRect(270, 60, 60, 40, cpuColor); // Head
            
            // Player Gloves
            if(action === 'JAB') drawRect(280, 150, 40, 40, '#00e5ff');
            else if(action === 'HAYMAKER') drawRect(320, 120, 50, 50, '#00e5ff');
            else if(action === 'BLOCK') {{
                ctx.strokeStyle = '#00e5ff'; ctx.lineWidth = 5; ctx.strokeRect(200, 200, 200, 150); // Shield visual
            }}
            else {{ drawRect(200, 350, 50, 50, '#00e5ff'); drawRect(350, 350, 50, 50, '#00e5ff'); }}

            ctx.font = '16px monospace'; ctx.fillStyle = '#fff';
            ctx.fillText("YOU: " + playerHP + "%", 20, 30);
            ctx.fillText("STAMINA: " + stamina, 20, 50);
            ctx.fillStyle = '#ff0055'; ctx.fillText("AUDITOR: " + cpuHP, 450, 30);
            ctx.fillStyle = '#FFD700'; ctx.font = '24px monospace'; ctx.textAlign = 'center'; ctx.fillText(timeLeft, 300, 40);
            if(message) {{ ctx.font = '30px monospace'; ctx.fillStyle = '#fff'; ctx.fillText(message, 300, 200); }}
        }}
    </script>
    </body>
    </html>
    """

# ==============================================================================
# 5. UI COMPONENTS
# ==============================================================================

def show_sidebar():
    with st.sidebar:
        st.markdown("### 🛰️ MISSION CONTROL")
        
        # Mission Status Visual
        status_color = "#00ff00" if st.session_state.mission_status == "ONGOING" else "#ff0055"
        st.markdown(f"""
        <div style="border: 1px solid {status_color}; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; background: rgba(0,0,0,0.5);">
            <div style="font-size: 0.8rem; color: #888;">STATUS</div>
            <div style="font-size: 1.2rem; font-weight: bold; color: {status_color};">{st.session_state.mission_status}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏠 MAIN MENU"):
            st.session_state.game_state = 'MENU'
            st.rerun()
            
        st.markdown("---")
        
        st.markdown("### PROTOCOLS")
        if st.button("🚀 SPACE CAMPAIGN"):
            st.session_state.mode = 'CAMPAIGN'
            st.session_state.game_state = 'INTEL'
            st.rerun()
            
        if st.button("🥊 BOXING GYM"):
            st.session_state.mode = 'BOXING'
            st.session_state.game_state = 'INTEL' # Re-use intel briefing logic
            st.rerun()
            
        if st.button("🎓 OFFICER EXAM"):
            st.session_state.mode = 'TRAINING'
            st.session_state.game_state = 'TRIVIA'
            if not st.session_state.q_queue:
                available = TRIVIA_DB.copy()
                st.session_state.q_queue = random.sample(available, 3)
            st.rerun()
            
        if st.button("📂 INTEL VIEWER"):
            st.session_state.game_state = 'VIEWER'
            st.rerun()
            
        st.markdown("---")
        st.caption("Quality Wars v3.1 | ROI Edition")

def show_menu():
    st.markdown("# QUALITY WARS")
    st.markdown("<h4 style='text-align:center; color:#FFE81F; margin-top:-15px'>THE ROI STRIKES BACK</h4>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background:rgba(0,20,40,0.6); padding:25px; border:1px solid #00e5ff; border-radius:10px; margin-bottom:30px; text-align:center; box-shadow: 0 0 20px rgba(0,229,255,0.2);">
            <p style="font-size: 1.2rem; color: #fff;"><strong>INCOMING TRANSMISSION:</strong></p>
            <p style="color: #ccc;">The Quality Control systems are failing. We need Proactive Quality Assurance. Choose your simulation module.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 START SPACE CAMPAIGN (ARCADE)", key="btn_camp"):
            st.session_state.mode = 'CAMPAIGN'
            st.session_state.game_state = 'INTEL'
            st.rerun()
            
        if st.button("🥊 ENTER BOXING GYM (FIGHT)", key="btn_box"):
            st.session_state.mode = 'BOXING'
            st.session_state.game_state = 'INTEL'
            st.rerun()
            
        if st.button("📂 OPEN INTEL VIEWER (PRESENTATIONS)", key="btn_intel"):
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
        <h3 style="border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 20px;">{deck['title']} // PAGE {st.session_state.slide_index + 1}</h3>
        <div class="slide-content">{deck['slides'][st.session_state.slide_index]}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
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
    if st.session_state.mode == 'CAMPAIGN':
        title = f"SECTOR {st.session_state.current_round} BRIEFING"
        msg1 = "**OBJECTIVE:** Survive the asteroid field. Shoot down Process Defects."
        msg2 = "**THREAT LEVEL:** HIGH. Avoid hull impact at all costs."
        btn = "INITIATE LAUNCH SEQUENCE"
    else:
        title = f"ROUND {st.session_state.current_round} WEIGH-IN"
        msg1 = "**OBJECTIVE:** Defeat The Auditor. Use Jabs [A] and Haymakers [S]."
        msg2 = "**STRATEGY:** The Auditor does not accept excuses. Block [D] to survive."
        btn = "STEP INTO THE RING"

    st.markdown(f"## {title}")
    
    st.markdown("""
    <div style="background: rgba(0,0,0,0.6); padding: 20px; border-left: 5px solid #FFE81F; margin-bottom: 20px;">
        <p style="font-family: 'Orbitron'; color: #FFE81F; font-size: 1.2rem;">COMMANDER'S NOTE:</p>
        <p>Review the Intel if you are unsure of the protocols. Failure is not an option.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1: st.info(msg1)
    with col2: st.error(msg2)
    
    st.write("")
    if st.button(btn, type="primary"):
        st.session_state.game_state = 'GAME' if st.session_state.mode == 'CAMPAIGN' else 'BOXING_GAME'
        st.rerun()

def show_trivia_round():
    st.markdown(f"## KNOWLEDGE CHECKPOINT: ROUND {st.session_state.current_round}")
    
    # Fallback queue population
    if not st.session_state.q_queue:
        available = [q for q in TRIVIA_DB if q not in st.session_state.questions_asked]
        if len(available) < 3: available = TRIVIA_DB
        st.session_state.q_queue = random.sample(available, 3)

    with st.form("quiz_form"):
        score_delta = 0
        for i, q in enumerate(st.session_state.q_queue):
            st.markdown(f"##### {i+1}. {q['q']}")
            
            # Randomized options
            opts = q['options'].copy()
            random.seed(q['q'] + str(st.session_state.current_round))
            random.shuffle(opts)
            random.seed()
            
            choice = st.radio(f"select_{i}", opts, key=f"q{i}", index=None, label_visibility="collapsed")
            
            if choice:
                if choice == q['correct']:
                    score_delta += 1
                    st.success(f"Correct! {q['feedback']}")
                else:
                    st.error(f"Incorrect. The answer was: {q['correct']}")
            
            st.markdown("---")
        
        if st.form_submit_button("SUBMIT ANSWERS"):
            st.session_state.trivia_score += score_delta
            
            if score_delta == 3:
                st.balloons()
            
            time.sleep(2)
            
            if st.session_state.current_round < st.session_state.total_rounds:
                st.session_state.current_round += 1
                # Next state logic
                next_state = 'TRIVIA' if st.session_state.mode == 'TRAINING' else 'INTEL'
                st.session_state.game_state = next_state
                
                # Re-roll queue
                available = [q for q in TRIVIA_DB if q not in st.session_state.questions_asked]
                if len(available) < 3: available = TRIVIA_DB
                st.session_state.q_queue = random.sample(available, 3)
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
        <div style="text-align:center; padding:40px; border:2px solid #ff0055; border-radius:10px; background:rgba(0,0,0,0.8);">
            <h1 style="color:#ff0055; font-size:40px !important; margin:0;">CRITICAL SYSTEM FAILURE</h1>
            <p>Your department has been shut down due to excessive defects.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("RESET SIMULATION", type="primary"):
            for k in ['current_round', 'trivia_score', 'game_score']: st.session_state[k] = 0
            st.session_state.current_round = 1
            st.session_state.questions_asked = []
            st.session_state.mission_status = 'ONGOING'
            st.session_state.game_state = 'MENU'
            st.rerun()
        return

    # Standard Scoring for Success
    st.markdown("# MISSION DEBRIEF")
    max_trivia = st.session_state.total_rounds * 3
    trivia_pct = (st.session_state.trivia_score / max_trivia) * 100
    game_pct = min((st.session_state.game_score / 3000) * 100, 100)
    
    if st.session_state.mode == 'TRAINING':
        final_score = trivia_pct
    else:
        final_score = (trivia_pct * 0.60) + (game_pct * 0.40)
    
    # Rank
    if final_score >= 90: rank, color = "QUALITY MASTER", "#00ff00"
    elif final_score >= 70: rank, color = "QUALITY KNIGHT", "#00e5ff"
    else: rank, color = "INTERN", "#ff0055"
    
    st.markdown(f"""
    <div style="text-align:center; padding:40px; border:2px solid {color}; border-radius:10px; background:rgba(0,0,0,0.8);">
        <h1 style="color:{color}; font-size:80px !important; margin:0;">{final_score:.1f}%</h1>
        <h2 style="color:{color}; letter-spacing:5px; font-family:'Orbitron';">{rank}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**KNOWLEDGE:** {st.session_state.trivia_score}/{max_trivia}")
        st.progress(trivia_pct/100)
    with c2:
        if st.session_state.mode != 'TRAINING':
            st.write(f"**PERFORMANCE:** {st.session_state.game_score} PTS")
            st.progress(game_pct/100)

    st.markdown("---")
    if st.button("START NEW CAMPAIGN"):
        for k in ['current_round', 'trivia_score', 'game_score']: st.session_state[k] = 0
        st.session_state.current_round = 1
        st.session_state.questions_asked = []
        st.session_state.mission_status = 'ONGOING'
        st.session_state.game_state = 'MENU'
        st.rerun()

# ==============================================================================
# 6. MAIN CONTROLLER
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
    components.html(get_space_shooter_html(st.session_state.current_round), height=550)
elif st.session_state.game_state == 'BOXING_GAME':
    components.html(get_boxing_html(st.session_state.current_round), height=450)
elif st.session_state.game_state == 'TRIVIA':
    show_trivia_round()
elif st.session_state.game_state == 'GAMEOVER':
    show_gameover()
