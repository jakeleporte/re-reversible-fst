#!/usr/bin/env python3

from enum import Enum, auto

def test_old():
    fst = 2 * [3 * [None]]
    for col in range(2):
        for row in range(3):
            fst[col][row] = RE()

    con = {}
    con[(0, 2, REDir.e)] = (0, 0, REDir.n)
    con[(0, 2, REDir.w)] = (0, 0, REDir.n)
    con[(0, 2, REDir.s)] = (0, 2, REDir.s)
    con[(0, 2, REDir.n)] = (0, 1, REDir.s)

    con[(1, 2, REDir.e)] = (1, 0, REDir.n)
    con[(1, 2, REDir.w)] = (1, 0, REDir.n)
    con[(1, 2, REDir.s)] = (1, 2, REDir.s)
    con[(1, 2, REDir.n)] = (1, 1, REDir.s)

    con[(0, 1, REDir.e)] = (1, 1, REDir.w)
    con[(0, 1, REDir.s)] = (0, 2, REDir.n)
    con[(0, 1, REDir.w)] = (0, 0, REDir.e)
    con[(0, 1, REDir.n)] = (0, 0, REDir.s)

    con[(1, 1, REDir.e)] = 'y'
    con[(1, 1, REDir.s)] = (1, 2, REDir.n)
    con[(1, 1, REDir.n)] = (1, 0, REDir.s)

    con[(0, 0, REDir.e)] = (1, 0, REDir.w)
    con[(0, 0, REDir.s)] = (0, 1, REDir.n)
    con[(0, 0, REDir.w)] = (1, 0, REDir.e)

    con[(1, 0, REDir.e)] = 'x'
    con[(1, 0, REDir.s)] = (1, 1, REDir.n)
    con[(1, 0, REDir.w)] = (0, 1, REDir.e)

    new_msg = {}

    for key, value in con.items():
        new_msg[key] = value
        new_msg[value] = key

    new_msg[(0, 0, REDir.w)] = 'a'
    new_msg[(0, 1, REDir.w)] = 'b'

    msg = (1, 1, REDir.e)

    while msg not in ('a', 'b', 'x', 'y'):
        col, row, in_dir = msg
        out_dir = fst[col][row].re_input(in_dir)
        msg = new_msg[(col, row, out_dir)]

    print(msg)

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

    def re_input(self, direction):
        if self.state == REState.V:
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
        elif self.state == REState.H:
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

class DFA:
    def __init__(self, Q: set, Sigma: set, delta: dict,
                 q_0: str, F: set, Gamma: set = set(), transducer=False):
        self.Q = Q
        self.Sigma = Sigma
        self.delta = delta
        self.q_0 = q_0
        self.F = F
        self.transducer = transducer
        self.Gamma = Gamma

        self.state = q_0
        return

    def step_forward(self, input_char: str):
        if input_char not in self.Sigma:
            raise ValueError('Given input is not in input alphabet')

        if self.transducer:
            next_state, output_char = self.delta[(self.state, input_char)]
            self.state = next_state
        else:
            next_state = self.delta[(self.state, input_char)]
            output_char = None
        return output_char

    def run_forward(self, input_string: str):
        output_string = ''
        for char in input_string:
            output_char = self.step_forward(char)
            if output_char: output_string += output_char
        accepted = (self.state in self.F)
        if self.transducer:
            return (accepted, output_string)
        else:
            return accepted

class RFA:
    def __init__(self, DFA):
        num_inputs = len(DFA.Sigma)
        self.states = {}
        return

def main():
    Q = {'1', '2'}
    Sigma = {'a', 'b'}
    delta = {
        ('1', 'a'): ('2', 'x'),
        ('1', 'b'): ('1', 'x'),
        ('2', 'a'): ('1', 'y'),
        ('2', 'b'): ('2', 'x')
    }
    q_0 = '1'
    F = {'1'}
    Gamma = {'x', 'y'}
    dfa = DFA(Q, Sigma, delta, q_0, F, Gamma, True)

    print(dfa.run_forward('aaaabaaa'))

    return

main()
