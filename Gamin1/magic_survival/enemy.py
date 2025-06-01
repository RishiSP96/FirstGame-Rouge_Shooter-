import pygame

class Enemy:
    def __init__(self, x, y, radius= 15, color=(255, 0, 0), speed= 1.5):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)

    def update(self, player_x, player_y):
        # Compute direction (dx, dy) toward the player
        dx = player_x - self.x
        dy = player_y - self.y
        dist = (dx * dx + dy * dy) ** 0.5
        if dist > 0:
            dx /= dist
            dy /= dist
        # Move (glide) toward the player
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

    def separate(self, other):
        # Push this enemy away from another enemy if too close
        dx = self.x - other.x
        dy = self.y - other.y
        dist = (dx * dx + dy * dy) ** 0.5
        min_dist = self.radius + other.radius
        if dist < min_dist and dist > 0:
            push = (min_dist - dist) / 2
            dx /= dist
            dy /= dist
            self.x += dx * push
            self.y += dy * push
            other.x -= dx * push
            other.y -= dy * push
            self.rect.x = self.x - self.radius
            self.rect.y = self.y - self.radius
            other.rect.x = other.x - other.radius
            other.rect.y = other.y - other.radius

    def draw(self, screen, offset_x, offset_y):
        # Draw enemy (as a red diamond shape) at its world position offset by the camera
        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        diamond_points = [
            (int(screen_x), int(screen_y - self.radius)),  # top
            (int(screen_x + self.radius), int(screen_y)),  # right
            (int(screen_x), int(screen_y + self.radius)),  # bottom
            (int(screen_x - self.radius), int(screen_y))   # left
        ]
        pygame.draw.polygon(screen, self.color, diamond_points) 