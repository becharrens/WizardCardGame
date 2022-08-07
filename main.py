from WizardAI.Game import Game
from WizardAI.MonteCarloPlayer import MonteCarloPlayer
from WizardAI.RandomAIPlayer import RandomAIPlayer


def main():
    num_players = 4
    game: Game = Game(
        [
            RandomAIPlayer("P1", num_players),
            MonteCarloPlayer("CPU2", num_players, 1, 1000),
            MonteCarloPlayer("CPU3", num_players, 1, 1000),
            MonteCarloPlayer("CPU4", num_players, 1, 1000),
        ]
    )
    game.play_game()


if __name__ == "__main__":
    main()
