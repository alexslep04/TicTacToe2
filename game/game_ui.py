"""
Pygame graphical UI for TicTacToe2.
Visualizes the board with stackable pieces and supports human play.
"""

import pygame
import sys
from typing import Optional, Tuple

from game.game_logic import TicTacToe2


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
PLAYER1_COLOR = (65, 105, 225)  # Royal Blue
PLAYER2_COLOR = (220, 20, 60)   # Crimson
HIGHLIGHT_COLOR = (255, 255, 0, 100)  # Yellow with alpha
BOARD_COLOR = (245, 222, 179)   # Wheat

# Dimensions
WINDOW_SIZE = 600
BOARD_SIZE = 450
CELL_SIZE = BOARD_SIZE // 3
BOARD_OFFSET = (WINDOW_SIZE - BOARD_SIZE) // 2
PIECE_PANEL_HEIGHT = 60

# Piece sizes (radius multipliers)
PIECE_RADII = {1: 0.2, 2: 0.32, 3: 0.44}


class GameUI:
    """Pygame-based UI for TicTacToe2."""
    
    def __init__(self, game: Optional[TicTacToe2] = None):
        pygame.init()
        pygame.display.set_caption("TicTacToe2 - Gobblet Style")
        
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + PIECE_PANEL_HEIGHT * 2))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.game = game if game else TicTacToe2()
        self.selected_piece: Optional[int] = None
        self.hover_cell: Optional[Tuple[int, int]] = None
        self.game_over = False
        self.winner: Optional[int] = None
    
    def run(self) -> None:
        """Main game loop."""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self._handle_hover(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self._reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            self._draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def _reset_game(self) -> None:
        """Reset the game state."""
        self.game.reset_board()
        self.selected_piece = None
        self.hover_cell = None
        self.game_over = False
        self.winner = None
    
    def _handle_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse click events."""
        if self.game_over:
            return
        
        # Check if clicking on piece panel
        piece = self._get_clicked_piece(pos)
        if piece is not None:
            if piece in self.game.get_current_player_pieces():
                self.selected_piece = piece
            return
        
        # Check if clicking on board
        cell = self._get_clicked_cell(pos)
        if cell is not None and self.selected_piece is not None:
            x, y = cell
            if self.game.is_valid_move(self.selected_piece, x, y):
                self.game.make_move(self.selected_piece, x, y)
                
                # Check for win
                if self.game.check_winner(x, y):
                    self.game_over = True
                    self.winner = self.game.current_player
                # Check for draw
                elif self.game.check_draw():
                    self.game_over = True
                    self.winner = None
                else:
                    # Switch player
                    self.game.current_player = 3 - self.game.current_player
                
                self.selected_piece = None
    
    def _handle_hover(self, pos: Tuple[int, int]) -> None:
        """Handle mouse hover for cell highlighting."""
        self.hover_cell = self._get_clicked_cell(pos)
    
    def _get_clicked_cell(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Get the board cell at the given screen position."""
        x, y = pos
        board_x = x - BOARD_OFFSET
        board_y = y - BOARD_OFFSET - PIECE_PANEL_HEIGHT
        
        if 0 <= board_x < BOARD_SIZE and 0 <= board_y < BOARD_SIZE:
            col = board_x // CELL_SIZE
            row = board_y // CELL_SIZE
            return (row, col)
        return None
    
    def _get_clicked_piece(self, pos: Tuple[int, int]) -> Optional[int]:
        """Get the piece size clicked in the piece panel."""
        x, y = pos
        current_player = self.game.current_player
        
        # Top panel for player 1, bottom panel for player 2
        if current_player == 1:
            panel_y = 0
        else:
            panel_y = WINDOW_SIZE + PIECE_PANEL_HEIGHT
        
        if panel_y <= y < panel_y + PIECE_PANEL_HEIGHT:
            # Check each piece size
            for i, size in enumerate([1, 2, 3]):
                piece_x = BOARD_OFFSET + i * (BOARD_SIZE // 3) + CELL_SIZE // 2
                piece_y = panel_y + PIECE_PANEL_HEIGHT // 2
                radius = int(CELL_SIZE * PIECE_RADII[size])
                
                if (x - piece_x) ** 2 + (y - piece_y) ** 2 <= radius ** 2:
                    return size
        return None
    
    def _draw(self) -> None:
        """Draw the entire game state."""
        self.screen.fill(WHITE)
        
        self._draw_piece_panels()
        self._draw_board()
        self._draw_pieces()
        self._draw_hover_highlight()
        self._draw_status()
        
        if self.game_over:
            self._draw_game_over()
    
    def _draw_piece_panels(self) -> None:
        """Draw the piece selection panels for both players."""
        # Player 1 panel (top)
        pygame.draw.rect(self.screen, LIGHT_GRAY, (0, 0, WINDOW_SIZE, PIECE_PANEL_HEIGHT))
        self._draw_player_pieces(1, 0)
        
        # Player 2 panel (bottom)
        pygame.draw.rect(
            self.screen, 
            LIGHT_GRAY, 
            (0, WINDOW_SIZE + PIECE_PANEL_HEIGHT, WINDOW_SIZE, PIECE_PANEL_HEIGHT)
        )
        self._draw_player_pieces(2, WINDOW_SIZE + PIECE_PANEL_HEIGHT)
    
    def _draw_player_pieces(self, player: int, panel_y: int) -> None:
        """Draw available pieces for a player in their panel."""
        pieces = self.game.player_pieces[player]
        color = PLAYER1_COLOR if player == 1 else PLAYER2_COLOR
        
        # Count pieces of each size
        piece_counts = {1: pieces.count(1), 2: pieces.count(2), 3: pieces.count(3)}
        
        for i, size in enumerate([1, 2, 3]):
            x = BOARD_OFFSET + i * (BOARD_SIZE // 3) + CELL_SIZE // 2
            y = panel_y + PIECE_PANEL_HEIGHT // 2
            radius = int(CELL_SIZE * PIECE_RADII[size])
            
            # Draw piece
            if piece_counts[size] > 0:
                piece_color = color
                # Highlight if selected
                if self.selected_piece == size and self.game.current_player == player:
                    pygame.draw.circle(self.screen, (255, 255, 0), (x, y), radius + 4)
                pygame.draw.circle(self.screen, piece_color, (x, y), radius)
                pygame.draw.circle(self.screen, BLACK, (x, y), radius, 2)
                
                # Draw count
                count_text = self.small_font.render(f"x{piece_counts[size]}", True, BLACK)
                self.screen.blit(count_text, (x + radius + 5, y - 8))
            else:
                # Grayed out if none available
                pygame.draw.circle(self.screen, GRAY, (x, y), radius)
                pygame.draw.circle(self.screen, BLACK, (x, y), radius, 1)
        
        # Player label
        label = self.small_font.render(f"Player {player}", True, color)
        self.screen.blit(label, (10, panel_y + 20))
    
    def _draw_board(self) -> None:
        """Draw the game board grid."""
        board_rect = pygame.Rect(
            BOARD_OFFSET, 
            BOARD_OFFSET + PIECE_PANEL_HEIGHT, 
            BOARD_SIZE, 
            BOARD_SIZE
        )
        pygame.draw.rect(self.screen, BOARD_COLOR, board_rect)
        
        # Grid lines
        for i in range(4):
            # Vertical
            x = BOARD_OFFSET + i * CELL_SIZE
            pygame.draw.line(
                self.screen, BLACK,
                (x, BOARD_OFFSET + PIECE_PANEL_HEIGHT),
                (x, BOARD_OFFSET + PIECE_PANEL_HEIGHT + BOARD_SIZE),
                2
            )
            # Horizontal
            y = BOARD_OFFSET + PIECE_PANEL_HEIGHT + i * CELL_SIZE
            pygame.draw.line(
                self.screen, BLACK,
                (BOARD_OFFSET, y),
                (BOARD_OFFSET + BOARD_SIZE, y),
                2
            )
    
    def _draw_pieces(self) -> None:
        """Draw pieces on the board."""
        for row in range(3):
            for col in range(3):
                piece_size = self.game.board_pieces[row][col]
                owner = self.game.board_owners[row][col]
                
                if piece_size > 0 and owner > 0:
                    x = BOARD_OFFSET + col * CELL_SIZE + CELL_SIZE // 2
                    y = BOARD_OFFSET + PIECE_PANEL_HEIGHT + row * CELL_SIZE + CELL_SIZE // 2
                    radius = int(CELL_SIZE * PIECE_RADII[piece_size])
                    color = PLAYER1_COLOR if owner == 1 else PLAYER2_COLOR
                    
                    pygame.draw.circle(self.screen, color, (x, y), radius)
                    pygame.draw.circle(self.screen, BLACK, (x, y), radius, 2)
    
    def _draw_hover_highlight(self) -> None:
        """Draw hover highlight on valid moves."""
        if self.hover_cell and self.selected_piece and not self.game_over:
            row, col = self.hover_cell
            if self.game.is_valid_move(self.selected_piece, row, col):
                x = BOARD_OFFSET + col * CELL_SIZE
                y = BOARD_OFFSET + PIECE_PANEL_HEIGHT + row * CELL_SIZE
                
                # Create a surface with alpha
                highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                highlight.fill((0, 255, 0, 80))
                self.screen.blit(highlight, (x, y))
    
    def _draw_status(self) -> None:
        """Draw current player status."""
        if not self.game_over:
            color = PLAYER1_COLOR if self.game.current_player == 1 else PLAYER2_COLOR
            text = self.font.render(f"Player {self.game.current_player}'s Turn", True, color)
            text_rect = text.get_rect(center=(WINDOW_SIZE // 2, BOARD_OFFSET + PIECE_PANEL_HEIGHT // 2))
            self.screen.blit(text, text_rect)
            
            if self.selected_piece:
                piece_text = self.small_font.render(
                    f"Selected: Size {self.selected_piece}", True, BLACK
                )
                self.screen.blit(piece_text, (WINDOW_SIZE - 150, BOARD_OFFSET + PIECE_PANEL_HEIGHT // 2 - 8))
    
    def _draw_game_over(self) -> None:
        """Draw game over overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE + PIECE_PANEL_HEIGHT * 2), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Winner text
        if self.winner:
            color = PLAYER1_COLOR if self.winner == 1 else PLAYER2_COLOR
            text = self.font.render(f"Player {self.winner} Wins!", True, color)
        else:
            text = self.font.render("It's a Draw!", True, WHITE)
        
        text_rect = text.get_rect(center=(WINDOW_SIZE // 2, (WINDOW_SIZE + PIECE_PANEL_HEIGHT * 2) // 2 - 30))
        self.screen.blit(text, text_rect)
        
        # Restart instructions
        restart_text = self.small_font.render("Press R to restart, ESC to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_SIZE // 2, (WINDOW_SIZE + PIECE_PANEL_HEIGHT * 2) // 2 + 20))
        self.screen.blit(restart_text, restart_rect)


def main():
    """Entry point for the graphical game."""
    ui = GameUI()
    ui.run()


if __name__ == "__main__":
    main()
