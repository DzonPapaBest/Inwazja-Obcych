import pygame
from pygame.sprite import Sprite

class Ship(Sprite):
    """Klasa przeznaczona do zarządzania statkiem kosmicznym."""

    def __init__(self, ai_game):
        """Inicjalizacja statku kosmicznego i jego położenie początkowe"""
        super().__init__()
        
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings
        #Wczytanie statku kosmicznego i pobranie jego prostokąta.
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()

        #Każdy nowy statek kosmiczny pojawia sie na dole ekranu.
        self.rect.midbottom = self.screen_rect.midbottom

        #położenie statku jest przechowywane w postaci liczby zmienniprzecinkowej
        self.x = float(self.rect.x)

        #opcja wskazująca na poruszanie się statku
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """Uaktualnianie położenia statku na podstawie opcji wskazującej na jego ruch"""
        
        #Uaktualnienie wartości współżędnej X statku, an ie jego prostokąta.
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        #uaktualnienie obiektu rect na podstawie wartości self.x
        self.rect.x = self.x


    def blitme(self):
        """Wyświetlanie statku kosmicznego w jego aktualnym położeniu."""
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        """Umieszczenie statku na środku przy dolnej krawędzi ekranu."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)