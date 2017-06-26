"""Simplified version of a Hungarian algorithm-based WUDC draw generator.
Requires the munkres package (available on PyPI).

Chuan-Zheng Lee <czlee@stanford.edu>
June 2017
"""

import argparse
import munkres
import random
from collections import Counter
from itertools import chain, repeat
from badness import get_position_badness

munkres.DISALLOWED_PRINTVAL = "-"
DISALLOWED = munkres.DISALLOWED
m = munkres.Munkres()


def read_input_file(filename):
    """Reads an input file, returns a list of 3-tuples, (team, points, history).
    """
    f = open(filename)
    data = []
    for line in f:
        team, points, history, active = line.split("\t")
        if int(active) == 0:
            continue
        history = [int(x) for x in history.split(",")]
        data.append((team, int(points), history))
    assert len(data) % 4 == 0
    return data

def define_rooms(points):
    """Returns a list of tuples, each one being the team points
    values that are allowed to be in that room. Example:
    [(17, 16, 15), (15, 14), (15, 14), ...]
    """
    assert len(points) % 4 == 0
    counts = Counter(points)
    rooms = []
    bracket = []
    nteams = 0
    pullups_needed = 0
    for p in range(max(points), -1, -1):
        if pullups_needed < counts[p]: # complete the bracket
            if pullups_needed:
                bracket.append(p)
                counts[p] -= pullups_needed
                nteams += pullups_needed
            assert nteams % 4 == 0
            rooms += [tuple(bracket)] * (nteams // 4)
            nteams = 0
            bracket = []

        # add this entire bracket to the bracket
        if counts[p] > 0:
            bracket.append(p)
        nteams += counts[p]
        pullups_needed = (-nteams) % 4

    assert nteams % 4 == 0
    rooms += [tuple(bracket)] * (nteams // 4)

    return rooms

def generate_cost_matrix(data):
    """Returns a cost matrix for the tournament.
    Rows (inner lists) are teams, in the same order as in data.
    Columns (elements) are positions in rooms, ordered first by room in the
    order returned by `rooms`, then in speaking order (OG, OO, CG, CO).
    Rules:
     - if the team (given its points) is not allowed in the room, use DISALLOWED.
     - otherwise, for each position, use the position badness that would arise
       if the team were allocated to that position.
    """
    nteams = len(data)
    assert nteams % 4 == 0

    rooms = define_rooms([p for _, p, _ in data])
    assert len(rooms) == nteams / 4

    costs = []
    for _, points, history in data:
        row = []
        for room in rooms:
            if points not in room:
                row.extend([DISALLOWED, DISALLOWED, DISALLOWED, DISALLOWED])
            else:
                for pos in range(4):
                    new_history = history.copy()
                    new_history[pos] += 1
                    cost = get_position_badness(new_history)
                    row.append(cost)
        assert len(row) == nteams
        costs.append(row)
    assert len(costs) == nteams
    return costs

def hungarian_shuffled(costs):
    """Applies the Hungarian algorithm to `costs`, but permutes the rows and
    columns of the matrix first. Returns a list of column numbers."""
    n = len(costs)
    I = random.sample(range(n), n)
    J = random.sample(range(n), n)
    C = [[costs[i][j] for j in J] for i in I]
    indices = m.compute(C)
    return [(I[i], J[j]) for i, j in indices]

def collate_rooms(data, indices):
    rooms = [[None, None, None, None] for i in range(len(indices) // 4)]
    for t, r in indices:
        rooms[r // 4][r % 4] = data[t]
    return rooms

def generate_draw(data):
    costs = generate_cost_matrix(data)
    indices = hungarian_shuffled(costs)
    rooms = collate_rooms(data, indices)
    return rooms

def show_rooms(rooms):
    for room in rooms:
        teams = ["{team:>12s} {points:>2d} {history:7s}".format(
            team=team[:12], points=points, history=",".join(map(str, history)))
            for team, points, history in room]
        print("   ".join(teams))
    print()

def compare_badness(rooms, other_filename):
    """Compares the position badness implied by `data` and `indices`, to that
    stored in `other_filename`."""
    other_histories = {team: history for team, _, history in read_input_file(other_filename)}
    this_total = 0
    other_total = 0
    print("           team      ours      original")
    for room in rooms:
        for i, (team, _, history) in enumerate(room):
            history = history.copy()
            history[i] += 1
            this_badness = get_position_badness(history)
            this_total += this_badness
            other_badness = get_position_badness(other_histories[team])
            other_total += other_badness
            print("{team:>15s}: {bad1:>2d} {hist1:7s}  {bad2:>2d} {hist2:7s}".format(
                team=team[:15], bad1=this_badness, bad2=other_badness,
                hist1=",".join(map(str, history)),
                hist2=",".join(map(str, other_histories[team]))
            ))

    print("ours total:", this_total, ", comparison total:", other_total)

def show_original_rooms(data, filename):
    properties = {team: (points, history) for team, points, history in data}
    f = open(filename)
    for line in f:
        names = line.split("\t")
        room_properties = [properties[name.strip()] for name in names]
        teams = ["{team:>12s} {points:>2d} {history:7s}".format(
            team=team.strip()[:12], points=points, history=",".join(map(str, history)))
            for team, (points, history) in zip(names, room_properties)]
        print("   ".join(teams))
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tournament")
    parser.add_argument("round", type=int, nargs='?',    default=None)
    parser.add_argument("-c", "--compare-file")
    parser.add_argument("-d", "--actual-draw")
    args = parser.parse_args()

    import os.path
    if os.path.isfile(args.tournament):
        filename = args.tournament
        comparefile = args.compare_file
        actualdrawfile = args.actual_draw
    elif args.round is not None:
        filename = os.path.join("data", args.tournament, "round{:d}_after.tsv".format(args.round - 1))
        comparefile = os.path.join("data", args.tournament, "round{:d}_after.tsv".format(args.round))
        actualdrawfile = os.path.join("data", args.tournament, "round{:d}_actual.tsv".format(args.round))
    else:
        print("Either the first argument must be a file name, or the second argument must be a round number.")
        exit()

    data = read_input_file(filename)
    rooms = generate_draw(data)
    print("Our draw:")
    show_rooms(rooms)
    if actualdrawfile:
        print("Original draw:")
        show_original_rooms(data, actualdrawfile)
    if comparefile:
        compare_badness(rooms, comparefile)
