#!/usr/bin/env python3


class Engines:
    """
    Engines base class containing core information that all other engines
    (PSI4, Gaussian etc) will have.
    """

    def __init__(self, molecule):

        self.molecule = molecule

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__dict__!r})'
