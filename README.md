# Python CS:GO External Cheat

Simple external cheat for Counter-Strike: Global Offensive using Python + pymem + ImGui (GLFW backend).

**For educational / reverse engineering / research purposes only.**  
Using this (or any cheat) in online matchmaking / VAC-secured servers will almost certainly result in a **permanent VAC ban**.

## Features

- Triggerbot
- Glow ESP
- Radar hack
- Chams
- Bunnyhop
- Auto-strafe
- No flash
- Recoil Control System (RCS)
- Custom FOV changer

## Requirements

- **Windows** 10 / 11 (64-bit recommended)
- [**CS:GO**](https://store.steampowered.com/app/4465480/CounterStrikeGlobal_Offensive)
- **Python** [3.11](https://www.python.org/downloads/release/python-3119/)
- Administrator rights (pymem needs it for memory reading/writing)

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/Limitrious/csgo-external.git
   cd csgo-external
   ```
2. Install dependenciesBash
   ```bash
   pip install -r requirements.txt
   ```
3. Run
   ```bash
   python main.py
   ```

## TODO

- Auto bhop being too perfect, easy to detect
- Auto strafe being inconsistence
