import pygame

class Orb:
    def __init__(self, x, y, radius=10, color=(0, 128, 255), exp_value=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.exp_value = exp_value
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)

    def draw(self, screen, offset_x, offset_y):
        # Draw orb at its world position offset by the camera
        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.radius)

    def update_rect(self):
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius 