#!/usr/bin/python3
"""Processes data that is copied and pasted from the round pages in Tabbie2, to
remove confidential information. The resulting files will be a list of debates,
one debate per line, with team names separated by tabs on each line.

Chuan-Zheng Lee <czlee@stanford.edu>
June 2017
"""

import argparse
from os.path import isfile, join


def process_raw_file(filename):
    rawfile = open(join(directory, "round{:d}_raw.txt".format(seq)))
    outfile = open(join(directory, "round{:d}_actual.tsv".format(seq)), 'w')

    for line in rawfile:
        if not line or line.isspace():
            continue

        parts = line.split("\t")
        if len(parts) < 2:
            continue

        teams = parts[1:5]
        outfile.write("\t".join(team.strip() for team in teams) + "\n")

    outfile.close()
    rawfile.close()


parser = argparse.ArgumentParser()
parser.add_argument("directory")
args = parser.parse_args()
directory = args.directory

seq = 1
while isfile(join(directory, "round{:d}_raw.txt".format(seq))):
    process_raw_file(seq)
    seq += 1
