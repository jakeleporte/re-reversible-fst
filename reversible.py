#!/usr/bin/env python3

from enum import Enum, auto
from collections import defaultdict

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
        n = len(DFA.Sigma)
        m = len(DFA.Q)
        self.inputs = list(DFA.Sigma)
        self.outputs = list(DFA.Gamma)
        self.states = list(DFA.Q)
        # self.REs = m * [(n + 1) * [None]]
        # for col in range(m):
        #     for row in range(n + 1):
        #         self.REs[col][row] = RE()
        # Put the machine in the initial state
        self.REs = {}
        q_0_i = self.states.index(DFA.q_0)
        # self.REs[q_0_i][n].state = REState.V

        self.fwd = defaultdict()
        for q in DFA.Q:
            qi = self.states.index(q)
            # Initialize the "state-keeping" REs, by convention
            # numbered `n`.
            self.fwd[(qi, n, REDir.n)] = (qi, n-1, REDir.s)
            self.fwd[(qi, n, REDir.s)] = (qi, n, REDir.s)
            # self.fwd[(qi, n, REDir.e)] = (qi, 0, REDir.s)
            self.fwd[(qi, n, REDir.w)] = (qi, 0, REDir.n)


        # Initialize the array of REs that forms the "brains" of the
        # RFA, state column by state column
        for q in DFA.Q:
            qi = self.states.index(q)
            init_state = REState.V if q == DFA.q_0 else REState.H
            RE_n_conn = {
                'n': ((qi, n-1), REDir.s),
                'e': ((qi, 0), REDir.n),
                's': ((qi, n), REDir.s),
                'w': ((qi, 0), REDir.n)
            }
            # This is the "state-keeping" RE, corresponding to the
            # "bottom" RE in the slides from class; it corresponds to
            # no inputs or outputs, it just maintains state
            self.REs[(qi, n)] = RFAE(RE(init_state), REConn(**RE_n_conn))
            # These are the "input" and "output" REs for each state
            RE_0_conn = {
                'n': ((qi, n), REDir.e),
                's': ((qi, 1), REDir.n)
            }
            self.REs[(qi, 0)] = RFAE(RE(), REConn(**RE_0_conn))
            for i in range(1, n):
                RE_conn = {
                    'n': ((qi, i-1), REDir.s),
                    's': ((qi, i+1), REDir.n)
                }
                self.REs[(qi, i)] = RFAE(RE(), REConn(**RE_conn))
        # Now, make the connections "between columns" by connecting
        # corresponding REs between consecutive columns
        for qi in range(1, m):
            for i in range(n - 1):
                self.REs[(qi - 1, i)].REConn.e = \
                    ((qi, i), REDir.w)
        # Now, make connections corresponding to the input DFA's state
        # transition function, delta
        for input_pair, output_pair in DFA.delta.items():
            print(input_pair, output_pair)
            # Extract relevant information
            state_curr, input_char = input_pair
            curr_index = self.states.index(state_curr)
            input_index = self.inputs.index(input_char)
            state_next, output_char = output_pair
            next_index = self.states.index(state_next)
            output_index = self.outputs.index(output_char)
            # Make the forward connections
            self.REs[(curr_index, input_index)].REConn.w = \
                ((next_index, output_index), REDir.e)
        # This completes initialization of the forward-capable RFA
        return

    def io(self, target, message):
        out_dir = self.REs[target].RE.re_input(message)
        if out_dir == REDir.n:
            return self.REs[target].REConn.n
        elif out_dir == REDir.e:
            return self.REs[target].REConn.e
        elif out_dir == REDir.s:
            return self.REs[target].REConn.s
        elif out_dir == REDir.w:
            return self.REs[target].REConn.w

    def get_state(self):
        n = len(self.inputs)
        for i, q in enumerate(self.states):
            if self.REs[(i, n)].RE.state == REState.V:
                return q

    def step_forward(self, input_char: str):
        input_index = self.inputs.index(input_char)
        input_state = 0
        input_target = (input_state, input_index)
        # All inputs come in from the West ports of the first column
        result = self.io(input_target, REDir.w)
        while result:
            target, message = result
            result = self.io(target, message)

        return self.outputs[target[1]]

    def run_forward(self, input_string: str):
        output_string = ''
        for char in input_string:
            output_char = self.step_forward(char)
            if output_char: output_string += output_char
        return output_string

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

    rfa = RFA(dfa)
    print(rfa.run_forward('aaaabaaa'))

    return

main()
