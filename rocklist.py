#!/usr/bin/env python
#
# Prepend each line in a file with a fixed string.
#

import fileinput
import sys

for playlist in sys.argv[1:]:
    for line in fileinput.input([playlist], inplace=True):
        sys.stdout.write('../music/{l}'.format(l=line))
