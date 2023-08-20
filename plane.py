import os
import pygame as pg


def load_image(filename, colorkey=-1, scale=1):
    image = pg.image.load(filename)
    image = image.convert()
    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image, image.get_rect()


class CellGraphic:

    def __init__(self, x, y, cell, width):
        self.x, self.y = x, y
        self.cell = cell
        self.down = False
        self.width = width
        self.flagged = False

    def draw(self, screen):
        if not self.cell.revealed:
            pg.draw.rect(screen, "gray", (self.x+1, self.y+1, self.width-2, self.width-2))
            if self.flagged:
                pg.draw.rect(screen, "red", (self.x+5, self.y+5, 3, 3))
        elif self.cell.label == "*":
            pg.draw.rect(screen, "red", (self.x + 1, self.y + 1, self.width - 2, self.width - 2))
            myfont = pg.font.SysFont("monospace", 40)
            text = myfont.render(self.cell.label, 1, "white")
            text_h, text_w = text.get_size()
            screen.blit(text, (self.x + 1 + (self.width - 2) // 2 - text_h / 2,
                               self.y + 1 + (self.width - 2) // 2 - text_h / 2))
        else:
            pg.draw.rect(screen, "white", (self.x + 1, self.y + 1, self.width - 2, self.width - 2))
            if self.cell.label != "0":
                myfont = pg.font.SysFont("monospace", 15)
                text = myfont.render(self.cell.label, 1, "black")
                text_h, text_w = text.get_size()
                screen.blit(text, (self.x+1 + (self.width-2)/2 - text_h/2,
                                   self.y+1 + (self.width-2)/2 - text_w/2))

    def notify(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            event_x, event_y = event.pos
            in_x_range = self.x < event_x < self.x + self.width
            in_y_range = self.y < event_y < self.y + self.width
            if in_x_range and in_y_range:
                if event.button == 1:
                    self.down = True
                elif event.button == 3:
                    self.flagged = True
        elif event.type == pg.MOUSEBUTTONUP and self.down:
            self.down = False
            self.cell.reveal()


class Message:

    def __init__(self, x, y, msg, color, font_size):
        self.x, self.y = x, y
        self.msg = msg
        self.color = color
        self.font_size = font_size
        self.completion_percentage = 0.0

    def reset_message(self, msg):
        self.msg = msg

    def set_completion_percentage(self, percent):
        self.completion_percentage = percent

    def draw(self, screen):
        myfont = pg.font.SysFont("monospace", self.font_size)
        text = myfont.render(self.msg, 1, self.color)
        screen.blit(text, (self.x, self.y))

    def notify(self, event):
        pass


class PlayButton(pg.sprite.Sprite):

    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.x, self.y = x, y
        self.image_file = f"images/play.png"
        self.image_width = 28
        self.image, self.rect = None, None
        self.down = False
        self.redraw()

    def size(self):
        return self.rect.width, self.rect.height

    def current_position(self):
        return self.x, self.y

    def notify(self, event, plane):
        if event.type == pg.MOUSEBUTTONDOWN and not self.down:
            x, y = event.pos
            button_x, button_y = plane.translate_coordinates(self.x, self.y)
            if (button_x - self.image_width/2 <= x <= button_x + self.image_width/2
                and button_y - self.image_width/2 <= y <= button_y + self.image_width/2):
                self.image_file = f"images/play_pushed.png"
                self.down = True
                plane.button_pushed = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.image_file = f"images/play.png"
            self.down = False

    def redraw(self):
        self.image, self.rect = load_image(self.image_file)

    def update(self):
        self.redraw()

class CartesianPlane:
    def __init__(self, x_max, y_max, screen_width, screen_height,
                 bg_color=(0, 0, 200),
                 grid_color=(0, 0, 200)):
        self.screen = pg.display.set_mode((screen_width, screen_height), pg.SCALED)
        self.screen_width, self.screen_height = self.screen.get_size()
        self.x_max = x_max
        self.y_max = y_max
        self.x_pixel_increment = self.screen_width // self.x_max
        self.y_pixel_increment = self.screen_height // self.y_max
        self.sprite_list = []
        self.sprites = pg.sprite.RenderPlain(self.sprite_list)
        self.screen = pg.display.get_surface()
        self.widgets = []
        self.background = None
        self.bg_color = bg_color
        self.grid_color = grid_color
        self.clock = Message(5, screen_height - 25, "-.--", "white", 20)
        self.average = None
        self.completion_percentage = 0.0
        self.refresh()
        self.button_pushed = False

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)
        self.sprites = pg.sprite.RenderPlain(self.sprite_list)

    def add_widget(self, widget):
        self.widgets.append(widget)

    def report_game_over(self, win):
        self.grid_color=(0, 120, 0) if win else (200, 0, 0)
        self.bg_color = (0, 120, 0) if win else (200, 0, 0)

    def report_time(self, time):
        if self.average is None:
            self.clock.msg = f"{time:.2f}"
        else:
            self.clock.msg = f"{time:.2f} [{self.average:.2f}]"

    def report_average(self, time):
        self.average = time

    def report_completion_percentage(self, percent):
        self.completion_percentage = percent

    def refresh(self):
        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(self.bg_color)
        for y in range(self.y_pixel_increment, self.screen_height, self.y_pixel_increment):
            pg.draw.aaline(self.background, self.grid_color, (0, y), (self.screen_width, y))
        for x in range(self.x_pixel_increment, self.screen_width, self.x_pixel_increment):
            pg.draw.aaline(self.background, self.grid_color, (x, 0), (x, self.screen_height))
        self.screen.blit(self.background, (0, 0))
        self.sprites.update()
        for sprite in self.sprites:
            sprite.redraw()
            x, y = sprite.current_position()
            coords = self.translate_coordinates(x, y)
            if coords is not None:
                width, height = sprite.size()
                sprite.rect = coords[0] - width//2, coords[1] - height//2
        pg.draw.rect(self.screen, (120,120,255),
                     (0, self.screen_height-30, self.completion_percentage * self.screen_width, 30))
        self.clock.draw(self.screen)
        self.sprites.draw(self.screen)
        for widget in self.widgets:
            widget.draw(self.screen)
        pg.display.flip()

    def notify(self, event):
        for sprite in self.sprites:
            sprite.notify(event, self)
        for widget in self.widgets:
            widget.notify(event)

    def in_bounds(self, x, y):
        return 0 <= x <= self.x_max, 0 <= y <= self.y_max

    def translate_coordinates(self, x, y):
        return (x * self.x_pixel_increment,
                self.screen_height - (y * self.y_pixel_increment))


