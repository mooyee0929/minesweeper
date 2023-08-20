from abc import ABC, abstractmethod
from dpll import dpll, unit_resolution
import cnf
import random
import re
import itertools


class MinesweeperMove(ABC):
    """Abstract base class for moves that a MinesweeperAgent can make during a game."""


class RandomReveal(MinesweeperMove):
    """Requests the Minesweeper game to press the parachute button, i.e. reveal a non-mine cell at random.

    """

    def __init__(self):
        pass

    def __eq__(self, other):
        return type(other) == RandomReveal


class Reveal(MinesweeperMove):
    """Requests the Minesweeper game to reveal the cell in the specified row and column.

    Rows and columns are specified counting from zero. The upper left cell of the Minesweeper board
    is in row 0 and column 0.

    """

    def __init__(self, row, column):
        self.row, self.column = row, column

    def __eq__(self, other):
        return (type(other).__name__ == Reveal
                and self.row == other.row
                and self.column == other.column)


class MinesweeperAgent(ABC):

    def __init__(self, num_rows, num_columns, num_mines):
        """Constructs a MinesweeperAgent designed to play a game with the specified grid.

        Parameters
        ----------
        num_rows : int
            The number of rows in the Minesweeper grid
        num_columns : int
            The number of columns in the Minesweeper grid
        num_mines : int
            The number of mines in the Minesweeper grid

        """
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.num_mines = num_mines

    @abstractmethod
    def report(self, row, column, num_mine_neighbors):
        """Informs the agent about the number of cell neighbors containing a mine.

        The cell is specified by its (row, column) coordinates, counting from 0.
        For instance, (0, 0) is the upper left cell of the Minesweeper board.

        A neighbor is any cell that is adjacent (including diagonally adjacent).
        Therefore, a cell can have up to 8 neighbors.

        Parameters
        ----------
        row : int
            The cell's row (counting from 0)
        column : int
            The cell's column (counting from 0)
        num_mine_neighbors : int
            The number of neighbors of the cell containing a mine

        """

    @abstractmethod
    def next_move(self):
        """Returns the next cell to reveal on a given Minesweeper board.

        Returns
        ----------
        (int, int)
            The (row, column) coordinates of the next cell that the agent wants to reveal.

        """


# class NotSoGoodAgent(MinesweeperAgent):
#     """A MinesweeperAgent who plays rather poorly.

#     90% of the time, this agent just pushes the parachute button. The other 10% of the time,
#     the agent reveals the unrevealed cell that is closest to the upper left (i.e. proceeding
#     left-to-right through each row, until an unrevealed cell is found).

#     """
#     def __init__(self, num_rows, num_columns, num_mines):
#         super().__init__(num_rows, num_columns, num_mines)
#         self.unrevealed = set()
#         for row in range(num_rows):
#             for col in range(num_columns):
#                 self.unrevealed.add((row, col))

#     def report(self, row, column, num_mine_neighbors):
#         """Removes the reported cell from the agent's list of unrevealed cells."""
#         self.unrevealed.remove((row, column))

#     def next_move(self):
#         """Executes the agent's not so good strategy."""
#         if random.random() < 0.1 and len(self.unrevealed) > 0:
#             row, col = sorted(self.unrevealed)[0]
#             return Reveal(row, col)
#         else:
#             return RandomReveal()


