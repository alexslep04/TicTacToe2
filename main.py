import pygame
from ui.renderer import Renderer
from ui.events import Events
from game.board import Board
from game.game_manager import GameManager
from game.player import Player

class Main:
    def __init__(self):
        """Initialize the game."""
        # Initialize Pygame
        pygame.init()
        self.cell_size = 200  # Size of each grid cell
        self.grid_size = 3  # Grid size (e.g., 3x3)
        self.side_padding = self.cell_size  # Space on each side for player pieces
        self.screen_width = self.cell_size * self.grid_size + 2 * self.side_padding
        self.screen_height = self.cell_size * self.grid_size
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Tic-Tac-Toe with Pieces")

        # Initialize game components
        self.board = Board()
        self.renderer = Renderer(self.screen, cell_size=self.cell_size)
        self.events = Events()

        # Create players
        self.player1 = Player(name="Player 1", color="Blue")
        self.player2 = Player(name="Player 2", color="Red")

        # Initialize Game Manager
        self.game_manager = GameManager(self.player1, self.player2, self.renderer, self.events)

    def run(self):
        """Run the main game loop."""
        self.game_manager.start_game()

if __name__ == "__main__":
    main = Main()
    main.run()
