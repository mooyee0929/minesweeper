from collections import defaultdict

def l(s):
    """Convenience function for constructing literals.
        
    e.g., l('!b') should create a negative literal for symbol b.
    
    The symbol should only consist of alphanumeric characters [A-Za-z0-9] 
    and underscores, however it can be of arbitrary length. The symbol may
    optionally be prefixed with !, which indicates a negative literal.
    
    """
    return Literal(s[1:], False) if s[0] == '!' else Literal(s, True)


def c(s):
    """Convenience function for constructing CNF clauses.
        
    e.g., c('!a || b || e') should create a Clause instance that is the
    disjunction of negative literal a, positive literal b and, and 
    positive literal e.   

    There is a special string "FALSE" that creates a Clause, representing
    a disjunction of zero literals.
    
    """
    if s == 'FALSE':
        literal_strings = []
    else:
        literal_strings = [x.strip() for x in s.split('||')]
    return Clause([l(x) for x in literal_strings])

def sentence(*clauses):
    """Convenience function for constructing CNF sentences.

    e.g., sentence('!a || b', '!b || d') should create a Sentence
    instance with two clauses: (!a || b) AND (!b || d').

    """
    return Cnf([c(clause.strip()) for clause in clauses])


class Literal:
    """A class representing a literal in propositional logic."""

    def __init__(self, symbol, polarity=True):
        """
        Parameters
        ----------
        symbol : str
            the literal's symbol
        polarity : bool
            the literal's polarity (i.e., whether it's true or false)
        """

        self.symbol = symbol
        self.polarity = polarity

    def get_symbol(self):
        """Returns the literal's symbol."""
        return self.symbol

    def get_polarity(self):
        """Returns the literal's polarity."""
        return self.polarity

    def negate(self):
        """Returns a negated version of the literal.

        For instance, if this is cnf.l("A"), this would return cnf.l("!A").
        If this is cnf.l("!A"), this would return cnf.l("A").

        Returns
        -------
        Literal
            a new Literal, which is the negation of the current Literal
        """

        return Literal(self.symbol, not self.polarity)

    def __eq__(self, other):
        """Value-based equality. Checks whether two literals have the same symbol and polarity."""
        return self.symbol == other.symbol and self.polarity == other.polarity
    
    def __lt__(self, other):
        if self.symbol < other.symbol:
            return True
        elif other.symbol < self.symbol:
            return False
        else:
            return self.polarity < other.polarity

    def __hash__(self):
        return hash(self.symbol) + hash(self.polarity)
    
    def __str__(self):
        result = ''
        if not self.polarity:
            result = '!'
        return result + self.symbol

    def __repr__(self):
        return f'Literal({str(self)})'


class Clause:
    """A class representing a CNF clause in propositional logic."""

    def __init__(self, literals):
        """
        Parameters
        ----------
        literals : list[Literal]
            the literals of the clause
        """

        self.literals = literals
        self.literal_values = None

    def get_literals(self):
        """Returms the literals of the clause, as a list."""
        return self.literals

    def get_symbols(self):
        """Returms the set of all symbols found in the clause."""
        return set([l.symbol for l in self.literals])

    def __len__(self):
        """Returns the number of literals in the clause."""
        return len(self.literals)

    def __bool__(self):
        """Returns True iff the clause contains at least one literal."""
        return len(self.literals) > 0

    def __eq__(self, other):
        """Value-based equality. Checks whether the clauses have the same literals."""
        return set(self.literals) == set(other.literals)

    def __lt__(self, other):
        return str(self) < str(other)

    def __hash__(self):
        return hash(tuple(sorted(self.literals)))

    def __str__(self):
        if len(self.literals) == 0:
            return 'FALSE'
        else:
            ordered = sorted(self.literals)
            return ' || '.join([str(l) for l in ordered])

    def __repr__(self):
        return f'Clause({str(self)})'

    def _get_literal_polarities(self):
        if self.literal_values is None:
            self.literal_values = dict()
            for lit in self.literals:
                self.literal_values[lit.symbol] = lit.polarity
        return self.literal_values

    def __contains__(self, sym):
        return sym in self._get_literal_polarities()

    def __getitem__(self, sym):
        return self._get_literal_polarities()[sym]
    
    def __or__(self, other):
        polarities, other_polarities = self._get_literal_polarities(), other._get_literal_polarities()
        common_symbols = polarities.keys() & other_polarities.keys()
        for sym in common_symbols:
            if polarities[sym] != other_polarities[sym]:
                return None
        return Clause(list(set(self.literals + other.literals)))


class Cnf:
    """A class representing a CNF sentence in propositional logic."""

    def __init__(self, clauses):
        """
        Parameters
        ----------
        clauses : list[Clause]
            the clauses of the sentence
        """

        self.clauses = set(clauses)

    def get_symbols(self):
        """Returns a set of all symbols in the sentence.

        Returns
        -------
        set[str]
            a set of all the symbols found in the sentence
        """

        syms = set([])
        for clause in self.clauses:
            syms = syms | clause.get_symbols()
        return syms

    def get_clauses(self):
        """Returns a set of all clauses in the sentence.

        Returns
        -------
        set[Clause]
            the set of all the clauses of the sentence
        """

        return self.clauses
    
    def __str__(self):
        clause_strs = sorted([str(c) for c in self.clauses])     
        return '\n'.join(clause_strs)

    def __repr__(self):
        clause_strs = sorted([str(c) for c in self.clauses])
        return f'Cnf({", ".join(clause_strs)})'

    def __eq__(self, other):
        """Value-based equality. Returns True iff the sentences have the same clauses."""
        return self.clauses == other.clauses

    def check_model(self, model):
        """Checks whether the model satisfies this sentence.

        Parameters
        ----------
        model : dict[str, bool]
            Maps each signature variable to either True (1) or False (0).

        Returns
        -------
        bool
            whether the model satisfies the sentence
        """

        def check_against_clause(clause):
            for symbol in clause.get_symbols():
                if ((not model[symbol] and not clause[symbol]) or
                    (model[symbol] and clause[symbol])):
                    return True                
            return False
        for clause in self.clauses:
            if not check_against_clause(clause):
                return False
        return True
    
