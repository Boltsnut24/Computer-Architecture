#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *
print("anything")

cpu = CPU()

cpu.load("ls8\examples\sctest.ls8")
cpu.run()