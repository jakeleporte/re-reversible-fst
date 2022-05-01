#!/usr/bin/env python3

from enum import Enum, auto
from sys import stdout
from time import sleep
import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class REState(Enum):
    H = auto()
    V = auto()

class REDir(Enum):
    n = auto()
    s = auto()
    e = auto()
    w = auto()

class RE:
    delta_fwd = {
        (REState.V, REDir.n): (REState.V, REDir.s),
        (REState.V, REDir.s): (REState.V, REDir.n),
        (REState.V, REDir.e): (REState.H, REDir.n),
        (REState.V, REDir.w): (REState.H, REDir.s),
        (REState.H, REDir.n): (REState.V, REDir.w),
        (REState.H, REDir.s): (REState.V, REDir.e),
        (REState.H, REDir.e): (REState.H, REDir.w),
        (REState.H, REDir.w): (REState.H, REDir.e)
    }
    delta_rev = {v: k for k, v in delta_fwd.items()}

    def __init__(self, init_state=REState.V):
        self.state = init_state
        return

    def re_input(self, direction, reverse=False):
        if reverse:
            next_state, output_dir = RE.delta_rev[(self.state, direction)]
        else:
            next_state, output_dir = RE.delta_fwd[(self.state, direction)]
        self.state = next_state
        return output_dir

class FST:
    """A Mealy-Machine FST model"""
    def __init__(self, Q: set, Sigma: set, delta: dict,
                 q_0: str, F: set, Gamma: set):
        # Do some basic checking for correctness
        if q_0 not in Q:
            raise ValueError(f'Invalid initial state: {q_0}')
        for state in F:
            if state not in Q:
                raise ValueError(f'Invalid final state: {state}')
        for src, dst in delta.items():
            src_state, input_char = src
            dst_state, output_char = dst
            if src_state not in Q:
                raise ValueError(f'Transition function invalid: {src_state} is not in Q')
            if dst_state not in Q:
                raise ValueError(f'Transition function invalid: {dst_state} is not in Q')
            if input_char not in Sigma:
                raise ValueError(f'Transition function invalid: {input_char} is not in Sigma')
            if output_char not in Gamma:
                raise ValueError(f'Transition function invalid: {output_char} is not in Gamma')

        self.Q = Q
        self.Sigma = Sigma
        self.delta = delta
        self.q_0 = q_0
        self.F = F
        self.Gamma = Gamma

        self.state = q_0
        return

    def step_forward(self, input_char: str):
        if input_char not in self.Sigma:
            raise ValueError(f'Input \'{input_char}\' is not in input alphabet')

        next_state, output_char = self.delta[(self.state, input_char)]
        self.state = next_state
        return output_char

    def run_forward(self, input_string: str):
        output_string = ''
        for char in input_string:
            output_char = self.step_forward(char)
            if output_char: output_string += output_char
        accepted = (self.state in self.F)
        return accepted, output_string

    def reverse(self):
        transitions = {}
        for src, dst in self.delta.items():
            src_list = transitions.get(dst, [])
            src_list.append(src)
            transitions[dst] = src_list
        imprecise = {}
        rho = {}
        for src, dst in transitions.items():
            if len(dst) > 1:
                imprecise[src] = dst
            else:
                rho[src] = dst[0]
        return len(imprecise) == 0, imprecise, rho

