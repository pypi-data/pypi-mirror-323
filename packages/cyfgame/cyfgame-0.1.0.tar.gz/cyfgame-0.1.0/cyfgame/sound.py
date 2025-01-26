import pygame.mixer as pm

pm.init()

def load(sound):
    return pm.Sound(sound)