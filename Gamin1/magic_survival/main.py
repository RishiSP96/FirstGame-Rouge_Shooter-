import pygame
import sys
from pygame.locals import *
from player import Player
from orb import Orb
from enemy import Enemy
import random
import math
import time

# Initialize Pygame
pygame.init()

# Get the screen info for fullscreen
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
PURPLE = (200, 0, 200)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Load pixel font
try:
    PIXEL_FONT = pygame.font.Font("fonts/pixel.ttf", 32)  # You'll need to add this font
except:
    PIXEL_FONT = pygame.font.Font(None, 32)  # Fallback to default font

def get_cover_surface(image, target_width, target_height):
    img_width, img_height = image.get_size()
    scale = max(target_width / img_width, target_height / img_height)
    new_size = (int(img_width * scale), int(img_height * scale))
    scaled_img = pygame.transform.smoothscale(image, new_size)
    # Crop to center
    x = (scaled_img.get_width() - target_width) // 2
    y = (scaled_img.get_height() - target_height) // 2
    return scaled_img.subsurface((x, y, target_width, target_height)).copy()

# Load menu background image
try:
    raw_img = pygame.image.load("assets/menu_bg.jpg")
    MENU_BG = get_cover_surface(raw_img, SCREEN_WIDTH, SCREEN_HEIGHT)
    print("Menu background loaded successfully!")
except Exception as e:
    MENU_BG = None
    print(f"Failed to load menu background: {e}")

# Game States
STATE_MENU = 'menu'
STATE_CLASS_SELECT = 'class_select'
STATE_RUNNING = 'running'
STATE_GAME_OVER = 'game_over'
STATE_DETAILS = 'details'
STATE_LEVEL_UP = 'level_up'  # New state for level up screen
STATE_ABOUT = 'about'  # New state for about screen

# Arcane Mage Arrow Cooldown (in seconds)
ARROW_COOLDOWN = 1.0

