from abc import ABC, abstractmethod
import argparse
from random import sample, choice
from plane import CartesianPlane, CellGraphic, PlayButton
import pygame as pg
from agent import Reveal, RandomReveal
from agent import initialize_agent
import time

def generate_board(num_rows, num_columns, num_mines):
    num_squares = num_rows * num_columns
    mines = [(x // num_columns, x % num_columns)
             for x in sample(range(num_squares), num_mines)]
    return MinesweeperBoard(num_rows, num_columns, mines)


class Cell:
    def __init__(self, row, column, label, board, revealed=False):
        self.label = label
        self.revealed = revealed
        self.row, self.column = row, column
        self.board = board

    def reveal(self):
        self.board.report_reveal(self.row, self.column)

    def known_info(self):
        return self.label if self.revealed else None

    def __str__(self):
        return self.label if self.revealed else "#"


class MinesweeperBoard:

    def __init__(self, num_rows, num_columns, mines):
        self.num_rows, self.num_columns = num_rows, num_columns
        mine_map = [[0 for _ in range(num_columns)] for _ in range(num_rows)]
        for (row, col) in mines:
            for nrow, ncol in self.get_neighbors(row, col):
                mine_map[nrow][ncol] += 1
        for (row, col) in mines:
            mine_map[row][col] = "*"
        self.cell_map = [[Cell(row, col, str(mine_map[row][col]), self)
                          for col in range(num_columns)]
                         for row in range(num_rows)]
        self.mines = set(mines)
        self.unrevealed = set()
        for row in range(num_rows):
            for col in range(num_columns):
                self.unrevealed.add((row, col))
        self.game_status = 0

    def get_game_status(self):
        return self.game_status

    def get_neighbors(self, row, col):
        neighbors = [(row - 1, col - 1), (row - 1, col), (row - 1, col + 1),
                     (row, col - 1), (row, col + 1),
                     (row + 1, col - 1), (row + 1, col), (row + 1, col + 1)]
        result = []
        for nrow, ncol in neighbors:
            if 0 <= nrow < self.num_rows and 0 <= ncol < self.num_columns:
                result.append((nrow, ncol))
        return result

    def get_unrevealed_neighbors(self, row, col):
        neighbors = self.get_neighbors(row, col)
        return [(r, c) for (r, c) in neighbors if not self.at(r, c).revealed]

    def get_revealed_neighbors(self, row, col):
        neighbors = self.get_neighbors(row, col)
        return [(r, c) for (r, c) in neighbors if self.at(r, c).revealed]

    def at(self, row, col):
        return self.cell_map[row][col]

    def random_reveal(self):
        candidates = list(self.unrevealed - self.mines)
        if len(candidates) > 0:
            row, col = choice(candidates)
            return self.report_reveal(row, col)
        else:
            return []

    def report_reveal(self, row, col):
        stack = [(row, col)]
        revelations = []
        while len(stack) > 0:
            (r, c), stack = stack[0], stack[1:]
            if not self.at(r, c).revealed:
                if self.at(r, c).label in "0123456789":
                    revelations.append((r, c, int(self.at(r, c).label)))
                self.unrevealed.remove((r, c))
                self.at(r, c).revealed = True
                if self.at(r, c).label == "0":
                    for (nrow, ncol) in self.get_neighbors(r, c):
                        stack.append((nrow, ncol))
        if self.at(row, col).label == "*":
            self.game_status = -1
        elif self.unrevealed == self.mines:
            self.game_status = 1
        return revelations

    def reveal_all(self):
        for row in self.cell_map:
            for cell in row:
                cell.reveal()

    def __str__(self):
        return '\n'.join([''.join([str(s) for s in row]) for row in self.cell_map])

    __repr__ = __str__


class MinesweeperGame(ABC):

    def __init__(self, num_rows, num_columns, num_mines):
        pg.init()
        if not pg.font:
            print("Warning, fonts disabled")
        if not pg.mixer:
            print("Warning, sound disabled")
        pg.display.set_caption("Minesweeper")
        pg.mouse.set_visible(True)
        self.num_rows, self.num_columns, self.num_mines = num_rows, num_columns, num_mines
        self.cell_width = 35
        self.loss_penalty = 100
        self.random_reveal_penalty = 2
        self.plane = CartesianPlane(x_max=num_columns, y_max=num_rows,
                                    screen_width=num_columns*self.cell_width,
                                    screen_height=num_rows*self.cell_width + 30)
        self.button = PlayButton(num_columns-0.5, 0.4)
        self.plane.add_sprite(self.button)
        self.board = self.initialize_new_game()

    def initialize_new_game(self):
        board = generate_board(self.num_rows, self.num_columns, self.num_mines)
        cells = [[CellGraphic(col*self.cell_width, row*self.cell_width,
                              board.at(row, col), self.cell_width)
                       for col in range(self.num_columns)] for row in range(self.num_rows)]
        for row in cells:
            for col, cell in enumerate(row):
                self.plane.add_widget(cell)
        return board

    @abstractmethod
    def start(self):
        ...


class InteractiveGame(MinesweeperGame):
    def __init__(self, num_rows, num_columns, num_mines):
        super().__init__(num_rows, num_columns, num_mines)

    def start(self):
        clock = pg.time.Clock()
        going = True
        quit_now = False
        start_time = time.time()
        penalty = 0
        while going:
            clock.tick(60)
            for event in pg.event.get():
                self.plane.notify(event)
                if event.type == pg.QUIT:
                    going = False
                    quit_now = True
            if self.plane.button_pushed:
                self.plane.button_pushed = False
                self.board.random_reveal()
                penalty += self.random_reveal_penalty
            if self.board.get_game_status() != 0:
                going = False
                self.plane.report_game_over(self.board.get_game_status() == 1)
            if self.board.get_game_status() == -1:
                penalty += self.loss_penalty
            self.plane.report_time(time.time() - start_time + penalty)
            self.plane.refresh()
        while not quit_now:
            clock.tick(60)
            for event in pg.event.get():
                self.plane.notify(event)
                if event.type == pg.QUIT:
                    quit_now = True
        pg.quit()


class AgentBasedGame(MinesweeperGame):
    def __init__(self, num_rows, num_columns, num_mines):
        super().__init__(num_rows, num_columns, num_mines)
        self.clock = pg.time.Clock()
        self.games_to_play = 50

    def play_one(self):
        self.board = self.initialize_new_game()
        agent = initialize_agent(self.num_rows, self.num_columns, self.num_mines)
        start_time = time.time()
        going, quit_now = True, False
        penalty = 0
        while going:
            next_move = agent.next_move()
            if next_move == RandomReveal():
                revelations = self.board.random_reveal()
                penalty += self.random_reveal_penalty
            else:
                revelations = self.board.report_reveal(next_move.row, next_move.column)
            for (row, col, info) in revelations:
                agent.report(row, col, info)
            if self.board.get_game_status() != 0:
                going = False
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    going = False
                    quit_now = True
            self.plane.report_time(time.time() - start_time + penalty)
            self.plane.refresh()
        elapsed = time.time() - start_time
        if self.board.get_game_status() == -1:
            penalty += self.loss_penalty
        return elapsed + penalty, quit_now

    def start(self):
        going = True
        games_played = 0
        elapsed_sum = 0
        while going:
            elapsed, quit_now = self.play_one()
            elapsed_sum += elapsed
            games_played += 1
            self.plane.report_average(elapsed_sum / games_played)
            self.plane.report_completion_percentage(games_played / self.games_to_play)
            if quit_now or games_played >= self.games_to_play:
                going = False
        pg.quit()


class NoGraphicsGame:
    def __init__(self, num_rows, num_columns, num_mines, games_to_play):
        self.num_rows, self.num_columns, self.num_mines = num_rows, num_columns, num_mines
        self.loss_penalty = 100
        self.random_reveal_penalty = 2
        self.games_to_play = games_to_play

    def play_one(self):
        board = generate_board(self.num_rows, self.num_columns, self.num_mines)
        agent = initialize_agent(self.num_rows, self.num_columns, self.num_mines)
        start_time = time.time()
        penalty = 0
        going = True
        while going:
            next_move = agent.next_move()
            if next_move == RandomReveal():
                revelations = board.random_reveal()
                penalty += self.random_reveal_penalty
            else:
                revelations = board.report_reveal(next_move.row, next_move.column)
            for (row, col, info) in revelations:
                agent.report(row, col, info)
            if board.get_game_status() != 0:
                going = False
        elapsed = time.time() - start_time
        if board.get_game_status() == -1:
            penalty += self.loss_penalty
        return elapsed + penalty

    def start(self):
        going = True
        games_played = 0
        elapsed_sum = 0
        while going:
            elapsed = self.play_one()
            elapsed_sum += elapsed
            games_played += 1
            if games_played >= self.games_to_play:
                going = False
        return elapsed_sum / games_played


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='The game of Minesweeper.')
    parser.add_argument('-r', '--num_rows', required=False, type=int, default=9,
                        help='number of rows in the grid')
    parser.add_argument('-c', '--num_columns', required=False, type=int, default=9,
                        help='number of columns in the grid')
    parser.add_argument('-m', '--num_mines', required=False, type=int, default=10,
                        help='number of mines in the grid')
    parser.add_argument('--ai', dest='use_ai', action='store_true', default=False,
                        help='only output sentences (rather than trees)')
    parser.add_argument('-e', dest='eval', action='store_true', default=False,
                        help='run in evaluation mode (no graphics)')
    args = parser.parse_args()
    if args.use_ai:
        game = AgentBasedGame(args.num_rows, args.num_columns, args.num_mines)
        game.start()
    elif args.eval:
        game = NoGraphicsGame(args.num_rows, args.num_columns, args.num_mines, 5)
        result = game.start()
        print(f"Average score: {result:.2f}")
    else:
        game = InteractiveGame(args.num_rows, args.num_columns, args.num_mines)
        game.start()
