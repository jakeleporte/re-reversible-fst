# Reversible FST Simulator based on Rotary Elements
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

## Usage

This repository contains a library (`re_rfst.py`) and some example
driver code (`driver.py`).  The library contains several classes, the
most important of which are documented below.

### Class `RE`

This class models a Rotary Element, which is a simple state machine
that can be in one of two states, horizontal (`REState.H`), and
vertical (`REState.V`).  States and directional inputs and outputs are
indicated with Enum types.  Directions are the same for inputs and
outputs of the RE model (`REDir.n`, `REDir.s`, etc.)

RE objects can be instantiated with an optional initial state
argument, which by default is vertical (`REDir.V`).  The only class
method other than `__init__` is `re_input`, which takes in a direction
enum type, changes the internal state of the RE as in the referenced
book *Theory of Reversible Computing*, and outputs a direction enum
type.

### Class `FST`

This class implements a Mealy-Machine FST model.  Inputs for
initialization are:

- `Q`, a `set` of states (strings)
- `Sigma`, a `set` of input characters
- `delta`, a `dict` mapping `tuple`s of `(state, input_char)` to
  `(new_state, output_char)`
- `q_0`, the initial state of the machine
- `F`, the `set` of accepting states
- `Gamma`, the `set` of output characters

The methods are as follows:

- `step_forward(self, input_char: str)`: Takes in an input character from
  `Sigma`, and steps the machine forward, returning the appropriate
  output character according to `delta`
- `run_forward(self, input_string: str)`: Takes in an entire input
  tape, runs the machine forward using `step_forward` for each input
  character, and returns a pair of `(accepted, output_string)`, where
  `accepted` is a `bool` indicating whether or not the machine
  accepted the string
- `reverse(self)`: Identifies imprecice transitions in the FST, and
  returns a `tuple` of `(is_reversible, imprecise, rho)`, where
  `is_reversible` is a `bool` indicating reversibility, `imprecise` is
  a dictionary containing imprecise states (this will be empty is the
  machine `is_reversible`, and `rho` is the reverse transition
  function for the FST.

### Class `RFA`:

This class implements the RE-based reversible FST model.  Its
initializer takes in an object of type `FST`, checks for reversiblity
using `FST.reverse`, and constructs an RE-column-based model.  Its
most important methods are:

- `get_state(self)`: Returns the machine's current state, from `Q`
- `step(self, char, reverse=False, trace=False, pause=0,
  file=stdout)`: Steps the machine forward (or in reverse, if
  `reverse` is `True`, tracing execution (if `trace` is `True`) every
  `pause` seconds by printing text to the file `file`.  This is not
  very portable, since it relies on the `clear` command being present,
  and on VT100 terminal codes; only tested on Linux with `vterm`.
  Returns the output character.
- `run(self, input_string, reverse=False, trace=False, pause=0,
  file=stdout)`: Runs the machine forward (or in reverse) using
  `step`, for a whole input string, and returns a tuple of `(accepted,
  output_string)`.  In reverse operation, `accepted` means the machine
  ends in the initial state.
- `print_res(self, file=stdout, inptu_msg, output_msg)`: Prints the
  current state of each RE in text form to file `file`.

## Example Driver Code

Two test cases are provided; the examples should show how to specify
FST configurations using a dictionary.  Forward and reverse execution
is tested for both examples, and the forward execution for both is
traced.

## References

- Frost-Murphy, [Reversibility for Nanoscale
Systems](https://onesearch.library.nd.edu/permalink/f/1phik6l/ndu_aleph002640081)

- Morita, [Theory of Reversible Computing](https://doi.org/10.1007/978-4-431-56606-9)
