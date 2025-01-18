class Config:
    # Screen dimensions
    SCREEN_WIDTH = 1600
    SCREEN_HEIGHT = 1600

    # Colors
    BACKGROUND_COLOR = (30, 30, 30)  # Dark gray
    LINE_COLOR = (200, 200, 200)     # Light gray
    PLAYER_COLORS = {
        "player1": (50, 150, 250),  # Blue
        "player2": (250, 50, 50),   # Red
    }

    # Board properties
    GRID_SIZE = 3
    CELL_SIZE = SCREEN_WIDTH // GRID_SIZE

    # Frames per second
    FPS = 30
