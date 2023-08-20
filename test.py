import unittest
from game import NoGraphicsGame, MinesweeperBoard
from agent import AgentMcAgentFace
import itertools

class TestOne(unittest.TestCase):

    def test_a_9x9(self):
        try:
            game = NoGraphicsGame(num_rows=9, num_columns=9, num_mines=10, games_to_play=1)
            result = game.start()
            print(f"Played a single 9x9 game (10 mines) with a final score of {result:.2f}.")
        except Exception as e:
            print(f"Game crashed! It triggered the following exception:\n{e}")

class TestTwo(unittest.TestCase):

    def test_five_9x9s(self):
        try:
            game = NoGraphicsGame(num_rows=9, num_columns=9, num_mines=10, games_to_play=5)
            result = game.start()
            print(f"Played five 9x9 games (10 mines) with average score of {result:.2f}.")
        except Exception as e:
            print(f"Game crashed! It triggered the following exception:\n{e}")

class TestThree(unittest.TestCase):

    def test_five_20x30s(self):
        try:
            game = NoGraphicsGame(num_rows=20, num_columns=30, num_mines=50, games_to_play=5)
            result = game.start()
            print(f"Played five 20x30 games (50 mines) with average score of {result:.2f}.")
        except Exception as e:
            print(f"Game crashed! It triggered the following exception:\n{e}")

class TestFour(unittest.TestCase):

    def test_fifty_9x9s(self):
        try:
            game = NoGraphicsGame(num_rows=9, num_columns=9, num_mines=10, games_to_play=50)
            result = game.start()
            print(f"Played fifty 9x9 games (10 mines) with average score of {result:.2f}.")
        except Exception as e:
            print(f"Game crashed! It triggered the following exception:\n{e}")


class TestFive(unittest.TestCase):

    agent = OptimizedAgent(6, 6, 3)

    def test_board(self):
        board = MinesweeperBoard(6, 6, [(1, 1), (4,4), (4,1)])

        print(board)

        revelations = board.report_reveal(0, 0)
        for revelation in revelations:
            self.agent.report(*revelation)
        next_move = self.agent.next_move()

        print(board)

        revelations = board.report_reveal(3, 0)
        for revelation in revelations:
            self.agent.report(*revelation)
        next_move = self.agent.next_move()

        print(board)

        revelations = board.report_reveal(2, 5)
        for revelation in revelations:
            self.agent.report(*revelation)
        next_move = self.agent.next_move()

        print(board)

        revelations = board.report_reveal(5, 5)
        for revelation in revelations:
            self.agent.report(*revelation)
        next_move = self.agent.next_move()

        print(board)
