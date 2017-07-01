#!/usr/bin/python3
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
from math import log2
from statistics import pvariance
from badness import get_vanschelven_position_badness

munkres.DISALLOWED_PRINTVAL = "-"
DISALLOWED = munkres.DISALLOWED
m = munkres.Munkres()


def read_input_file(filename, include_all=False):
    """Reads an input file, returns a list of 3-tuples, (team, points, history).
    """
    f = open(filename)
    data = []
    for line in f:
        team, points, history, active = line.split("\t")
        if not include_all and int(active) == 0:
            continue
        history = [int(x) for x in history.split(",")]
        data.append((team, int(points), history))
    if not include_all:
        assert len(data) % 4 == 0, "There were %d teams" % len(data)
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

def profile_after(pos, profile):
    new_profile = profile.copy()
    new_profile[pos] += 1
    return new_profile

def cost_simple(pos, profile):
    return profile[pos] - min(profile)

def cost_vanschelven(pos, profile):
    return get_vanschelven_position_badness(profile_after(pos, profile))

def cost_entropy(pos, profile):
    profile = profile_after(pos, profile)
    n = sum(profile)
    probs = [p/n for p in profile]
    selfinfo = [0 if p == 0 else -p*log2(p) for p in probs]
    return (2 - sum(selfinfo)) * n

def cost_pvariance(pos, profile):
    return pvariance(profile_after(pos, profile))

