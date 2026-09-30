"""
CMD AI Agent - Natural Language Command Executor
Chain-of-Thought powered Windows CMD agent
"""

import os
import sys
import json
import subprocess
import time
import re
import platform
from datetime import datetime
from config import Config
from llm_client import LLMClient


try:
    import colorama
    colorama.init(autoreset=True)
    C = {
        'reset':   '\033[0m',
        'bold':    '\033[1m',
        'blue':    '\033[94m',
        'cyan':    '\033[96m',
        'green':   '\033[92m',
        'yellow':  '\033[93m',
        'red':     '\033[91m',
        'magenta': '\033[95m',
        'white':   '\033[97m',
        'gray':    '\033[90m',
    }
except ImportError:
    C = {k: '' for k in ['reset','bold','blue','cyan','green','yellow','red','magenta','white','gray']}



class CMDAgent:
    def __init__(self):
        self.config = Config()
        errors = self.config.validate()
        if errors:
            self._print(f"❌ Config Error: {errors[0]}", 'red')
            self._print("   Please edit your .env file and add an API key.", 'yellow')
            sys.exit(1)

        self.llm      = LLMClient(self.config)
        self.history  = []
        self.current_dir = os.getcwd()


    def _c(self, text, *names):
        """Apply color codes."""
        code = ''.join(C.get(n, '') for n in names)
        return f"{code}{text}{C['reset']}"

    def _print(self, text, *colors):
        print(self._c(text, *colors))

    def _typewrite(self, text, delay=0.012):
        """Print text character by character (typewriter effect)."""
        for ch in text:
            sys.stdout.write(self._c(ch, 'white'))
            sys.stdout.flush()
            time.sleep(delay)
        print()

    def _divider(self, char='─', length=68, color='gray'):
        print(self._c(char * length, color))

    def _step_header(self, num, emoji, title, color='cyan'):
        print()
        print(self._c(f"  {emoji}  STEP {num}  ──  {title}", color, 'bold'))

    def _step_line(self, icon, text, color='white', indent=6):
        print(self._c(f"{'':>{indent}}{icon} {text}", color))

    # ── System context for prompts ────────────────────────────────

    def _system_context(self):
        return (
            f"Current Directory : {self.current_dir}\n"
            f"OS                : Windows (CMD)\n"
            f"Date/Time         : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Username          : {os.environ.get('USERNAME', 'Unknown')}\n"
            f"UserProfile       : {os.environ.get('USERPROFILE', 'C:\\Users\\User')}\n"
            f"Desktop           : {os.path.join(os.environ.get('USERPROFILE',''), 'Desktop')}\n"
        )

    def _system_prompt(self):
        return f"""You are an expert Windows CMD command interpreter.
Your task: convert natural language requests into precise CMD commands using step-by-step chain-of-thought reasoning.

SYSTEM CONTEXT:
{self._system_context()}

RULES:
- Generate ONLY valid Windows CMD (not PowerShell) commands
- Wrap paths that may contain spaces in double quotes
- Use env vars like %USERPROFILE%, %TEMP%, %APPDATA% when appropriate
- Mark destructive operations (del, rmdir /s, format) as high risk
- For ambiguous requests, choose the safest interpretation
- Prefer absolute paths over relative ones

CRUD → CMD MAPPING:
  CREATE : mkdir, echo > file.txt, type nul > file.txt, copy nul file.txt
  READ   : type, dir, dir /s /b, findstr, more, tree
  UPDATE : echo >> file.txt (append), copy /y, ren, move, attrib
  DELETE : del, rmdir /s /q, rd

RESPOND WITH VALID JSON ONLY — no markdown fences, no extra text:
{{
  "steps": [
    {{
      "step": 1,
      "title": "Understanding Intent",
      "thinking": "<detailed analysis of what the user wants>",
      "conclusion": "<one-line goal statement>"
    }},
    {{
      "step": 2,
      "title": "Identifying Operation",
      "thinking": "<what category of operation is this>",
      "operation_type": "CREATE|READ|UPDATE|DELETE|SYSTEM|NETWORK|OTHER",
      "targets": ["<file/folder/resource involved>"]
    }},
    {{
      "step": 3,
      "title": "Planning Commands",
      "thinking": "<reasoning about which commands and why>",
      "command_plan": ["<explanation of command 1>", "<explanation of command 2>"]
    }},
    {{
      "step": 4,
      "title": "Safety Assessment",
      "thinking": "<evaluate risks>",
      "risk_level": "low|medium|high",
      "risks": ["<specific risk>"],
      "needs_confirmation": false
    }},
    {{
      "step": 5,
      "title": "Final Commands",
      "thinking": "<finalizing exact syntax>",
      "commands": ["<exact cmd command 1>", "<exact cmd command 2>"]
    }}
  ],
  "final_commands": ["<exact cmd command 1>", "<exact cmd command 2>"],
  "summary": "<one-line description of what will happen>",
  "expected_output": "<what user should expect to see>"
}}"""

    # ── Chain-of-Thought display ──────────────────────────────────

    def _display_cot(self, data):
        cfg = [
            (1, "🧠", "blue"),
            (2, "🔍", "magenta"),
            (3, "📋", "cyan"),
            (4, "🛡️ ", "yellow"),
            (5, "⚙️ ", "green"),
        ]

        for step_data in data.get("steps", []):
            n     = step_data.get("step", 0)
            title = step_data.get("title", f"Step {n}")
            _, emoji, color = cfg[n - 1] if 1 <= n <= 5 else (n, "📌", "white")

            self._step_header(n, emoji, title, color)

            if "thinking" in step_data:
                sys.stdout.write(self._c("        💭 ", 'gray'))
                self._typewrite(step_data["thinking"], delay=0.008)

            # Per-step extras
            if "conclusion" in step_data:
                self._step_line("→", step_data["conclusion"], 'cyan')

            if "operation_type" in step_data:
                self._step_line("→", f"Type: {step_data['operation_type']}", 'magenta')

            if step_data.get("targets"):
                self._step_line("→", f"Targets: {', '.join(step_data['targets'])}", 'white')

            for plan in step_data.get("command_plan", []):
                self._step_line("•", plan, 'gray')

            if "risk_level" in step_data:
                icons = {"low": "✅ LOW", "medium": "⚠️  MEDIUM", "high": "🚨 HIGH"}
                rl_color = {"low": "green", "medium": "yellow", "high": "red"}
                rl = step_data["risk_level"]
                self._step_line("→", f"Risk: {icons.get(rl, rl)}", rl_color.get(rl, "white"))
                for r in step_data.get("risks", []):
                    self._step_line("  ⚠", r, 'yellow')

            for cmd in step_data.get("commands", []):
                self._step_line("$", cmd, 'green')

            time.sleep(0.2)


    _DANGEROUS = [
        r'\bformat\b', r'\bdiskpart\b',
        r'\brd\s+/s\s+/q\s+[a-zA-Z]:\\',
        r'\brmdir\s+/s\s+/q\s+[a-zA-Z]:\\',
        r'\bdel\s+/[sfSF].*\*',
        r'del\s+.*C:\\Windows',
    ]

    def _is_dangerous(self, cmd):
        return any(re.search(p, cmd, re.IGNORECASE) for p in self._DANGEROUS)

    def _exec_one(self, command):
        """Execute one CMD command; handle 'cd' specially."""
        command = command.strip()

        cd_m = re.match(r'^cd\s+(.+)$', command, re.IGNORECASE)
        if cd_m:
            target = cd_m.group(1).strip().strip('"')
            if not os.path.isabs(target):
                target = os.path.join(self.current_dir, target)
            target = os.path.normpath(target)
            if os.path.isdir(target):
                self.current_dir = target
                return True, f"Directory changed to: {target}"
            return False, f"Directory not found: {target}"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.config.COMMAND_TIMEOUT,
                cwd=self.current_dir,
                encoding='utf-8',
                errors='replace'
            )
            out = result.stdout.strip()
            err = result.stderr.strip()

            if result.returncode == 0:
                return True, out or "(no output — command ran successfully)"
            else:
                return False, err or f"Exit code {result.returncode}"
        except subprocess.TimeoutExpired:
            return False, f"Timed out after {self.config.COMMAND_TIMEOUT}s"
        except Exception as exc:
            return False, str(exc)

    def _run_commands(self, commands):
        """Run list of commands; display outputs."""
        print()
        self._divider('═', color='green')
        self._print("  🚀  EXECUTING COMMANDS", 'green', 'bold')
        self._divider('═', color='green')

        all_ok = True

        for i, cmd in enumerate(commands, 1):
            print()
            self._print(f"  [{i}/{len(commands)}]  Running command…", 'yellow')
            self._print(f"  $ {cmd}", 'white', 'bold')

            # Danger check
            if self.config.SAFE_MODE and self._is_dangerous(cmd):
                self._print("\n  🚨  DANGEROUS COMMAND DETECTED!", 'red', 'bold')
                ans = input(self._c("  Proceed anyway? (yes / no): ", 'red'))
                if ans.strip().lower() not in ('yes', 'y'):
                    self._print("  ⏭️   Skipped.", 'yellow')
                    continue

            ok, output = self._exec_one(cmd)

            if ok:
                self._print("\n  📊  OUTPUT:", 'green')
                for line in output.split('\n'):
                    print(self._c(f"     {line}", 'white'))
                self._print("\n  ✅  Success", 'green')
            else:
                self._print("\n  ❌  ERROR:", 'red')
                print(self._c(f"     {output}", 'red'))
                all_ok = False

        return all_ok


    def _parse(self, raw):
        raw = raw.strip()
        raw = re.sub(r'```json\s*', '', raw)
        raw = re.sub(r'```\s*',     '', raw)
        raw = raw.strip()
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            return json.loads(m.group())
        raise ValueError("LLM did not return JSON")


    def process(self, user_input):
        print()
        self._divider('═', color='cyan')
        self._print(f"\n  🎯  Query: \"{user_input}\"", 'cyan', 'bold')
        self._divider('─')

        # --- LLM call ---
        self._print("\n  🤖  AI is thinking…", 'yellow')
        msgs = self.history + [{"role": "user", "content": user_input}]

        try:
            raw = self.llm.complete(self._system_prompt(), msgs)
        except Exception as exc:
            self._print(f"\n  ❌  LLM Error: {exc}", 'red')
            return

        try:
            data = self._parse(raw)
        except Exception as exc:
            self._print(f"\n  ❌  Could not parse LLM response: {exc}", 'red')
            self._print(f"     Raw (first 400 chars): {raw[:400]}", 'gray')
            return

        print()
        self._divider()
        self._print("  ─── CHAIN OF THOUGHT ───", 'cyan', 'bold')
        self._divider()
        self._display_cot(data)

        # --- Summary ---
        if data.get("summary"):
            print()
            self._divider()
            self._print(f"\n  📌  PLAN: {data['summary']}", 'cyan', 'bold')

        # --- Commands ---
        commands = data.get("final_commands", [])
        if not commands:
            self._print("\n  ℹ️   No commands to execute.", 'yellow')
            return

        steps   = data.get("steps", [])
        safety  = next((s for s in steps if s.get("step") == 4), {})
        risky   = safety.get("needs_confirmation", False) or safety.get("risk_level") in ("medium", "high")

        if risky and self.config.SAFE_MODE:
            print()
            self._print("  ⚠️   Commands that will run:", 'yellow', 'bold')
            for c in commands:
                self._print(f"     $ {c}", 'white')
            ans = input(self._c("\n  Proceed? (yes / no): ", 'yellow'))
            if ans.strip().lower() not in ('yes', 'y'):
                self._print("  ❌  Cancelled.", 'red')
                return

        # --- Execute ---
        ok = self._run_commands(commands)

        # --- Footer ---
        print()
        self._divider('═', color='green' if ok else 'red')
        if ok:
            self._print("  ✨  ALL DONE", 'green', 'bold')
            if data.get("expected_output"):
                self._print(f"     {data['expected_output']}", 'gray')
        else:
            self._print("  ⚠️   FINISHED WITH ERRORS", 'red', 'bold')

        self._print(f"  📁  Dir: {self.current_dir}", 'gray')

        # --- Update history ---
        self.history.append({"role": "user",      "content": user_input})
        self.history.append({"role": "assistant",  "content": raw})
        if len(self.history) > self.config.MAX_HISTORY:
            self.history = self.history[-self.config.MAX_HISTORY:]

    # ── Banner & Help ─────────────────────────────────────────────

    def _banner(self):
        b = r"""
  ╔══════════════════════════════════════════════════════════════╗
  ║          CMD  AI  AGENT  —  Natural Language Shell           ║
  ╚══════════════════════════════════════════════════════════════╝"""
        print(self._c(b, 'cyan', 'bold'))
        print(self._c(f"    Provider : {self.config.LLM_PROVIDER.upper()}  |  Model : {self.config.get_model()}", 'gray'))
        print(self._c(f"    Safe Mode: {'ON ✅' if self.config.SAFE_MODE else 'OFF ⚠️ '}  |  Dir: {self.current_dir}", 'gray'))
        print(self._c("    Type  'help' for examples  |  'exit' to quit\n", 'yellow'))

    def _show_help(self):
        h = """
  ┌────────────────────────────────────────────────────────────┐
  │                  EXAMPLE NATURAL LANGUAGE QUERIES           │
  ├────────────────────────────────────────────────────────────┤
  │  📁 FILE / FOLDER CRUD                                     │
  │     "create a folder called projects on the desktop"       │
  │     "list all files in the current directory"              │
  │     "create a text file named notes.txt with hello world"  │
  │     "show contents of notes.txt"                           │
  │     "rename notes.txt to journal.txt"                      │
  │     "delete the file journal.txt"                          │
  │     "copy config.txt to the backup folder"                 │
  │     "move all .log files to C:\\Logs"                      │
  │                                                            │
  │  💻 SYSTEM                                                 │
  │     "show system information"                              │
  │     "list all running processes"                           │
  │     "show disk usage"                                      │
  │     "what is the current date and time"                    │
  │     "show environment variables"                           │
  │                                                            │
  │  🌐 NETWORK                                                │
  │     "ping google.com"                                      │
  │     "show network configuration"                           │
  │     "show open ports"                                      │
  │                                                            │
  │  🔍 SEARCH                                                 │
  │     "find all .py files in C:\\Users\\Me"                  │
  │     "search for the word 'error' in all .log files"        │
  │                                                            │
  │  ⌨️  SPECIAL COMMANDS                                      │
  │     help     Show this help                                │
  │     history  Show recent queries                           │
  │     clear    Clear the screen                              │
  │     exit     Quit the agent                                │
  └────────────────────────────────────────────────────────────┘"""
        print(self._c(h, 'cyan'))

    def _show_history(self):
        if not self.history:
            self._print("  No history yet.", 'gray')
            return
        self._print("\n  📜  HISTORY:", 'cyan', 'bold')
        user_msgs = [m for m in self.history if m["role"] == "user"]
        for i, m in enumerate(user_msgs, 1):
            print(self._c(f"  [{i:>2}]  {m['content'][:70]}", 'white'))


    def run(self):
        self._banner()

        while True:
            try:
                prompt = (
                    self._c(f"\n [{os.path.basename(self.current_dir) or self.current_dir}]", 'green', 'bold') +
                    self._c(" ❯ ", 'cyan')
                )
                user_input = input(prompt).strip()

                if not user_input:
                    continue

                lo = user_input.lower()
                if lo in ('exit', 'quit', 'q'):
                    self._print("\n  👋  Goodbye!\n", 'cyan')
                    break
                elif lo == 'help':
                    self._show_help()
                elif lo == 'history':
                    self._show_history()
                elif lo in ('clear', 'cls'):
                    os.system('cls' if platform.system() == 'Windows' else 'clear')
                    self._banner()
                else:
                    self.process(user_input)

            except KeyboardInterrupt:
                self._print("\n\n  👋  Interrupted. Goodbye!\n", 'yellow')
                break
            except EOFError:
                break


if __name__ == "__main__":
    agent = CMDAgent()
    agent.run()
