"""Processes data to produce a ranked list of teams, with position histories,
for each round. Within each brackets, teams are sorted alphabetically, to make
failure to randomise easy to detect.

Chuan-Zheng Lee <czlee@stanford.edu>
June 2017
"""

import argparse
from os.path import isfile, join


def update_position_history(seq):
    rawfile = open(join(directory, "round{:d}_actual.tsv".format(seq)))

    for line in rawfile:
        teams = line.split("\t")
        for pos, team in enumerate(teams):
            positions = history.setdefault(team.strip(), [0, 0, 0, 0])
            positions[pos] += 1


def read_teams(seq):
    rawfile = open(join(directory, "round{:d}_actual.tsv".format(seq)))
    all_teams = []
    for line in rawfile:
        teams = line.split("\t")
        all_teams.extend([team.strip() for team in teams])
    return all_teams


def read_team_tab():
    tab = {}
    tabfile = open(join(directory, "team_tab.tsv"))
    team_col = tabfile.readline().split("\t").index("Team")

    for line in tabfile:
        if not line or line.isspace():
            continue

        parts = line.split("\t")
        team = parts[team_col].strip()
        points = []
        cumul = 0
        for r in range(1, 10):
            try:
                x = parts[r+team_col+2]
            except IndexError:
                x = ''
            x = x.strip()
            if x and x != '-':
                cumul += int(x)
            points.append(cumul)
        tab[team] = points
    return tab


def write_round(seq):
    try:
        teams_in_next_round = read_teams(seq+1)
    except FileNotFoundError:
        teams_in_next_round = []
    points = {team: totals[seq-1] for team, totals in team_tab.items()}
    teams = sorted(points.keys(), key=lambda t: (-points.get(t, 0), t))
    outfile = open(join(directory, "round{:d}_after.tsv".format(seq)), "w")
    for team in teams:
        outfile.write("{team}\t{points}\t{history}\t{active}\n".format(
            team=team, points=points.get(team, 0),
            history=",".join(map(str, history.get(team, [0,0,0,0]))),
            active=int(team in teams_in_next_round),
        ))
    outfile.close()


parser = argparse.ArgumentParser()
parser.add_argument("directory")
args = parser.parse_args()
directory = args.directory

team_tab = read_team_tab()
history = {}

seq = 1
while isfile(join(directory, "round{:d}_actual.tsv".format(seq))):
    update_position_history(seq)
    write_round(seq)
    seq += 1
