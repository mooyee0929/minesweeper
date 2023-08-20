
## Minesweeper

A reasoning agent, based on propositional logic, that plays Minesweeper.

- `agent.py`: The reasoning agent. 
- `dpll.py`: Includes an implementation of the DPLL algorithm for satisfiability and methods for unit resolution. 
- `cnf.py`: Classes and functions to build CNF clauses. 
- `search.py`: An implementation of a simple search-based satisfiability solver.
- `test.py`: Test cases.
- `util.py`: Miscellaneous classes and functions.
- `game.py`: Implementation of the Minesweeper game.
- `plane.py`: Graphics support for the game.

From Artifical Intelligence course at Williams College taught by Mark Hopkins Fall 2022. Code for a functioning Minesweeper game was provided, from which I implemented the reasoning agent in `agent.py`, `dpll.py` and `search.py`.

To run the game with the Agent, type `python game.py --ai`. 

To set your own number of rows, columns and mines, type `python game.py –-ai -r R -c C -m M`.

