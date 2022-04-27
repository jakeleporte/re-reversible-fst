# Reversible FTS Simulator based on Rotary Elements
## Spring 2022 CSE 60932 Exotic Computing Project

## Description

This repository contains a simple Mealy machine FST simulator, as well
as a reversible FST simulator which builds an FST out of [Rotary
Elements
(REs)](https://link.springer.com/chapter/10.1007/978-4-431-56606-9_2).
The reversible FST simulator takes a general Mealy machine model as
input, determines if it has imprecise transitions, and builds a
reversible model of the machine based on REs.  The resulting model can
step forward or backward, "run" forward or backward consuming an
entire input string, and can output a "trace" of the run, showing
which state each RE is in at each step, and showing inputs and outputs
from the relevant REs.

## References

- Frost-Murphy, [Reversibility for Nanoscale
Systems](https://onesearch.library.nd.edu/permalink/f/1phik6l/ndu_aleph002640081)

- Morita, [Theory of Reversible Computing](https://doi.org/10.1007/978-4-431-56606-9)
