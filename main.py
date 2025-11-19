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
        font-size: 3rem !important;
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
        font-family: 'Roboto', sans-serif;
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

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 15, 0.95);
        border-right: 1px solid #333;
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
# 2. CONTENT DATABASES
# ==============================================================================

TRIVIA_DB = [
    # --- VIVE HISTORY & STRATEGY ---
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
    # --- TEAM & CULTURE ---
    {
        "q": "Who leads Product Testing at the Naples Office and is a retired PhD Chemist?",
        "options": ["Jim Ahearn", "Carolina Silva", "Annie", "Jason"],
        "correct": "Jim Ahearn",
        "feedback": "Correct. Jim leads research and testing."
    },
    {
        "q": "Who is the Customer Service Troubleshooting Specialist assisting support agents?",
        "options": ["Luis Hidalgo", "Tom Trump", "Dayna Plummer", "Allen Parker"],
        "correct": "Luis Hidalgo",
        "feedback": "Correct. Luis is a Biomedical Engineer who helps train support agents."
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
    # --- QUALITY TOOLS ---
    {
        "q": "In the Project Charter, what captures the problem in the form of a measurement?",
        "options": ["Problem Statement", "Business Case", "Goal Statement", "Timeline"],
        "correct": "Problem Statement",
        "feedback": "Correct. The Problem Statement defines *what* is wrong in measurable terms."
    },
    {
        "q": "According to the Kano Model, features that customers do not expect but love (the 'Wow' factor) are called:",
        "options": ["Delighters/Excitement Attributes", "Basic Needs", "Performance Attributes", "Threshold Attributes"],
        "correct": "Delighters/Excitement Attributes",
        "feedback": "Correct. Like Bluetooth speakers or Gucci logos (though those might not add value!)."
    },
    {
        "q": "What tool is used to trace a problem (like 'discomfort') to sources like Man, Machine, Method, Material?",
        "options": ["Fishbone Diagram (Ishikawa)", "Pareto Chart", "Scatter Plot", "Control Chart"],
        "correct": "Fishbone Diagram (Ishikawa)",
        "feedback": "Correct. It helps move from 'What' is wrong to 'Why' it is happening."
    },
    {
        "q": "In FMEA, what three factors are multiplied to get the Risk Priority Number (RPN)?",
        "options": ["Severity x Occurrence x Detection", "Cost x Time x Scope", "Quality x Speed x Price", "Severity x Frequency x Budget"],
        "correct": "Severity x Occurrence x Detection",
        "feedback": "Correct. S x O x D = RPN."
    },
    # --- REGULATORY & LEADERSHIP ---
    {
        "q": "What is the 'Comfort Trap' in strategic planning?",
        "options": ["Focusing on activities you control instead of competitive outcomes.", "Buying expensive office chairs.", "Staying in old markets.", "Ignoring safety regulations."],
        "correct": "Focusing on activities you control instead of competitive outcomes.",
        "feedback": "Correct. Real strategy requires specifying a competitive outcome you don't control."
    },
    {
        "q": "In Military Leadership models, which level of autonomy minimizes the Commander's cognitive burden?",
        "options": ["Command by Intent", "Command by Plan", "Command by Directive", "Command by Hope"],
        "correct": "Command by Intent",
        "feedback": "Correct. 'Command by Intent' gives goals and constraints, allowing decisions at the point of action."
    },
    {
        "q": "Design Controls (21 CFR 820.30) apply to ALL Class II and III devices, but only select Class I devices. Which Class I device requires it?",
        "options": ["Devices automated with computer software", "Tongue Depressors", "Elastic Bandages", "Reading Glasses"],
        "correct": "Devices automated with computer software",
        "feedback": "Correct. Software-driven Class I devices require Design Controls."
    },
    {
        "q": "What is the difference between Verification and Validation?",
        "options": ["Verification = Built it Right (Specs); Validation = Built the Right Thing (User Needs)", "Verification = User Needs; Validation = Specs", "They are the same", "Validation is for marketing"],
        "correct": "Verification = Built it Right (Specs); Validation = Built the Right Thing (User Needs)",
        "feedback": "Correct! Verification is internal (lab tests); Validation is external (user tests)."
    }
]

# --- FULL DOCUMENT CONTENT ---
SLIDE_DECKS = {
    "leadership": {
        "title": "Quality Leadership Presentation 11/2025",
        "slides": [
            "**QUALITY APPROVED**\nVive Health - November 2025\n\n---\n\n**VIVE'S QUALITY TEAM**\n\n* **Carolina Silva (Quality Analyst):** Analyzes trends, Biomedical Engineer w/ Data Analytics skill set.\n* **Annie (QC Manager China):** Contracts ~25 inspectors, manages reports/data.\n* **Jim Ahearn (Research & Testing):** Retired PhD Chemist, leads testing in Naples.\n* **Luis Hidalgo (CS Troubleshooting):** Biomedical Engineer, trains support agents.\n* **Jason (QC at MPF):** Leads MPF inspection team (~7 inspectors).\n* **Jessica Marshall (Regulatory Affairs):** Leads ISO 13485 & EU Market Access.",
            "**AGENDA**\n\n1. **Strategic Value:** Our 'Why' - Quality as a market differentiator and revenue generator.\n2. **Performance Review:** The 'What' - A data-driven look at core metrics.\n3. **Process & Proactivity:** The 'How' - Systems for finding, fixing, and preventing issues.",
            "**WINS: QUALITY AS REVENUE GENERATOR**\n\n* **Market Expansion:** CE Mark & ISO 13485 will >2x our TAM (Total Addressable Market) by unlocking EU & UK (+$150B market).\n* **Revenue:** Developed memory foam seat cushion to offset costs.\n* **AI Efficiency:** Using Gemini/Claude ('Vibe Coding') to build custom analytics apps with $0 budget.",
            "**GLOBAL MARKET EXPANSION**\n\n* **Class I Market:** EU/UK market size is ~$22B-$37B.\n* **Impact:** 153% increase in market reach (population) and 75% increase in market value.\n* **Goal:** CE Mark submission estimated Nov 2025.",
            "**STRATEGY & PHILOSOPHY**\n\n* **Lifecycle Management:**\n   - *Concept:* Regulatory landscape & Risk analysis.\n   - *Launch:* Factory audits & V&V testing.\n   - *Post-Market:* Root Cause Analysis & CI.\n* **Core Metrics:**\n   - FBA Return Rate: 5.54% (Goal < 7.50%) - EXCEEDING.\n   - B2B Return Rate: 2.29% (Goal < 2.00%) - NEEDS FOCUS.\n   - ISO 13485: 42.5% Complete.",
            "**PERFORMANCE: VoC**\n\n* **Metric:** 77.61% of Listings have 'Good/Excellent' NCX categorization.\n* **Goal:** 85%.\n* **Loop:** Find (Situation) -> Fix (Task/Action) -> Follow-Up (Result).",
            "**CASE STUDY: POST-OP SHOE**\n\n* **Situation:** High return rate (20-40%) due to 'size' complaints.\n* **Action:** Deep analysis against competitors. Found our shoes were 5-11% larger than market leader.\n* **Result:** Data-driven resizing in progress.",
            "**CASE STUDY: PACKAGING MISTAKE**\n\n* **Problem:** Changed to shrink wrap to save FBA fees.\n* **Cost:** Hurt B2B sales perception (net negative).\n* **Solution:** Decisions now require cross-department sign-off (Product + Sales + Quality).",
            "**ACTIVE PROJECTS**\n\n* **CE for EU/UK:** Project Health: Good.\n* **ISO 13485:** Project Health: Fair (Switched consultants).\n* **Return Rate Reduction:** Project Health: Stable.\n* **Packaging Optimization:** Project Health: Stable.",
            "**MILITARY LEADERSHIP MODEL**\n\n* **Command by Directive:** Low autonomy, micromanagement (High cognitive burden on leader).\n* **Command by Plan:** Mid autonomy.\n* **Command by Intent:** High autonomy. Give goals/constraints, let team decide at point of action. (Goal state).",
            "**EXECUTION TOOLS**\n\n* **Genchi Genbutsu:** 'Go and See' (Visit the source/warehouse).\n* **Kaizen:** Continuous small improvements.\n* **Extreme Ownership:** We own the mission, not just the task.\n* **RACI Matrix:** Defining roles (Responsible, Accountable, Consulted, Informed)."
        ]
    },
    "product_dev": {
        "title": "Product Dev Quality Strategies",
        "slides": [
            "**INTRODUCTION**\n\n'How things start is how they'll go...' - FDA Postmarket Branch.\n\n**Small Changes, Big Impacts:**\n* Project Charter\n* Risk Assessment\n* Affinity Diagrams\n* Kano Analysis",
            "**PROJECT CHARTER**\n\nA living document outlining:\n* **Problem Statement:** The problem in measurement form.\n* **Business Case:** Why are we doing this?\n* **Goal Statement:** The target.\n* **Scope:** What is IN and OUT.\n* **Team:** Who is participating.",
            "**PROJECT RISK ASSESSMENT**\n\nEvaluate risks by:\n* **Probability:** Low/Med/High score (1-3).\n* **Impact:** Low/Med/High score (1-2).\n* **PI Score:** Probability x Impact.\n* *Example Risk:* Scope Creep (Probability 3 x Impact 2 = Score 6).",
            "**VOICE OF CUSTOMER (VoC)**\n\n* **Fishbone Diagram:** Trace 'discomfort' to Man, Machine, Material, Method, Environment.\n* **Kano Analysis:** \n   - *Basic Needs:* Must be there (Breathable fabric).\n   - *Performance:* More is better (Padding).\n   - *Delighters:* Wow factor (Bluetooth?). Don't waste money on things customers don't care about.",
            "**FMEA (FAILURE MODE & EFFECTS ANALYSIS)**\n\n* **Formula:** Severity (S) x Occurrence (O) x Detection (D) = RPN.\n* **Goal:** Solve problems on the whiteboard, not via returns.\n* **Example:** Gel pad leak. S(9) x O(4) x D(7) = RPN 252. Prioritize mitigation immediately.",
            "**HOUSE OF QUALITY (LITE)**\n\nA translation map connecting:\n* **Customer 'Whats':** 'Brace must be comfortable.'\n* **Engineering 'Hows':** 'Fabric Air Permeability > 100 CFM.'\n\nPrevents the 'Lost in Translation' gap between Marketing and Engineering.",
            "**VERIFICATION VS VALIDATION**\n\n* **Verification:** 'Did we build it RIGHT?' (Does it meet specs? Lab testing).\n* **Validation:** 'Did we build the RIGHT THING?' (Does it solve the user's problem? User testing).\n\n*Remember: Reactive = Problem Solving. Proactive = Problem Prevention.*",
            "**FDA DESIGN CONTROLS**\n\nRequired for Class II/III and **Software-Automated Class I** devices.\n\n*Why?* 44% of recalls could be prevented by design controls.\n*Key Elements:* Design Inputs, Outputs, Reviews, Verification, Validation, Transfer, Changes, History File (DHF)."
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
    st.session_state.mode = 'CAMPAIGN' # CAMPAIGN, TRAINING, BOXING
if 'slide_index' not in st.session_state:
    st.session_state.slide_index = 0
if 'current_deck' not in st.session_state:
    st.session_state.current_deck = 'leadership'

# --- SCORE SYNC LOGIC ---
if 'score' in st.query_params:
    try:
        incoming_score = int(st.query_params['score'])
        # Check which game mode we are in
        if st.session_state.game_state in ['GAME', 'BOXING_GAME']:
            st.session_state.game_score += incoming_score
            
            # If score is 0, they likely died/lost, but for this logic let's always go to trivia
            # unless it's a pure fail condition.
            # However, in this app, "Trivia" acts as the "Respawn/Repair" mechanic too.
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
# 4. SPACE SHOOTER (FIXED RESET)
# ==============================================================================
def get_space_shooter_html(round_num):
    difficulty = round_num * 0.6
    
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
        <p>MISSION: PROTECT HULL INTEGRITY</p>
        <p style="color:#ff0055">WARNING: ASTEROIDS DETECTED</p>
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
            if(rand > 0.75) {{
                enemies.push({{x: Math.random() * (canvas.width - 50), y: -50, width: 50, height: 50, speed: 2 + ({difficulty}*0.5), type: 'ASTEROID', hp: 4, color: '#888888'}});
            }} else {{
                enemies.push({{x: Math.random() * (canvas.width - 30), y: -30, width: 30, height: 30, speed: 4 + ({difficulty}), type: 'DEFECT', hp: 1, color: '#ff0055'}});
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
            
            ctx.fillStyle = 'rgba(0, 0, 0, 0.4)'; 
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = '#fff';
            stars.forEach(s => {{
                s.y += s.speed; if(s.y > canvas.height) s.y = 0; ctx.fillRect(s.x, s.y, s.size, s.size);
            }});
            
            ctx.fillStyle = player.color;
            ctx.beginPath(); ctx.moveTo(player.x, player.y); ctx.lineTo(player.x - 15, player.y + 40); ctx.lineTo(player.x + 15, player.y + 40); ctx.fill();
            
            ctx.fillStyle = '#FFE81F';
            for(let i = bullets.length - 1; i >= 0; i--) {{
                let b = bullets[i]; b.y -= b.speed; ctx.fillRect(b.x - 2, b.y, 4, 15); if(b.y < 0) bullets.splice(i, 1);
            }}
            
            for(let i = enemies.length - 1; i >= 0; i--) {{
                let e = enemies[i]; e.y += e.speed;
                ctx.fillStyle = e.color;
                if(e.type === 'ASTEROID') {{ ctx.beginPath(); ctx.arc(e.x + e.width/2, e.y + e.height/2, e.width/2, 0, Math.PI*2); ctx.fill(); }} else {{ ctx.fillRect(e.x, e.y, e.width, e.height); }}
                
                if(Math.abs(player.x - (e.x + e.width/2)) < 30 && Math.abs(player.y - e.y) < 30) {{
                    hull -= (e.type === 'ASTEROID' ? 50 : 20);
                    createExplosion(e.x, e.y, '#ffaa00', 20);
                    enemies.splice(i, 1);
                    if(hull <= 0) {{
                        gameActive = false;
                        // NO ALERT. JUST REDIRECT.
                        window.parent.location.search = '?score=0'; 
                    }}
                }}
                
                for(let j = bullets.length - 1; j >= 0; j--) {{
                    let b = bullets[j];
                    if(b.x > e.x - 10 && b.x < e.x + e.width + 10 && b.y < e.y + e.height && b.y > e.y) {{
                        e.hp--; bullets.splice(j, 1); createExplosion(b.x, b.y, '#fff', 3);
                        if(e.hp <= 0) {{ score += (e.type === 'ASTEROID' ? 250 : 100); createExplosion(e.x, e.y, e.color, 15); enemies.splice(i, 1); }}
                        break;
                    }}
                }}
                if(e.y > canvas.height) enemies.splice(i, 1);
            }}
            
            for(let i = particles.length - 1; i >= 0; i--) {{
                let p = particles[i]; p.x += p.vx; p.y += p.vy; p.life--; ctx.fillStyle = p.color; ctx.fillRect(p.x, p.y, 2, 2); if(p.life <= 0) particles.splice(i, 1);
            }}
            
            ctx.fillStyle = '#00e5ff'; ctx.font = '20px Orbitron'; ctx.fillText('SCORE: ' + score, 20, 30);
            ctx.fillStyle = hull < 30 ? '#ff0055' : '#00ff00'; ctx.fillText('HULL: ' + hull + '%', 20, 60);
            ctx.fillStyle = '#fff'; ctx.fillText('TIME: ' + timeLeft, 700, 30);
        }}

        function createExplosion(x, y, color, count) {{
            for(let i = 0; i < count; i++) {{ particles.push({{ x: x, y: y, vx: (Math.random() - 0.5) * 10, vy: (Math.random() - 0.5) * 10, life: 10 + Math.random() * 20, color: color }}); }}
        }}
    </script>
    </body>
    </html>
    """

# ==============================================================================
# 5. BOXING MODULE (NEW)
# ==============================================================================
def get_boxing_html(round_num):
    """
    A Punch-Out style boxing game with stamina and blocking.
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; overflow: hidden; background: #111; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Press Start 2P', cursive; }}
        canvas {{ border: 4px solid #FFD700; box-shadow: 0 0 30px #FFD700; background: linear-gradient(to bottom, #000 0%, #222 100%); }}
        #overlay {{ position: absolute; color: #FFD700; text-align: center; font-size: 20px; pointer-events: none; text-shadow: 2px 2px #000; width: 100%; }}
    </style>
    </head>
    <body>
    <div id="overlay">
        <h2>ROUND {round_num}</h2>
        <p>VS. THE AUDITOR</p>
        <p style="font-size:12px; color:#aaa;">KEYS: [A] JAB | [S] HAYMAKER | [D] BLOCK</p>
        <p style="color:#00e5ff; margin-top:20px;">CLICK TO START FIGHT</p>
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
        let action = 'IDLE'; // IDLE, JAB, HAYMAKER, BLOCK, HIT
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
            if(action !== 'IDLE') return; // Wait for animation
            
            if(e.key.toLowerCase() === 'a' && stamina >= 10) {{
                action = 'JAB';
                stamina -= 10;
                checkHit(10, 0.8); // Low dmg, high accuracy
                setTimeout(() => action = 'IDLE', 200);
            }} else if (e.key.toLowerCase() === 's' && stamina >= 30) {{
                action = 'HAYMAKER';
                stamina -= 30;
                checkHit(30, 0.4); // High dmg, low accuracy
                setTimeout(() => action = 'IDLE', 600);
            }} else if (e.key.toLowerCase() === 'd') {{
                action = 'BLOCK';
                stamina = Math.min(100, stamina + 5); // Regen
                setTimeout(() => action = 'IDLE', 300);
            }}
        }}

        function checkHit(dmg, accuracy) {{
            // CPU Block chance
            if(cpuAction === 'BLOCK') {{
                message = "BLOCKED!";
                return;
            }}
            
            if(Math.random() < accuracy) {{
                cpuHP -= dmg;
                score += dmg * 10;
                message = "HIT!";
                if(cpuHP <= 0) endGame(true);
            }} else {{
                message = "MISSED!";
            }}
        }}

        function cpuThink() {{
            if(!gameActive) return;
            const rand = Math.random();
            if(rand > 0.6) {{
                cpuAction = 'PUNCH';
                // Player Block Check
                if(action === 'BLOCK') {{
                    stamina = Math.min(100, stamina + 10);
                    message = "YOU BLOCKED!";
                }} else {{
                    playerHP -= 10 + ({round_num} * 2);
                    message = "OUCH!";
                    if(playerHP <= 0) endGame(false);
                }}
                setTimeout(() => cpuAction = 'IDLE', 400);
            }} else if (rand > 0.3) {{
                cpuAction = 'BLOCK';
                setTimeout(() => cpuAction = 'IDLE', 600);
            }}
        }}

        function updateTimer() {{
            if(!gameActive) return;
            timeLeft--;
            stamina = Math.min(100, stamina + 5); // Passive regen
            if(timeLeft <= 0) endGame(true); // Win by survival
        }}

        function endGame(win) {{
            gameActive = false;
            // Send score back
            const finalScore = win ? score + 1000 : 0;
            window.parent.location.search = '?score=' + finalScore;
        }}

        function drawRect(x, y, w, h, color) {{ ctx.fillStyle = color; ctx.fillRect(x, y, w, h); }}

        function gameLoop() {{
            if(!gameActive) return;
            requestAnimationFrame(gameLoop);
            
            // BG
            drawRect(0, 0, 600, 400, '#222');
            
            // CPU
            let cpuColor = cpuAction === 'BLOCK' ? '#555' : (cpuAction === 'PUNCH' ? '#ff0000' : '#ff00ff');
            drawRect(250, 100, 100, 200, cpuColor); // Body
            drawRect(270, 60, 60, 40, cpuColor); // Head
            
            // Player Gloves (Visuals based on action)
            if(action === 'JAB') drawRect(280, 150, 40, 40, '#00e5ff'); // Left Hand Extended
            else if(action === 'HAYMAKER') drawRect(320, 120, 50, 50, '#00e5ff'); // Right Hand Smash
            else if(action === 'BLOCK') drawRect(250, 300, 100, 20, '#00e5ff'); // Block
            else {{
                 // Idle Hands
                 drawRect(200, 350, 50, 50, '#00e5ff');
                 drawRect(350, 350, 50, 50, '#00e5ff');
            }}

            // HUD
            ctx.font = '16px monospace';
            ctx.fillStyle = '#fff';
            ctx.fillText("YOU: " + playerHP + "%", 20, 30);
            ctx.fillText("STAMINA: " + stamina, 20, 50);
            
            ctx.fillStyle = '#ff0055';
            ctx.fillText("AUDITOR: " + cpuHP, 450, 30);
            
            ctx.fillStyle = '#FFD700';
            ctx.font = '24px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(timeLeft, 300, 40);
            
            if(message) {{
                ctx.font = '30px monospace';
                ctx.fillStyle = '#fff';
                ctx.fillText(message, 300, 200);
            }}
        }}
    </script>
    </body>
    </html>
    """

# ==============================================================================
# 6. UI COMPONENTS
# ==============================================================================

def show_sidebar():
    with st.sidebar:
        st.markdown("### MISSION CONTROL")
        
        if st.button("🏠 MAIN MENU"):
            st.session_state.game_state = 'MENU'
            st.rerun()
            
        st.markdown("---")
        
        st.markdown("### PROTOCOLS")
        if st.button("⚔️ SPACE CAMPAIGN"):
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
        st.caption("Quality Wars v3.0")

def show_menu():
    st.markdown("# QUALITY WARS")
    st.markdown("<h4 style='text-align:center; color:#FFE81F; margin-top:-15px'>THE ROI STRIKES BACK</h4>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background:rgba(0,0,0,0.5); padding:20px; border:1px solid #333; border-radius:10px; margin-bottom:20px; text-align:center;">
            <p><strong>INCOMING TRANSMISSION:</strong></p>
            <p>Quality Control is not enough. We need Quality Assurance. Choose your training simulation below.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚔️ SPACE CAMPAIGN (ARCADE)", key="btn_camp"):
            st.session_state.mode = 'CAMPAIGN'
            st.session_state.game_state = 'INTEL'
            st.rerun()
            
        if st.button("🥊 BOXING GYM (FIGHT)", key="btn_box"):
            st.session_state.mode = 'BOXING'
            st.session_state.game_state = 'INTEL'
            st.rerun()
            
        if st.button("🎓 OFFICER EXAM (QUIZ ONLY)", key="btn_exam"):
            st.session_state.mode = 'TRAINING'
            st.session_state.game_state = 'TRIVIA'
            available = TRIVIA_DB.copy()
            st.session_state.q_queue = random.sample(available, 3)
            st.rerun()

def show_viewer():
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
    
    st.markdown(f"""
    <div class="intel-viewer">
        <div class="intel-header">{deck['title']} | SLIDE {st.session_state.slide_index + 1}/{total_slides}</div>
        <div class="slide-content">{deck['slides'][st.session_state.slide_index]}</div>
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
    if st.session_state.mode == 'CAMPAIGN':
        title = f"SECTOR {st.session_state.current_round} BRIEFING"
        msg1 = "OBJECTIVE: Survive asteroid field. Eliminate defects."
        msg2 = "THREAT: Heavy Asteroids detected. Avoid impact."
        btn = "INITIATE LAUNCH"
    else:
        title = f"ROUND {st.session_state.current_round} WEIGH-IN"
        msg1 = "OBJECTIVE: Defeat The Auditor. Use Jabs [A] and Haymakers [S]."
        msg2 = "THREAT: The Auditor ignores excuses. Block [D] to survive."
        btn = "ENTER RING"

    st.markdown(f"## {title}")
    col1, col2 = st.columns(2)
    with col1: st.info(msg1)
    with col2: st.warning(msg2)
        
    if st.button(btn):
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
            st.markdown(f"**{i+1}. {q['q']}**")
            opts = q['options'].copy()
            # Randomized seed ensures shuffle is consistent during this render but random per question
            random.seed(q['q'] + str(st.session_state.current_round))
            random.shuffle(opts)
            random.seed()
            
            choice = st.radio(f"Options for {i}", opts, key=f"q{i}", index=None, label_visibility="collapsed")
            st.markdown("---")
            if choice == q['correct']:
                score_delta += 1
        
        if st.form_submit_button("SUBMIT ANSWERS"):
            st.session_state.trivia_score += score_delta
            if score_delta == 3:
                st.balloons()
                st.success("PERFECT SCORE!")
            else:
                st.info(f"RESULTS: {score_delta}/3 CORRECT.")
            
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
                st.session_state.game_state = 'GAMEOVER'
                st.rerun()

def show_gameover():
    st.markdown("# MISSION DEBRIEF")
    
    # Scoring
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
        if st.session_state.mode != 'TRAINING':
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
# 7. MAIN CONTROLLER
# ==============================================================================

show_sidebar()

# HUD (Skip on Menu/Gameover/Viewer)
if st.session_state.game_state not in ['MENU', 'GAMEOVER', 'VIEWER']:
    st.markdown(f"""
    <div class="hud-container">
        <div class="metric-box"><div class="metric-label">ROUND</div><div class="metric-value">{st.session_state.current_round}/{st.session_state.total_rounds}</div></div>
        <div class="metric-box"><div class="metric-label">XP</div><div class="metric-value">{st.session_state.game_score}</div></div>
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
