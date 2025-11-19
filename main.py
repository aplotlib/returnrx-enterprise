import streamlit as st
import streamlit.components.v1 as components
import random
import time

# ==============================================================================
# 1. CONFIGURATION & CSS (THEME: SPACE / NEON)
# ==============================================================================
st.set_page_config(
    page_title="Quality Wars",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for the Star Wars / Arcade aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    
    .stApp {
        background-color: #000000;
        background-image: radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 40px),
        radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 30px),
        radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 40px),
        radial-gradient(rgba(255,255,255,.4), rgba(255,255,255,.1) 2px, transparent 30px);
        background-size: 550px 550px, 350px 350px, 250px 250px, 150px 150px;
        background-position: 0 0, 40px 60px, 130px 270px, 70px 100px;
        color: #FFE81F;
    }
    
    h1, h2, h3 {
        font-family: 'Press Start 2P', cursive;
        color: #FFE81F;
        text-shadow: 0 0 10px #FFE81F;
        text-align: center;
    }
    
    .stButton>button {
        font-family: 'Press Start 2P', cursive;
        color: #000 !important;
        background-color: #FFE81F !important;
        border: 2px solid #fff;
        width: 100%;
        padding: 15px;
    }
    .stButton>button:hover {
        background-color: #fff !important;
        box-shadow: 0 0 15px #FFE81F;
    }
    
    .score-card {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid #32CD32;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-family: 'Courier New', monospace;
        color: #32CD32;
    }
    
    .trivia-box {
        background: rgba(20, 20, 40, 0.9);
        border: 2px solid #00BFFF;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. GAME LOGIC (JAVASCRIPT/CANVAS)
# ==============================================================================
def get_game_html(round_num):
    """
    Generates the HTML5 Canvas game.
    Note: Since Streamlit allows limited bi-directional communication in standard mode,
    the game displays the score at the end, and we ask the user to 'transmit' it.
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; overflow: hidden; background: transparent; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Courier New', monospace; }}
        canvas {{ border: 4px solid #FFE81F; box-shadow: 0 0 20px #FFE81F; background: rgba(0,0,0,0.8); }}
        #overlay {{ position: absolute; color: white; text-align: center; font-size: 24px; pointer-events: none; }}
    </style>
    </head>
    <body>
    <div id="overlay">MISSION: DEFEND QUALITY CONTROL<br>Move mouse to fly & shoot<br>Click to start</div>
    <canvas id="gameCanvas" width="800" height="500"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const overlay = document.getElementById('overlay');
        
        let gameActive = false;
        let score = 0;
        let timeLeft = 30; // 30 second rounds
        let lastTime = Date.now();
        
        // Game Objects
        const player = {{ x: 400, y: 450, width: 40, height: 40, color: '#00BFFF' }};
        let bullets = [];
        let enemies = [];
        let particles = [];
        
        // Controls
        canvas.addEventListener('mousemove', (e) => {{
            const rect = canvas.getBoundingClientRect();
            player.x = e.clientX - rect.left;
            // Clamp to screen
            if(player.x < 0) player.x = 0;
            if(player.x > canvas.width) player.x = canvas.width;
        }});
        
        canvas.addEventListener('mousedown', () => {{
            if(!gameActive && timeLeft > 0) {{
                gameActive = true;
                overlay.style.display = 'none';
                gameLoop();
                setInterval(spawnEnemy, 800 - ({round_num} * 100)); // Harder each round
                setInterval(updateTimer, 1000);
            }}
        }});

        function spawnEnemy() {{
            if(!gameActive) return;
            const size = 30;
            enemies.push({{
                x: Math.random() * (canvas.width - size),
                y: -size,
                width: size,
                height: size,
                speed: 2 + ({round_num} * 0.5),
                type: Math.random() > 0.8 ? 'DEFECT' : 'ALIEN'
            }});
        }}

        function updateTimer() {{
            if(!gameActive) return;
            timeLeft--;
            if(timeLeft <= 0) {{
                gameActive = false;
                ctx.fillStyle = "rgba(0,0,0,0.8)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#32CD32";
                ctx.font = "40px Courier New";
                ctx.textAlign = "center";
                ctx.fillText("MISSION COMPLETE", canvas.width/2, canvas.height/2 - 40);
                ctx.fillStyle = "white";
                ctx.font = "20px Courier New";
                ctx.fillText("FINAL BATTLE SCORE: " + score, canvas.width/2, canvas.height/2 + 20);
                ctx.fillStyle = "#FFE81F";
                ctx.fillText("--> SCROLL DOWN TO ENTER SCORE <--", canvas.width/2, canvas.height/2 + 60);
            }}
        }}

        function gameLoop() {{
            if(!gameActive) return;
            requestAnimationFrame(gameLoop);
            
            // Clear
            ctx.fillStyle = 'rgba(0, 0, 0, 0.3)'; // Trail effect
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Player (Ship)
            ctx.fillStyle = player.color;
            ctx.beginPath();
            ctx.moveTo(player.x, player.y);
            ctx.lineTo(player.x - 20, player.y + 40);
            ctx.lineTo(player.x + 20, player.y + 40);
            ctx.fill();
            
            // Auto fire
            if(Date.now() % 10 === 0) {{
                bullets.push({{ x: player.x, y: player.y, speed: 10 }});
            }}
            
            // Update Bullets
            for(let i = bullets.length - 1; i >= 0; i--) {{
                let b = bullets[i];
                b.y -= b.speed;
                ctx.fillStyle = '#FF0000';
                ctx.fillRect(b.x - 2, b.y, 4, 10);
                if(b.y < 0) bullets.splice(i, 1);
            }}
            
            // Update Enemies
            for(let i = enemies.length - 1; i >= 0; i--) {{
                let e = enemies[i];
                e.y += e.speed;
                
                // Draw Enemy
                ctx.fillStyle = e.type === 'DEFECT' ? '#FF00FF' : '#00FF00';
                ctx.fillRect(e.x, e.y, e.width, e.height);
                
                // Draw Text on Enemy
                ctx.fillStyle = 'black';
                ctx.font = '10px Arial';
                ctx.fillText(e.type === 'DEFECT' ? 'BUG' : 'NC', e.x + 5, e.y + 20);
                
                // Collision with Player
                if(Math.abs(player.x - e.x) < 30 && Math.abs(player.y - e.y) < 30) {{
                    score -= 50; // Penalty
                    enemies.splice(i, 1);
                    createExplosion(e.x, e.y, '#FF0000');
                }}
                
                // Collision with Bullets
                for(let j = bullets.length - 1; j >= 0; j--) {{
                    let b = bullets[j];
                    if(b.x > e.x && b.x < e.x + e.width && b.y > e.y && b.y < e.y + e.height) {{
                        score += 100;
                        createExplosion(e.x, e.y, '#FFA500');
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
                ctx.fillStyle = p.color;
                ctx.fillRect(p.x, p.y, 3, 3);
                if(p.life <= 0) particles.splice(i, 1);
            }}
            
            // HUD
            ctx.fillStyle = 'white';
            ctx.font = '20px Courier New';
            ctx.textAlign = 'left';
            ctx.fillText('SCORE: ' + score, 20, 30);
            ctx.fillText('TIME: ' + timeLeft, 20, 60);
            ctx.fillText('WAVE: ' + {round_num}, 20, 90);
        }}

        function createExplosion(x, y, color) {{
            for(let i = 0; i < 10; i++) {{
                particles.push({{
                    x: x,
                    y: y,
                    vx: (Math.random() - 0.5) * 10,
                    vy: (Math.random() - 0.5) * 10,
                    life: 20,
                    color: color
                }});
            }}
        }}
    </script>
    </body>
    </html>
    """

# ==============================================================================
# 3. TRIVIA DATABASE
# ==============================================================================
TRIVIA_DB = [
    {
        "q": "What type of battery is in the Vive MOB1027 4-wheel mobility scooter?",
        "options": ["Nuclear Fusion Cell", "Lead Acid (Sealed)", "Lithium-Ion", "AA Duracell"],
        "correct": "Lead Acid (Sealed)",
        "feedback": "Correct! The MOB1027 uses two 12V 12AH Sealed Lead Acid batteries."
    },
    {
        "q": "What does 'CAPA' stand for in Quality Management?",
        "options": ["Captain America Protection Agency", "Corrective and Preventative Action", "Cost Analysis Per Asset", "Customer Acquisition Plan A"],
        "correct": "Corrective and Preventative Action",
        "feedback": "Correct! CAPA is fundamental for eliminating the causes of non-conformities."
    },
    {
        "q": "What does TQM stand for?",
        "options": ["Total Quality Management", "The Quality Man", "Total Quantity Marketing", "Technological Quality Metrics"],
        "correct": "Total Quality Management",
        "feedback": "Correct! TQM describes a management approach to long-term success through customer satisfaction."
    },
    {
        "q": "What is an OA knee brace designed to treat?",
        "options": ["Over Active Knees", "Osteoarthritis", "Open Air Exposure", "Only Athletes"],
        "correct": "Osteoarthritis",
        "feedback": "Correct! OA stands for Osteoarthritis. The brace offloads pressure from the affected compartment."
    },
    {
        "q": "Which ISO standard specifically governs Medical Devices?",
        "options": ["ISO 9001", "ISO 13485", "ISO 14001", "ISO 27001"],
        "correct": "ISO 13485",
        "feedback": "Correct! ISO 13485 specifies requirements for a quality management system for medical devices."
    },
    {
        "q": "In the 5S methodology, what does the first 'S' stand for?",
        "options": ["Shine", "Sort", "Sustain", "Safety"],
        "correct": "Sort",
        "feedback": "Correct! Sort (Seiri) involves removing unnecessary items from the workspace."
    }
]

# ==============================================================================
# 4. APP STATE MANAGEMENT
# ==============================================================================
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'MENU' # MENU, GAME, TRIVIA, GAMEOVER
if 'current_round' not in st.session_state:
    st.session_state.current_round = 1
if 'trivia_score' not in st.session_state:
    st.session_state.trivia_score = 0
if 'game_score' not in st.session_state:
    st.session_state.game_score = 0
if 'total_rounds' not in st.session_state:
    st.session_state.total_rounds = 3 # Number of rounds to play
if 'questions_asked' not in st.session_state:
    st.session_state.questions_asked = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = None

# ==============================================================================
# 5. APPLICATION PAGES
# ==============================================================================

def show_menu():
    st.markdown("# QUALITY WARS")
    st.markdown("### Episode IV: A New Standard")
    
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("""
        <div style="text-align: justify; color: #FFE81F; font-family: 'Courier New'; padding: 20px;">
        It is a dark time for the Returns Department. <br><br>
        Defective products and lack of knowledge have infiltrated the galaxy. 
        As a Quality Jedi, you must pilot your ship through fields of asteroids and non-conformities (NCs).<br><br>
        <b>THE RULES:</b><br>
        1. <b>THE BATTLE (10%):</b> Survive 30 seconds, shoot defects.<br>
        2. <b>THE KNOWLEDGE (90%):</b> Answer technical trivia correctly.<br>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("START MISSION"):
            st.session_state.game_state = 'GAME'
            st.session_state.current_round = 1
            st.session_state.trivia_score = 0
            st.session_state.game_score = 0
            st.session_state.questions_asked = []
            st.rerun()

def show_game():
    st.markdown(f"## ROUND {st.session_state.current_round}: DEFEND THE WAREHOUSE")
    st.caption("INSTRUCTIONS: Click the game window below to activate controls. Survive for 30s.")
    
    # Render the HTML5 Game
    components.html(get_game_html(st.session_state.current_round), height=520)
    
    st.markdown("---")
    st.markdown("### 📡 TRANSMIT BATTLE DATA")
    
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        # Since we can't easily get the JS variable back in pure Streamlit without plugins,
        # we ask the user to report the number shown on the "Mission Complete" screen.
        reported_score = st.number_input("Enter the Score shown on your HUD:", min_value=0, step=100)
        
        if st.button("LOCK IN SCORE & PROCEED"):
            st.session_state.game_score += reported_score
            # Select a random question not yet asked
            available_q = [q for q in TRIVIA_DB if q not in st.session_state.questions_asked]
            if not available_q:
                available_q = TRIVIA_DB # Reset if we run out
            
            st.session_state.current_question = random.choice(available_q)
            st.session_state.questions_asked.append(st.session_state.current_question)
            
            st.session_state.game_state = 'TRIVIA'
            st.rerun()

def show_trivia():
    st.markdown(f"## KNOWLEDGE CHECKPOINT {st.session_state.current_round}")
    
    q_data = st.session_state.current_question
    
    st.markdown(f"""
    <div class="trivia-box">
        <h3 style="color:white;">{q_data['q']}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Display Options
    options = q_data['options']
    random.shuffle(options) # Randomize order
    
    # Use a form to hold state until submission
    with st.form("trivia_form"):
        selected = st.radio("Select the correct protocol:", options)
        submitted = st.form_submit_button("SUBMIT ANSWER")
        
        if submitted:
            if selected == q_data['correct']:
                st.balloons()
                st.success("✅ CORRECT! The Force is strong with this one.")
                st.info(q_data['feedback'])
                st.session_state.trivia_score += 1
            else:
                st.error(f"❌ INCORRECT. The correct answer was: {q_data['correct']}")
                st.warning(q_data['feedback'])
            
            # Wait a moment then show button to next
            time.sleep(1) 
            st.session_state.round_complete = True

    if st.session_state.get('round_complete', False):
        if st.button("NEXT SECTOR"):
            st.session_state.round_complete = False
            if st.session_state.current_round < st.session_state.total_rounds:
                st.session_state.current_round += 1
                st.session_state.game_state = 'GAME'
            else:
                st.session_state.game_state = 'GAMEOVER'
            st.rerun()

def show_gameover():
    st.markdown("# MISSION DEBRIEF")
    
    # Calculations
    # Trivia is 90% of the score. Total 3 rounds. Max trivia score = 3.
    # Game score is 10% of the score. Let's normalize 5000 pts as "max" game score.
    
    trivia_pct = (st.session_state.trivia_score / st.session_state.total_rounds) * 100
    game_pct = min((st.session_state.game_score / 5000) * 100, 100) # Cap at 100%
    
    final_score = (trivia_pct * 0.90) + (game_pct * 0.10)
    
    # Determine Rank
    if final_score >= 90:
        rank = "GRAND MASTER OF QUALITY"
        img = "🏆"
        color = "#32CD32"
    elif final_score >= 70:
        rank = "QUALITY KNIGHT"
        img = "⚔️"
        color = "#00BFFF"
    else:
        rank = "QUALITY PADAWAN"
        img = "🧹"
        color = "#FFA500"
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown(f"""
        <div class="score-card">
            <h2>FINAL SCORE</h2>
            <h1 style="font-size: 60px; color: {color};">{final_score:.1f}%</h1>
            <h3>RANK: {rank} {img}</h3>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("### PERFORMANCE BREAKDOWN")
        st.write(f"**Trivia Accuracy (90% Weight):** {st.session_state.trivia_score}/{st.session_state.total_rounds} Correct")
        st.progress(trivia_pct / 100)
        
        st.write(f"**Battle Performance (10% Weight):** {st.session_state.game_score} pts")
        st.progress(game_pct / 100)

    st.markdown("---")
    if st.button("RESTART TRAINING"):
        st.session_state.game_state = 'MENU'
        st.rerun()

# ==============================================================================
# 6. MAIN CONTROLLER
# ==============================================================================
if st.session_state.game_state == 'MENU':
    show_menu()
elif st.session_state.game_state == 'GAME':
    show_game()
elif st.session_state.game_state == 'TRIVIA':
    show_trivia()
elif st.session_state.game_state == 'GAMEOVER':
    show_gameover()
