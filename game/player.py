class Player:
    def __init__(self, name, color):
        """Initialize a player with a name, color, and pieces."""
        self.name = name
        self.color = color
        self.pieces = {'S': 2, 'M': 2, 'L': 2}  # Two of each piece size

    def use_piece(self, size):
        """Decrement the count of a piece if available."""
        if self.pieces.get(size, 0) > 0:
            self.pieces[size] -= 1
            return True
        return False

    def reset_pieces(self):
        """Reset the pieces to their initial counts."""
        self.pieces = {'S': 2, 'M': 2, 'L': 2}
