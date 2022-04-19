#!/usr/bin/env python3

from enum import Enum, auto
from collections import defaultdict
from sys import stdout

class REState(Enum):
    H = auto()
    V = auto()

class REDir(Enum):
    n = auto()
    s = auto()
    e = auto()
    w = auto()

class RE:
    def __init__(self, init_state=REState.V):
        self.state = init_state
        return

    def re_input(self, direction, reverse=False):
        if not reverse and self.state == REState.V:
            if direction == REDir.n:
                return REDir.s
            elif direction == REDir.s:
                return REDir.n
            elif direction == REDir.e:
                self.state = REState.H
                return REDir.n
            elif direction == REDir.w:
                self.state = REState.H
                return REDir.s
        elif not reverse and self.state == REState.H:
            if direction == REDir.e:
                return REDir.w
            elif direction == REDir.w:
                return REDir.e
            elif direction == REDir.n:
                self.state = REState.V
                return REDir.w
            elif direction == REDir.s:
                self.state = REState.V
                return REDir.e
        elif self.state == REState.V:
            if direction == REDir.n:
                return REDir.s
            elif direction == REDir.s:
                return REDir.n
            elif direction == REDir.e:
                self.state = REState.H
                return REDir.s
            elif direction == REDir.w:
                self.state = REState.H
                return REDir.n
        elif self.state == REState.H:
            if direction == REDir.e:
                return REDir.w
            elif direction == REDir.w:
                return REDir.e
            elif direction == REDir.n:
                self.state = REState.V
                return REDir.e
            elif direction == REDir.s:
                self.state = REState.V
                return REDir.w


class FST:
    """A Mealy-Machine FST model"""
    def __init__(self, Q: set, Sigma: set, delta: dict,
                 q_0: str, F: set, Gamma: set):
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
            raise ValueError('Given input is not in input alphabet')

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

class RFA:
    """An RE-based reversible FST model"""
    def __init__(self, FST):
        n = len(FST.Sigma)
        m = len(FST.Q)
        self.n = n
        self.m = m
        self.inputs = sorted(list(FST.Sigma))
        self.outputs = sorted(list(FST.Gamma))
        self.states = sorted(list(FST.Q))
        self.q_0 = FST.q_0
        self.F = FST.F
        self.delta = FST.delta
        self.REs = [[None for row in range(self.n + 1)] for col in range(self.m)]
        for col in range(m):
            for row in range(n + 1):
                self.REs[col][row] = RE()
        # Put the machine in the initial state
        q_0_i = self.states.index(self.q_0)
        self.REs[q_0_i][n].state = REState.H

        self.fwd = {}
        self.bwd = {}
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
        for input_pair, output_pair in FST.delta.items():
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
            self.bwd[dest] = src
        # Add the inputs
        for e in range(n):
            self.bwd[(0, e, REDir.w)] = self.inputs[e]

        return

    def get_state(self):
        for qi, q in enumerate(self.states):
            if self.REs[qi][self.n].state == REState.H:
                return q

    def step_forward(self, input_char: str):
        ichar_i = self.inputs.index(input_char)
        # All inputs go into the first column, on the west side of an
        # RE at the input character's index
        message = (0, ichar_i, REDir.w)
        while message not in self.outputs:
            col, row, dir_in = message
            dir_out = self.REs[col][row].re_input(dir_in)
            message = self.fwd[(col, row, dir_out)]
        return message

    def step_backward(self, output_char: str, trace=False, file=stdout):
        ochar_i = self.outputs.index(output_char)
        # All outputs get fed back into the last column, on the east
        # side of an RE at the output character's index
        message = (self.m-1, ochar_i, REDir.e)
        while message not in self.inputs:
            if trace:
                print(message, file=file)
                self.print_res(file=file)
            col, row, dir_in = message
            dir_out = self.REs[col][row].re_input(dir_in, reverse=True)
            message = self.bwd[(col, row, dir_out)]
        return message

    def step(self, char: str, reverse=False, trace=False, file=stdout):
        if reverse:
            return self.step_backward(char, trace=trace)
        else:
            return self.step_forward(char)

    def run(self, input_string: str, reverse=False, trace=False, file=stdout):
        output_string = ''
        for char in input_string:
            if reverse:
                output_char = self.step_backward(char, trace=trace)
            else:
                output_char = self.step_forward(char)
            output_string += output_char
        if reverse:
            accepted = self.get_state() == self.q_0
        else:
            accepted = self.get_state() in self.F
        return accepted, output_string

    def print_res(self, file=stdout):
        for row in range(self.n + 1):
            for col in range(self.m):
                print(self.REs[col][row].state, "\t", end="", file=file)
            print(file=file)

def main():
    Q = {'1', '2'}
    Sigma = {'a', 'b'}
    delta = {
        ('1', 'a'): ('2', 'x'),
        ('1', 'b'): ('1', 'x'),
        ('2', 'a'): ('1', 'y')
    }
    q_0 = '1'
    F = {'1'}
    Gamma = {'x', 'y'}
    fst = FST(Q, Sigma, delta, q_0, F, Gamma)

    input_str = 'aaaabaaaa'
    _, fst_output = fst.run_forward(input_str)

    rfa = RFA(fst)
    _, rfa_output = rfa.run(input_str)

    print(rfa_output, fst_output)
    print(rfa_output == fst_output)

    # Reverse output must be fed in reversed
    rfa_reverse_input = rfa_output[::-1]
    _, rfa_reverse_output = rfa.run(rfa_reverse_input, reverse=True)
    print(rfa_reverse_output, input_str)
    print(rfa_reverse_output == input_str)

    return

main()
