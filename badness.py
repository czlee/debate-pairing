"""Just here to avoid cluttering other files.
The definition is taken directly from Tabbie2, to allow direct comparisons."""

def get_position_badness(history):
    return POSITION_BADNESS[tuple(sorted(history))]


POSITION_BADNESS = {
    (0, 0, 0, 0): 0,
    (0, 0, 0, 1): 0,
    (0, 0, 0, 2): 4,
    (0, 0, 0, 3): 36,
    (0, 0, 0, 4): 144,
    (0, 0, 0, 5): 324,
    (0, 0, 0, 6): 676,
    (0, 0, 0, 7): 1296,
    (0, 0, 0, 8): 2304,
    (0, 0, 0, 9): 3600,
    (0, 0, 1, 1): 0,
    (0, 0, 1, 2): 4,
    (0, 0, 1, 3): 36,
    (0, 0, 1, 4): 100,
    (0, 0, 1, 5): 256,
    (0, 0, 1, 6): 576,
    (0, 0, 1, 7): 1156,
    (0, 0, 1, 8): 1936,
    (0, 0, 2, 2): 16,
    (0, 0, 2, 3): 36,
    (0, 0, 2, 4): 100,
    (0, 0, 2, 5): 256,
    (0, 0, 2, 6): 576,
    (0, 0, 2, 7): 1024,
    (0, 0, 3, 3): 64,
    (0, 0, 3, 4): 144,
    (0, 0, 3, 5): 324,
    (0, 0, 3, 6): 576,
    (0, 0, 4, 4): 256,
    (0, 0, 4, 5): 400,
    (0, 1, 1, 1): 0,
    (0, 1, 1, 2): 4,
    (0, 1, 1, 3): 16,
    (0, 1, 1, 4): 64,
    (0, 1, 1, 5): 196,
    (0, 1, 1, 6): 484,
    (0, 1, 1, 7): 900,
    (0, 1, 2, 2): 4,
    (0, 1, 2, 3): 16,
    (0, 1, 2, 4): 64,
    (0, 1, 2, 5): 196,
    (0, 1, 2, 6): 400,
    (0, 1, 3, 3): 36,
    (0, 1, 3, 4): 100,
    (0, 1, 3, 5): 196,
    (0, 1, 4, 4): 144,
    (0, 2, 2, 2): 4,
    (0, 2, 2, 3): 16,
    (0, 2, 2, 4): 64,
    (0, 2, 2, 5): 144,
    (0, 2, 3, 3): 36,
    (0, 2, 3, 4): 64,
    (0, 3, 3, 3): 36,
    (1, 1, 1, 1): 0,
    (1, 1, 1, 2): 0,
    (1, 1, 1, 3): 4,
    (1, 1, 1, 4): 36,
    (1, 1, 1, 5): 144,
    (1, 1, 1, 6): 324,
    (1, 1, 2, 2): 0,
    (1, 1, 2, 3): 4,
    (1, 1, 2, 4): 36,
    (1, 1, 2, 5): 100,
    (1, 1, 3, 3): 16,
    (1, 1, 3, 4): 36,
    (1, 2, 2, 2): 0,
    (1, 2, 2, 3): 4,
    (1, 2, 2, 4): 16,
    (1, 2, 3, 3): 4,
    (2, 2, 2, 2): 0,
    (2, 2, 2, 3): 0,
}