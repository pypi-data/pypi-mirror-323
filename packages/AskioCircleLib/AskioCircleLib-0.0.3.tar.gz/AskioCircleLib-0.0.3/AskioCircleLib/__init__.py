import pygame
import math

class Circle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def collidepoint(self, point):
        px, py = point
        return math.hypot(px - self.x, py - self.y) <= self.radius

    def colliderect(self, rect):
        rect_x, rect_y, rect_w, rect_h = rect
        closest_x = max(rect_x, min(self.x, rect_x + rect_w))
        closest_y = max(rect_y, min(self.y, rect_y + rect_h))
        return self.collidepoint((closest_x, closest_y))
    
    def draw(self, surface, color):
        pygame.draw.circle(surface, color, (self.x, self.y), self.radius)