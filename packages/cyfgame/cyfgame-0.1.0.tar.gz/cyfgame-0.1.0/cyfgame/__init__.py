# -*- coding:utf-8 -*-

import pygame
import time
import copy

Run = True
name = "cyfgame"
width = 500
height = 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption(name)

def init():
    global screen
    pygame.init()
    screen = pygame.display.set_mode((width, height), 0, 32)
    pygame.display.set_caption(name)

def quit():
    global Run
    Run = False

def python_pos(x, y):
    return width//2+x, height//2-y

def collision(self, role):
    image1 = self.image[self.imageid].convert_alpha()
    new_width = image1.get_width() * self.size / 200
    new_height = image1.get_height() * self.size / 200
    image1 = pygame.transform.scale(image1, (new_width, new_height))
    image1 = pygame.transform.rotate(image1, (450 - self.d) % 360)
    rect1 = image1.get_rect(center=python_pos(self.x, self.y))
    mask1 = pygame.mask.from_surface(image1)

    image2 = role.image[role.imageid].convert_alpha()
    new_width = image2.get_width() * role.size / 200
    new_height = image2.get_height() * role.size / 200
    image2 = pygame.transform.scale(image2, (new_width, new_height))
    image2 = pygame.transform.rotate(image2, (450 - role.d) % 360)
    rect2 = image2.get_rect(center=python_pos(role.x, role.y))
    mask2 = pygame.mask.from_surface(image2)

    offset = (rect2.x - rect1.x, rect2.y - rect1.y)

    return mask1.overlap(mask2, offset) is not None

def wait(t):
    return t

class Role:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.d = 90
        self.alpha = 0
        self.actionid = 0
        self.size = 100
        self.name = "Role"
        self.image = []
        self.imageid = 0
        self.cloneMe = []
        self.isShow = True
        self.var = {}

    def left(self, angle):
        self.d -= angle

    def right(self, angle):
        self.d += angle

    def setx(self, x):
        self.x = x
    
    def sety(self, y):
        self.y = y

    def goto(self, x, y):
        if type(x) == type((0, 0)):
            x, y = x
        self.x = x
        self.y = y

    def setd(self, d):
        self.d = d

    def setSize(self, size):
        self.size = size

    def addx(self, x):
        self.x += x

    def addy(self, y):
        self.y += y

    def addSize(self, size):
        self.size += size

    def insertImage(self, image):
        self.image.append(image)

    def setImage(self, id):
        self.imageid = id - 1

    def nextImage(self):
        self.imageid = (self.imageid + 1) % len(self.image)

    def hide(self):
        self.isShow = False

    def show(self):
        self.isShow = True

    def clone(self):
        cloneMe = copy.copy(self)
        cloneMe.cloneMe = []
        self.cloneMe.append(cloneMe)

    def collision(self, role):
        if role.isShow and collision(self, role): return True
        for i in role.cloneMe:
            if i.isShow and collision(self, i): return True
        return False

    def display(self):
        if self.isShow:
            image = self.image[self.imageid]
            new_width = image.get_width() * self.size / 200
            new_height = image.get_height() * self.size / 200
            image = pygame.transform.scale(image, (new_width, new_height))
            rect = image.get_rect()
            image = pygame.transform.rotate(image, (450-self.d)%360)
            rect = image.get_rect(center=rect.center)
            rect.center = (python_pos(self.x, self.y))
            image.set_alpha((100-self.alpha)/20*51)
            screen.blit(image, rect)

class GameControl:
    def __init__(self):
        self.gameid = 0
        self.lastKey = {}

    def key(self, k):
        self.lastKey = pygame.key.get_pressed()
        return pygame.key.get_pressed()[k]
    
    def updatekey(self):
        self.lastKey = pygame.key.get_pressed()

    def keydown(self, k):
        return not self.lastKey[k] and self.key(k)

class MixerControl:
    def __init__(self):
        self.sound = {}

    def insertSound(self, name, sound):
        self.sound[name] = sound

    def play(self, name):
        self.sound[name].play()

def app():
    pass

def main():
    global Run
    screen.fill("#ffffff")
    pygame.display.update()
    while Run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Run = False

        app()
        time.sleep(0.015)
        pygame.display.update()