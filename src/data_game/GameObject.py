import pygame
import time

pygame.init()

class GameObject:
    def __init__(self):
        pass

    def update(self, game_state, render_surface):
        pass

    def render(self, render_surface):
        pass



class TextSurface(GameObject):
    def __init__(self, pos=(0, 0), size=(0, 0), text='', margin=((5, 5), (5, 5)), surface_color=(10, 10, 10), text_color=(220, 220, 220), text_font=pygame.font.SysFont('Arial', 16)):
        self.pos = pos
        self.size = size
        self.margin = margin
        self.text = text
        self.surface_color = surface_color
        self.text_color = text_color
        self.text_font = text_font
        self.surface = pygame.Surface(size)
        self.text_surface = self.text_font.render(text, True, self.text_color, None, wraplength=self.size[0]-sum(self.margin[0]))
        self.text_rect = self.text_surface.get_rect(topleft=self.pos)

    def update(self):
        pass

    def render(self, render_surface):
        self.text_surface = self.text_font.render(self.text, True, self.text_color, None, wraplength=self.size[0]-sum(self.margin[0]))
        self.text_rect = self.text_surface.get_rect(topleft=self.margin[0])
        self.surface.fill(self.surface_color)
        self.surface.blit(self.text_surface, self.margin[0])
        render_surface.blit(self.surface, self.pos)

class InteractiveTextSurface(TextSurface):
    def __init__(self, pos=(0, 0), size=(0, 0), text='', margin=((5, 5), (5, 5)), surface_color=(20, 20, 20), text_color=(72, 242, 21), text_font=pygame.font.SysFont('Arial', 16)):
        super().__init__(pos=pos, size=size, margin=margin, text=text, surface_color=surface_color, text_color=text_color, text_font=text_font)
        self.keydown_events = []
        self.active = False

    def update(self):
        for event in self.keydown_events:
            if event.key == pygame.K_BACKSPACE:
                if self.text:
                    self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.text = self.text + '\n'
            else:
                self.text = self.text + str(event.unicode)
        self.keydown_events = []
        super().update()

    def render(self, render_surface):
        super().render(render_surface)