class OptimizedAgent(MinesweeperAgent):
    """ A MinesweeperAgent.  """
    def __init__(self, num_rows, num_columns, num_mines):
        super().__init__(num_rows, num_columns, num_mines)

        self.unrevealed = set()
        for row in range(num_rows):
            for col in range(num_columns):
                self.unrevealed.add((row, col))
        
        self.frontier = set()
        self.clauses = set()
        self.most_recent_report = []
        self.move_num = 0


    def get_unrevealed_neighbors(self, row, col):
        """ For a given cell, returns the coordinates for the unrevealed neighbors.

            Parameters
            ----------
            row : int
                The cell's row (counting from 0)
            column : int
                The cell's column (counting from 0)

            Returns
            ---------
            result : list[(int, int)]
                List of coordinates for unrevealed cells. 
        """

        neighbors = [(row - 1, col - 1), (row - 1, col), (row - 1, col + 1),
                     (row, col - 1), (row, col + 1),
                     (row + 1, col - 1), (row + 1, col), (row + 1, col + 1)]
        result = []
        for nrow, ncol in neighbors:
            if 0 <= nrow < self.num_rows and 0 <= ncol < self.num_columns and (nrow, ncol) in self.unrevealed:
                result.append((nrow, ncol))
        return result
    

    def at_most_clauses(self, row, col, k, unrevealed_neighbors):
        """ Creates propositional logic in CNF form saying that at most k cells of the 
        unrevealed neighbors is a mine. 

        Parameters
        ----------
        row : int
            The cell's row (counting from 0)
        column : int
            The cell's column (counting from 0)
        k: int
            The number of neighbors of the cell containing a mine.
        unrevealed_neighbors: list[(int, int)]
            For the given cell, the list of neighbors that are still unrevealed.

        Returns
        ---------
        result : [str]
            The propositional logic clause.

        """
        # every group of (k+1) must have !B
        combos = itertools.combinations(unrevealed_neighbors, k+1)

        res = []
        for combo in combos:
            combo = [f"!B_{r}_{c}" for r,c in combo]
            s = " || ".join(combo)
            res.append(s)
        
        return res


    def at_least_clauses(self, row, col, k, unrevealed_neighbors):
        """ Creates propositional logic in CNF form saying that at least k cells out of the unrevealed neighbors are mines.

        Parameters
        ----------
        row : int
            The cell's row (counting from 0)
        column : int
            The cell's column (counting from 0)
        k: int
            The number of neighbors of the cell containing a mine.
        unrevealed_neighbors: list[(int, int)]
            For the given cell, the list of neighbors that are still unrevealed.

        Returns
        ---------
        result : [str]
            The propositional logic clause.
        """

        # every group of (num unrevealed) - k + 1 contains at least one mine
        combos = itertools.combinations(unrevealed_neighbors, len(unrevealed_neighbors) - k + 1)
        res = []
        for combo in combos:
            combo = [f"B_{r}_{c}" for r,c in combo]
            s = " || ".join(combo)
            res.append(s)
        return res


    def report(self, row, column, num_mine_neighbors):
        """ 
        This method adds logic for the revealed cell passed in saying it is not a mine, 
        removes it from the unrevealed list and adds it to the list of recently revealed mines.

        Parameters
        ----------
        row : int
            The cell's row (counting from 0)
        column : int
            The cell's column (counting from 0)
        num_mine_neighbors: int
            The number of neighbors of the cell containing a mine.
        """

        self.clauses.add(f"!B_{row}_{column}")
    
        if (row, column) in self.unrevealed:
            self.unrevealed.remove((row, column))
    
        self.most_recent_report.append((row, column, num_mine_neighbors))


    def next_move(self):
        '''
            Determines the next move. It creates CNF clauses encoding the new information revealed for all of the cells that were just revealed, completes unit resolution with these clauses, and then uses DPLL to determine if a cell is confirmed to not have a mine. If so, it reveals that cell. If there are no cells that are guaranteed to not be mines, it randomly reveals a cell.
        '''
        self.move_num += 1

        #Creates propositional logic for each cell
        for report in self.most_recent_report:
            self.process_report(*report)
        
        if len(self.frontier) == 0:
            return RandomReveal()
        
        # reset most recent reports 
        self.most_recent_report = []

        # Use clause list to create unit clause and regular clause list, 
        # then resolve the clauses to create new list of clauses.
        if self.move_num % 5 == 0:
            sent = cnf.sentence(*self.clauses)
            unit_clauses = set()
            regular_clauses = set()
            for clause in sent.clauses:
                if len(clause) == 1:
                    unit_clauses.add(clause)
                else:
                    regular_clauses.add(clause)
            res_unit_clauses, res_regular_clauses = unit_resolution(unit_clauses, regular_clauses)
            clauses = res_unit_clauses.union(res_regular_clauses)
            self.clauses = {str(c) for c in clauses}
        
        #create frontier priority with cells found to be mines
        frontier_priority = []
        for (r,c) in self.frontier:
            if f"B_{r}_{c}" in self.clauses:
                mine_unrevealed_neighbors = self.get_unrevealed_neighbors(r,c)
                frontier_priority.extend(set(mine_unrevealed_neighbors).intersection(self.frontier))
        
        #check priority frontier first to save time and then the rest of the frontier, 
        #if a cell is confirmed to not be a mine via dpll, it is revealed as the guess
        for (r,c) in frontier_priority:
            if f"B_{r}_{c}" not in self.clauses and dpll(cnf.sentence(*self.clauses.union({f"B_{r}_{c}"}))) is None:
                return Reveal(r, c)

        for (r,c) in self.frontier - set(frontier_priority):
            if f"B_{r}_{c}" not in self.clauses and dpll(cnf.sentence(*self.clauses.union({f"B_{r}_{c}"}))) is None:
                return Reveal(r, c)

        #if no cells are guaranteed to not be mines, a cell is randomly reveal as the guess 
        return RandomReveal()
    

    def process_report(self, row, column, num_mine_neighbors):
        """ Updates frontier, adds clauses encoding logic about this cell's neighbors

        Parameters
        ----------
        row : int
            The cell's row (counting from 0)
        column : int
            The cell's column (counting from 0)
        num_mine_neighbors: int
            The number of neighbors of the cell containing a mine.

        """


        # Update frontier, adding unrevealed neighbors of the cell
        if (row, column) in self.frontier:
            self.frontier.remove((row, column))
        if num_mine_neighbors == 0:
            return
        unrevealed_neighbors = self.get_unrevealed_neighbors(row, column)
        self.frontier = self.frontier.union(set(unrevealed_neighbors))
    

        if len(unrevealed_neighbors) == 0:
            return
    
        if num_mine_neighbors == len(unrevealed_neighbors):
            # all neighbors are mines
            for (r,c) in unrevealed_neighbors:
                self.clauses.add(f"B_{r}_{c}")
            return
        
        #create logic saying that of the unrevealed neighbors, exactly num_mine_neighbors 
        #are mines
        self.clauses = self.clauses\
                .union(set(self.at_most_clauses(row, column, num_mine_neighbors, unrevealed_neighbors)))\
                .union(set(self.at_least_clauses(row, column, num_mine_neighbors, unrevealed_neighbors)))
        

