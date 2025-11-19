import streamlit as st
import streamlit.components.v1 as components
import random
import time
import os
import base64

# ==============================================================================
# 1. CONFIGURATION & ASSETS
# ==============================================================================
st.set_page_config(
    page_title="Quality Wars: Return of the ROI",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CUSTOM CSS: EARTH/SPACE THEME & ANIMATIONS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');

    /* BACKGROUND & ATMOSPHERE */
    .stApp {
        background-color: #000;
        background-image: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop");
        background-size: cover;
        background-position: center center;
        background-attachment: fixed;
        font-family: 'Rajdhani', sans-serif;
        color: #e0e0e0;
    }
    
    /* SCANLINE OVERLAY FOR CRT EFFECT */
    .stApp::before {
        content: " ";
        display: block;
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        z-index: 0;
        background-size: 100% 2px, 3px 100%;
        pointer-events: none;
    }

    /* TYPOGRAPHY */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 3px;
        position: relative;
        z-index: 1;
    }
    
    h1 {
        background: linear-gradient(180deg, #FFE81F 0%, #9B870C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 20px rgba(255, 232, 31, 0.6);
        text-align: center;
        font-weight: 900;
        font-size: 4.5rem !important;
        padding: 30px 0;
        margin-bottom: 0;
    }

    h2 { 
        color: #00e5ff; 
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.8);
        border-bottom: 2px solid #00e5ff;
        padding-bottom: 10px;
        display: inline-block;
    }

    /* UI PANELS (Glassmorphism) */
    .intel-viewer, .mission-card, .hud-container, .result-card {
        background: rgba(16, 20, 24, 0.85);
        backdrop-filter: blur(10px);
        border: 1px solid #333;
        border-left: 5px solid #FFE81F;
        box-shadow: 0 0 30px rgba(0,0,0, 0.8);
        border-radius: 4px;
        padding: 30px;
        margin-bottom: 20px;
        position: relative;
        z-index: 1;
    }
    
    .mission-card:hover {
        border-color: #00e5ff;
        transform: translateY(-2px);
        transition: all 0.3s ease;
        box-shadow: 0 0 40px rgba(0, 229, 255, 0.2);
    }

    /* BUTTONS */
    .stButton>button {
        font-family: 'Orbitron', sans-serif;
        background: rgba(0, 0, 0, 0.7) !important;
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
        position: relative;
        z-index: 2;
    }
    
    .stButton>button:hover {
        background: #FFE81F !important;
        color: #000 !important;
        box-shadow: 0 0 25px #FFE81F;
        transform: scale(1.02);
    }
    
    /* HUD METRICS */
    .hud-container {
        display: flex;
        justify-content: center;
        gap: 3rem;
        background: linear-gradient(90deg, rgba(0,0,0,0.5) 0%, rgba(0,229,255,0.1) 50%, rgba(0,0,0,0.5) 100%);
        border-top: 1px solid #00e5ff;
        border-bottom: 1px solid #00e5ff;
        padding: 15px;
        margin-bottom: 40px;
        margin-top: -20px;
    }
    
    .metric-box { text-align: center; }
    .metric-label { color: #00e5ff; font-size: 0.8rem; letter-spacing: 2px; font-family: 'Orbitron'; }
    .metric-value { color: #fff; font-size: 1.8rem; font-weight: bold; font-family: 'Orbitron'; text-shadow: 0 0 10px #00e5ff; }
    
    /* RADIO BUTTONS FOR QUIZ */
    .stRadio > div {
        background: rgba(0,0,0,0.6);
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #444;
    }
    .stRadio label { color: #fff !important; font-size: 1.1rem; }
    
    /* TOASTS */
    div[data-testid="stToast"] {
        background-color: rgba(0, 20, 40, 0.95) !important;
        border: 1px solid #00e5ff !important;
        color: #fff !important;
        font-family: 'Orbitron', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CONTENT DATABASES (UPDATED)
# ==============================================================================

TRIVIA_DB = [
    # --- VIVE HISTORY & STRATEGY ---
    {
        "id": 1,
        "q": "Vive Health was founded in which year and is based in which city?",
        "options": ["2014, Naples FL", "2010, Austin TX", "2016, Miami FL", "2012, New York NY"],
        "correct": "2014, Naples FL",
        "feedback": "Correct! Vive was founded in 2014 and is headquartered in Naples, Florida."
    },
    {
        "id": 2,
        "q": "Which certification is specifically required to affix the CE Mark and unlock the EU/UK markets?",
        "options": ["The CE Technical File (MDR Compliance)", "ISO 13485", "ISO 9001", "FDA 510(k)"],
        "correct": "The CE Technical File (MDR Compliance)",
        "feedback": "Correct. While ISO 13485 is a quality system standard, the CE Mark itself is the legal requirement for EU market access."
    },
    {
        "id": 3,
        "q": "Vive Health recently registered with authorities in which country, allowing CE marking for 100s of products?",
        "options": ["Germany", "France", "Italy", "Spain"],
        "correct": "Germany",
        "feedback": "Correct. Registration via Germany has opened the door for CE marking across the EU."
    },
    {
        "id": 4,
        "q": "According to the 'Quality Leadership Presentation', the in-house AI categorization tool saves approximately how many hours per month?",
        "options": ["~40 hours", "~10 hours", "~100 hours", "It costs time, doesn't save it"],
        "correct": "~40 hours",
        "feedback": "Correct! The slide 'Overcoming Challenges' states the in-house AI tool saves ~40hrs/Month."
    },
    
    # --- MEDICAL DEVICE REGS & ANATOMY ---
    {
        "id": 5,
        "q": "Most of Vive Health's products (mobility aids, braces) fall under which FDA device class?",
        "options": ["Class I", "Class II", "Class III", "Unclassified"],
        "correct": "Class I",
        "feedback": "Correct. These are low-risk devices subject to general controls."
    },
    {
        "id": 6,
        "q": "Which bone is commonly supported by a 'Post-Op Shoe' after surgery?",
        "options": ["Metatarsals (Foot bones)", "Femur (Thigh)", "Humerus (Arm)", "Clavicle (Collarbone)"],
        "correct": "Metatarsals (Foot bones)",
        "feedback": "Correct. Post-op shoes protect the foot bones and toes."
    },
    {
        "id": 7,
        "q": "In FMEA (Failure Mode & Effects Analysis), what does RPN stand for?",
        "options": ["Risk Priority Number", "Rapid Prototype Number", "Real Problem Notification", "Return Percentage Net"],
        "correct": "Risk Priority Number",
        "feedback": "Correct. RPN helps prioritize which risks to fix first."
    },
    
    # --- METRICS ---
    {
        "id": 8,
        "q": "What was the FBA Return Rate in October 2025?",
        "options": ["5.54%", "7.50%", "10.2%", "2.1%"],
        "correct": "5.54%",
        "feedback": "Correct. This exceeded the goal of 7.50% significantly."
    },
    {
        "id": 9,
        "q": "What is the 'B2B Return Rate' goal mentioned in the November 2025 presentation?",
        "options": ["<= 2.00%", "<= 5.00%", "<= 1.00%", "0%"],
        "correct": "<= 2.00%",
        "feedback": "Correct. The actual was 2.29%, so it 'Needs Focus'."
    },
    {
        "id": 10,
        "q": "In the 'Post-Op Shoe' case study, what was the root cause of the high return rate?",
        "options": ["Shoes were 5-11% larger than competitors", "The fabric was tearing", "The velcro failed", "They were too expensive"],
        "correct": "Shoes were 5-11% larger than competitors",
        "feedback": "Correct. Analysis revealed the sizing was significantly larger than the market leader."
    }
]

# ==============================================================================
# 3. STATE MANAGEMENT & LOGIC
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
if 'mission_status' not in st.session_state:
    st.session_state.mission_status = 'ONGOING'
# SETTINGS
if 'game_duration_setting' not in st.session_state:
    st.session_state.game_duration_setting = 15 
if 'last_round_msg' not in st.session_state:
    st.session_state.last_round_msg = None

# --- SCORE SYNC LOGIC ---
if 'score' in st.query_params:
    try:
        incoming_score = int(st.query_params['score'])
        duration = st.session_state.game_duration_setting
        
        if st.session_state.game_state in ['GAME', 'BOXING_GAME']:
            # HANDLING DEATH / FAILURE
            if incoming_score == 0 and duration != 9999:
                st.session_state.mission_status = 'FAILED'
                st.session_state.game_state = 'GAMEOVER'
            else:
                # SUCCESS CHECKS
                congrats_msg = None
                if duration == 15 and incoming_score > 1000:
                    congrats_msg = "OUTSTANDING PERFORMANCE! (> $1000)"
                elif duration == 45 and incoming_score > 3000:
                    congrats_msg = "LEGENDARY PERFORMANCE! (> $3000)"
                elif duration == 15 and incoming_score > 500: # Boxing lower threshold
                     congrats_msg = "SOLID KNOCKOUT!"
                
                if congrats_msg:
                    st.session_state.last_round_msg = congrats_msg
                else:
                    st.session_state.last_round_msg = "OBJECTIVE COMPLETE."

                st.session_state.game_score += incoming_score
                st.session_state.game_state = 'TRIVIA'
                
                # Prepare questions (5 per round)
                available = [q for q in TRIVIA_DB if q['id'] not in st.session_state.questions_asked_ids]
                if len(available) < 5:
                    st.session_state.questions_asked_ids = []
                    available = TRIVIA_DB
                
                st.session_state.q_queue = random.sample(available, min(5, len(available)))
                
    except Exception as e:
        pass
    finally:
        st.query_params.clear()

# ==============================================================================
# 4. GAME MODULES (IMPROVED)
# ==============================================================================
def get_space_shooter_html(round_num, duration):
    difficulty = round_num * 0.5
    is_survival = "true" if duration == 9999 else "false"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; overflow: hidden; background: transparent; font-family: 'Courier New', monospace; }}
        canvas {{ display: block; margin: 0 auto; border: 2px solid #00e5ff; box-shadow: 0 0 20px rgba(0, 229, 255, 0.2); background: rgba(0,0,0,0.6); border-radius: 4px; }}
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
        let timerInterval;
        
        const player = {{ x: 400, y: 450, width: 40, height: 40, color: '#00e5ff', speed: 5 }};
        let bullets = [];
        let enemies = [];
        let particles = [];
        let stars = [];

        for(let i=0; i<50; i++) {{
            stars.push({{ x: Math.random() * canvas.width, y: Math.random() * canvas.height, size: Math.random() * 2, speed: 0.5 + Math.random() * 2 }});
        }}
        
        canvas.addEventListener('mousemove', (e) => {{
            const rect = canvas.getBoundingClientRect();
            player.x = e.clientX - rect.left;
        }});
        
        canvas.addEventListener('mousedown', () => {{
            if(!gameActive && hull > 0) {{
                gameActive = true;
                overlay.style.display = 'none';
                requestAnimationFrame(gameLoop);
                timerInterval = setInterval(() => {{ 
                    if(gameActive && !isSurvival) {{
                        timeLeft--; 
                        if(timeLeft <= 0) endGame(true);
                    }}
                }}, 1000);
            }}
            if(gameActive) bullets.push({{ x: player.x, y: player.y, speed: 10 }});
        }});

        function spawnEnemy() {{
            const rand = Math.random();
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
            
            ctx.fillStyle = 'rgba(0, 0, 0, 0.3)'; 
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = '#fff';
            stars.forEach(s => {{ 
                s.y += s.speed; 
                if(s.y > canvas.height) s.y = 0; 
                ctx.globalAlpha = Math.random();
                ctx.fillRect(s.x, s.y, s.size, s.size);
                ctx.globalAlpha = 1.0;
            }});
            
            enemyTimer += 16;
            if(enemyTimer > (800 - ({difficulty} * 100))) {{
                spawnEnemy();
                enemyTimer = 0;
            }}

            ctx.save(); 
            ctx.translate(player.x, player.y); 
            ctx.fillStyle = player.color;
            ctx.shadowBlur = 10;
            ctx.shadowColor = player.color;
            ctx.beginPath(); 
            ctx.moveTo(0, -20); ctx.lineTo(-20, 20); ctx.lineTo(0, 10); ctx.lineTo(20, 20); 
            ctx.closePath(); ctx.fill();
            ctx.shadowBlur = 0;
            ctx.fillStyle = '#FFE81F';
            ctx.beginPath(); ctx.moveTo(-5, 15); ctx.lineTo(0, 30 + Math.random()*10); ctx.lineTo(5, 15); ctx.fill();
            ctx.restore();
            
            ctx.fillStyle = '#00ff00';
            ctx.shadowBlur = 5;
            ctx.shadowColor = '#00ff00';
            for(let i = bullets.length - 1; i >= 0; i--) {{
                let b = bullets[i]; b.y -= b.speed; 
                ctx.fillRect(b.x - 2, b.y, 4, 15); 
                if(b.y < 0) bullets.splice(i, 1);
            }}
            ctx.shadowBlur = 0;
            
            for(let i = enemies.length - 1; i >= 0; i--) {{
                let e = enemies[i]; e.y += e.speed;
                
                ctx.fillStyle = e.color;
                if(e.type === 'ASTEROID') {{ 
                    ctx.beginPath(); ctx.arc(e.x + e.width/2, e.y + e.height/2, e.width/2, 0, Math.PI*2); ctx.fill(); 
                }} else {{ 
                    ctx.fillRect(e.x, e.y, e.width, e.height); 
                    ctx.fillStyle = "#000";
                    ctx.fillRect(e.x + 5, e.y + 5, e.width - 10, e.height - 10);
                    ctx.fillStyle = e.color;
                    ctx.fillRect(e.x + 12, e.y + 12, 6, 6);
                }}
                
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
            
            for(let i = particles.length - 1; i >= 0; i--) {{
                let p = particles[i]; 
                p.x += p.vx; p.y += p.vy; p.life--; 
                ctx.fillStyle = p.color; ctx.fillRect(p.x, p.y, 2, 2); 
                if(p.life <= 0) particles.splice(i, 1);
            }}
            
            ctx.fillStyle = '#00e5ff'; ctx.font = 'bold 20px Courier New'; ctx.fillText('ROI: $' + score, 20, 30);
            
            ctx.fillStyle = '#333'; ctx.fillRect(20, 45, 200, 15);
            ctx.fillStyle = hull < 30 ? '#ff0055' : '#00ff00'; ctx.fillRect(20, 45, hull * 2, 15);
            ctx.fillStyle = '#fff'; ctx.font = '12px Courier New'; ctx.fillText('HULL INTEGRITY', 230, 57);

            ctx.fillStyle = '#fff'; 
            let timerTxt = isSurvival ? "SURVIVAL MODE" : timeLeft + "s";
            ctx.font = 'bold 20px Courier New';
            ctx.fillText(timerTxt, 650, 30);

            requestAnimationFrame(gameLoop);
        }}

        function createExplosion(x, y, color, count) {{
            for(let i = 0; i < count; i++) {{ 
                particles.push({{ x: x, y: y, vx: (Math.random() - 0.5) * 10, vy: (Math.random() - 0.5) * 10, life: 10 + Math.random() * 10, color: color }}); 
            }}
        }}

        function endGame(success) {{
            gameActive = false;
            clearInterval(timerInterval);
            // Force wait to ensure UI update
            setTimeout(() => {{
                let finalScore = isSurvival ? score : (success ? score : 0);
                window.parent.location.search = '?score=' + finalScore; 
            }}, 500);
        }}
        
        const style = document.createElement('style');
        style.innerHTML = `@keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}`;
        document.head.appendChild(style);
    </script>
    </body>
    </html>
    """

def get_boxing_html(round_num, duration):
    is_survival = "true" if duration == 9999 else "false"
    # Lowered CPU HP for balance: Base 80 + (Round * 15)
    cpu_start_hp = 9999 if duration == 9999 else 80 + (round_num * 15)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; overflow: hidden; background: transparent; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Courier New', monospace; }}
        canvas {{ border: 4px solid #FFE81F; box-shadow: 0 0 30px rgba(255, 232, 31, 0.4); background: rgba(0,0,0,0.8); border-radius: 8px; }}
        #overlay {{ position: absolute; color: #FFE81F; text-align: center; pointer-events: none; width: 100%; text-shadow: 2px 2px #000; z-index: 10; }}
    </style>
    </head>
    <body>
    <div id="overlay">
        <h2 style="font-size:40px; margin-bottom: 10px;">ROUND {round_num}</h2>
        <p style="font-size:18px; color:#ff0055; background: rgba(0,0,0,0.8); display:inline-block; padding: 5px 15px;">OPPONENT: DR. DEFECT</p>
        <div style="margin-top:20px; color:#fff;">
            <p>[A] LEFT JAB  |  [S] RIGHT HOOK  |  [D] BLOCK</p>
        </div>
        <p style="color:#FFE81F; font-size: 24px; font-weight:bold; margin-top:30px; animation: blink 1s infinite;">CLICK TO FIGHT</p>
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
        let stamina = 100;
        let timeLeft = {duration};
        let isSurvival = {is_survival};
        
        let action = 'IDLE';
        let cpuAction = 'IDLE';
        let message = '';
        let msgTimer = 0;
        let msgColor = '#fff';
        
        let timerInterval;
        let cpuInterval;
        
        canvas.addEventListener('mousedown', () => {{
            if(!gameActive && playerHP > 0) {{
                gameActive = true;
                overlay.style.display = 'none';
                gameLoop();
                
                let thinkSpeed = Math.max(500, 1200 - ({round_num} * 100));
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

        function cpuThink() {{
            if(!gameActive) return;
            const rand = Math.random();
            
            if(rand > 0.6) {{
                cpuAction = 'WINDUP';
                setTimeout(() => {{
                    if(!gameActive) return;
                    cpuAction = 'PUNCH';
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
            setTimeout(() => {{
                let finalScore = score;
                if (!isSurvival && !win) finalScore = 0;
                if (isSurvival) finalScore += 500; 
                else if (win) finalScore += 1000;
                window.parent.location.search = '?score=' + finalScore;
            }}, 500);
        }}

        // --- DRAWING FUNCTIONS FOR REALISTIC FIGHTERS ---

        function drawFighter(ctx, x, y, color, pose, isFacingLeft) {{
            ctx.strokeStyle = color;
            ctx.lineWidth = 12; // Thicker limbs
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            ctx.shadowBlur = 15;
            ctx.shadowColor = color;
            
            let dir = isFacingLeft ? -1 : 1;

            // HEAD
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(x, y - 60, 18, 0, Math.PI * 2);
            ctx.fill();
            
            // TORSO (Thick line)
            ctx.beginPath();
            ctx.moveTo(x, y - 40);
            ctx.lineTo(x, y + 40);
            ctx.stroke();
            
            // LEGS (Thicker, bent knees)
            ctx.beginPath();
            ctx.moveTo(x, y + 40);
            ctx.lineTo(x - (20 * dir), y + 90); // Back leg
            ctx.moveTo(x, y + 40);
            ctx.lineTo(x + (25 * dir), y + 90); // Front leg
            ctx.stroke();
            
            // ARMS
            ctx.beginPath();
            let shoulderY = y - 30;
            
            if (pose === 'IDLE') {{
                // Guard up (Bent arms)
                ctx.moveTo(x, shoulderY);
                ctx.lineTo(x + (20 * dir), y + 10); // Elbow
                ctx.lineTo(x + (40 * dir), y - 20); // Hand
                
                // Other arm
                ctx.moveTo(x, shoulderY);
                ctx.lineTo(x + (10 * dir), y + 15);
                ctx.lineTo(x + (30 * dir), y - 10);
            }} 
            else if (pose === 'JAB' || pose === 'PUNCH') {{
                // Punching Arm Straight
                ctx.moveTo(x, shoulderY);
                ctx.lineTo(x + (80 * dir), shoulderY - 5); 
                // Guard Arm
                ctx.moveTo(x, shoulderY);
                ctx.lineTo(x + (10 * dir), y + 15);
                ctx.lineTo(x + (30 * dir), y - 10);
            }}
            else if (pose === 'HOOK') {{
                // Wide hook
                ctx.moveTo(x, shoulderY);
                ctx.quadraticCurveTo(x + (30*dir), shoulderY - 60, x + (60*dir), shoulderY);
                // Guard Arm
                ctx.moveTo(x, shoulderY);
                ctx.lineTo(x + (10 * dir), y + 15);
                ctx.lineTo(x + (30 * dir), y - 10);
            }}
            else if (pose === 'BLOCK') {{
                // Shielding face
                ctx.moveTo(x, shoulderY);
                ctx.lineTo(x + (25 * dir), shoulderY - 25);
                ctx.moveTo(x, shoulderY);
                ctx.lineTo(x + (15 * dir), shoulderY - 25);
            }}
            else if (pose === 'WINDUP') {{
                // Pull back
                ctx.moveTo(x, shoulderY);
                ctx.lineTo(x - (30 * dir), shoulderY); 
                ctx.moveTo(x, shoulderY);
                ctx.lineTo(x + (10 * dir), y); 
            }}
            
            ctx.stroke();
            ctx.shadowBlur = 0; 
        }}

        function gameLoop() {{
            if(!gameActive) return;
            requestAnimationFrame(gameLoop);
            
            // Clear
            ctx.clearRect(0,0,600,400);
            
            // Floor
            var grd = ctx.createLinearGradient(0, 300, 0, 400);
            grd.addColorStop(0, "rgba(50,50,50,0.8)");
            grd.addColorStop(1, "rgba(0,0,0,0.8)");
            ctx.fillStyle = grd;
            ctx.fillRect(0, 320, 600, 80);
            
            // Ropes
            ctx.strokeStyle = '#FFE81F';
            ctx.lineWidth = 3;
            ctx.beginPath(); ctx.moveTo(0, 100); ctx.lineTo(600, 100); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(0, 200); ctx.lineTo(600, 200); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(0, 280); ctx.lineTo(600, 280); ctx.stroke();

            // PLAYER (Blue, facing right)
            let pColor = '#00e5ff';
            if (action === 'BLOCK') pColor = '#ffffff';
            drawFighter(ctx, 200, 250, pColor, action, false);

            // OPPONENT (Red, facing left)
            let eColor = '#ff0055';
            if (cpuAction === 'BLOCK') eColor = '#aaa';
            if (cpuAction === 'WINDUP') eColor = '#ffa500';
            drawFighter(ctx, 400, 250, eColor, cpuAction, true);

            // UI
            ctx.font = 'bold 20px Courier New'; 
            ctx.fillStyle = '#00e5ff';
            ctx.fillText("YOU: " + playerHP + "%", 20, 30);
            // Stamina
            ctx.fillStyle = '#00e5ff';
            ctx.fillRect(20, 40, stamina * 1.5, 8);
            
            ctx.fillStyle = '#ff0055'; 
            ctx.textAlign = "right";
            ctx.fillText("DR. DEFECT: " + cpuHP, 580, 30);
            ctx.textAlign = "left";

            // Timer
            ctx.fillStyle = '#FFE81F'; 
            ctx.font = 'bold 40px Courier New'; 
            ctx.textAlign = "center";
            let timeTxt = isSurvival ? "∞" : timeLeft;
            ctx.fillText(timeTxt, 300, 50);
            
            // Messages
            if(msgTimer > 0) {{
                ctx.font = 'bold 30px Courier New'; 
                ctx.fillStyle = msgColor; 
                ctx.fillText(message, 300, 150); 
                msgTimer--;
            }}
            ctx.textAlign = "left"; 
        }}
        
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
            if not st.session_state.q_queue:
                available = [q for q in TRIVIA_DB if q['id'] not in st.session_state.questions_asked_ids]
                st.session_state.q_queue = random.sample(available, min(5, len(available)))
            st.rerun()
            
        if st.button("📂 INTEL VIEWER"):
            st.session_state.game_state = 'VIEWER'
            st.rerun()
            
        st.markdown("---")
        st.caption("Quality Wars v5.2 | Earth Defense")

def show_menu():
    st.markdown("# QUALITY WARS")
    st.markdown("<h3 style='text-align:center; color:#00e5ff; margin-top:-20px; letter-spacing: 8px;'>RETURN OF THE ROI</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background:rgba(0,20,40,0.8); padding:30px; border:1px solid #00e5ff; border-top: 5px solid #FFE81F; border-radius:4px; margin-bottom:30px; text-align:center; box-shadow: 0 0 50px rgba(0,229,255,0.1);">
            <p style="color: #ccc; font-size: 1.2rem; line-height: 1.6;">
                The Earth Market is under attack by <b>defects</b> and <b>audit droids</b>. 
                <br><br>
                As a Quality Officer, you must master the archives of <b>Medical Device Regulations</b>, 
                battle <b>Dr. Defect</b>, and secure the <b>Profit Margin</b>.
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
    
    # Scan for PDFs in the current directory
    # In a real app we might look recursively, but here we look in the known path or current dir
    target_dir = "aplotlib/returnrx-enterprise/returnrx-enterprise-main"
    
    # Fallback to current dir if path doesn't exist (local testing)
    if not os.path.exists(target_dir):
        target_dir = "."
        
    pdf_files = [f for f in os.listdir(target_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        st.warning("No Classified Intel (PDFs) found in the archives.")
        if st.button("BACK"):
            st.session_state.game_state = 'MENU'
            st.rerun()
        return

    file_choice = st.selectbox("SELECT FILE:", pdf_files)
    file_path = os.path.join(target_dir, file_choice)
    
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error decrypting file: {e}")

    st.write("")
    if st.button("RETURN TO BASE"):
        st.session_state.game_state = 'MENU'
        st.rerun()

def show_intel_briefing():
    dur = st.session_state.game_duration_setting
    dur_txt = "UNTIL DEATH" if dur == 9999 else f"{dur} SECONDS"
    
    if st.session_state.mode == 'CAMPAIGN':
        title = f"SECTOR {st.session_state.current_round} BRIEFING"
        msg1 = f"**OBJECTIVE:** Survive the asteroid field for **{dur_txt}**."
        msg2 = "**THREAT:** Heavy Asteroids & Defects. 100% Hull Loss = Failure."
        controls = "**CONTROLS:** Use Mouse to Move. Click to Shoot."
        btn = "INITIATE LAUNCH SEQUENCE"
    else:
        title = f"ROUND {st.session_state.current_round} WEIGH-IN"
        msg1 = f"**OBJECTIVE:** Defeat Dr. Defect in **{dur_txt}**."
        msg2 = "**THREAT:** Manage Stamina. Time blocks correctly."
        controls = "**CONTROLS:** [A] Left Jab | [S] Right Hook | [D] Block"
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
        st.markdown(controls)
    with col2: 
        st.warning(msg2)
    
    st.write("")
    if st.button(btn, type="primary"):
        st.session_state.game_state = 'GAME' if st.session_state.mode == 'CAMPAIGN' else 'BOXING_GAME'
        st.rerun()

def show_trivia_round():
    st.markdown(f"## KNOWLEDGE CHECKPOINT: ROUND {st.session_state.current_round}")
    
    # Show Congratulatory Message if it exists from the game round
    if st.session_state.last_round_msg:
        st.markdown(f"""
        <div class="result-card" style="text-align:center; border-color:#00ff00;">
            <h2 style="color:#00ff00; border:none;">{st.session_state.last_round_msg}</h2>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.last_round_msg = None # Clear it so it doesn't persist

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
        for i, q in enumerate(st.session_state.q_queue):
            st.markdown(f"##### {i+1}. {q['q']}")
            
            opts = q['options'].copy()
            random.seed(q['q']) 
            random.shuffle(opts)
            random.seed() 
            
            st.radio(f"Select Answer:", opts, key=f"q_{st.session_state.current_round}_{i}", label_visibility="collapsed")
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
                
                if q['id'] not in st.session_state.questions_asked_ids:
                    st.session_state.questions_asked_ids.append(q['id'])

            st.session_state.trivia_score += correct_count
            
            time.sleep(2) 
            
            if st.session_state.current_round < st.session_state.total_rounds:
                st.session_state.current_round += 1
                next_state = 'TRIVIA' if st.session_state.mode == 'TRAINING' else 'INTEL'
                st.session_state.game_state = next_state
                st.session_state.q_queue = []
                st.rerun()
            else:
                st.session_state.mission_status = 'SUCCESS'
                st.session_state.game_state = 'GAMEOVER'
                st.rerun()

def show_gameover():
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
