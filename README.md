# Space Invaders

A feature-rich Space Invaders clone built with Python and pygame, featuring multiple invader themes, power-ups, boss fights, and a full settings menu.

## Features

- 30 levels of escalating difficulty
- 3 difficulty modes — Easy, Medium, Hard
- 4 selectable invader themes with unique pixel art
- 4 selectable player ships
- 4 background music tracks with volume controls
- UFO bonus enemy with point scaling
- Boss fights every 5 levels
- 4 power-up types dropped by invaders and UFOs
- Destructible barriers with pixel-level erosion
- Armored invaders (level 5+) that take 3 hits
- Dive bomber mechanic (level 3+)
- Particle explosion effects and screen shake
- Persistent high score (saved to `highscore.json`)
- Scrolling starfield background

## Requirements

- Python 3.10+
- pygame 2.x
- Pillow (PIL)

## Installation

```bash
# Clone the repo
git clone <repo-url>
cd Space-Invaders

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install pygame pillow
```

## Running the Game

```bash
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| `A` / `←` | Move left |
| `D` / `→` | Move right |
| `Space` | Shoot |
| `Enter` | Start / Confirm |
| `S` | Open settings (from start screen) |
| `↑` / `↓` | Navigate settings options |
| `←` / `→` | Change setting value |
| `Escape` | Back / Quit |

## Gameplay

### Scoring

| Enemy | Points |
|-------|--------|
| Bottom row invader | 10 |
| Middle row invader | 20 |
| Upper row invader | 30 |
| Top row invader | 40 |
| UFO (first 2s) | 200 |
| UFO (2–4s) | 150 |
| UFO (4–6s) | 100 |
| UFO (6s+) | 50 |
| Boss hit | 50 |

### Power-ups

Dropped randomly when invaders are killed (5% chance) or always when the UFO is shot:

| Power-up | Effect | Duration |
|----------|--------|----------|
| Multi-shot | Fire 3 bullets at once | 10 seconds |
| Extra life | +1 life (max 5) | Permanent |
| Time freeze | Stops all invaders and bullets | 5 seconds |
| Laser | Penetrating shot that passes through invaders | 5 seconds |

### Levels

- Every 3 levels the invader fleet gains an extra row (up to 8 rows)
- Every level invader speed increases slightly
- **Level 3+**: Invaders can break formation and dive-bomb the player
- **Level 5+**: Top-row invaders are armored — they take 3 hits and are visually tinted
- **Every 5th level**: Boss fight — no invader fleet, a single powerful boss appears
- **Level 30**: Final level — completing it triggers the win screen

### Barriers

Four destructible bunkers protect the player. They erode from:
- Invader bullets hitting them
- Player bullets passing through them
- Invaders physically touching them

Collision uses pixel-level mask detection, so the arch cutout is a true gap.

### UFO

A bonus UFO flies across the top of the screen at random intervals (every 20–40 seconds). Shooting it awards points and always drops a power-up. Point value decreases the longer it has been flying.

## Settings

Access from the start screen with `S`. Changes apply when you press `Enter` to start a game.

| Setting | Options |
|---------|---------|
| Difficulty | Easy / Medium / Hard |
| Player ship | 4 visual skins |
| Invader theme | Theme 1 / 2 / 3 / 4 |
| Music track | 4 tracks (previewed on selection) |
| Music volume | 0–100% |
| SFX volume | 0–100% |

## Project Structure

```
Space Invaders/
├── main.py               # Entry point
├── highscore.json        # Persisted high score
├── assets/
│   ├── images/           # All sprites and backgrounds
│   └── sounds/           # Music and sound effects
└── src/
    ├── game.py           # Main game loop, state machine, collision
    ├── settings.py       # All tunable constants
    ├── player.py         # Player ship movement and shooting
    ├── invader.py        # Invader sprite and fleet logic
    ├── bullet.py         # Player and invader projectiles
    ├── barrier.py        # Destructible bunkers
    ├── ufo.py            # Bonus UFO enemy
    ├── boss.py           # Boss enemy (every 5th level)
    ├── powerup.py        # Power-up drops
    ├── hud.py            # Score, lives, boss health bar
    ├── particle.py       # Explosion particle system
    ├── starfield.py      # Scrolling star background
    └── mixer.py          # Audio utilities
```
