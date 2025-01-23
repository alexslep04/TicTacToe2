from game.game_logic import TicTacToe2

def main():
    print("Welcome to Tic Tac Toe 2.0!")
    
    # Create a new game instance
    game = TicTacToe2()

    # Start the game loop
    game.turn()

    # Ask if players want to play again
    while True:
        play_again = input("Would you like to play again? (yes/no): ").strip().lower()
        if play_again == "yes":
            game.reset_board()
            game.turn()
        elif play_again == "no":
            print("Thanks for playing! Goodbye!")
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

if __name__ == "__main__":
    main()