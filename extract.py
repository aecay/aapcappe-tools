#!/usr/bin/env python2

import nltk.tree as T
import soundfile
import sys
import textgrid
import math


def get_interval(tree):
    metadata = tree[0]          # TODO: assumes metadata is first
    if metadata.node != "METADATA":
        return

    start = float(metadata[0][0][0])
    end = float(metadata[0][1][0])
    return (start, end)

sound_data, sample_rate = soundfile.read(sys.argv[2])

with open(sys.argv[1]) as infile:
    trees = list(map(T.Tree, infile.read().split("\n\n")))

intervals = list(filter(lambda x: x is not None, map(get_interval, trees)))

for interval in intervals:
    soundfile.write("%s_%s.wav" % (int(interval[0] * 100),
                                   int(interval[1] * 100)),
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
    tg.write("%s_%s.TextGrid" % (int(interval[0] * 100),
                                 int(interval[1] * 100)))
