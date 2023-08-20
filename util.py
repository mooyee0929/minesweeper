from queue import LifoQueue, Queue
from abc import ABC, abstractmethod

class SearchSpace(ABC):

    @abstractmethod
    def get_start_state(self):
        """Returns the start state.

        Returns
        -------
        tuple[str]
            The start state
        """

    @abstractmethod
    def is_goal_state(self, state):
        """Checks whether a given state is a goal state.

        Parameters
        ----------
        state : tuple[str]
            A state of the search space

        Returns
        -------
        bool
            True iff the state is a goal state
        """

    @abstractmethod
    def get_successors(self, state):
        """Determines the possible successors of a state.

        Parameters
        ----------
        state : tuple[str]
            A state of the search space

        Returns
        -------
        list[tuple[str]]
            The list of valid successor states
        """


def uninformed_search(space, container, verbose=False):
    """General-purpose algorithm for "uninformed" search, e.g. DFS or BFS.

    Parameters
    ----------
    space : SnakePuzzleSearchSpace
        The search space
    container : queue.Queue or queue.LifoQueue
        The container for processing nodes of the search tree.
    """

    container.put(space.get_start_state())
    count = 0
    while not container.empty():
        count += 1
        next_state = container.get()
        if space.is_goal_state(next_state):
            if verbose:
                print(f"Search nodes visited: {count}")
            return next_state, count
        successors = space.get_successors(next_state)
        for successor in successors:
            container.put(successor)
    if verbose:
        print(f"Search nodes visited: {count}")
    return None, count


def bfs(space):
    """Runs breadth-first search (BFS) on a search space.

    Parameters
    ----------
    space : SearchSpace
        The search space
    """
    return uninformed_search(space, Queue())


def dfs(space):
    """Runs depth-first search (DFS) on a search space.

    Parameters
    ----------
    space : SearchSpace
        The search space
    """
    return uninformed_search(space, LifoQueue())