def initialize_agent(num_rows, num_columns, num_mines):
    """Initializes the agent who will play Minesweeper.

    """
    return OptimizedAgent(num_rows, num_columns, num_mines)


"""
Creating the Minesweeper as a logical statement:

- The board state starts off as an empty set of sentences. We know nothing.

- Assume we have a logical variable for every cell representing whether or not it contains a mine.
  E.g. B_1_1 // B_1_2 // ... B_9_9 denoting mines at those cells

- We reveal a cell, for example the top left corner of this mini grid:
              1   2   3
            +---+---+---+
          1 |   | 1 | # |
            +---+---+---+
          2 | 1 | # | # |
            +---+---+---+
          3 | # | # | # |
            +---+---+---+

Here, # denotes an unrevealed cell.
- For all the revealed cells with coordinates x,y we learn !B_x_y
 
- When we consider a cell that was just revealed that has a number, we add some new clauses to our set of sentences representing our board state.
E.g. for the board above, when we learn that the upper middle cell is a 1, we learn that exactly one of B_1_2's unrevealed neighbors is a mine.
 We can write:
       (B_1_3 & !B_2_2 & !B_2_3) OR (!B_1_3 & B_2_2 & !B_2_3) OR (!B_1_3 & !B_2_2 & B_2_3)
   In CNF:
       No more than one:
           (!B_1_3 OR !B_2_2) & (!B_1_3 OR !B_2_3) & (!B_2_2 OR !B_2_3)
       At least one:
           (B_1_3 OR B_2_2 OR B_2_3)

"""
