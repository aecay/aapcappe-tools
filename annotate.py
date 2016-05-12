#!/usr/bin/env python2


import nltk.tree as T
import sys
import re

TIMECODE_RE = "<(\\$\\$)?([A-Za-z]+)_(xmin|xmax)=(?P<time>[0-9]+\\.[0-9]+)>"


def is_timecode_first(tree):
    if tree.node == "CODE":
        if re.match(TIMECODE_RE, tree[0]):
            return True
        else:
            return False
    elif type(tree[0]) == T.Tree:
        return is_timecode_first(tree[0])
    else:
        return False


def is_timecode_last(tree):
    if tree.node == "CODE":
        if re.match(TIMECODE_RE, tree[0]):
            return True
        else:
            return False
    elif type(tree[-1]) == T.Tree:
        # TODO: Skip punctuation backwards?  But at least in the test file it
        # seems not to matter in that the timestamps are after punctuation.
        return is_timecode_last(tree[-1])
    else:
        return False


def get_timecodes(tree):
    r = []
    for leaf in tree.pos():
        if leaf[1] == "CODE":
            m = re.match(TIMECODE_RE, leaf[0])
            if m:
                r.append(float(m.group("time")))
    return r


def get_root(tree):
    for leaf in tree:
        if leaf.node != "ID" and leaf.node != "METADATA":
            return leaf

with open(sys.argv[1]) as infile:
    trees = list(map(T.Tree, infile.read().split("\n\n")))

for i in range(len(trees)):
    if trees[i][0].node == "CODE":
        continue
    timecodes = get_timecodes(trees[i])
    if is_timecode_first(get_root(trees[i])):
        first = timecodes[0]
    else:
        back_timecodes = []
        back_idx = i - 1
        while len(back_timecodes) == 0:
            back_timecodes = get_timecodes(trees[back_idx])
            back_idx = back_idx - 1
        first = back_timecodes[-1]

    if is_timecode_last(get_root(trees[i])):
        last = timecodes[-1]
    else:
        fwd_timecodes = []
        fwd_idx = i + 1
        while len(fwd_timecodes) == 0:
            if fwd_idx >= len(trees):
                last = 9999     # TODO: fixme
                break
            fwd_timecodes = get_timecodes(trees[fwd_idx])
            fwd_idx = fwd_idx + 1
        try:
            last = fwd_timecodes[0]
        except:
            last = 9999         # TODO: fixme

    trees[i].insert(0, T.Tree("(METADATA (TIME (START %s) (END %s)))"
                              % (first, last)))

sys.stdout.write("\n\n".join(map(lambda x: x.pprint(), trees)))


# Local Variables:
# python-shell-interpreter: "ipython2"
# End:
