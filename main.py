from WizardGame.Game import Game
from WizardGame.ProbailisticAIPlayer import ProbabilisticAIPlayer
from WizardGame.RandomAIPlayer import RandomAIPlayer


def main():
    num_players = 4
    game: Game = Game(
        [
            RandomAIPlayer("P1", num_players),
            ProbabilisticAIPlayer("CPU2", num_players),
            ProbabilisticAIPlayer("CPU3", num_players),
            ProbabilisticAIPlayer("CPU4", num_players)
        ]
    )
    game.play_game()


if __name__ == '__main__':
    main()
