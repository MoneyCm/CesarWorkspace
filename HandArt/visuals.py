import pygame
import random
import colorsys

class Particle:
    def __init__(self, x, y, hue):
        self.x = x
        self.y = y
        self.size = random.randint(4, 10)
        self.life = 255
        self.color = (255, 255, 255)
        self.hue = hue
        
        # Physics
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.decay = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size -= 0.1
        
        # Color Cycle
        self.hue = (self.hue + 0.005) % 1.0
        r, g, b = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
        self.color = (int(r*255), int(g*255), int(b*255))

    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            # Allow transparency
            s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.life), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class ArtEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = []
        self.hue = 0.0
        
    def add_particles(self, x, y, amount=2):
        for _ in range(amount):
            self.particles.append(Particle(x, y, self.hue))
        self.hue = (self.hue + 0.002) % 1.0

    def update_and_draw(self, surface):
        for p in self.particles:
            p.update()
            p.draw(surface)
            
        # Remove dead particles
        self.particles = [p for p in self.particles if p.life > 0 and p.size > 0]
        
    def clear(self):
        self.particles = []
