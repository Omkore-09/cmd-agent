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
| LLM providers |  Groq  |

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
