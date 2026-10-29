# Minesweeper Reasoning Agent

A Minesweeper-playing agent based on propositional logic. The board state is encoded as a
set of CNF clauses, and the agent decides which cells are provably safe (or provably
mines) by running a satisfiability solver over those clauses. When logic alone cannot
determine a safe move, the agent falls back to a random reveal. The game itself can be
played interactively, watched while the agent plays it, or run headless for evaluation.

## How it works

The reasoning loop lives in `agent.py`. For each uncovered number it builds CNF clauses
describing how many of the surrounding cells are mines, then uses unit resolution and the
DPLL algorithm in `dpll.py` to test whether a candidate cell can be safely revealed. The
`cnf.py` module provides the `Literal`, `Clause` and `Cnf` types and convenience
constructors; `search.py` offers a simple search-based satisfiability solver as an
alternative backend; `util.py` supplies the generic search-space and depth-first-search
helpers that both solvers build on.

## Repository structure

| File | Role |
|------|------|
| `agent.py` | The reasoning agent and its move types |
| `dpll.py` | DPLL satisfiability algorithm and unit resolution |
| `search.py` | Simple search-based satisfiability solver |
| `cnf.py` | CNF literals, clauses and sentence construction |
| `util.py` | Generic search space and DFS helpers |
| `game.py` | Minesweeper game engine and interactive/evaluation drivers |
| `plane.py` | Pygame graphics for the interactive game |
| `test.py` | Test cases |
| `images/` | Button sprites used by the UI |

The game engine (`game.py`, `plane.py`), the CNF scaffolding in `cnf.py` and `util.py`,
and the test cases came from a provided starter framework. The reasoning logic in
`agent.py`, `dpll.py` and `search.py` is the original work in this repository.

## Requirements

- Python 3.
- [pygame](https://www.pygame.org/) for the interactive and agent-driven graphical modes.

## Running

Watch the agent play a standard 9x9 board with 10 mines:

```bash
python game.py --ai
```

Choose your own board size and mine count with `-r` (rows), `-c` (columns) and `-m`
(mines):

```bash
python game.py --ai -r 16 -c 16 -m 40
```

Run headless in evaluation mode (no graphics, plays several games and prints the average
score):

```bash
python game.py -e
```

Omit all flags to play the game yourself in the graphical window:

```bash
python game.py
```
