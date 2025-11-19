import streamlit as st
import streamlit.components.v1 as components
import random
import time
import base64
import json

# ==============================================================================
# 1. CONFIGURATION & ASSETS
# ==============================================================================
st.set_page_config(
    page_title="Quality Wars: The ROI Strikes Back",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Force Dark Mode & Custom "Space" CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto:wght@300;400&display=swap');

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
    }

    /* TYPOGRAPHY */
    h1, h2, h3 {
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
    }

    /* NEON BOXES */
    .intel-card {
        background: rgba(16, 20, 24, 0.95);
        border: 1px solid #00e5ff;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        color: #e0e0e0;
    }

    .intel-header {
        color: #00e5ff;
        font-family: 'Orbitron', sans-serif;
        border-bottom: 1px solid #00e5ff;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }

    /* BUTTONS */
    .stButton>button {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(45deg, #00e5ff, #2979ff) !important;
        color: #000 !important;
        border: none;
        padding: 15px 30px;
        font-weight: bold;
        transition: all 0.3s ease;
        text-transform: uppercase;
        border-radius: 4px;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(0, 229, 255, 0.8);
    }

    /* SCORE HUD */
    .hud-container {
        display: flex;
        justify-content: space-around;
        background: rgba(0,0,0,0.8);
        border-bottom: 2px solid #FFE81F;
        padding: 10px;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    
    .metric-box {
        text-align: center;
        font-family: 'Orbitron', sans-serif;
    }
    .metric-label { color: #888; font-size: 0.8rem; }
    .metric-value { color: #FFE81F; font-size: 1.5rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. DATA & INTEL (Vive Health Specifics)
# ==============================================================================

TRIVIA_DB = [
    # VIVE HISTORY & VALUES
    {
        "q": "Vive Health was founded in which year, establishing itself as a family-owned leader in home health?",
        "options": ["2014", "2012", "2016", "2010"],
        "correct": "2014",
        "feedback": "Correct! Vive was founded in 2014 and now boasts over 150+ employees and 1500+ products."
    },
    {
        "q": "Which of the following is NOT one of Vive Health's Core Values?",
        "options": ["Move Fast and Break Things", "Extreme Ownership", "Delight Our Customers", "Enjoy the Journey"],
        "correct": "Move Fast and Break Things",
        "feedback": "Correct. Our values are Growth Mindset, Extreme Ownership, Delight Customers, Data & System Driven, Best Ideas Rise, and Enjoy the Journey."
    },
    {
        "q": "What does the core value 'Extreme Ownership' imply at Vive?",
        "options": ["We take full responsibility for actions and results; no excuses.", "We own as much equity as possible.", "We micro-manage every process.", "We only focus on our specific job description."],
        "correct": "We take full responsibility for actions and results; no excuses.",
        "feedback": "Right! External obstacles are just hurdles, not roadblocks."
    },
    
    # PRODUCT & REGULATORY (Class I/II, ISO)
    {
        "q": "What is the estimated size of the Class I Equivalent Medical Device market in the EU & UK (our new TAM)?",
        "options": ["$22B - $37B", "$5B - $10B", "$100B+", "$1B - $2B"],
        "correct": "$22B - $37B",
        "feedback": "Correct. Obtaining the CE Mark unlocks this massive market, increasing our reach by 153% in population."
    },
    {
        "q": "The Vive MOB1027 Mobility Scooter uses which battery technology?",
        "options": ["Sealed Lead Acid (SLA)", "Lithium Ion", "Nuclear Fission", "AA Alkaline"],
        "correct": "Sealed Lead Acid (SLA)",
        "feedback": "Correct. It uses two 12V 12AH Sealed Lead Acid batteries."
    },
    {
        "q": "What is the primary purpose of ISO 13485 certification?",
        "options": ["Quality Management Systems for Medical Devices", "Environmental Management", "Occupational Safety", "Information Security"],
        "correct": "Quality Management Systems for Medical Devices",
        "feedback": "Correct. This certification is key to our expansion strategy and regulatory compliance."
    },
    {
        "q": "In the context of the Post-Op Shoe packaging issue, what was the conflict?",
        "options": ["FBA fee savings vs. B2B revenue loss", "Color preference vs. Cost", "Shipping speed vs. Weight", "Plastic vs. Paper"],
        "correct": "FBA fee savings vs. B2B revenue loss",
        "feedback": "Exactly. Shrink wrapping saved FBA fees but damaged B2B relationships. Proactive QA prevents this."
    },
    
    # QUALITY TOOLS
    {
        "q": "What does FMEA stand for?",
        "options": ["Failure Mode and Effects Analysis", "Fast Manufacturing Engineering Action", "Federal Medical Equipment Association", "Final Market Entry Assessment"],
        "correct": "Failure Mode and Effects Analysis",
        "feedback": "Correct. FMEA is a proactive tool to identify risks (RPN scores) before they happen."
    },
    {
        "q": "What is the difference between Verification and Validation?",
        "options": ["Verification: Did we build it right? Validation: Did we build the right thing?", "They are the same.", "Verification is for customers, Validation is for engineers.", "Verification is optional."],
        "correct": "Verification: Did we build it right? Validation: Did we build the right thing?",
        "feedback": "Correct! Verification checks specs; Validation checks user needs."
    },
    {
        "q": "What is a CAPA?",
        "options": ["Corrective and Preventive Action", "Cost Analysis Per Asset", "Customer Acquisition Plan", "Corporate Annual Performance Assessment"],
        "correct": "Corrective and Preventive Action",
        "feedback": "Correct. CAPA is the system for investigating and solving systemic quality issues."
    }
]

# ==============================================================================
# 3. STATE MANAGEMENT
# ==============================================================================
# Initialize session state
defaults = {
    'game_state': 'MENU', # MENU, INTEL, GAME, TRIVIA, GAMEOVER
    'current_round': 1,
    'trivia_score': 0,
    'game_score': 0,
    'total_rounds': 3,
    'questions_asked': [],
    'q_queue': [], # Queue for the current round
    'mode': 'CAMPAIGN' # CAMPAIGN or TRAINING
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Handle URL Query Params for Score Sync (The "Automatic" Trick)
if 'score' in st.query_params:
    try:
        incoming_score = int(st.query_params['score'])
        # Only update if we are in a game state transition
        st.session_state.game_score += incoming_score
        st.session_state.game_state = 'TRIVIA'
        
        # Prepare questions for this round
        available = [q for q in TRIVIA_DB if q not in st.session_state.questions_asked]
        if len(available) < 3:
            st.session_state.questions_asked = [] # Reset if out of questions
            available = TRIVIA_DB
        
        st.session_state.q_queue = random.sample(available, 3)
        for q in st.session_state.q_queue:
            st.session_state.questions_asked.append(q)
            
    except:
        pass
    finally:
        # Clear params to prevent re-add on refresh
        st.query_params.clear()

# ==============================================================================
# 4. HTML5 GAME ENGINE (With Score Auto-Sync)
# ==============================================================================
def get_game_html(round_num):
    """
    Injects a high-quality HTML5 Canvas shooter.
    On Game Over, it reloads the parent page with ?score=XXXX
    """
    difficulty_modifier = round_num * 0.5
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; overflow: hidden; background: transparent; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Orbitron', monospace; }}
        canvas {{ border: 2px solid #00e5ff; box-shadow: 0 0 30px #00e5ff; background: rgba(0,0,0,0.9); cursor: none; }}
        #overlay {{ position: absolute; color: #00e5ff; text-align: center; font-size: 24px; pointer-events: none; text-shadow: 0 0 10px #00e5ff; }}
        .hidden {{ display: none; }}
    </style>
    </head>
    <body>
    <div id="overlay">
        <h2>SECTOR {round_num}</h2>
        <p>PILOT: MOUSE TO MOVE</p>
        <p>CLICK TO FIRE</p>
        <p>ELIMINATE NON-CONFORMITIES</p>
        <p style="font-size: 16px; color: #FFE81F">CLICK TO ENGAGE</p>
    </div>
    <canvas id="gameCanvas" width="800" height="500"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const overlay = document.getElementById('overlay');
        
        let gameActive = false;
        let score = 0;
        let timeLeft = 30; 
        let lastTime = Date.now();
        
        // Assets
        const player = {{ x: 400, y: 450, width: 40, height: 40, color: '#00e5ff' }};
        let bullets = [];
        let enemies = [];
        let particles = [];
        let stars = [];

        // Starfield Background
        for(let i=0; i<100; i++) {{
            stars.push({{
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                size: Math.random() * 2,
                speed: Math.random() * 3
            }});
        }}
        
        canvas.addEventListener('mousemove', (e) => {{
            const rect = canvas.getBoundingClientRect();
            player.x = e.clientX - rect.left;
            if(player.x < 0) player.x = 0;
            if(player.x > canvas.width) player.x = canvas.width;
        }});
        
        canvas.addEventListener('mousedown', () => {{
            if(!gameActive && timeLeft > 0) {{
                gameActive = true;
                overlay.style.display = 'none';
                gameLoop();
                setInterval(spawnEnemy, 1000 - ({difficulty_modifier} * 100)); 
                setInterval(updateTimer, 1000);
            }}
            // Fire logic
            if(gameActive) {{
                bullets.push({{ x: player.x, y: player.y, speed: 15 }});
            }}
        }});

        function spawnEnemy() {{
            if(!gameActive) return;
            const size = 30;
            const types = ['DEFECT', 'RISK', 'NC', 'BUG'];
            const colors = ['#ff0055', '#ff9900', '#ff0055', '#cc00ff'];
            const randIndex = Math.floor(Math.random() * types.length);
            
            enemies.push({{
                x: Math.random() * (canvas.width - size),
                y: -size,
                width: size,
                height: size,
                speed: 3 + ({difficulty_modifier}),
                label: types[randIndex],
                color: colors[randIndex]
            }});
        }}

        function updateTimer() {{
            if(!gameActive) return;
            timeLeft--;
            if(timeLeft <= 0) {{
                endGame();
            }}
        }}

        function endGame() {{
            gameActive = false;
            // AUTOMATIC SCORE SYNC HACK
            // Reloads the parent window with the score in URL
            window.parent.location.search = '?score=' + score;
        }}

        function gameLoop() {{
            if(!gameActive) return;
            requestAnimationFrame(gameLoop);
            
            // Background
            ctx.fillStyle = 'rgba(0, 0, 0, 0.4)'; 
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Stars
            ctx.fillStyle = '#ffffff';
            stars.forEach(star => {{
                star.y += star.speed;
                if(star.y > canvas.height) star.y = 0;
                ctx.fillRect(star.x, star.y, star.size, star.size);
            }});
            
            // Player
            ctx.fillStyle = player.color;
            ctx.beginPath();
            ctx.moveTo(player.x, player.y);
            ctx.lineTo(player.x - 15, player.y + 40);
            ctx.lineTo(player.x + 15, player.y + 40);
            ctx.shadowBlur = 20;
            ctx.shadowColor = player.color;
            ctx.fill();
            ctx.shadowBlur = 0;
            
            // Bullets
            ctx.fillStyle = '#FFE81F';
            for(let i = bullets.length - 1; i >= 0; i--) {{
                let b = bullets[i];
                b.y -= b.speed;
                ctx.fillRect(b.x - 2, b.y, 4, 15);
                if(b.y < 0) bullets.splice(i, 1);
            }}
            
            // Enemies
            ctx.font = '12px Orbitron';
            ctx.textAlign = 'center';
            for(let i = enemies.length - 1; i >= 0; i--) {{
                let e = enemies[i];
                e.y += e.speed;
                
                ctx.shadowBlur = 10;
                ctx.shadowColor = e.color;
                ctx.fillStyle = e.color;
                ctx.fillRect(e.x - e.width/2, e.y, e.width, e.height);
                ctx.shadowBlur = 0;
                
                ctx.fillStyle = '#fff';
                ctx.fillText(e.label, e.x, e.y + e.height + 12);
                
                // Collision Player
                if(Math.abs(player.x - e.x) < 30 && Math.abs(player.y - e.y) < 30) {{
                    score = Math.max(0, score - 50);
                    enemies.splice(i, 1);
                    createExplosion(e.x, e.y, '#ff0000');
                }}
                
                // Collision Bullet
                for(let j = bullets.length - 1; j >= 0; j--) {{
                    let b = bullets[j];
                    if(b.x > e.x - e.width/2 && b.x < e.x + e.width/2 && b.y < e.y + e.height && b.y > e.y) {{
                        score += 100;
                        createExplosion(e.x, e.y, e.color);
                        enemies.splice(i, 1);
                        bullets.splice(j, 1);
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
                ctx.globalAlpha = p.life / 20;
                ctx.fillStyle = p.color;
                ctx.fillRect(p.x, p.y, 3, 3);
                ctx.globalAlpha = 1.0;
                if(p.life <= 0) particles.splice(i, 1);
            }}
            
            // HUD in Canvas
            ctx.fillStyle = '#00e5ff';
            ctx.font = '20px Orbitron';
            ctx.textAlign = 'left';
            ctx.fillText('PTS: ' + score, 20, 30);
            ctx.fillText('T-MINUS: ' + timeLeft, 20, 60);
        }}

        function createExplosion(x, y, color) {{
            for(let i = 0; i < 15; i++) {{
                particles.push({{
                    x: x,
                    y: y,
                    vx: (Math.random() - 0.5) * 10,
                    vy: (Math.random() - 0.5) * 10,
                    life: 20 + Math.random() * 10,
                    color: color
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
            <div class="metric-label">ROUND</div>
            <div class="metric-value">{st.session_state.current_round}/{st.session_state.total_rounds}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">BATTLE SCORE</div>
            <div class="metric-value">{st.session_state.game_score}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">KNOWLEDGE</div>
            <div class="metric-value">{st.session_state.trivia_score}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_menu():
    # Title Animation
    st.markdown("# QUALITY WARS")
    st.markdown("<h3 style='text-align:center; color:#00e5ff'>THE ROI STRIKES BACK</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="intel-card" style="text-align: center;">
            <p>The Galaxy is plagued by non-conformities and inefficiencies. 
            As a Quality Commander for Vive Health, you must balance 
            tactical skill (Game) with strategic knowledge (Trivia).</p>
            <p style="color: #FFE81F; font-weight: bold;">SCORING PROTOCOL: 90% KNOWLEDGE | 10% BATTLE SKILL</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("START CAMPAIGN (GAME + TRIVIA)"):
            st.session_state.mode = 'CAMPAIGN'
            st.session_state.game_state = 'INTEL'
            st.rerun()
            
        if st.button("CADET TRAINING (TRIVIA ONLY)"):
            st.session_state.mode = 'TRAINING'
            st.session_state.game_state = 'TRIVIA'
            # Init first round queue for training
            available = TRIVIA_DB.copy()
            st.session_state.q_queue = random.sample(available, 3)
            st.rerun()
            
        if st.button("ACCESS MISSION INTEL (PRESENTATIONS)"):
            st.session_state.game_state = 'LIBRARY'
            st.rerun()

def show_library():
    st.markdown("## 📂 CLASSIFIED INTEL: VIVE ARCHIVES")
    if st.button("⬅ RETURN TO BASE"):
        st.session_state.game_state = 'MENU'
        st.rerun()
        
    tab1, tab2 = st.tabs(["Product Dev Quality Strategies", "Quality Leadership 11/2025"])
    
    with tab1:
        st.markdown("""
        <div class="intel-card">
            <div class="intel-header">STRATEGY SUMMARY [Product Development Quality Strategies.pptx (5).pdf]</div>
            <ul>
                <li><strong>Project Charter:</strong> Defines problem, goal, and scope to prevent "scope creep".</li>
                <li><strong>FMEA (Failure Mode Effects Analysis):</strong> Proactive risk management. RPN = Severity x Occurrence x Detection.</li>
                <li><strong>Voice of Customer (VoC):</strong> Using Amazon NCX data and B2B feedback to drive design changes.</li>
                <li><strong>Validation vs Verification:</strong> Validation = "Right Product?" (User needs). Verification = "Product Right?" (Specs).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with tab2:
        st.markdown("""
        <div class="intel-card">
            <div class="intel-header">PERFORMANCE REPORT [Quality Leadership Presentation 11_2025 (8).pdf]</div>
            <ul>
                <li><strong>Wins:</strong> Saved $570k+ projected annual savings via return reduction & FBA fee optimization.</li>
                <li><strong>ISO 13485:</strong> 42.5% implementation progress. Critical for EU/UK expansion.</li>
                <li><strong>Return Rates:</strong> FBA Return Rate slashed to 5.54% (Goal < 7.5%).</li>
                <li><strong>Philosophy:</strong> "Genchi Genbutsu" (Go and See) & Extreme Ownership.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_intel_briefing():
    """Shows visuals from the docs to prep the user for the round"""
    st.markdown(f"## MISSION BRIEFING: SECTOR {st.session_state.current_round}")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="intel-card">
            <div class="intel-header">OBJECTIVE</div>
            <p>Review the data below. Intelligence suggests high return rates in the Post-Op Shoe sector due to sizing issues. 
            Your mission: Eliminate defects in the asteroid field.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        # Showing a "Chart" (Simulated with progress bars for visual flair)
        st.markdown("""
        <div class="intel-card">
            <div class="intel-header">RETURN RATE TELEMETRY</div>
            <p>FBA RETURN RATE</p>
            <div style="background:#333; width:100%; height:20px; border-radius:10px;">
                <div style="background:#00ff00; width:75%; height:100%; border-radius:10px;"></div>
            </div>
            <p style="text-align:right; font-size:0.8rem">TARGET: < 7.5% | ACTUAL: 5.54%</p>
        </div>
        """, unsafe_allow_html=True)
        
    if st.button("LAUNCH FIGHTER"):
        st.session_state.game_state = 'GAME'
        st.rerun()

def show_trivia_round():
    st.markdown(f"## KNOWLEDGE CHECKPOINT {st.session_state.current_round}")
    st.caption("Answer all questions to proceed.")
    
    # If queue is empty (shouldn't happen if logic is right, but safety check)
    if not st.session_state.q_queue:
        st.session_state.game_state = 'MENU'
        st.rerun()
    
    with st.form("trivia_form"):
        answers = {}
        for i, q in enumerate(st.session_state.q_queue):
            st.markdown(f"**Q{i+1}: {q['q']}**")
            answers[i] = st.radio(f"Select answer for Q{i+1}", q['options'], key=f"q_{st.session_state.current_round}_{i}", label_visibility="collapsed")
            st.markdown("---")
            
        submitted = st.form_submit_button("SUBMIT ANSWERS")
        
        if submitted:
            correct_count = 0
            for i, q in enumerate(st.session_state.q_queue):
                if answers[i] == q['correct']:
                    correct_count += 1
                    st.success(f"Q{i+1}: Correct! {q['feedback']}")
                else:
                    st.error(f"Q{i+1}: Incorrect. {q['feedback']}")
            
            st.session_state.trivia_score += correct_count
            
            # Advancement Logic
            if st.session_state.current_round < st.session_state.total_rounds:
                if st.button("NEXT SECTOR"): # Requires double click due to form reload, usually better to use session state flag
                    pass
                st.session_state.current_round += 1
                st.session_state.game_state = 'INTEL' if st.session_state.mode == 'CAMPAIGN' else 'TRIVIA'
                
                # Replenish Queue
                available = [q for q in TRIVIA_DB if q not in st.session_state.questions_asked]
                if len(available) < 3:
                    available = TRIVIA_DB # Recycle
                st.session_state.q_queue = random.sample(available, 3)
                
                time.sleep(2) # Let them read feedback
                st.rerun()
            else:
                st.session_state.game_state = 'GAMEOVER'
                st.rerun()

def show_gameover():
    st.markdown("## MISSION DEBRIEF")
    
    # Calculations
    # Max trivia = 9 (3 rounds * 3 questions)
    # Normalize game score (Approx 3000 is 'good' for 3 rounds)
    
    max_trivia = st.session_state.total_rounds * 3
    trivia_pct = (st.session_state.trivia_score / max_trivia) * 100
    game_pct = min((st.session_state.game_score / 3000) * 100, 100)
    
    # Weighted Score: 90% Trivia, 10% Game
    final_score = (trivia_pct * 0.90) + (game_pct * 0.10)
    
    if final_score >= 90:
        rank = "JEDI MASTER"
        color = "#00ff00"
    elif final_score >= 70:
        rank = "QUALITY KNIGHT"
        color = "#00e5ff"
    else:
        rank = "PADAWAN LEARNER"
        color = "#ff0055"
        
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="intel-card" style="text-align:center; border-color: {color};">
            <h3>FINAL ASSESSMENT</h3>
            <h1 style="color: {color}; font-size: 4rem !important;">{final_score:.1f}%</h1>
            <h2 style="color: {color}">{rank}</h2>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""<div class="intel-card"><div class="intel-header">PERFORMANCE BREAKDOWN</div>""", unsafe_allow_html=True)
        st.write(f"🧠 **Quality Knowledge:** {st.session_state.trivia_score}/{max_trivia}")
        st.progress(trivia_pct/100)
        st.write(f"🚀 **Operational Agility:** {st.session_state.game_score} pts")
        st.progress(game_pct/100)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("RESTART MISSION"):
        # Reset State
        st.session_state.game_state = 'MENU'
        st.session_state.current_round = 1
        st.session_state.trivia_score = 0
        st.session_state.game_score = 0
        st.session_state.questions_asked = []
        st.rerun()

# ==============================================================================
# 6. MAIN CONTROLLER
# ==============================================================================

show_hud()

if st.session_state.game_state == 'MENU':
    show_menu()
elif st.session_state.game_state == 'LIBRARY':
    show_library()
elif st.session_state.game_state == 'INTEL':
    show_intel_briefing()
elif st.session_state.game_state == 'GAME':
    # Render Game with auto-sync hack
    components.html(get_game_html(st.session_state.current_round), height=550)
elif st.session_state.game_state == 'TRIVIA':
    show_trivia_round()
elif st.session_state.game_state == 'GAMEOVER':
    show_gameover()
