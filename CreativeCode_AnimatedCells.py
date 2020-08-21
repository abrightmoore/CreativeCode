# coding=utf-8
# @TheWorldFoundry

import pygame
import math
import random

class Display:
    def __init__(self, size, position):
        self.width, self.height = size
        self.center_of_view = position
        self.age = 0
        self.colour = ((40,20,80,255))

        pygame.init()

        print "Creating Surface and Window"
        self.surface = pygame.display.set_mode((self.width, self.height), pygame.SRCALPHA)
        print "Converting the surface to optimise rendering"
        self.surface.convert()
        print "Changing the caption"
        pygame.display.set_caption('SiNGe: the Simulation eNGine')
        self.labelfont = pygame.font.SysFont("monospace", 16)
        pygame.key.set_repeat(100) # Milliseconds before new key event issued
        self.FPS = 30
        fpsClock = pygame.time.Clock()
        fpsClock.tick(self.FPS)
        self.initialised = True

    def draw(self, elements):
        self.surface.fill((2,2,1,0), None, pygame.BLEND_SUB)

        for e in elements:
            if e.alive:
                e.draw(self)

    def update(self, elements):
        self.age += 1
        unhandledEvents = []
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                # Clicked on a UI element?
                unhandledEvents.append(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos  # Position on screen
                x = x-(self.width>>1) # Offset from centre of screen
                y = y-(self.height>>1) # Offset from centre of screen
                for e in elements:
                    e.handle_mouse_button_down(self,(x,y))
                unhandledEvents.append(event)
            elif event.type == pygame.KEYDOWN:
                unhandledEvents.append(event)
            else:
                unhandledEvents.append(event)

        pygame.display.update()

        return unhandledEvents

class Mass:

    def __init__(self):
        # Current vector
        self.position = 0,0 # Pixel co-ordinates
        self.speed = 0.01 # Pixel units
        self.direction = 0.0 # Radians

        self.turning_rate = 90


        self.max_speed = 0.5

        self.alive = True
        self.age = 0

        # Visual defaults
        self.radius = 16
        self.colour = (255,255,255,255)

        # Processing
        self.target_position = None
        self.target_direction = None
        self.turning_direction = None
        self.last_direction = None
        self.target_speed = 0
        self.direction_delta = None

        self.selected = False

    def set_position(self, position):
        self.position = position

    def draw(self, display):
        cov_x, cov_y = display.center_of_view
        x, y = self.position
        px = x - cov_x
        py = y - cov_y
        # print px, py
        if -self.radius-(display.width>>1) <= px < display.width+self.radius and -self.radius-(display.height>>1) <= py < display.height+self.radius:
            # Onscreen
            px += (display.width>>1)
            py += (display.height>>1)
            pygame.draw.circle(display.surface, self.colour, (int(px), int(py)), int(self.radius), 1)

            # Directional line
            pygame.draw.line(display.surface, (0, 255, 0, 255), (int(px), int(py)),
                             (int(px + self.radius * math.cos(self.direction)), int(py + self.radius * math.sin(self.direction))), 1)

            # Target Directional line
            if self.target_direction != None:
                pygame.draw.line(display.surface, (255, 0, 0, 255), (int(px), int(py)),
                             (int(px + self.radius * math.cos(self.target_direction)), int(py + self.radius * math.sin(self.target_direction))), 1)


            if self.target_position != None:
                tpx, tpy = self.target_position
                tpx += (display.width >> 1)
                tpy += (display.height >> 1)
                pygame.draw.circle(display.surface, self.colour, (int(tpx), int(tpy)), self.age%int(self.radius)+1, 1)
                # print tpx, tpy


    def update(self):
        self.age += 1
        x, y = self.position

        if self.target_position != None: # Need to lerp to the target position
            tx, ty = self.target_position
            dx = tx-x
            dy = ty-y
            if abs(dx) < 1 and abs(dy) < 1: # Are we there yet?
                self.target_position = None
                self.target_speed = 0
                self.turning_direction = None
            else: # We need to head to the target

                if self.recalculate_target:
                    self.target_direction = math.atan2(dy, dx)
                    self.direction_delta = (self.target_direction-self.direction)/self.turning_rate
                if abs(self.target_direction-self.direction_delta) < 0.1:
                    self.recalculate_target = True
                else:
                    self.last_direction = self.direction
                    self.direction += self.direction_delta
                    if self.last_direction < -0.3 and self.direction > 0.3:
                        self.direction -= math.pi*2.0
                    if self.last_direction > 0.3 and self.direction < -0.3:
                        self.direction += math.pi*2.0
                    print self.direction, self.last_direction

                # print self.direction, self.target_direction
                self.speed = self.speed+(self.target_speed-self.speed)/2

        # And... drift
        self.speed = self.speed+0.5*(self.target_speed-self.speed)
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < 0:
            self.speed = 0

        dx = self.speed * math.cos(self.direction)
        dy = self.speed * math.sin(self.direction)
        self.position = x + dx, y + dy

    def handle_mouse_button_down(self, display, pos):
        mx, my = pos
        x, y = self.position
        if x-self.radius < mx < x+self.radius and y-self.radius < my < y+self.radius:
            self.selected = True
        else:
            self.target_position = mx,my
            self.recalculate_target = True
            self.target_speed = self.max_speed

class Cell:
    def __init__(self, renderer, position, size):
        self.alive = True
        self.age = 0
        self.colour = (255,255,255,255)
        self.renderer = renderer
        self.position = position
        self.size = size
        self.rate = 30


    def draw(self, display):
        if self.alive:
            self.renderer(self, display, self.position, self.size)

    def update(self):
        if self.alive:
            self.age += 1

    def handle_mouse_button_down(self, display, pos):
        width = display.width
        height = display.height
        px, py = pos
        px += width>>1
        py += height>>1
        x, y = self.position

        if x-self.size <= px <= x+self.size and y-self.size <= py <= y+self.size:
            if self.alive:
                self.alive = False
            else:
                self.alive = True

def draw_circle_pulsing(cell, display, position, size):
    pygame.draw.circle(display.surface, cell.colour, position, (cell.age/10) % int(size) + 1, 1)

def draw_lines_intersection(cell, display, position, size):
    px, py = position
    span = (cell.age / cell.rate)%int(size)
    pos = float(span)/float(int(size))

    radius = size*math.sin(pos*math.pi)

    pygame.draw.line(display.surface, (255, 0, 0, 255), (int(px-radius), int(py-radius)),
                     (int(px+radius), int(py+radius)), 1)
    pygame.draw.line(display.surface, (255, 0, 0, 255), (int(px-radius), int(py+radius)),
                     (int(px+radius), int(py-radius)), 1)
    pygame.draw.circle(display.surface, cell.colour, (int(px-radius), int(py-radius)), 3, 1)


def draw_circle_pulsing_bounce(cell, display, position, size):
    span = (cell.age / cell.rate)%int(size)
    pos = float(span)/float(int(size))

    radius = size*math.sin(pos*math.pi)
    if int(radius) >= 1:
        pygame.draw.circle(display.surface, cell.colour, position, int(radius), 1)

def draw_lines_grid(cell, display, position, size):
    px, py = position
    span = (cell.age / cell.rate)%int(size)
    pos = float(span)/float(int(size))

    radius = size*math.sin(pos*math.pi)

    pygame.draw.line(display.surface, (0, 255, 0, 255), (int(px-radius), int(py-radius)),
                     (int(px-radius), int(py+radius)), 1)
    pygame.draw.line(display.surface, (0, 255, 0, 255), (int(px-radius), int(py+radius)),
                     (int(px+radius), int(py+radius)), 1)

def draw_poly_random(cell, display, position, size):
    px, py = position
    span = (cell.age / cell.rate)%int(size)
    pos = float(span)/float(int(size))

    radius = size*math.sin(pos*math.pi)

    radius = int(radius)
    pygame.draw.polygon(display.surface, cell.colour,
                        [(random.randint(px - radius, px + radius), random.randint(py - radius, py + radius)),
                         (random.randint(px - radius, px + radius), random.randint(py - radius, py + radius)),
                         (random.randint(px - radius, px + radius), random.randint(py - radius, py + radius)), ], 0)

def draw_poly_random_fixed(cell, display, position, size):
    px, py = position
    span = (cell.age / cell.rate)%int(size)
    pos = float(span)/float(int(size))

    radius = size

    radius = int(radius)
    pygame.draw.polygon(display.surface, cell.colour,
                        [(random.randint(px - radius, px + radius), random.randint(py - radius, py + radius)),
                         (random.randint(px - radius, px + radius), random.randint(py - radius, py + radius)),
                         (random.randint(px - radius, px + radius), random.randint(py - radius, py + radius)), ], 0)


def draw_lines_grid_upper(cell, display, position, size):
    px, py = position
    span = (cell.age / cell.rate)%int(size)
    pos = float(span)/float(int(size))

    radius = size*math.sin(pos*math.pi)

    pygame.draw.line(display.surface, (0, 255, 0, 255), (int(px-radius), int(py-radius)),
                     (int(px+radius), int(py-radius)), 1)
    pygame.draw.line(display.surface, (0, 255, 0, 255), (int(px+radius), int(py-radius)),
                     (int(px+radius), int(py+radius)), 1)


def game_loop():

    # Set up display
    width = 680
    height = 680
    display = Display((width, height),(0,0))

    #   Player is a star fighter in a field of asteroids
    #   Using the mouse, the player can maneouver around and shoot at obstacles

    # Enter game loop
    #   Player is at rest in the centre of the screen
    #   Player has a waypoint marker showing the direction to travel in
    #   Player can navigate around obstacles, destroy them for salvage, thrust and slow


    elements = []

    cellSize = int(width/random.randint(10,30))


    # Cycling bubbles
    F_BUBBLE_CYCLE = False
    if F_BUBBLE_CYCLE:
        for x in xrange(0, int(width/cellSize)):
            for y in xrange(0, int(height/cellSize)):
                cell = Cell(draw_circle_pulsing_bounce, ( (cellSize>>1)+x*cellSize ,(cellSize>>1)+y*cellSize), cellSize>>1)
                cell.age = random.randint(0,1000)
                cell.rate = random.randint(10,30)
                cell.colour = (random.randint(128, 255), random.randint(128, 255), random.randint(128, 255), 255)
                elements.append(cell)

    F_GRID = False
    if F_GRID:
        for x in xrange(0, int(width/cellSize)):
            for y in xrange(0, int(height/cellSize)):
                if random.random() >= 0.0:
                    cell = Cell(draw_lines_grid, ( (cellSize>>1)+x*cellSize ,(cellSize>>1)+y*cellSize), cellSize>>1)
                    cell.age = random.randint(0,1000)
                    cell.rate = random.randint(10,11)
                    elements.append(cell)

    F_GRID_UPPER = False
    if F_GRID_UPPER:
        for x in xrange(0, int(width/cellSize)):
            for y in xrange(0, int(height/cellSize)):
                if random.random() >= 0.0:
                    cell = Cell(draw_lines_grid_upper, ( (cellSize>>1)+x*cellSize ,(cellSize>>1)+y*cellSize), cellSize>>1)
                    cell.age = random.randint(0,1000)
                    cell.rate = random.randint(10,11)
                    elements.append(cell)


    F_WALL_CYCLE = False
    if F_WALL_CYCLE:
        for x in xrange(0, int(width/cellSize)):
            for y in xrange(0, int(height/cellSize)):
                if random.random() > 0.3:
                    cell = Cell(draw_lines_intersection, ( (cellSize>>1)+x*cellSize ,(cellSize>>1)+y*cellSize), cellSize>>1)
                    cell.age = random.randint(0,1000)
                    cell.rate = random.randint(10,11)
                    cell.colour = (random.randint(128, 255), random.randint(128, 255), random.randint(128, 255), 255)
                    elements.append(cell)

    F_POLY_RANDOM = False
    if F_POLY_RANDOM:
        for x in xrange(0, int(width/cellSize)):
            for y in xrange(0, int(height/cellSize)):
                if random.random() > 0.3:
                    cell = Cell(draw_poly_random, ( (cellSize>>1)+x*cellSize ,(cellSize>>1)+y*cellSize), cellSize>>1)
                    cell.age = random.randint(0,1000)
                    cell.rate = random.randint(10,11)
                    cell.colour = (random.randint(128, 255), random.randint(128, 255), random.randint(128, 255), 255)
                    elements.append(cell)

    F_POLY_RANDOM_FIXED = True
    if F_POLY_RANDOM_FIXED:
        for x in xrange(0, int(width/cellSize)):
            for y in xrange(0, int(height/cellSize)):
                if random.random() > 0.3:
                    cell = Cell(draw_poly_random_fixed, ( (cellSize>>1)+x*cellSize ,(cellSize>>1)+y*cellSize), cellSize>>1)
                    cell.age = random.randint(0,1000)
                    cell.rate = random.randint(10,11)
                    cell.colour = (random.randint(128, 255), random.randint(128, 255), random.randint(128, 255), 255)
                    elements.append(cell)


    # Main loop
    keepGoing = True
    iterationCount = 0

    mousepos = -999, -999  # Default
    while keepGoing:
        iterationCount += 1

        # Tick the world
        newElements = []
        for e in elements:
            if e.alive:
                e.update()
                newElements.append(e)
        elements = newElements

        # Draw the world
        display.draw(elements)

        for event in display.update(elements):
            if event.type == pygame.QUIT:
                return False
            else:
                print event  # Placeholder

    # On quit, clean up


if __name__ == '__main__':
    game_loop()


