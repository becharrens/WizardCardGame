from WizardAI.Game import Game
from WizardAI.HumanPlayer import HumanPlayer
from WizardAI.MonteCarloPlayer import MonteCarloPlayer
from WizardAI.RandomAIPlayer import RandomAIPlayer


def main():
    num_players = 4
    game: Game = Game(
        [
            RandomAIPlayer("P1", num_players),
            # HumanPlayer("P1", num_players),
            MonteCarloPlayer("CPU2", num_players, 1, 100),
            MonteCarloPlayer("CPU3", num_players, 1, 100),
            MonteCarloPlayer("CPU4", num_players, 1, 100),
        ]
    )
    game.play_game()


if __name__ == "__main__":
    main()
