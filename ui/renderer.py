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
            "highlight": (255, 255, 0),
        }
        self.font = pygame.font.Font(None, 36)
        self.board_offset_x = self.cell_size  # Reserve space for side padding
        self.grid_size = screen.get_height() // cell_size  # Dynamically calculate grid size

    def draw_board(self, board, players, current_player, selected_piece):
        """Draw the game board, pieces, and player indicators."""
        # Fill background
        self.screen.fill(self.colors["background"])

        # Draw grid lines with horizontal offset
        for x in range(1, self.grid_size):
            pygame.draw.line(
                self.screen, self.colors["line"],
                (self.board_offset_x + x * self.cell_size, 0),
                (self.board_offset_x + x * self.cell_size, self.grid_size * self.cell_size), 2
            )
            pygame.draw.line(
                self.screen, self.colors["line"],
                (self.board_offset_x, x * self.cell_size),
                (self.board_offset_x + self.grid_size * self.cell_size, x * self.cell_size), 2
            )

        # Draw pieces on the board
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell = board.grid[row][col]
                if cell is not None:
                    piece, player = cell
                    color = self.colors[f"player{player}"]
                    radius = {"S": 30, "M": 50, "L": 70}[piece]
                    pygame.draw.circle(
                        self.screen, color,
                        (self.board_offset_x + col * self.cell_size + self.cell_size // 2,
                         row * self.cell_size + self.cell_size // 2), radius
                    )

        # Draw remaining pieces
        self.draw_remaining_pieces(players, current_player, selected_piece)

        # Update the screen
        pygame.display.flip()

    def draw_remaining_pieces(self, players, current_player, selected_piece):
        """Draw the remaining pieces for each player on the sides of the board."""
        player = players[current_player]
        y_offset = 20  # Initial vertical offset for piece placement
        side_width = self.cell_size // 2  # Space for side pieces

        for size, count in player.pieces.items():
            if count > 0:
                color = self.colors[f"player{current_player}"]
                # Determine X position: left for Player 1, right for Player 2
                x = self.cell_size // 2 if current_player == 1 else self.screen.get_width() - self.cell_size // 2
                radius = {"S": 30, "M": 50, "L": 70}[size]
                center_x = x  # Adjust to ensure proper alignment
                center_y = y_offset + radius

                # Draw the piece circle
                pygame.draw.circle(self.screen, color, (center_x, center_y), radius)

                # Draw the piece count
                text = self.font.render(f"x{count}", True, color)
                self.screen.blit(text, (center_x + radius + 10, center_y - 10))

                # Highlight the selected piece
                if size == selected_piece:
                    pygame.draw.circle(self.screen, self.colors["highlight"], (center_x, center_y), radius + 5, 3)

                y_offset += 100  # Increment offset for the next piece

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
