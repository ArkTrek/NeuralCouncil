import time
import requests
import threading
import re
import random
from flask import Flask, render_template
from flask_socketio import SocketIO
from difflib import SequenceMatcher # To detect and block "Echoing"

# ==========================================
# 1. CONFIGURATION
# ==========================================
MAX_PUBLIC_CONTEXT = 4 # Tightened to reduce copying
OLLAMA_MODEL = "qwen2.5-coder:1.5b" 
OLLAMA_API_URL = "http://localhost:11434/api/generate"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'boardroom_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

boardroom_active = False
current_turn_index = 0 

def get_similarity(a, b):
    """Returns a score between 0 and 1 on how similar two strings are."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def sanitize_history(text):
    text = re.sub(r'###.*?\n', '', text)
    text = re.sub(r'I await your decision.*', '', text, flags=re.IGNORECASE)
    # Strip common technical phrases that the model gets stuck on
    text = re.sub(r'AI-driven digital twin system', 'the system', text, flags=re.IGNORECASE)
    return text.strip()

def enforce_variety(text, role, pool):
    """Rejects responses that echo previous agents."""
    text = text.strip()
    
    # 1. Check against the last 3 messages in the pool
    for entry in pool[-3:]:
        if get_similarity(text, entry['message']) > 0.5:
            # If too similar, trigger an emergency pivot
            pivots = {
                "CEO": "Let's ignore the previous point. I want to talk about global expansion.",
                "CTO": "Actually, the real issue isn't scalability—it's data security.",
                "CMO": "We are targeting the wrong demographic. Let's look at Gen Z specifically.",
                "COO": "The roadmap is unrealistic. We need to cut 40% of these features."
            }
            return pivots.get(role, "I disagree with the current direction. Let's try a new approach.")
    
    # 2. Basic Brevity
    sentences = re.split(r'(?<=[.!?]) +|\n', text)
    clean = [s.strip() for s in sentences if len(s) > 10][:2]
    return " ".join(clean) if clean else "Let's move to the next phase."

def generate_llm_response(prompt, role):
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 1.1, # High temperature to force the 1.5B model to be creative
                "repeat_penalty": 2.0, # Massive penalty to stop loops
                "num_predict": 70,
                "seed": random.randint(1, 99999),
                "stop": ["CEO:", "CTO:", "CMO:", "COO:", "USER:", "###"]
            }
        }
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        raw = response.json().get("response", "")
        return enforce_variety(raw, role, public_memory.chat_pool)
    except Exception:
        return f"The {role} suggests a tactical pivot."

# ==========================================
# 2. AGENT DEFINITIONS
# ==========================================
class Agent:
    def __init__(self, role, persona):
        self.role = role
        self.persona = persona
        self.internal_history = [] 

    def think_and_speak(self, directive=""):
        if not boardroom_active: return
        
        socketio.emit('status', {'msg': f'{self.role} is interjecting...'})
        others_context = public_memory.get_public_context(excluding_agent=self.role)
        
        prompt = f"""
        Profile: {self.persona}
        History: {others_context}

        INSTRUCTION: {directive}
        
        MANDATORY: 
        - DO NOT REPEAT what others said. 
        - Use your own unique vocabulary.
        - If you find a gap in execution, the CEO can say 'HIRE: COO'.
        
        {self.role} (2 unique sentences):"""
        
        response = generate_llm_response(prompt, self.role)
        self.internal_history.append(response)
        public_memory.add_to_pool(self.role, response)
        return response

class BoardroomMemory:
    def __init__(self):
        self.user_profile = {}; self.chat_pool = [] 
    def add_to_pool(self, role, msg):
        self.chat_pool.append({"agent": role, "message": msg})
        socketio.emit('new_message', {"agent": role, "message": msg})
    def get_public_context(self, excluding_agent):
        context = ""
        others = [m for m in self.chat_pool if m['agent'] != excluding_agent]
        for entry in others[-MAX_PUBLIC_CONTEXT:]:
            context += f"{entry['agent']}: {sanitize_history(entry['message'])}\n"
        return context

public_memory = BoardroomMemory()
board_members = [
    Agent("CMO", "Marketing specialist. Focused on branding and users."),
    Agent("CTO", "Tech specialist. Focused on local AI and code."),
    Agent("CEO", "Visionary. Focused on strategy and hiring experts.")
]

# ==========================================
# 3. DECISION-GATED LOOP
# ==========================================
def continuous_boardroom_loop(user_data=None):
    global boardroom_active, current_turn_index
    boardroom_active = True
    
    if user_data is not None:
        public_memory.user_profile = {"bio": user_data.get('bio', '')}
        public_memory.chat_pool = []; current_turn_index = 0
        for agent in board_members: agent.internal_history = []
        public_memory.add_to_pool("SYSTEM", "Neural Session Started.")
    
    while boardroom_active:
        current_agent = board_members[current_turn_index % len(board_members)]
        
        # Determine specialized directive
        if current_agent.role == "CEO":
            directive = "If we are debating too much without doing, propose a 'HIRE: COO' to fix it. Otherwise, ask the User a '?' question."
        elif current_agent.role == "COO":
            directive = "Critique the plan's feasibility. Focus on logistics and the 30-day timeline."
        else:
            directive = "Propose a bold, unique specific solution based on your expertise."

        response_text = current_agent.think_and_speak(directive)
        current_turn_index += 1
        
        # --- DECISION PAUSES ---
        if "HIRE:" in response_text.upper():
            boardroom_active = False
            role = re.search(r'HIRE:\s*(.+)', response_text, re.IGNORECASE).group(1)
            socketio.emit('agent_proposal', {"role": role})
            break

        if current_agent.role == "CEO" and "?" in response_text:
            boardroom_active = False
            socketio.emit('new_question', {"id": random.randint(1,99), "text": response_text})
            break
            
        time.sleep(5)

# ==========================================
# 4. RESUME HANDLERS
# ==========================================
@app.route('/')
def index(): return render_template('index.html')

@socketio.on('start_council')
def handle_start(data):
    if not boardroom_active: socketio.start_background_task(continuous_boardroom_loop, data)

@socketio.on('approve_agent')
def handle_hire(data):
    global boardroom_active
    if data.get('action') == 'approve':
        role = data.get('role')
        # Create the new COO with its own unique memory
        new_agent = Agent(role, f"Expert in {role}. You focus on timelines and execution.")
        board_members.insert(-1, new_agent)
        public_memory.add_to_pool("SYSTEM", f"*** EXECUTIVE ACTION: {role} has joined with a clean memory bank. ***")
    
    # The moment you approve, the chat stops being "Continuous" and waits for this trigger to resume
    socketio.start_background_task(continuous_boardroom_loop, None)

@socketio.on('answer_question')
def handle_answer(data):
    public_memory.add_to_pool("USER (YOU)", f"[Directive]: {data['answer']}")
    socketio.start_background_task(continuous_boardroom_loop, None)

@socketio.on('user_input')
def handle_input(data):
    public_memory.add_to_pool("USER (YOU)", data['msg'])
    socketio.start_background_task(continuous_boardroom_loop, None)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)