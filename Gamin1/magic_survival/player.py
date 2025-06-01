import pygame
from pygame.locals import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.base_speed = 5  # Base speed before sprint
        self.speed = self.base_speed
        self.health = 100
        self.max_health = 100
        self.level = 1
        self.experience = 0
        self.experience_to_level = 100
        
        # Upgrade stats (all start at base level)
        self.arrow_count = 1
        self.arrow_speed = 10
        self.arrow_damage = 1
        self.sprint_duration = 5.0
        self.sprint_cooldown = 20.0
        self.sprint_speed_multiplier = 2.0
        
        # Stamina system
        self.stamina = 100
        self.max_stamina = 100
        self.is_sprinting = False
        self.sprint_timer = 0.0
        self.sprint_cooldown_timer = 0.0
        
        # The rect is now just for collision, not for drawing
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Available upgrades with their current levels
        self.upgrades = {
            'arrow_count': {'name': 'Arrow Count', 'description': 'Shoot multiple arrows at once', 'max_level': 3, 'current_level': 0, 
                          'effect': lambda: setattr(self, 'arrow_count', 1 + self.upgrades['arrow_count']['current_level'])},
            'arrow_speed': {'name': 'Arrow Speed', 'description': 'Increase arrow travel speed', 'max_level': 5, 'current_level': 0,
                          'effect': lambda: setattr(self, 'arrow_speed', 10 + (self.upgrades['arrow_speed']['current_level'] * 2))},
            'arrow_damage': {'name': 'Arrow Damage', 'description': 'Increase arrow damage', 'max_level': 5, 'current_level': 0,
                           'effect': lambda: setattr(self, 'arrow_damage', 1 + self.upgrades['arrow_damage']['current_level'])},
            'health': {'name': 'Max Health', 'description': 'Increase maximum health', 'max_level': 5, 'current_level': 0,
                      'effect': lambda: (setattr(self, 'max_health', 100 + (self.upgrades['health']['current_level'] * 20)),
                                       setattr(self, 'health', self.max_health))},
            'sprint_duration': {'name': 'Sprint Duration', 'description': 'Increase sprint duration', 'max_level': 3, 'current_level': 0,
                              'effect': lambda: setattr(self, 'sprint_duration', 5.0 + (self.upgrades['sprint_duration']['current_level'] * 2.0))},
            'sprint_cooldown': {'name': 'Sprint Cooldown', 'description': 'Decrease sprint cooldown', 'max_level': 3, 'current_level': 0,
                               'effect': lambda: setattr(self, 'sprint_cooldown', max(5.0, 20.0 - (self.upgrades['sprint_cooldown']['current_level'] * 5.0)))},
            'sprint_speed': {'name': 'Sprint Speed', 'description': 'Increase sprint speed multiplier', 'max_level': 3, 'current_level': 0,
                            'effect': lambda: setattr(self, 'sprint_speed_multiplier', 2.0 + (self.upgrades['sprint_speed']['current_level'] * 0.5))}
        }
    
    def apply_upgrade(self, upgrade_key):
        if upgrade_key not in self.upgrades:
            return False
            
        upgrade = self.upgrades[upgrade_key]
        if upgrade['current_level'] >= upgrade['max_level']:
            return False
            
        upgrade['current_level'] += 1
        upgrade['effect']()  # Apply the upgrade effect
        return True
    
    def get_available_upgrades(self):
        # Return only upgrades that haven't reached max level
        return {k: v for k, v in self.upgrades.items() 
                if v['current_level'] < v['max_level']}
    
    def move(self, keys, mouse_buttons):
        dt = 1/60  # Assuming 60 FPS
        
        # Handle sprinting with right mouse button
        if mouse_buttons[2] and not self.is_sprinting and self.sprint_cooldown_timer <= 0 and self.stamina >= 100:
            self.is_sprinting = True
            self.sprint_timer = self.sprint_duration
            self.speed = self.base_speed * self.sprint_speed_multiplier
            self.stamina = 0
        
        # Update sprint state
        if self.is_sprinting:
            self.sprint_timer -= dt
            if self.sprint_timer <= 0:
                self.is_sprinting = False
                self.speed = self.base_speed
                self.sprint_cooldown_timer = self.sprint_cooldown
        
        # Update cooldown
        if self.sprint_cooldown_timer > 0:
            self.sprint_cooldown_timer -= dt
            if self.sprint_cooldown_timer <= 0:
                self.stamina = self.max_stamina
        
        # Movement
        if keys[K_w] or keys[K_UP]:
            self.y -= self.speed
        if keys[K_s] or keys[K_DOWN]:
            self.y += self.speed
        if keys[K_a] or keys[K_LEFT]:
            self.x -= self.speed
        if keys[K_d] or keys[K_RIGHT]:
            self.x += self.speed
        # Update rect position
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, screen):
        # Always draw the player at the center of the screen
        screen_width, screen_height = screen.get_size()
        center_x = screen_width // 2 - self.width // 2
        center_y = screen_height // 2 - self.height // 2
        pygame.draw.rect(screen, (255, 255, 255), (center_x, center_y, self.width, self.height))
        
        # Draw health bar above the player
        health_bar_width = 50
        health_bar_height = 5
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (255, 0, 0), 
                        (center_x, center_y - 10, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, (0, 255, 0),
                        (center_x, center_y - 10, health_bar_width * health_ratio, health_bar_height))
        
        # Draw stamina bar below the player
        stamina_bar_width = 50
        stamina_bar_height = 5
        stamina_ratio = self.stamina / self.max_stamina
        # Color changes based on sprint state
        if self.is_sprinting:
            stamina_color = (255, 255, 0)  # Yellow while sprinting
        elif self.sprint_cooldown_timer > 0:
            stamina_color = (100, 100, 100)  # Gray during cooldown
        else:
            stamina_color = (0, 255, 255)  # Cyan when available
        
        pygame.draw.rect(screen, (50, 50, 50), 
                        (center_x, center_y + self.height + 5, stamina_bar_width, stamina_bar_height))
        pygame.draw.rect(screen, stamina_color,
                        (center_x, center_y + self.height + 5, stamina_bar_width * stamina_ratio, stamina_bar_height))
    
    def gain_experience(self, amount):
        self.experience += amount
        # Remove automatic level up call, let Game class handle it
        # if self.experience >= self.experience_to_level:
        #     self.level_up()
    
    def level_up(self):
        self.level += 1
        self.experience -= self.experience_to_level
        self.experience_to_level = int(self.experience_to_level * 1.5)
        # Note: We don't automatically increase health anymore
        # Health increases are now part of the upgrade system 