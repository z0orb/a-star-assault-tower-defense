# A* Assault - Tower Defense

A python-based tower defense game featuring A* pathfinding, dynamic map generation, and procedural terrain. Defend your base against waves of enemies by strategically placing towers and barricades to reroute their path.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/z0orb/a-star-assault-tower-defense
   cd a*-assault
   ```

2. **Set up a Virtual Environment (Recommended)**
    It is best practice to run Python projects in an isolated environment.

   **Windows**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   **Linux/macOS**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

Ensure your virtual environment is activated, then run:

```bash
python game.py
```

## How to Play

### Objective
Prevent enemies from reaching your base. You lose health if an enemy enters the base. Survive all 6 waves to win.

### Controls

| Key / Action | Function |
|--------------|----------|
| **Left Click** (UI) | Select tower type (Arrow/Bomb) |
| **Left Click** (Map) | Place selected tower |
| **Right Click** (Map) | Place or Remove Barricade |
| **SPACE** | Start next wave |
| **R** | Restart game (generates a new random map) |
| **F11** | Toggle Fullscreen |

### Game Mechanics

- **Towers**:
  - **Arrow Tower**: Fast firing, single target damage. Good for single enemies.
  - **Bomb Tower**: Slow firing, Area of Effect (AoE) damage. Good for clusters.
- **Barricades**: Cheap obstacles that force enemies to find a new path. Use them to create "kill zones" or lengthen the enemy's route.
- **Enemies**: They use A* pathfinding to find the shortest path to your base. If you block their path completely with barricades, they will still cross over the barricade to ensure no cheesing by blocking off the base entirely with barricades. But they will consider the cheapest path still.

## Custom Graphics

The game supports custom PNG themes (skins) for all visual elements.
See [ASSETS.md](ASSETS.md) for a detailed guide on how to add your own graphics.

## License

Open Source.