def cost_adjusted_pvariance(pos, profile):
    profile = profile_after(pos, profile)
    n = sum(profile)
    best = [n // 4] * (4 - n % 4) + [n // 4 + 1] * (n % 4)
    return pvariance(profile) - pvariance(best)

def generate_cost_matrix(data, cost_fn):
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
        min_hist = min(history)
        for room in rooms:
            if points not in room:
                row.extend([DISALLOWED, DISALLOWED, DISALLOWED, DISALLOWED])
            else:
                row.extend([cost_fn(i, history) for i in range(4)])
        assert len(row) == nteams
        costs.append(row)
    assert len(costs) == nteams
    return costs

def hungarian_shuffled(costs):
    """Applies the Hungarian algorithm to `costs`, but permutes the rows and
    columns of the matrix first. Returns a list of indices pairs (row, col)."""
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

def generate_draw(data, cost_fn):
    costs = generate_cost_matrix(data, cost_fn)
    indices = hungarian_shuffled(costs)
    rooms = collate_rooms(data, indices)
    return rooms

def show_rooms(rooms, color=False):
    if color:
        YELLOW = "\033[0;33m"
        GREEN = "\033[0;32m"
        NORMAL = "\033[0m"
    else:
        YELLOW = GREEN = NORMAL = ""

    for room in rooms:
        bracket = max([t[1] for t in room])
        teams = []
        for pos, (team, points, history) in enumerate(room):
            history = history.copy()
            history[pos] = GREEN + str(history[pos]) + NORMAL
            points_str = str(points).rjust(2)
            if points != bracket:
                points_str = YELLOW + points_str + NORMAL
            teams.append("{team:>12s} {points!s:>2s} {history:7s}".format(
                team=team[:12], points=points_str, history=",".join(map(str, history))))
        print("   ".join(teams))
    print()

def compare_badness(rooms, other_filename, cost_fn, color=False, quiet=False):
    """Compares the position badness implied by `data` and `indices`, to that
    stored in `other_filename`."""
    other_data = read_input_file(other_filename, include_all=True)
    other_histories = {team: history for team, _, history in other_data}
    this_total_cost = 0
    other_total_cost = 0
    this_total_badness = 0
    other_total_badness = 0

    teams = []
    for room in rooms:
        for pos, (team, _, history) in enumerate(room):
            this_history = history.copy()
            this_history[pos] += 1
            this_cost = cost_fn(pos, history)
            this_badness = cost_vanschelven(pos, history)
            this_total_cost += this_cost
            this_total_badness += this_badness

            other_pos = [x != y for x, y in zip(history, other_histories[team])].index(True)
            other_cost = cost_fn(other_pos, history)
            other_badness = cost_vanschelven(other_pos, history)
            other_total_cost += other_cost
            other_total_badness += other_badness

            teams.append((team, history, this_cost, this_badness, this_history, other_cost, other_badness, other_histories[team]))

    if not quiet:
        teams.sort(key=lambda x: (x[3], x[6]), reverse=True)

        if color:
            BLUE = "\033[0;34m"
            GREEN = "\033[32m"
            NORMAL = "\033[0m"
            BOLD_CYAN = "\033[1;36m"
            BOLD_YELLOW = "\033[1;33m"
        else:
            BOLD_CYAN = BLUE = GREEN = BOLD_YELLOW = NORMAL = ""

        def history_string(base, original, changed):
            strings = []
            for a, b in zip(original, changed):
                if a != b:
                    strings.append(GREEN + str(b) + base)
                else:
                    strings.append(str(b))
            return base + ",".join(strings) + NORMAL

        print(BOLD_CYAN + "             team         ours            original" + NORMAL)

        for team, original_history, this_cost, this_badness, this_history, other_cost, other_badness, other_history in teams:
            this_base = BLUE if this_badness == 0 else BOLD_YELLOW if this_badness > other_badness else NORMAL
            other_base = BLUE if other_badness == 0 else BOLD_YELLOW if other_badness > this_badness else NORMAL
            cost_format = "2d" if isinstance(this_cost, int) else "4.2f"
            this_cost_str = ("{c}{cost:>" + cost_format + "}{n}").format(cost=this_cost, c=this_base, n=NORMAL)
            other_cost_str = ("{c}{cost:>" + cost_format + "}{n}").format(cost=other_cost, c=other_base, n=NORMAL)
            this_badness_str = "{c}({bad:>2d}){n}".format(bad=this_badness, c=this_base, n=NORMAL)
            other_badness_str = "{c}({bad:>2d}){n}".format(bad=other_badness, c=other_base, n=NORMAL)
            this_history_str = history_string(this_base, original_history, this_history)
            other_history_str = history_string(other_base, original_history, other_history)

            print("{team:>17s}: {cost1:>2s} {bad1:>2s} {hist1:7s}   {cost2:>2s} {bad2:>2s} {hist2:7s}".format(
                team=team[:17], bad1=this_badness_str, bad2=other_badness_str,
                cost1=this_cost_str, cost2=other_cost_str,
                hist1=this_history_str, hist2=other_history_str,
            ))

    return this_total_cost, other_total_cost, this_total_badness, other_total_badness

def show_original_rooms(data, filename, color=False):
    properties = {team: (points, history) for team, points, history in data}
    f = open(filename)
    rooms = []
    for line in f:
        names = line.split("\t")
        rooms.append([(name.strip(),) + properties[name.strip()] for name in names])
    rooms.sort(key=lambda x: max(y[1] for y in x), reverse=True)
    show_rooms(rooms, color)

def _print_heading(message, color=False):
    if color:
        print("\033[1;36m" + message + "\033[0m")
    else:
        print(message)

COST_FUNCTIONS = {
    "simple": cost_simple,
    "vanschelven": cost_vanschelven,
    "entropy": cost_entropy,
    "pvar": cost_pvariance,
    "adjpvar": cost_adjusted_pvariance,
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tournament")
    parser.add_argument("round", type=int, nargs='?', default=None)
    parser.add_argument("-q", "--quiet", help="Print only the final costs", action="store_true", default=False)
    parser.add_argument("-C", "--compare-file")
    parser.add_argument("-D", "--actual-draw")
    parser.add_argument("-m", "--no-color", dest="color", action="store_false", default=True)
    parser.add_argument("-c", "--cost-method", choices=COST_FUNCTIONS.keys(), default="vanschelven")
    parser.add_argument("-e", "--exponent", type=float, default=None,
        help=("If specified, the cost function is raised to this exponent."))
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

    if args.exponent:
        exp = float(args.exponent)
        def cost_fn(pos, profile):
            return COST_FUNCTIONS[args.cost_method](pos, profile) ** exp
    else:
        cost_fn = COST_FUNCTIONS[args.cost_method]

    data = read_input_file(filename)
    rooms = generate_draw(data, cost_fn)

    if not args.quiet:
        _print_heading("Our draw:", args.color)
        show_rooms(rooms, args.color)
        if actualdrawfile:
            _print_heading("\033[1;36mOriginal draw:\033[0m", args.color)
            show_original_rooms(data, actualdrawfile, args.color)

    if comparefile:
        this_cost, other_cost, this_badness, other_badness = compare_badness(rooms, comparefile, cost_fn, args.color, args.quiet)

    if args.color:
        CYAN = "\033[1;36m"
        BOLD_WHITE = "\033[1;37m"
        NORMAL = "\033[0m"
    else:
        CYAN = BOLD_WHITE = NORMAL = ""

    print()
    print(CYAN + "        our total cost:" + BOLD_WHITE, this_cost, NORMAL)
    print(CYAN + "   original total cost:" + BOLD_WHITE, other_cost, NORMAL)
    print(CYAN + "     our total badness:" + BOLD_WHITE, this_badness, NORMAL)
    print(CYAN + "original total badness:" + BOLD_WHITE, other_badness, NORMAL)
