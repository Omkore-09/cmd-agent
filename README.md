# CMD AI Agent — Natural Language Shell

> Speak to your Windows CMD in plain English.  
> The agent thinks out loud (Chain of Thought), then runs the right commands.

---

## ✨ Features

| Feature | Details |
|---|---|
| Natural language → CMD | "create a folder called projects on desktop" just works |
| Chain of Thought | Prints every reasoning step before executing |
| Full CRUD | Create / Read / Update / Delete files, folders, content |
| All CMD commands | System info, networking, processes, search, file ops… |
| Safe Mode | Confirms before risky/destructive operations |
| Multi-turn memory | Remembers context across queries in a session |
| 3 free LLM providers | Gemini · Groq · Ollama (local) |

---

## 📁 Project Files

```
cmd_ai_agent/
├── cmd_agent.py      ← main entry point (run this)
├── llm_client.py     ← Gemini / Groq / Ollama client
├── config.py         ← all settings & validation
├── requirements.txt  ← pip dependencies
├── .env.example      ← copy to .env and fill in your key
├── setup.bat         ← one-click setup on Windows
└── README.md         ← this file
```

---

## 🚀 Quick Start

### Step 1 — Install Python
Download from https://www.python.org/downloads/  
✅ Check **"Add Python to PATH"** during install.

### Step 2 — Run Setup
Double-click **`setup.bat`**  
*(or in CMD: `setup.bat`)*

It will install dependencies and create your `.env` file.

### Step 3 — Get a FREE API Key

#### Option A — Google Gemini *(recommended)*
1. Go to **https://aistudio.google.com/apikey**
2. Sign in with a Google account (no credit card)
3. Click **"Create API key"**
4. Paste it in `.env` as `GEMINI_API_KEY=...`

Free tier: **15 requests/min · 1 million tokens/day**

---

#### Option B — Groq *(fastest inference)*
1. Go to **https://console.groq.com/keys**
2. Create a free account
3. Generate an API key
4. In `.env` set:
   ```
   LLM_PROVIDER=groq
   GROQ_API_KEY=your_key_here
   ```

Free tier: **30 requests/min · 6 000 requests/day**

---

#### Option C — Ollama *(100 % local, no account, works offline)*
1. Download from **https://ollama.com/download**
2. Install and open a terminal
3. Run: `ollama pull llama3.2`
4. In `.env` set:
   ```
   LLM_PROVIDER=ollama
   ```
   (No API key needed)

---

### Step 4 — Configure `.env`
Open `.env` in Notepad and fill in your key:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...your_key_here...
```

### Step 5 — Run the Agent
```
python cmd_agent.py
```

---

## 💬 Usage Examples

Once running, just type in plain English:

```
[cmd_ai_agent] ❯ create a folder called projects on the desktop
[cmd_ai_agent] ❯ list all files in the current directory
[cmd_ai_agent] ❯ create a text file named notes.txt with "Hello World" inside
[cmd_ai_agent] ❯ show contents of notes.txt
[cmd_ai_agent] ❯ rename notes.txt to journal.txt
[cmd_ai_agent] ❯ copy config.txt to the backup folder
[cmd_ai_agent] ❯ delete all .log files in C:\Logs
[cmd_ai_agent] ❯ show system information
[cmd_ai_agent] ❯ list all running processes
[cmd_ai_agent] ❯ ping google.com
[cmd_ai_agent] ❯ show my network configuration
[cmd_ai_agent] ❯ find all .py files under C:\Users\Me
[cmd_ai_agent] ❯ search for the word "error" in all .txt files here
```

### Special built-in commands
| Command | Action |
|---|---|
| `help` | Show example queries |
| `history` | Show queries from this session |
| `clear` | Clear the screen |
| `exit` / `quit` | Exit the agent |

---

## 🧠 Chain of Thought Output

For every query the agent prints 5 reasoning steps before running anything:

```
🧠 STEP 1 — Understanding Intent
   💭 The user wants to create a directory named "projects" on the Desktop
   → Goal: Create a new folder on the Desktop

🔍 STEP 2 — Identifying Operation
   → Type: CREATE
   → Targets: Desktop\projects

📋 STEP 3 — Planning Commands
   • Use mkdir with the full Desktop path from %USERPROFILE%

🛡️  STEP 4 — Safety Assessment
   → Risk: ✅ LOW

⚙️  STEP 5 — Final Commands
   $ mkdir "%USERPROFILE%\Desktop\projects"

══════════════════════════════
🚀 EXECUTING COMMANDS
  [1/1] Running…
  $ mkdir "%USERPROFILE%\Desktop\projects"
  ✅ Success
══════════════════════════════
✨ ALL DONE
```

---

## ⚙️ Configuration Reference (`.env`)

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `gemini` | `gemini` · `groq` · `ollama` |
| `GEMINI_API_KEY` | — | Your Gemini key |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Model name |
| `GROQ_API_KEY` | — | Your Groq key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Model name |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Local model name |
| `SAFE_MODE` | `true` | Confirm before risky commands |
| `COMMAND_TIMEOUT` | `30` | Seconds before timeout |
| `MAX_HISTORY` | `20` | Messages kept in memory |

---

## 🔒 Safe Mode

With `SAFE_MODE=true` (default) the agent:
- Warns before commands like `del`, `rmdir /s`, `format`
- Asks for confirmation before medium/high-risk operations
- Never silently deletes system directories

Set `SAFE_MODE=false` only if you know what you're doing.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `GEMINI_API_KEY is not set` | Edit `.env` and add your key |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Colors not showing | Run `pip install colorama` |
| Ollama connection error | Run `ollama serve` in another terminal |
| Command times out | Increase `COMMAND_TIMEOUT` in `.env` |

---

## 📜 License
MIT — use freely.
