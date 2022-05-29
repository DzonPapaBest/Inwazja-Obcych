class GameStats:
    """Monitorowanie danych statycznych w grze "Inwazja Obcych"."""

    def __init__(self, ai_game):
        """Inicjalizacja danych statystycznych."""
        self.settings = ai_game.settings
        self.reset_stats()
        #Uruchomienie gry "Inwazja Obcych" w stanie aktywnym
        self.game_active = False

        #Najlepszy winik nigdy nie powinien zostać wyzerowany.
        self.high_score = 0
        
    def reset_stats(self):
        """
        Inicjalizacja danych statystycznych, które moga zmieniać się
        w trakcie gry.
        """
        self.ships_left = self.settings.ship_limit
        self.score = 0