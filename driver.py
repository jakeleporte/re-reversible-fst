#!/usr/bin/env python3

import re_rfst

def main(test_case=2):
    test_1 = {
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

    lamp = {
        'Q': {'LL', 'LH', 'HH', 'HL'},
        'Sigma': set('rl'),
        'delta': {
            ('LL', 'r'): ('LH', 'r'),
            ('LL', 'l'): ('HL', 'l'),
            ('LH', 'r'): ('LL', 'r'),
            ('LH', 'l'): ('HH', 'l'),
            ('HH', 'r'): ('HL', 'r'),
            ('HH', 'l'): ('LH', 'l'),
            ('HL', 'r'): ('HH', 'r'),
            ('HL', 'l'): ('LL', 'l')
        },
        'q_0': 'LL',
        'F': {'LL', 'HH'},
        'Gamma': set('rl')
    }

    if test_case == 1:
        fst = re_rfst.FST(**test_1)

        input_str = 'abab'
        _, fst_output = fst.run_forward(input_str)

        rfa = re_rfst.RFA(fst)
        _, rfa_output = rfa.run(input_str, trace=True, pause=1)
        _, rfa_reverse_output = rfa.run(rfa_output[::-1], reverse=True)

        print(f'Output of FST model: {fst_output}')
        print(f'Output of RFA model: {rfa_output}')
        print('Match.' if rfa_output == fst_output else 'Not a match.')
        print()
        print(f'Input to FTS:\t\t  {input_str}')
        print(f'Output from reversed RFA: {rfa_reverse_output}')
        print('Match.' if rfa_reverse_output == input_str else 'Not a match.')
    elif test_case == 2:
        lamp_fst = re_rfst.FST(**lamp)
        lamp_input = 'rllrlrrlrrrrllll'
        _, lamp_output = lamp_fst.run_forward(lamp_input)


        lamp_rfa = re_rfst.RFA(lamp_fst)
        _, lamp_rfa_output = lamp_rfa.run(lamp_input, trace=True, pause=1)
        _, lamp_reverse_output = lamp_rfa.run(lamp_rfa_output[::-1], reverse=True)

        print(f'Output of FST model: {lamp_output}')
        print(f'Output of RFA model: {lamp_rfa_output}')
        print('Match.' if lamp_rfa_output == lamp_output else 'Not a match.')
        print()
        print(f'Input to FTS:\t\t  {lamp_input}')
        print(f'Output from reversed RFA: {lamp_reverse_output}')
        print('Match.' if lamp_reverse_output == lamp_input else 'Not a match.')

    return

main()
