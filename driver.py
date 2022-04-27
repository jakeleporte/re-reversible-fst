#!/usr/bin/env python3

import re_rfst

def main():
    fst_dict = {
        'Q': {'1', '2'},
        'Sigma': {'a', 'b'},
        'delta': {
            ('1', 'a'): ('2', 'x'),
            ('1', 'b'): ('1', 'x'),
            ('2', 'a'): ('1', 'y'),
            ('2', 'b'): ('2', 'y')
        },
        'q_0': '1',
        'F': {'1'},
        'Gamma': {'x', 'y'}
    }

    fst = re_rfst.FST(**fst_dict)

    input_str = 'aba'
    _, fst_output = fst.run_forward(input_str)

    rfa = re_rfst.RFA(fst)
    _, rfa_output = rfa.run(input_str, trace=True, pause=1)

    print(rfa_output, fst_output)
    print(rfa_output == fst_output)

    # Reverse output must be fed in reversed
    rfa_reverse_input = rfa_output[::-1]
    _, rfa_reverse_output = rfa.run(rfa_reverse_input, reverse=True)
    print(rfa_reverse_output, input_str)
    print(rfa_reverse_output == input_str)

    return

main()
