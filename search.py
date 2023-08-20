import cnf
from cnf import Clause, Literal, Cnf
from util import SearchSpace, dfs
from random import shuffle

class SatisfiabilitySearchSpace(SearchSpace):
    """A search space for a simple search-based satisfiability solver."""

    def __init__(self, sent):
        """
        Parameters
        ----------
        sent : Cnf
            a CNF sentence for which we want to find a satisfying model

        """
        self.sent = sent
        self.signature = sorted(sent.get_symbols())
        self.start_state = tuple()

    def get_start_state(self):
        """Returns the start state.

        Returns
        -------
        tuple[str]
            The start state
        """
        return self.start_state

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

        if len(state) < len(self.signature):
            return False
        model = {lit.get_symbol(): lit.get_polarity() for lit in state}
        return self.sent.check_model(model)

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

        if len(state) == len(self.signature):
            return []
        else:
            next_var = self.signature[len(state)]
            return [state + tuple([Literal(next_var, polarity=True)]),
                    state + tuple([Literal(next_var, polarity=False)])]


def search_solver(sent):
    """An implementation of a simple search-based satisfiability solver.

    Parameters
    ----------
    sent : cnf.Sentence
        the CNF sentence for which we want to find a satisfying model.

    Returns
    -------
    dict[str, bool]
        a satisfying model (if one exists), otherwise None is returned
    """

    search_space = SatisfiabilitySearchSpace(sent)
    state, num_visited = dfs(search_space)
    model = {lit.get_symbol(): lit.get_polarity() for lit in state} if state is not None else None
    return model, num_visited
