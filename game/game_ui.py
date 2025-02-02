import pygame

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
BOARD_SIZE = 200
BOARD_X = (WIDTH - BOARD_SIZE) // 2
BOARD_Y = (HEIGHT - BOARD_SIZE) // 2
PIECE_COLORS = {1: (0, 0, 255), 2: (255, 0, 0)}  # Blue for Player 1, Red for Player 2
HIGHLIGHT_COLOR = (255, 255, 0)
BACKGROUND_COLOR = (0, 0, 0)
BOX_COLOR = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)
LINE_COLOR = (200, 200, 200)

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stacking Tic-Tac-Toe")

# Font
font = pygame.font.Font(None, 36)

# Game state
selected_piece = None
current_player = 1
player_pieces = {1: [2, 2, 2], 2: [2, 2, 2]}  # Count of each size left

# Function to draw player pieces
def draw_player_pieces():
    for player in [1, 2]:
        x_pos = 100 if player == 1 else WIDTH - 100
        box_height = 200
        box_top = (HEIGHT - box_height) // 2
        piece_sizes = [30, 20, 10]  # Radii for large, medium, small
        total_piece_height = sum(2 * s for s in piece_sizes)
        spacing = (box_height - total_piece_height) / 4
        pygame.draw.rect(screen, BOX_COLOR, (x_pos - 40, box_top, 80, box_height), 2)
        
        y_pos = box_top + spacing + piece_sizes[0]  # Position first piece
        for i, size in enumerate(piece_sizes):
            color = PIECE_COLORS[player]
            pygame.draw.circle(screen, color, (x_pos, int(y_pos)), size)
            if selected_piece == (3 - i) and current_player == player:
                pygame.draw.circle(screen, HIGHLIGHT_COLOR, (x_pos, int(y_pos)), size + 3, 3)
            
            # Draw count indicator outside the box
            if player_pieces[player][i] > 0:
                text = font.render(f"x{player_pieces[player][i]}", True, TEXT_COLOR)
                text_x = x_pos + 50 if player == 1 else x_pos - 70
                screen.blit(text, (text_x, int(y_pos - 10)))
            
            y_pos += 2 * size + spacing  # Move down for the next piece

# Function to draw the board
def draw_board():
    cell_size = BOARD_SIZE // 3
    pygame.draw.rect(screen, BOX_COLOR, (BOARD_X - 2, BOARD_Y - 2, BOARD_SIZE + 4, BOARD_SIZE + 4), 2)
    
    for i in range(1, 3):
        pygame.draw.line(screen, LINE_COLOR, (BOARD_X, BOARD_Y + i * cell_size), (BOARD_X + BOARD_SIZE, BOARD_Y + i * cell_size), 2)
        pygame.draw.line(screen, LINE_COLOR, (BOARD_X + i * cell_size, BOARD_Y), (BOARD_X + i * cell_size, BOARD_Y + BOARD_SIZE), 2)

# Main loop
running = True
while running:
    screen.fill(BACKGROUND_COLOR)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                selected_piece = 1
            elif event.key == pygame.K_2:
                selected_piece = 2
            elif event.key == pygame.K_3:
                selected_piece = 3
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # Handle placing logic here
    
    # Draw UI
    draw_board()
    draw_player_pieces()
    pygame.display.flip()

pygame.quit()
