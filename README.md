# Neural Council: Autonomous AI Boardroom

The **Neural Council** is a privacy-first, multi-agent autonomous boardroom designed to stress-test your business objectives. Powered by a local **Qwen 2.5 Coder 1.5B** model via **Ollama**, this system orchestrates a dynamic debate between specialized AI agents—the CEO, CTO, and CMO—to provide deep strategic insights without your data ever leaving your machine.

---

## 🏛️ Project Overview

This application features a high-fidelity **Glassmorphism** interface and a **Decision-Gated Loop**. The agents interact with each other and only pause when your executive authority is required for final decisions or hiring new specialized nodes like a **COO**.

---

## 🛠️ Step-by-Step Installation

### 1. Prerequisites
Ensure you have the following installed on your local machine:
* **Python 3.10+**
* **Git**
* **Ollama** (Download from [ollama.com](https://ollama.com))

### 2. Clone the Repository
Open your terminal and run:
```bash
git clone https://github.com/ArkTrek/NeuralCouncil.git
cd neural-council
```

### 3. Setup Ollama and Download the Model
Start the Ollama service on your machine, then pull the specific **Qwen 2.5 Coder** model required for the council:
```bash
# In a separate terminal or background process
ollama serve

# Download the specific 1.5B model
ollama pull qwen2.5-coder:1.5b
```

### 4. Install Python Dependencies
It is recommended to use a virtual environment:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install required packages
pip install Flask Flask-SocketIO requests
```

---

## 🚀 Deployment

### Running the Application
1. Ensure **Ollama** is running in the background.
2. Execute the Flask server:
   ```bash
   python app.py
   ```
3. Open your browser and navigate to:
   `http://127.0.0.1:5000`

---

## 🎮 How to Use the Council

### 1. Initialization
Enter your name and your current business objective in the **Command Center** panel. Click **Initiate** to start the neural link.

### 2. The Decision-Gated Loop
* **Continuous Debate:** The agents will argue amongst themselves. The CTO focuses on technical moats, while the CMO pushes for growth.
* **CEO Inbox:** When the CEO reaches a point requiring your directive, the loop will pause. Open the **CEO Inbox** in the UI, provide your answer, and the council will resume.
* **Hiring Approvals:** If the CEO identifies a skill gap, they will propose hiring a new agent (e.g., a **COO**). An **Executive Decision Modal** will appear. Click **Authorize** to spawn the new agent with their own individual memory bank.

### 3. Ideas Tab
Click the **Ideas** button to view a list of unique keywords and strategies extracted in real-time from the council's discussion.

---

## 📂 Project Structure
* `app.py`: The core backend managing the SocketIO loop, individual agent memory, and Ollama API calls.
* `templates/index.html`: The Glassmorphic frontend with "Astral Night Sky Blue" styling and responsive UI.
* `static/`: (Optional) Folder for local CSS or JS assets.

---

## Snapshot
<img width="1915" height="857" alt="image" src="https://github.com/user-attachments/assets/e67ed981-1559-48b9-a3b2-8e71e5da92ef" />


---

## 📜 License & Socials
**© 2026 Made by Arpit Ramesan.**

* **GitHub:** [https://github.com/ArkTrek](https://github.com/ArkTrek)
* **LinkedIn:** [https://www.linkedin.com/in/arpitramesan/](https://www.linkedin.com/in/arpitramesan/)

---
*Note: This project is intended for local deployment and educational purposes regarding multi-agent AI orchestration.*
