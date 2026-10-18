#!/usr/bin/env python3
"""Bestiaire - Roguelite Deckbuilding"""

import pygame
import sys
from pathlib import Path

# Configuration directe
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


class BestiaireGame:
    """Classe principale du jeu"""

    def __init__(self):
        pygame.init()

        # Configuration de l'écran
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bestiaire: Écorces & Échos")

        # Police
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)

        # Horloge
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        """Boucle principale du jeu"""
        while self.running:
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        print("Démarrage du jeu...")

            # Dessiner
            self.screen.fill((20, 20, 30))

            # Titre
            title_text = self.font.render("BESTIAIRE", True, (200, 200, 255))
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
            self.screen.blit(title_text, title_rect)

            subtitle_text = self.small_font.render("Écorces & Échos", True, (150, 150, 200))
            subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
            self.screen.blit(subtitle_text, subtitle_rect)

            # Instructions
            instruction_text = self.small_font.render("Appuyez sur ESPACE pour commencer", True, (255, 255, 255))
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
            self.screen.blit(instruction_text, instruction_rect)

            quit_text = self.small_font.render("ESC pour quitter", True, (150, 150, 150))
            quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
            self.screen.blit(quit_text, quit_rect)

            # Version
            version_text = self.small_font.render("v1.0.0 - Prototype", True, (100, 100, 100))
            self.screen.blit(version_text, (10, SCREEN_HEIGHT - 30))

            pygame.display.flip()

            # Limiter à 60 FPS
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


# Point d'entrée
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════╗
    ║         BESTIAIRE: Écorces & Échos      ║
    ║              Version 1.0.0               ║
    ╚══════════════════════════════════════════╝
    """)

    game = BestiaireGame()
    game.run()