import pygame

class Events:
    def __init__(self):
        """Initialize the event handler."""
        self.selected_piece = None  # Track the currently selected piece
        self.piece_key_mapping = {pygame.K_1: "S", pygame.K_2: "M", pygame.K_3: "L"}  # Key bindings for piece sizes

    def get_event(self):
        """
        Capture user input and return the event as a dictionary.
        Event types include:
          - 'select_piece': When a piece is selected.
          - 'place_piece': When a move is attempted on the board.
        """
        for event in pygame.event.get():
            # Quit Event
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Key Press Event for Piece Selection
            if event.type == pygame.KEYDOWN:
                if event.key in self.piece_key_mapping:
                    self.selected_piece = self.piece_key_mapping[event.key]
                    return {"type": "select_piece", "piece": self.selected_piece}

            # Mouse Click Event for Piece Placement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    x, y = pygame.mouse.get_pos()
                    return {"type": "place_piece", "coordinates": self._get_cell_coordinates(x, y)}

        # No actionable event
        return None

    def _get_cell_coordinates(self, mouse_x, mouse_y):
        """
        Convert mouse click position into grid coordinates.
        """
        cell_size = 200  # Assuming a 3x3 grid with each cell 200x200 pixels
        row = mouse_y // cell_size
        col = mouse_x // cell_size
        return row, col
