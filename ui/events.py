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
                    coordinates = self._get_cell_coordinates(x, y)
                    if coordinates is not None:
                        return {"type": "place_piece", "coordinates": coordinates}
                    else:
                        print("Click outside the grid.")  # Debugging message

        # No actionable event
        return None


    def _get_cell_coordinates(self, mouse_x, mouse_y):
        """
        Convert mouse click position into grid coordinates.
        """
        board_offset_x = 200  # Matches Renderer.board_offset_x
        cell_size = 200       # Assuming each grid cell is 200x200 pixels

        # Adjust for the board's horizontal offset
        col = (mouse_x - board_offset_x) // cell_size
        row = mouse_y // cell_size

        # Ensure the coordinates are within bounds
        if col < 0 or row < 0 or col >= 3 or row >= 3:  # Assuming a 3x3 grid
            return None  # Return None for invalid clicks outside the grid

        return row, col
