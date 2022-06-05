import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """Ogólna klasa przeznaczona do zarządzania zasobami i sposobem
    działania gry"""
    def __init__(self):
        """Inicjalizacja gry i utworzenie jej zasobów."""
        pygame.init()

        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Inwazja obcych")

        self.clock = pygame.time.Clock()
        #Utworzenie egzemplarza przechowującego dane statystyczne dotyczące gry.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        #Utworzenie przycisku gra.
        self.play_button = Button(self, "Graj")

    def run_game(self):
        """Rozpoczęcie pętli głównej gry."""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                
            self._update_screen()
            self.clock.tick(self.settings.FPS)
    def _check_events(self):
        """Reakcja na zdarzenia generowane przez klawiaturę i mysz."""  
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)   
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            

    def _check_keydown_events(self, event):
        """Reakcja na naciśnięcie klawisza."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()


    def _check_keyup_events(self, event):
        """Reakcja na zwolnienie klawisza."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_play_button(self, mous_pos):
        """Rozpoczęcie nowej gry po kliknięciu przycisku Gra przez użytkownika."""
        button_clicked = self.play_button.rect.collidepoint(mous_pos)
        if button_clicked and not self.stats.game_active:
            #Wyzerowanie ustawień dotyczących gry.
            self.settings.initialize_dynamic_settings()

            #Wyzerowanie danych statystycznych gry.
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()

            #Usunięcie zawartości listy aliens i bullets.
            self.aliens.empty()
            self.bullets.empty()
        
            #Utworzenie nowej floty i wyśrodkowanie statku.
            self._create_fleet()
            self.ship.center_ship()

            #Ukrycie kursora myszy.
            pygame.mouse.set_visible(False)
            
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

    def _fire_bullet(self):
        """utworzenie nowego pocisku i dodanie go do grupy pocisków."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_screen(self):
        """Uaktualnienie obrazów na ekranie i przejście do nowego ekranu."""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        #Wyswietlanie informacji o punktacji.
        self.sb.show_score()

        #Wyświetlanie przycisku tylko w tedy gdy gra jest nieaktywna.
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()

    def _update_bullets(self):
        """Uaktualnienie położenia pocisków i usuniecie tych niewidocznych 
        na ekranie."""
        #uaktualnienie położenia pocisku
        self.bullets.update()

        #Usuwanie pocisków które znajdują się poza ekranem.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()
    
    def _check_bullet_alien_collisions(self):
        """Reakcja na kolizję między pociskiem i obcym."""
        #Usuniecie wszystkich pocisków i obcych, między którymi doszło do kolizji.
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            #pozbycie się istniejacych pocisków i utworzenie nowej floty.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            
            #inkrementacja numeru poziomu
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """
        Sprawdzenie, czy flota obcych znajduje się przy krawędzi,
        a następnieuaktualnienie położenia wszystkich obcych we flocie.
        """
        self._check_fleet_edges()
        self.aliens.update()

        #Wykrycie kolizji między obcym a statkiem.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        #Wykrywanie obcych docierających do dolnej krawędzi ekranu.
        self._check_aliens_bottom()

    def _ship_hit(self):
        """Reakcja na uderzenie obcego w statek."""
        if self.stats.ships_left > 0:
            #Zmniejszenie wartosci przechowywanej w ship_left
            #i uaktualnienie tablicy wyników.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            
            #Usunięcie zawartości listy aliens i bullets.
            self.aliens.empty()
            self.bullets.empty()

            #Utworzenie nowej floty i wyśrodkowanie statku.
            self._create_fleet()
            self.ship.center_ship()
            #Pauza
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Sprawdzenie czy którykolwiek obcy dotarł do dolnej krawędzi ekranu."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                #Tak samo jak w przypadku zderzenia statku z obcym.
                self._ship_hit()
                break

    def _create_fleet(self):
        """Utworzenie pełnej floty obcych."""
        #Utworzenie obcego i ustalenie liczby obcych, którzy zmieszczą się w rzędzie.
        #Odległość między poszczególnymi obcymi jest równa szerokości obcego.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        avalible_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = avalible_space_x // (2 * alien_width)

        #Ustalenie ile rzędów obcych zmieści się na ekranie.
        ship_height = self.ship.rect.height
        avalible_space_y = (self.settings.screen_height - 
            (3 * alien_height) - ship_height)
        number_rows = avalible_space_y // (2 * alien_height)

        #Utworzenie floty obcych.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):        
        """Utworzenie obcego i umieszczenie go w rzędzie."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)
    
    def _check_fleet_edges(self):
        """Odpowiednia reakcja gdy obcy dotrze do krawędzi ekranu."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """
        Przesunięcie całej folty w dół i zmiana kierunku,
        w którym się ona porusza.
        """
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


if __name__ == '__main__':
    #Utworzenie egzemplaza gry i jej uruchomienie.
    ai = AlienInvasion()
    ai.run_game()