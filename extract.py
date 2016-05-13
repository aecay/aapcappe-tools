#!/usr/bin/env python2

import nltk.tree as T
import soundfile
import sys
import textgrid
import math
import os


if not os.path.isdir("audio"):
    os.mkdir("audio")


def get_interval(tree):
    metadata = tree[0]          # TODO: assumes metadata is first
    if metadata.node != "METADATA":
        return

    for subtree in metadata:
        if subtree.node == "TIME":
            for sst in subtree:
                if sst.node == "START":
                    start = float(sst[0])
                elif sst.node == "END":
                    end = float(sst[0])
                elif sst.node == "FILE":
                    filename = sst[0]
    return (start, end, filename)

sound_data, sample_rate = soundfile.read(sys.argv[2])

with open(sys.argv[1]) as infile:
    trees = list(map(T.Tree, infile.read().split("\n\n")))

intervals = list(filter(lambda x: x is not None, map(get_interval, trees)))

for interval in intervals:
    centisecs_begin = int(interval[0] * 100)
    centisecs_end = int(interval[1] * 100)
    soundfile.write("audio/%s_%s_%s.wav" %
                    (interval[2], centisecs_begin, centisecs_end),
                    sound_data[int(math.floor(sample_rate * interval[0])):
                               int(math.ceil(sample_rate * interval[1]))],
                    sample_rate)
    # TODO: not very efficient; ideally we'd figure out how to read the TG
    # once and make a copy
    tg = textgrid.TextGrid()
    tg.read(sys.argv[3])
    for i in range(len(tg)):
        tier = tg[i]
        for j in range(len(tier) - 1, -1, -1):
            # Go backwards because we're modifying the list as we go
            praat_interval = tier[j]
            if praat_interval < interval[0]:
                tier.removeInterval(praat_interval)
            elif praat_interval > interval[1]:
                tier.removeInterval(praat_interval)
            else:
                praat_interval -= interval[0]
    tg.minTime = 0
    tg.maxTime = interval[1] - interval[0]
    # TODO: remove empty tiers
    tg.write("audio/%s_%s_%s.TextGrid" %
             (interval[2], centisecs_begin, centisecs_end))
