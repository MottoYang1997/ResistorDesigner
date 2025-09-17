"""
Resistor Designer - A Resistor Network Designer with Dynamic Programming
Copyright (C) 2023  Yiming Yang

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import math
import random


# Circuit Actions
action_list = ["serial", "parallel"]
# Resistor Scales
scale_list = [1e1, 1e3, 1e5]
# Resistor Value - E6 Standards
res_6_list = [1.0, 1.5, 2.2, 3.3, 4.7, 6.8]
# Maximum number of resistors to be used
max_decision_chain_length = 3
# Resistor Error Threshold for a Valid Solution
error = 1e-6


# standard resistor values
# res_6_list = [1.0, 1.5, 2.2, 3.3, 4.7, 6.8]
# res_6_error = 0.2
# res_12_list = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
# res_12_error = 0.10
# res_24_list = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
# res_24_error = 0.24


class Decision:
    def __init__(self, action: str, res: float):
        self.action = action
        self.res = res
        self.next_decision = None

    def __str__(self):
        return f"{self.action} {self.res} ohm"
    
    def inverse_propagate(self, res):
        if self.action == "serial":
            return res - self.res
        else:
            try:
                return (res * self.res) / (self.res - res)
            except ZeroDivisionError:
                return -1e9
    
    def forward_propagate(self, res):
        if self.action == "serial":
            return res + self.res
        else:
            return res * self.res / (res + self.res)


# Generate Possible Actions
decision_list = []
for res_6 in res_6_list:
    for scale in scale_list:
        for action in action_list:
            decision_list.append(Decision(action, res_6*scale))


print(f"Worst Case Total Calculations: {len(decision_list) ** max_decision_chain_length}")


# Append decisions without duplicates in the same decision layer to simplify calculations
def append_no_duplicate(l_result: list, l_decisions: list, new_res: float, new_decision: Decision):
    for res in l_result:
        if math.fabs(res - new_res) < error:
            # ignore this duplicate result
            return False
    l_result.append(new_res)
    l_decisions.append(new_decision)


def index_float(l: list, val: float):
    for a in l:
        if math.fabs(a - val) < error:
            return l.index(a)


def get_shortest_decision_chain(res: float):
    res_layers = [[res]]
    decision_layers = []

    while True:
        is_solution_found = False
        # Expand a new layer
        new_res_layer = []
        new_decision_layer = []
        for res in res_layers[-1]:
            random.shuffle(decision_list)
            for decision in decision_list:
                new_res = decision.inverse_propagate(res)
                if new_res >= error:
                    append_no_duplicate(new_res_layer, new_decision_layer, new_res, decision)
                elif math.fabs(new_res) < error:
                    append_no_duplicate(new_res_layer, new_decision_layer, new_res, decision)
                    is_solution_found = True
                else:
                    continue
        res_layers.append(new_res_layer)
        decision_layers.append(new_decision_layer)

        if is_solution_found:
            break
        
        if len(decision_layers) >= max_decision_chain_length:
            break

    decision_chain = []
    current_res = min(res_layers[-1])
    for i in range(len(res_layers) - 1, 0, -1):
        res_idx = index_float(res_layers[i], current_res)
        decision_chain.append(decision_layers[i - 1][res_idx])
        current_res = decision_chain[-1].forward_propagate(current_res)
    
    # Re-calcuate the designed resistance from 0 ohm if it is not optimum.
    if not is_solution_found:
        current_res = 0
        for decision in decision_chain:
            current_res = decision.forward_propagate(current_res)
    
    return decision_chain, current_res, is_solution_found


if __name__ == "__main__":

    res = float(input("Target Resistance (ohm): "))

    decision_chain, result, is_optimum = get_shortest_decision_chain(res)

    if is_optimum:
        print(f"Optimum Solution Found within maximum decision length {max_decision_chain_length}.")
    else:
        print(f"Solution may be better if considering a decision length longer than {max_decision_chain_length}.")
    
    print("---- begin from 0 ohm ----")
    for decision in decision_chain:
        print(decision)
    print("---- circuit complete ----")
    print(f"Result: {result} ohm")
