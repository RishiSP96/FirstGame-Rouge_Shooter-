# FirstGame-Rouge_Shooter-
My first attempt at a Rouge-like level up game

# Dark Messiah
A Python/Pygame game inspired by Magic Survival. Survive as long as you can.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Controls](#controls)
- [Gameplay](#gameplay)
- [Upgrades](#upgrades)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [Assets & Credits](#assets--credits)
- [License](#license)

---

## Overview

**Dark Messiah** is a top-down survival game where you control a mage, collect orbs for experience, defeat enemies, and choose upgrades as you level up. The game features a dynamic upgrade system, a beautiful fullscreen menu with a custom wallpaper, and a detailed in-game guide.

---

## Features
- **Fullscreen gameplay** with pixel font HUD and timer
- **Main menu** with custom wallpaper and About/How to Play section
- **Class selection** (Arcane Mage)
- **Dynamic enemy spawning and scaling**
- **Arrow shooting and sprint mechanics**
- **Stamina and health bars**
- **Level-up system** with upgrade choices:
  - Arrow Count, Arrow Speed, Arrow Damage
  - Max Health, Sprint Duration, Sprint Cooldown, Sprint Speed
- **Game over and run details screens**
- **Colorful, scrollable in-game guide**

---

## Screenshots

![Menu Wallpaper](assets/menu_bg.jpg)

---

## Controls

- **Movement:** WASD or Arrow Keys
- **Shoot Arrow:** Left Mouse Button (Arcane Mage)
- **Sprint:** Right Mouse Button (uses stamina, has cooldown)
- **Menu Navigation:** Mouse (click buttons)
- **Exit:** ESC or Exit button
- **Scroll About/Guide:** Mouse wheel

---

## Gameplay

- Collect blue orbs to gain experience and level up.
- Defeat enemies by shooting arrows (Arcane Mage).
- Each level up, choose one upgrade to enhance your abilities.
- Survive as long as possible as enemies get faster and spawn more frequently.
- Use sprint strategically to escape danger.

---

## Upgrades

- **Arrow Count:** Shoot more arrows at once (max 3)
- **Arrow Speed:** Arrows travel faster (max 5 levels)
- **Arrow Damage:** Arrows deal more damage (max 5 levels)
- **Max Health:** Increases your health pool (max 5 levels)
- **Sprint Duration:** Sprint lasts longer (max 3 levels)
- **Sprint Cooldown:** Sprint recharges faster (max 3 levels)
- **Sprint Speed:** Sprint is faster (max 3 levels)

---

## Installation

1. **Clone or download this repository.**
2. **Install Python 3.10+** (recommended: 3.12+)
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Add assets:**
   - Place your menu wallpaper image as `assets/menu_bg.jpg` (recommended size: your screen resolution, or larger)
   - (Optional) Add a pixel font as `fonts/pixel.ttf` for the timer (or use the default font)

---

## How to Run

From your project directory:

```bash
python -m magic_survival.main
```

Or, if you are in the `magic_survival` folder:

```bash
python main.py
```

---

## Assets & Credits

- **Menu Wallpaper:** [Image from here...](https://wall.alphacoders.com/big.php?i=559873)
- **Font:** [Pixel font](https://www.dafont.com/bitmap.php) (or system default)
- **Game Code:** Written in Python using [Pygame](https://www.pygame.org/)
- **Inspired by:** Magic Survival (mobile game)

---

## License

This project is just me trying to learn coding....feel free to improve and iterate on it.
Hope you enjoy this "game" ! 
