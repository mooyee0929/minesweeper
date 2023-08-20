import cnf
from cnf import Clause, Literal, Cnf
from util import SearchSpace, dfs
from random import shuffle
from search import SatisfiabilitySearchSpace
from collections import defaultdict

def unit_resolve(unit_clauses, clause):
    """Resolves a clause with a set of unit clauses.

    This function resolves the provided clause simultaneously with all
    of the provided unit clauses as follows:
    - If the clause contains the same literal as one of the unit clauses,
      e.g. the clause is !A || !B || C and one the unit clauses is !B, then
      the clause is redundant (entailed by that unit clause) and therefore
      unnecessary. Hence None should be returned.
    - Otherwise, any clause literals whose negations appear in a unit clause
      should be removed, e.g. if the clause is !A || !B || C || !D and the unit
      clauses contain both A and !C, then the resolved clause should be !B || D.

    Parameters
    ----------
    unit_clauses : set[Clause]
        The set of unit clauses.
    clause : Clause
        The clause to resolve with the unit clauses.

    Returns
    -------
    Clause
        The resolved clause (or None if the original clause is redundant)
    """

    preserved_literals = []
    for literal in clause.get_literals():
        if len(clause) > 1 and Clause([literal]) in unit_clauses:
            return None
        if Clause([literal.negate()]) not in unit_clauses:
            preserved_literals.append(literal)
    return Clause(preserved_literals)


def unit_resolution(unit_clauses, regular_clauses):
    """Resolves a set of clauses with a set of unit clauses.

    This function resolves each regular clause AND unit clause with each unit clause,
    using the unit_resolve function. The process continues 
    until no new clauses can be created through unit resolution.

    Parameters
    ----------
    unit_clauses : set[Clause]
        The set of unit clauses.
    regular_clauses : set[Clause]
        The set of non-unit clauses.

    Returns
    -------
    set[Clause], set[Clause]
        The resolved unit clauses and non-unit clauses, respectively.
    """

    regular_clauses = set(regular_clauses)
    unit_clauses = set(unit_clauses)
    while True:
        new_clauses = set()
        new_unit_clauses = set(unit_clauses)
        for clause in regular_clauses | unit_clauses:
            new_clause = unit_resolve(unit_clauses, clause)
            if new_clause is None:
                pass
            elif len(new_clause) == 1:
                new_unit_clauses.add(new_clause)
            else:
                new_clauses.add(new_clause)
        regular_clauses = new_clauses
        if len(unit_clauses) == len(new_unit_clauses):
            break
        unit_clauses = new_unit_clauses
    return unit_clauses, regular_clauses




class DpllSearchSpace(SatisfiabilitySearchSpace):
    """A search space for the DPLL algorithm."""

    def __init__(self, sent):
        """
        Parameters
        ----------
        sent : Cnf
            a CNF sentence for which we want to find a satisfying model

        """

        super().__init__(sent)
        unit_clauses = set()
        regular_clauses = set()
        for clause in sent.clauses:
            if len(clause) == 1:
                unit_clauses.add(clause)
            else:
                regular_clauses.add(clause)
        self.unit_clauses, self.regular_clauses = unit_resolution(unit_clauses, regular_clauses)

    def get_successors(self, state):
        """Computes the successors of a DPLL search state.

        A search state is a tuple of literals, one for each symbol in the signature.
        As with the SatisfiabilitySearchSpace, the successors of state
        (l_1, ..., l_k) should typically be (l_1, ..., l_k, !s_{k+1}) and
        (l_1, ..., l_k, s_{k+1}), where s_{k+1} is the (k+1)th symbol in the
        signature (according to an alphabetical ordering of the signature symbols).

        However:
        - if self.sent conjoined with literals l_1, ..., l_k entails False (according
          to unit resolution), then there is no successor and this method
          should return an empty list
        - if self.sent conjoined with literals l_1, ..., l_k entails !s_{k+1}
          (according to unit resolution), then the only successor is
          (l_1, ..., l_k, !s_{k+1})
        - if self.sent conjoined with literals l_1, ..., l_k entails s_{k+1},
          (according to unit resolution), then the only successor is
          (l_1, ..., l_k, s_{k+1}).

        Parameters
        ----------
        state : tuple[Literal]
            The literals currently assigned by the search node

        Returns
        -------
        list[tuple[Literal]]
            The successor states.
        """

        if len(state) == len(self.signature):
            return []
        unit_clauses = self.unit_clauses | set([Clause([lit]) for lit in state])
        unit_clauses, regular_clauses = unit_resolution(unit_clauses, self.regular_clauses)
        if cnf.c('FALSE') in regular_clauses:
            return []
        successors = []
        next_var = self.signature[len(state)]
        next_literal = None
        for uc in unit_clauses:
            if next_var == uc.get_literals()[0].get_symbol():
                next_literal = uc.get_literals()[0]
        if next_literal is not None:
            successors.append(state + tuple([next_literal]))
        else:
            for value in [False, True]:
                next_literal = Literal(next_var, polarity=value)
                successors.append(state + tuple([next_literal]))
        return successors


def dpll(sent):
    """An implementation of the DPLL algorithm for satisfiability.

    Parameters
    ----------
    sent : cnf.Sentence
        the CNF sentence for which we want to find a satisfying model.

    Returns
    -------
    dict[str, bool]
        a satisfying model (if one exists), otherwise None is returned
    """

    search_space = DpllSearchSpace(sent)
    state, _ = dfs(search_space)
    model = {lit.get_symbol(): lit.get_polarity() for lit in state} if state is not None else None
    return model