class RFA:
    """An RE-based reversible FST model"""
    def __init__(self, fst):
        # First, check for reversibility
        is_reversible, imprecise, _ = fst.reverse()
        if not is_reversible:
            error_msg = "Input must be reversible FST; input FST has imprecise transitions\n\n"
            for src, dst in imprecise.items():
                error_msg += f'Transition to state \'{src[0]}\' with input ' + \
                f'\'{src[1]}\' has {len(dst)} sources:\n'
                for e in dst:
                    error_msg += f'{e}\n'
                error_msg += '\n'
            error_msg += 'Correct the transition function and re-try.'
            raise ValueError(error_msg)

        if len(fst.Sigma) != len(fst.Gamma):
            raise ValueError('Input and output alphabets must be the same length for this algorithm')

        n = len(fst.Sigma)
        m = len(fst.Q)
        self.n = n
        self.m = m
        self.inputs = sorted(list(fst.Sigma))
        self.outputs = sorted(list(fst.Gamma))
        self.states = sorted(list(fst.Q))
        self.q_0 = fst.q_0
        self.F = fst.F
        self.delta = fst.delta
        self.REs = [[None for row in range(self.n + 1)] for col in range(self.m)]
        for col in range(m):
            for row in range(n + 1):
                self.REs[col][row] = RE()
        # Put the machine in the initial state
        q_0_i = self.states.index(self.q_0)
        self.REs[q_0_i][n].state = REState.H

        self.fwd = {}
        self.rev = {}
        for qi in range(m):
            # Initialize the "state-keeping" REs, by convention
            # numbered `n`.
            self.fwd[(qi, n, REDir.n)] = (qi, n-1, REDir.s)
            self.fwd[(qi, n, REDir.s)] = (qi, n, REDir.s)
            self.fwd[(qi, n, REDir.w)] = (qi, 0, REDir.n)

            # Next, initialize the 0th element, which is also a
            # special case
            self.fwd[(qi, 0, REDir.n)] = (qi, n, REDir.e)
            self.fwd[(qi, 0, REDir.s)] = (qi, 1, REDir.n)

            # Next, initialize the remaining REs in the column, which
            # can be done in a loop
            for e in range(1, n):
                self.fwd[(qi, e, REDir.n)] = (qi, e-1, REDir.s)
                self.fwd[(qi, e, REDir.s)] = (qi, e+1, REDir.n)

        # Add the connections "between columns"
        for qi in range(0, m-1):
            for e in range(n):
                self.fwd[(qi, e, REDir.e)] = (qi+1, e, REDir.w)

        # Now, make the connections corresponding to the input FST's
        # state transition function, `delta`
        for input_pair, output_pair in fst.delta.items():
            q_curr, input_char = input_pair
            qi_curr = self.states.index(q_curr)
            ichar_i = self.inputs.index(input_char)
            q_next, output_char = output_pair
            qi_next = self.states.index(q_next)
            ochar_i = self.outputs.index(output_char)
            self.fwd[(qi_curr, ichar_i, REDir.w)] = (qi_next, ochar_i, REDir.e)

        # Add the outputs
        for e in range(n):
            self.fwd[(m-1, e, REDir.e)] = self.outputs[e]

        # Finally, create a backwards connection map so the RFA can be
        # run in reverse
        for src, dest in self.fwd.items():
            self.rev[dest] = src
        # Add the inputs
        for e in range(n):
            self.rev[(0, e, REDir.w)] = self.inputs[e]

        return

    def get_state(self):
        for qi, q in enumerate(self.states):
            if self.REs[qi][self.n].state == REState.H:
                return q

    def step_forward(self, input_char: str, trace=False, pause=0, file=stdout):
        ichar_i = self.inputs.index(input_char)
        # All inputs go into the first column, on the west side of an
        # RE at the input character's index
        message = (0, ichar_i, REDir.w)
        while message not in self.outputs:
            col, row, dir_in = message
            dir_out = self.REs[col][row].re_input(dir_in)
            trace_out_msg = (col, row, dir_out)
            message = self.fwd[(col, row, dir_out)]
            if trace:
                print(message, file=file)
                self.print_res(file=file, output_msg=trace_out_msg, input_msg=message)
                sleep(pause)
        return message

    def step_backward(self, output_char: str, trace=False, pause=0, file=stdout):
        ochar_i = self.outputs.index(output_char)
        # All outputs get fed back into the last column, on the east
        # side of an RE at the output character's index
        message = (self.m-1, ochar_i, REDir.e)
        while message not in self.inputs:
            col, row, dir_in = message
            dir_out = self.REs[col][row].re_input(dir_in, reverse=True)
            if trace:
                print(message, file=file)
                self.print_res(file=file)
                sleep(pause)
            message = self.rev[(col, row, dir_out)]
        return message

    def step(self, char: str, reverse=False, trace=False, pause=0, file=stdout):
        if reverse:
            return self.step_backward(char, trace=trace, pause=pause, file=file)
        else:
            return self.step_forward(char, trace=trace, pause=pause, file=file)

    def run(self, input_string: str, reverse=False, trace=False, pause=0, file=stdout):
        if trace:
            self.print_res()
            sleep(pause)
        output_string = ''
        for char in input_string:
            if reverse:
                output_char = self.step_backward(char, trace=trace, pause=pause, file=file)
            else:
                output_char = self.step_forward(char, trace=trace, pause=pause, file=file)
            output_string += output_char
        if reverse:
            accepted = self.get_state() == self.q_0
            return accepted, output_string[::-1]
        else:
            accepted = self.get_state() in self.F
            return accepted, output_string

    def print_res(self, file=stdout, input_msg=None, output_msg=None):
        basic_box = ["       ",
                     " +---+ ",
                     " |   | ",
                     " +---+ ",
                     "       "]
        red_box = [bcolors.WARNING + line + bcolors.ENDC for line in basic_box]
        box_rows = len(basic_box)
        box_cols = len(basic_box[0])
        box_mid_row = 2
        boxes = [[basic_box.copy() for row in range(self.n + 1)] for col in range(self.m)]
        # Add the state indicators
        for col in range(self.m):
            for row in range(self.n + 1):
                state = self.REs[col][row].state
                if state == REState.V:
                    state_char = "|"
                else:
                    state_char = "-"
                boxes[col][row][box_mid_row] = boxes[col][row][box_mid_row][0:3] + \
                    state_char + boxes[col][row][box_mid_row][4:7]
                if input_msg and type(input_msg) == tuple:
                    in_col, in_row, in_dir = input_msg
                    if col == in_col and row == in_row:
                        if in_dir == REDir.n:
                            boxes[col][row][0] = boxes[col][row][0][0:2] + "↓" \
                                + boxes[col][row][0][3:7]
                        elif in_dir == REDir.e:
                            boxes[col][row][box_mid_row-1] = \
                                boxes[col][row][box_mid_row-1][0:6] + "←"
                        elif in_dir == REDir.s:
                            boxes[col][row][4] = boxes[col][row][4][0:4] + "↑" \
                                + boxes[col][row][4][5:7]
                        elif in_dir == REDir.w:
                            boxes[col][row][box_mid_row+1] = "→" \
                                + boxes[col][row][box_mid_row+1][1:7]
                if output_msg and type(output_msg) == tuple:
                    out_col, out_row, out_dir = output_msg
                    if col == out_col and row == out_row:
                        if out_dir == REDir.n:
                            boxes[col][row][0] = boxes[col][row][0][0:4] + "↑" \
                                + boxes[col][row][0][5:7]
                        elif out_dir == REDir.e:
                            boxes[col][row][box_mid_row+1] = \
                                boxes[col][row][box_mid_row+1][0:6] + "→"
                        elif out_dir == REDir.s:
                            boxes[col][row][4] = boxes[col][row][4][0:2] + "↓" \
                                + boxes[col][row][4][3:7]
                        elif out_dir == REDir.w:
                            boxes[col][row][box_mid_row-1] = "←" \
                                + boxes[col][row][box_mid_row-1][1:7]
                        boxes[col][row] = [bcolors.WARNING + line + bcolors.ENDC
                                           for line in boxes[col][row]]

        # Print the boxes
        os.system('clear')
        for row in range(self.n + 1):
            for box_row in range(box_rows):
                for col in range(self.m):
                    print(boxes[col][row][box_row], file=file, end="")
                print(file=file)
