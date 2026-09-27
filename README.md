# 🤖 JARVIS: Real-Time Voice Telemetry & Dynamic Audio Ducking for AI Coding IDEs

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Neural Voice](https://img.shields.io/badge/TTS-Neural%20Edge-brightgreen)](https://github.com/rany2/edge-tts)
[![Audio Engine](https://img.shields.io/badge/Mixer-Pygame%20Audio%20Channels-red)](https://www.pygame.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)]()

> **"Why wait in silence while your AI Agent executes heavy commands? Turn your coding workspace into Tony Stark's actual lab."**

Developed & Engineered by **[Luis Andrés López Frías](https://github.com/DesarrolladorWebFrias)**.

---

## ⚡ The Problem with Modern AI IDEs (Cursor, Copilot, Windsurf)

Modern agentic IDEs are revolutionary, but they have a glaring UX flaw: **Dead Silence**.
When an AI agent executes terminal commands, installs dependencies, refactors thousands of rows, or runs unit tests, the developer is left staring at a frozen spinning wheel.

**JARVIS solves this fundamentally:**
Instead of waiting for the final text output, JARVIS intercepts the agent's `tool_calls` stream in **real time**, translates the pending actions into natural colloquial speech, and narrates what the model is doing **before and during execution**, with automatic studio-grade music ducking.

---

## 🚀 Key Innovations & Features

* 🎙️ **Zero-Silence Real-Time Telemetry:** Narrates terminal commands, file inspections, and code generation steps as they are triggered.
* 🎧 **Dynamic Audio Ducking:** Background focus music automatically attenuates (*50% → 10%*) when JARVIS speaks, and smoothly swells back up when processing begins.
* 🧠 **Colloquial Action Translation:** Automatically converts dry technical tool calls (`"Inspeccionando inventario"`, `"Executing pip install"`) into natural, elegant assistant dialogue (*"Voy a revisar los archivos para ver los datos, Señor Luis..."*).
* 💬 **Dual-Channel Control:** Supports both keyboard shortcuts (`[P]` pause, `[T]` track switch, `[M]` mute, `[1]` volume 100%) and natural chat commands directly within the IDE (`"Jarvis, pausa"`, `"cambia a lofi"`, `"sube al 100%"`).
* 🎵 **Built-In Focus Soundscapes:** Bundled with Synthwave Lab, Lo-Fi Rhodes, Cyber Focus, and Stark Ambient soundtracks.

---

## 🏗️ System Architecture

```text
       ┌───────────────────────────────────────────────────────────┐
       │                 Antigravity / AI Coding IDE               │
       └─────────────────────────────┬─────────────────────────────┘
                                     │
                                     ▼ (Live Event Stream)
       ┌───────────────────────────────────────────────────────────┐
       │                transcript.jsonl (Event Log)               │
       └─────────────────────────────┬─────────────────────────────┘
                                     │
                                     ▼ (Poll & Real-Time Intercept)
 ╔═════════════════════════════════════════════════════════════════════════╗
 ║                     JARVIS ENGINE (jarvis_voice.py)                     ║
 ║                                                                         ║
 ║  ┌─────────────────────────┐           ┌─────────────────────────────┐  ║
 ║  │ Natural Action Parsing  │           │ Dual-Channel Pygame Mixer   │  ║
 ║  │ • Tool Action Converter │           │ • Channel 0: Neural Voice   │  ║
 ║  │ • Chat Commands Watcher │           │ • Channel 1: Focus Music    │  ║
 ║  └───────────┬─────────────┘           └──────────────┬──────────────┘  ║
 ║              │                                        ▲                 ║
 ║              ▼                                        │ (Audio Ducking) ║
 ║  ┌─────────────────────────┐                          │                 ║
 ║  │ Neural Speech Synthesis ├──────────────────────────┘                 ║
 ║  │ (Edge-TTS High Fidelity)│                                            ║
 ║  └─────────────────────────┘                                            ║
 ╚═════════════════════════════════════════════════════════════════════════╝
                                     │
                                     ▼
                      🔊 Studio Audio Output (Speakers / Headphones)
```

---

## 🛠️ Quickstart Installation (3 Minutes)

### 1. Clone the repository
```bash
git clone https://github.com/luisfriasdesarrollador/jarvis-ide-voice-telemetry.git
cd jarvis-ide-voice-telemetry
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch JARVIS
On Windows, simply double-click:
```cmd
iniciar_jarvis.bat
```
Or run directly from terminal:
```bash
python jarvis_voice.py
```

---

## 🎹 Keyboard Controls

| Key | Action | Description |
| :---: | :--- | :--- |
| **`[1]`** | Volume 100% | Sets background music to maximum focus volume |
| **`[5]`** | Volume 50% | Sets background music to standard ambient volume |
| **`[P]`** | Play / Pause | Toggles background music on or off |
| **`[T]`** | Next Track | Switches between Synthwave, Lo-Fi, Cyber, and Ambient |
| **`[M]`** | Mute Voice | Toggles JARVIS speech output on/off |
| **`[S]`** | Skip Speech | Instantly interrupts current voice output |
| **`[Q]`** | Shutdown | Gracefully shuts down the voice telemetry server |

---

## 💬 Natural In-Chat Commands

You don't need to touch the console while coding. Just write in your IDE chat:
* *"Jarvis, sube la música al 100%"*
* *"Silencia la música"*
* *"Pon Lo-Fi"*
* *"Siguiente canción"*
* *"Jarvis, ¿estás en línea?"*

---

## 👤 Author & Creator

**Luis Andrés López Frías**  
*Fullstack Engineer & AI Agent Systems Architect*  
* Email: [luisfriasdesarrollador@gmail.com](mailto:luisfriasdesarrollador@gmail.com)  
* GitHub: [@DesarrolladorWebFrias](https://github.com/DesarrolladorWebFrias)  

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
Open source, extensible, and built for the next generation of software creators.
