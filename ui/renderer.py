import pygame

class Renderer:
    def __init__(self, screen, cell_size=200):
        """Initialize the renderer with screen and cell dimensions."""
        self.screen = screen
        self.cell_size = cell_size
        self.colors = {
            "background": (30, 30, 30),
            "line": (200, 200, 200),
            "player1": (50, 150, 250),
            "player2": (250, 50, 50),
            "highlight": (255, 255, 0)
        }
        self.font = pygame.font.Font(None, 36)

    def draw_board(self, board, players, current_player, selected_piece):
        """Draw the game board, pieces, and player indicators."""
        # Fill background
        self.screen.fill(self.colors["background"])

        # Draw grid lines
        for x in range(1, 3):  # Assuming a 3x3 grid
            pygame.draw.line(self.screen, self.colors["line"],
                             (x * self.cell_size, 0),
                             (x * self.cell_size, 3 * self.cell_size), 2)
            pygame.draw.line(self.screen, self.colors["line"],
                             (0, x * self.cell_size),
                             (3 * self.cell_size, x * self.cell_size), 2)

        # Draw pieces on the board
        for row in range(3):
            for col in range(3):
                cell = board.grid[row][col]
                if cell is not None:
                    piece, player = cell
                    color = self.colors[f"player{player}"]
                    radius = {"S": 30, "M": 50, "L": 70}[piece]
                    pygame.draw.circle(self.screen, color,
                                       (col * self.cell_size + self.cell_size // 2,
                                        row * self.cell_size + self.cell_size // 2), radius)

        # Draw remaining pieces
        self.draw_remaining_pieces(players, current_player, selected_piece)

        # Update the screen
        pygame.display.flip()

    def draw_remaining_pieces(self, players, current_player, selected_piece):
        """Draw the remaining pieces for each player on the sides of the board."""
        player = players[current_player]
        y_offset = 20

        for size, count in player.pieces.items():
            if count > 0:
                color = self.colors[f"player{current_player}"]
                x = 20 if current_player == 1 else self.screen.get_width() - 60
                radius = {"S": 30, "M": 50, "L": 70}[size]
                pygame.draw.circle(self.screen, color, (x, y_offset + radius), radius)
                text = self.font.render(f"x{count}", True, color)
                self.screen.blit(text, (x + 40, y_offset + radius - 10))
                if size == selected_piece:
                    pygame.draw.circle(self.screen, self.colors["highlight"],
                                       (x, y_offset + radius), radius + 5, 3)
                y_offset += 100

    def highlight_piece(self, piece):
        """Highlight a piece when it is selected."""
        # This is handled dynamically in `draw_remaining_pieces` by highlighting the selected piece.
        pass

    def show_message(self, message):
        """Display a message to the screen."""
        text_surface = self.font.render(message, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, 10))
        pygame.draw.rect(self.screen, self.colors["background"],
                         text_rect.inflate(20, 10))  # Clear area for message
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()