class UpgradeButton:
    def __init__(self, rect, upgrade_key, upgrade_data, font):
        self.rect = pygame.Rect(rect)
        self.upgrade_key = upgrade_key
        self.upgrade_data = upgrade_data
        self.font = font
        self.title = self.font.render(f"{upgrade_data['name']} (Level {upgrade_data['current_level']}/{upgrade_data['max_level']})", True, (255, 255, 255))
        self.description = pygame.font.Font(None, 24).render(upgrade_data['description'], True, (200, 200, 200))
        self.title_rect = self.title.get_rect(topleft=(self.rect.x + 10, self.rect.y + 10))
        self.desc_rect = self.description.get_rect(topleft=(self.rect.x + 10, self.rect.y + 40))
        self.hover = False
    
    def draw(self, screen):
        # Draw button background
        bg_color = (70, 70, 70) if self.hover else (50, 50, 50)
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, (150, 150, 150) if self.hover else (100, 100, 100), self.rect, 2)
        
        # Draw upgrade info
        screen.blit(self.title, self.title_rect)
        screen.blit(self.description, self.desc_rect)
        
        # Draw current effect
        effect_text = ""
        if self.upgrade_key == 'arrow_count':
            effect_text = f"Current: {self.upgrade_data['current_level'] + 1} arrows"
        elif self.upgrade_key == 'arrow_speed':
            effect_text = f"Current: {10 + (self.upgrade_data['current_level'] * 2)} speed"
        elif self.upgrade_key == 'arrow_damage':
            effect_text = f"Current: {1 + self.upgrade_data['current_level']} damage"
        elif self.upgrade_key == 'health':
            effect_text = f"Current: {100 + (self.upgrade_data['current_level'] * 20)} health"
        elif self.upgrade_key == 'sprint_duration':
            effect_text = f"Current: {5.0 + (self.upgrade_data['current_level'] * 2.0)}s duration"
        elif self.upgrade_key == 'sprint_cooldown':
            effect_text = f"Current: {max(5.0, 20.0 - (self.upgrade_data['current_level'] * 5.0))}s cooldown"
        elif self.upgrade_key == 'sprint_speed':
            effect_text = f"Current: {2.0 + (self.upgrade_data['current_level'] * 0.5)}x speed"
        
        effect_surface = pygame.font.Font(None, 24).render(effect_text, True, (0, 255, 0))
        effect_rect = effect_surface.get_rect(topleft=(self.rect.x + 10, self.rect.y + 70))
        screen.blit(effect_surface, effect_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

class ArcaneMage(Player):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.arrow_cooldown = 0.0
        self.arrows = []  # List of active arrows (x, y, dx, dy)

    def shoot_arrow(self, enemies):
        if self.arrow_cooldown > 0 or not enemies:
            return
            
        # Find nearest enemies up to arrow_count
        nearest_enemies = []
        for enemy in enemies:
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            dist = (dx * dx + dy * dy) ** 0.5
            nearest_enemies.append((enemy, dist))
        
        nearest_enemies.sort(key=lambda x: x[1])  # Sort by distance
        nearest_enemies = nearest_enemies[:self.arrow_count]  # Take only as many as we can shoot
        
        for enemy, _ in nearest_enemies:
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > 0:
                dx /= dist
                dy /= dist
            self.arrows.append((self.x, self.y, dx, dy))
        
            self.arrow_cooldown = ARROW_COOLDOWN

    def update_arrow(self, dt, enemies):
        if self.arrow_cooldown > 0:
            self.arrow_cooldown -= dt
            
        # Update all arrows
        for i in range(len(self.arrows) - 1, -1, -1):
            x, y, dx, dy = self.arrows[i]
            x += dx * 10  # Arrow speed
            y += dy * 10
            self.arrows[i] = (x, y, dx, dy)
            
        # Check collision with enemies
            arrow_rect = pygame.Rect(x - 5, y - 5, 10, 10)
            for enemy in enemies[:]:
                if arrow_rect.colliderect(enemy.rect):
                    enemies.remove(enemy)
                    self.gain_experience(15)
                    self.arrows.pop(i)
                break

    def draw_arrow(self, screen, offset_x, offset_y):
        for x, y, _, _ in self.arrows:
            screen_x = x - offset_x
            screen_y = y - offset_y
            pygame.draw.circle(screen, (255, 255, 255), (int(screen_x), int(screen_y)), 5)

class Button:
    def __init__(self, rect, text, font, color=WHITE, bg=GRAY):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.color = color
        self.bg = bg
        self.rendered = self.font.render(self.text, True, self.color)
        self.text_rect = self.rendered.get_rect(center=self.rect.center)
    def draw(self, screen):
        pygame.draw.rect(screen, self.bg, self.rect)
        screen.blit(self.rendered, self.text_rect)
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class AboutButton:
    def __init__(self, rect, text, font, color=WHITE, bg=GRAY):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.color = color
        self.bg = bg
        self.hover = False
        self.rendered = self.font.render(self.text, True, self.color)
        self.text_rect = self.rendered.get_rect(center=self.rect.center)
    
    def draw(self, screen):
        bg_color = (min(self.bg[0] + 30, 255), min(self.bg[1] + 30, 255), min(self.bg[2] + 30, 255)) if self.hover else self.bg
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.rendered, self.text_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        # Initialize fullscreen display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Dark Messiah")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_MENU
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.tiny_font = pygame.font.Font(None, 24)  # New font for about screen text
        self.selected_class = None
        # Base values for scaling
        self.base_enemy_spawn_time = 1.5
        self.base_enemy_speed = 2.0
        self.reset_game()
        # Adjust button positions for fullscreen
        self.menu_buttons = [
            Button((SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2+50, 200, 50), "Start", self.font),
            Button((SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2+120, 200, 50), "About", self.font)  # New about button
        ]
        self.game_over_buttons = [
            Button((SCREEN_WIDTH//2-120, SCREEN_HEIGHT//2+40, 110, 50), "Details", self.small_font),
            Button((SCREEN_WIDTH//2+10, SCREEN_HEIGHT//2+40, 110, 50), "Main Menu", self.small_font)
        ]
        self.details_buttons = [
            Button((SCREEN_WIDTH//2-100, SCREEN_HEIGHT-100, 200, 50), "Main Menu", self.font)
        ]
        self.about_buttons = []
        # Adjust class selection screen for fullscreen
        self.arcane_box = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 100, 200, 100)
        self.arcane_label = self.small_font.render("Arcane Mage", True, WHITE)
        self.arcane_label_rect = self.arcane_label.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.begin_venture_btn = Button((SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100, 180, 50), "Begin venture", self.small_font, GREEN, (0, 100, 0))
        # Add exit button
        self.exit_button = Button((SCREEN_WIDTH - 100, SCREEN_HEIGHT - 50, 80, 40), "Exit", self.small_font, RED, (100, 0, 0))
        self.upgrade_buttons = []
        self.level_up_title = None
        self.level_up_title_rect = None
        
        # About screen content
        self.about_sections = {
            'controls': {
                'title': 'Controls',
                'color': BLUE,
                'content': [
                    "Movement:",
                    "- WASD or Arrow Keys to move your character",
                    "",
                    "Combat:",
                    "- Left Mouse Button to shoot arrows at enemies",
                    "",
                    "Special Abilities:",
                    "- Right Mouse Button to sprint (uses stamina)",
                    "- Sprint has a cooldown period",
                    "",
                    "Menu Navigation:",
                    "- Click buttons to navigate menus",
                    "- ESC to exit game"
                ]
            },
            'gameplay': {
                'title': 'Gameplay',
                'color': GREEN,
                'content': [
                    "Core Mechanics:",
                    "- Collect orbs to gain experience",
                    "- Defeat enemies to gain XP and survive longer",
                    "- Level up to become stronger",
                    "",
                    "Survival:",
                    "- Avoid enemies or defeat them with arrows",
                    "- Use sprint strategically to escape",
                    "- Health increases every 5 levels",
                    "",
                    "Difficulty:",
                    "- Enemies get faster as you level up",
                    "- Enemy spawn rate increases with level",
                    "- Choose upgrades wisely to survive longer"
                ]
            },
            'classes': {
                'title': 'Classes',
                'color': PURPLE,
                'content': [
                    "Arcane Mage:",
                    "- Primary class available",
                    "- Shoots magical arrows at enemies",
                    "- Can upgrade arrow properties",
                    "",
                    "Class Features:",
                    "- Multiple arrow upgrades",
                    "- Sprint ability",
                    "- Health and stamina management",
                    "",
                    "Future Classes:",
                    "- More classes coming soon!",
                    "- Each with unique abilities"
                ]
            },
            'upgrades': {
                'title': 'Upgrades',
                'color': ORANGE,
                'content': [
                    "Arrow Upgrades:",
                    "- Arrow Count: Shoot multiple arrows",
                    "- Arrow Speed: Faster projectile speed",
                    "- Arrow Damage: Increased damage",
                    "",
                    "Survival Upgrades:",
                    "- Max Health: Increase health pool",
                    "- Sprint Duration: Longer sprint time",
                    "- Sprint Cooldown: Faster cooldown",
                    "- Sprint Speed: Faster sprint speed",
                    "",
                    "Upgrade Strategy:",
                    "- Choose based on playstyle",
                    "- Balance offense and defense",
                    "- Prioritize survival upgrades early"
                ]
            }
        }
        
        # About screen buttons
        button_width = 200
        button_height = 50
        button_spacing = 20
        start_x = (SCREEN_WIDTH - (button_width * 2 + button_spacing)) // 2
        start_y = 150
        
        self.about_buttons = []
        for i, (key, section) in enumerate(self.about_sections.items()):
            row = i // 2
            col = i % 2
            x = start_x + col * (button_width + button_spacing)
            y = start_y + row * (button_height + button_spacing)
            self.about_buttons.append(AboutButton(
                (x, y, button_width, button_height),
                section['title'],
                self.font,
                section['color'],
                (30, 30, 30)
            ))
        
        self.about_back_button = Button(
            (SCREEN_WIDTH//2-100, SCREEN_HEIGHT-100, 200, 50),
            "Back to Menu",
            self.font
        )
        
        self.current_about_section = None
        self.about_scroll_offset = 0
        self.max_scroll = 0

    def reset_game(self):
        if self.selected_class == "Arcane Mage":
            self.player = ArcaneMage(0, 0)
        else:
            self.player = Player(0, 0)
        self.camera_x = 0
        self.camera_y = 0
        self.orbs = []
        self.enemies = []
        self.spawn_timer = 0.0
        self.enemy_spawn_timer = 0.0
        self.start_ticks = pygame.time.get_ticks()
        self.xp_gained = 0
        self.enemies_defeated = 0
        self.level_reached = 1
        self.game_time = 0
        self.last_health_increase_level = 0
        self.last_scaling_level = 0
        self.venture_start_time = None  # Will be set when game starts
        self.upgrade_buttons = []
        self.level_up_title = None
        self.level_up_title_rect = None

    def apply_level_scaling(self):
        # Health increase every 5 levels
        if self.player.level >= self.last_health_increase_level + 5:
            self.player.health += 20
            self.last_health_increase_level = self.player.level

        # Enemy speed and spawn rate scaling every 5 levels
        if self.player.level >= self.last_scaling_level + 5:
            self.last_scaling_level = self.player.level
            # Update enemy speed for all existing enemies
            for enemy in self.enemies:
                enemy.speed *= 1.5  # Increase speed by 50%

    def show_level_up_screen(self):
        self.state = STATE_LEVEL_UP
        available_upgrades = self.player.get_available_upgrades()
        
        # Create upgrade buttons
        self.upgrade_buttons = []
        button_width = 300
        button_height = 120  # Increased height to accommodate effect text
        padding = 20
        start_x = (SCREEN_WIDTH - (button_width * 2 + padding)) // 2
        start_y = (SCREEN_HEIGHT - (len(available_upgrades) // 2 + 1) * (button_height + padding)) // 2
        
        for i, (key, data) in enumerate(available_upgrades.items()):
            row = i // 2
            col = i % 2
            x = start_x + col * (button_width + padding)
            y = start_y + row * (button_height + padding)
            self.upgrade_buttons.append(UpgradeButton((x, y, button_width, button_height), key, data, self.font))
        
        # Create title and instruction
        self.level_up_title = self.font.render(f"Level {self.player.level} Up!", True, (255, 255, 255))
        self.level_up_instruction = pygame.font.Font(None, 36).render("Choose ONE upgrade:", True, (200, 200, 200))
        self.level_up_title_rect = self.level_up_title.get_rect(center=(SCREEN_WIDTH // 2, start_y - 80))
        self.level_up_instruction_rect = self.level_up_instruction.get_rect(center=(SCREEN_WIDTH // 2, start_y - 30))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.state == STATE_RUNNING:
                        self.running = False
                    elif self.state in [STATE_MENU, STATE_CLASS_SELECT, STATE_GAME_OVER, STATE_DETAILS, STATE_LEVEL_UP, STATE_ABOUT]:
                        self.running = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.state == STATE_RUNNING and isinstance(self.player, ArcaneMage):
                        self.player.shoot_arrow(self.enemies)
                    elif self.state == STATE_LEVEL_UP:
                        for button in self.upgrade_buttons:
                            if button.is_clicked(event.pos):
                                if self.player.apply_upgrade(button.upgrade_key):
                                    self.state = STATE_RUNNING
                                    return
                    elif self.state == STATE_MENU:
                        for btn in self.menu_buttons:
                            if btn.is_clicked(event.pos):
                                if btn.text == "Start":
                                    self.state = STATE_CLASS_SELECT
                                elif btn.text == "About":
                                    self.state = STATE_ABOUT
                    elif self.state == STATE_CLASS_SELECT:
                        if self.arcane_box.collidepoint(event.pos):
                            self.selected_class = "Arcane Mage"
                        if self.begin_venture_btn.is_clicked(event.pos) and self.selected_class == "Arcane Mage":
                            self.reset_game()
                            self.venture_start_time = time.time()  # Set start time when game begins
                            self.state = STATE_RUNNING
                    elif self.state == STATE_GAME_OVER:
                        if self.game_over_buttons[0].is_clicked(event.pos):
                            self.state = STATE_DETAILS
                        elif self.game_over_buttons[1].is_clicked(event.pos):
                            self.state = STATE_MENU
                    elif self.state == STATE_DETAILS:
                        if self.details_buttons[0].is_clicked(event.pos):
                            self.state = STATE_MENU
                    elif self.state == STATE_ABOUT:
                        if self.about_back_button.is_clicked(event.pos):
                            self.state = STATE_MENU
                            self.current_about_section = None
                            self.about_scroll_offset = 0
                        elif not self.current_about_section:
                            for button in self.about_buttons:
                                if button.is_clicked(event.pos):
                                    self.current_about_section = button.text.lower()
                                    self.about_scroll_offset = 0
                                    # Calculate max scroll based on content length
                                    content = self.about_sections[self.current_about_section]['content']
                                    self.max_scroll = max(0, len(content) * 30 - (SCREEN_HEIGHT - 400))
                    # Check exit button in all states
                    if self.exit_button.is_clicked(event.pos):
                        self.running = False
                elif event.button == 4 and self.state == STATE_ABOUT:  # Mouse wheel up
                    self.about_scroll_offset = max(0, self.about_scroll_offset - 30)
                elif event.button == 5 and self.state == STATE_ABOUT:  # Mouse wheel down
                    self.about_scroll_offset = min(self.max_scroll, self.about_scroll_offset + 30)
            elif event.type == MOUSEMOTION and self.state == STATE_LEVEL_UP:
                # Update hover state for all upgrade buttons
                for button in self.upgrade_buttons:
                    button.update_hover(event.pos)
            elif event.type == MOUSEMOTION and self.state == STATE_ABOUT:
                if not self.current_about_section:
                    for button in self.about_buttons:
                        button.update_hover(event.pos)

    def update(self):
        if self.state != STATE_RUNNING:
            return
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()  # Get mouse button states
        self.player.move(keys, mouse_buttons)
        
        # Apply level scaling
        self.apply_level_scaling()
        
        dt = self.clock.get_time() / 1000.0
        if isinstance(self.player, ArcaneMage):
            self.player.update_arrow(dt, self.enemies)
        self.camera_x = self.player.x - SCREEN_WIDTH // 2 + self.player.width // 2
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2 + self.player.height // 2
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        collected_orbs = []
        for orb in self.orbs:
            orb.update_rect()
            if player_rect.colliderect(orb.rect):
                self.player.gain_experience(orb.exp_value)
                self.xp_gained += orb.exp_value
                collected_orbs.append(orb)
        for orb in collected_orbs:
            self.orbs.remove(orb)
        self.spawn_timer += dt
        if self.spawn_timer >= 0.5:
            orb_spawn_min = 500
            orb_spawn_max = 800
            jitter = 50
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(orb_spawn_min, orb_spawn_max)
            orbx = self.player.x + dist * math.cos(angle) + random.randint(-jitter, jitter)
            orby = self.player.y + dist * math.sin(angle) + random.randint(-jitter, jitter)
            self.orbs.append(Orb(orbx, orby))
            self.spawn_timer = 0.0

        # Calculate current enemy spawn time based on level
        current_spawn_time = self.base_enemy_spawn_time / (1.5 ** (self.player.level // 5))
        self.enemy_spawn_timer += dt
        if self.enemy_spawn_timer >= current_spawn_time:
            enemy_spawn_min = 500
            enemy_spawn_max = 800
            jitter = 50
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(enemy_spawn_min, enemy_spawn_max)
            enemyx = self.player.x + dist * math.cos(angle) + random.randint(-jitter, jitter)
            enemyy = self.player.y + dist * math.sin(angle) + random.randint(-jitter, jitter)
            # Calculate current enemy speed based on level
            current_enemy_speed = self.base_enemy_speed * (1.5 ** (self.player.level // 5))
            enemy = Enemy(enemyx, enemyy, speed=current_enemy_speed)
            self.enemies.append(enemy)
            self.enemy_spawn_timer = 0.0

        for enemy in self.enemies:
            enemy.update(self.player.x, self.player.y)
        for i in range(len(self.enemies)):
            for j in range(i + 1, len(self.enemies)):
                self.enemies[i].separate(self.enemies[j])
        hit_enemies = []
        for enemy in self.enemies:
            if player_rect.colliderect(enemy.rect):
                self.player.health -= 10
                self.enemies_defeated += 1
                hit_enemies.append(enemy)
        for enemy in hit_enemies:
            self.enemies.remove(enemy)
        self.level_reached = self.player.level
        self.game_time = (pygame.time.get_ticks() - self.start_ticks) // 1000
        if self.player.health <= 0:
            self.state = STATE_GAME_OVER

        # Check for level up
        if self.player.experience >= self.player.experience_to_level:
            self.player.level_up()
            self.show_level_up_screen()
            return

    def draw(self):
        if self.state == STATE_MENU:
            if MENU_BG:
                self.screen.blit(MENU_BG, (0, 0))
            else:
                self.screen.fill(BLACK)
            title = self.font.render("Dark Messiah", True, WHITE)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 100))
            for btn in self.menu_buttons:
                btn.draw(self.screen)
            self.exit_button.draw(self.screen)
        elif self.state == STATE_CLASS_SELECT:
            self.screen.fill(BLACK)
            pygame.draw.rect(self.screen, (GRAY if self.selected_class != "Arcane Mage" else GREEN), self.arcane_box, 2)
            self.screen.blit(self.arcane_label, self.arcane_label_rect)
            self.begin_venture_btn.draw(self.screen)
            self.exit_button.draw(self.screen)
        elif self.state == STATE_RUNNING:
            self.screen.fill(BLACK)
            for orb in self.orbs:
                orb.draw(self.screen, self.camera_x, self.camera_y)
            for enemy in self.enemies:
                enemy.draw(self.screen, self.camera_x, self.camera_y)
            self.player.draw(self.screen)
            if isinstance(self.player, ArcaneMage):
                self.player.draw_arrow(self.screen, self.camera_x, self.camera_y)
            
            # Draw HUD
            font = pygame.font.Font(None, 36)
            level_text = font.render(f"Level: {self.player.level}", True, WHITE)
            exp_text = font.render(f"XP: {self.player.experience}/{self.player.experience_to_level}", True, WHITE)
            health_text = font.render(f"Health: {self.player.health}", True, WHITE)
            self.screen.blit(level_text, (10, 10))
            self.screen.blit(exp_text, (10, 50))
            self.screen.blit(health_text, (10, 90))
            
            # Draw pixelated timer
            if self.venture_start_time is not None:
                elapsed_time = int(time.time() - self.venture_start_time)
                minutes = elapsed_time // 60
                seconds = elapsed_time % 60
                timer_text = PIXEL_FONT.render(f"{minutes:02d}:{seconds:02d}", True, WHITE)
                timer_rect = timer_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
                self.screen.blit(timer_text, timer_rect)
            
            self.exit_button.draw(self.screen)
        elif self.state == STATE_GAME_OVER:
            self.screen.fill(BLACK)
            over = self.font.render("You Died!", True, RED)
            self.screen.blit(over, (SCREEN_WIDTH//2 - over.get_width()//2, SCREEN_HEIGHT//2 - 100))
            for btn in self.game_over_buttons:
                btn.draw(self.screen)
            self.exit_button.draw(self.screen)
        elif self.state == STATE_DETAILS:
            self.screen.fill(BLACK)
            details_title = self.font.render("Run Details", True, WHITE)
            self.screen.blit(details_title, (SCREEN_WIDTH//2 - details_title.get_width()//2, 60))
            stats = [
                f"Time Survived: {self.game_time} seconds",
                f"XP Gained: {self.xp_gained}",
                f"Level Reached: {self.level_reached}",
                f"Enemies Defeated: {self.enemies_defeated}"
            ]
            for i, stat in enumerate(stats):
                stat_text = self.small_font.render(stat, True, WHITE)
                self.screen.blit(stat_text, (SCREEN_WIDTH//2 - stat_text.get_width()//2, 150 + i*50))
            for btn in self.details_buttons:
                btn.draw(self.screen)
            self.exit_button.draw(self.screen)
        elif self.state == STATE_LEVEL_UP:
            self.screen.fill(BLACK)
            # Draw title and instruction
            self.screen.blit(self.level_up_title, self.level_up_title_rect)
            self.screen.blit(self.level_up_instruction, self.level_up_instruction_rect)
            # Draw upgrade buttons
            for button in self.upgrade_buttons:
                button.draw(self.screen)
            # Draw exit button
            self.exit_button.draw(self.screen)
        elif self.state == STATE_ABOUT:
            self.screen.fill(BLACK)
            
            if not self.current_about_section:
                # Draw main about screen with section buttons
                title = self.font.render("How to Play", True, WHITE)
                self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 60))
                
                subtitle = self.small_font.render("Select a category to learn more:", True, CYAN)
                self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 100))
                
                for button in self.about_buttons:
                    button.draw(self.screen)
            else:
                # Draw selected section content
                section = self.about_sections[self.current_about_section]
                title = self.font.render(section['title'], True, section['color'])
                self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 60))
                
                # Draw content with scrolling
                y_offset = 150 - self.about_scroll_offset
                for line in section['content']:
                    if y_offset > 100 and y_offset < SCREEN_HEIGHT - 150:  # Only draw visible text
                        text = self.tiny_font.render(line, True, WHITE)
                        self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_offset))
                    y_offset += 30
                
                # Draw scroll indicator if content is scrollable
                if self.max_scroll > 0:
                    scroll_height = (SCREEN_HEIGHT - 300) * (SCREEN_HEIGHT - 300) / (len(section['content']) * 30)
                    scroll_y = 150 + (SCREEN_HEIGHT - 300 - scroll_height) * (self.about_scroll_offset / self.max_scroll)
                    pygame.draw.rect(self.screen, GRAY, (SCREEN_WIDTH - 20, scroll_y, 10, scroll_height))
            
            # Draw back button
            if self.current_about_section:
                back_text = self.small_font.render("← Back to Categories", True, CYAN)
                back_rect = back_text.get_rect(topleft=(20, 20))
                pygame.draw.rect(self.screen, (30, 30, 30), back_rect.inflate(20, 10))
                self.screen.blit(back_text, back_rect)
                if back_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(self.screen, (50, 50, 50), back_rect.inflate(20, 10))
                if pygame.mouse.get_pressed()[0] and back_rect.collidepoint(pygame.mouse.get_pos()):
                    self.current_about_section = None
                    self.about_scroll_offset = 0
            
            self.about_back_button.draw(self.screen)
            self.exit_button.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 