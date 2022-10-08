from types import FunctionType


def randomStrategy():
    pass


def secondLastStrategy():
    pass


def firstStrategy():
    pass


def entireMatchStrategy():
    pass


def sampleTurns(strategy: FunctionType = randomStrategy):
    strategy()


# Write code for different strategies: random sampling for training,
# always taking n-1, taking the first, taking the second,
# taking the center etc...
