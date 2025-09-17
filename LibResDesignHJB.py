'''
Copyright (C) 2025  YimingYang

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
'''

import math
import random


class Decision:
    def __init__(self, action: str, res: float):
        self.action = action
        self.res = res
        self.next_decision = None

    def __str__(self):
        return f"{self.action} {self.res:.3f} Ω"

    def __repr__(self):
        return self.__str__()

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
            return (res * self.res) / (res + self.res) if (res + self.res) != 0 else math.inf


def append_no_duplicate(l_result: list, l_decisions: list, new_res: float, new_decision: Decision, error=1e-6):
    for res in l_result:
        if math.fabs(res - new_res) < error:
            return False
    l_result.append(new_res)
    l_decisions.append(new_decision)
    return True


def index_float(l: list, val: float, error=1e-6):
    for idx, a in enumerate(l):
        if math.fabs(a - val) < error:
            return idx
    return None


class ResistorCalculator:
    """
    可配置的电阻网络计算引擎（逆推实现，但返回格式与 BFS 保持一致）
    """

    def __init__(self, error_threshold=1e-3):
        self.error = error_threshold
        self.reset()

    def reset(self):
        self.target = None
        self.decision_list = []
        self.max_depth = 3
        self.res_layers = []
        self.decision_layers = []
        self.is_solution_found = False
        self.finished = False
        self.iter_depth = 0
        self.decision_chain = []
        self.result_value = None

    def configure(self, target, resistors, max_depth=3):
        self.reset()
        self.target = target
        self.max_depth = max_depth

        self.decision_list = []
        for r in resistors:
            self.decision_list.append(Decision("serial", r))
            self.decision_list.append(Decision("parallel", r))

        # 第一层只允许串联
        self.first_decision_list = [Decision("serial", r) for r in resistors]

        self.res_layers = [[self.target]]
        self.decision_layers = []

    def step(self):
        if self.finished:
            return False

        new_res_layer = []
        new_decision_layer = []
        is_solution_found = False

        # 深度为0时只允许串联
        decisions = self.first_decision_list if self.iter_depth == 0 else self.decision_list

        for res in self.res_layers[-1]:
            random.shuffle(decisions)
            for decision in decisions:
                new_res = decision.inverse_propagate(res)
                if new_res >= self.error:
                    append_no_duplicate(new_res_layer, new_decision_layer, new_res, decision, self.error)
                elif math.fabs(new_res) < self.error:  # 命中
                    append_no_duplicate(new_res_layer, new_decision_layer, new_res, decision, self.error)
                    is_solution_found = True
                else:
                    continue

        self.res_layers.append(new_res_layer)
        self.decision_layers.append(new_decision_layer)
        self.iter_depth += 1
        self.is_solution_found = is_solution_found

        if is_solution_found or self.iter_depth >= self.max_depth:
            self.finished = True
            self._build_chain()
            return False

        return True

    def run_until_done(self):
        while self.step():
            pass
        return self.get_result()

    def _build_chain(self):
        if not self.decision_layers:
            return

        decision_chain = []
        current_res = min(self.res_layers[-1]) if self.res_layers[-1] else 0
        for i in range(len(self.res_layers) - 1, 0, -1):
            res_idx = index_float(self.res_layers[i], current_res, self.error)
            if res_idx is None:
                continue
            decision_chain.append(self.decision_layers[i - 1][res_idx])
            current_res = decision_chain[-1].forward_propagate(current_res)

        if not self.is_solution_found:
            current_res = 0
            for decision in decision_chain:
                current_res = decision.forward_propagate(current_res)

        self.decision_chain = list(reversed(decision_chain))  # 顺序调整为 forward
        self.result_value = current_res

    def get_result(self):
        steps = []
        current = 0.0
        for d in self.decision_chain:
            prev = current
            current = d.forward_propagate(current)
            act = "串联" if d.action == "serial" else "并联"
            steps.append(f"{prev:.3f}Ω --{act}{d.res:.3f}Ω--> {current:.3f}Ω")

        note = "精确解" if self.is_solution_found else (
            f"近似解 (误差 {abs((self.result_value or 0) - self.target):.3f}Ω)"
            if self.result_value is not None else "未找到解"
        )

        return {
            "target": self.target,
            "chain": self.decision_chain,
            "result": self.result_value,
            "depth": len(self.decision_chain),
            "steps": steps,
            "note": note
        }


# ---------------- 测试 ----------------
def test_case():
    resistors = [r * s for r in [1.0, 1.5, 2.2, 3.3, 4.7, 6.8] for s in [1e1, 1e2, 1e3, 1e5]]
    calc = ResistorCalculator(error_threshold=1e-3)

    calc.configure(target=9600, resistors=resistors, max_depth=3)
    result = calc.run_until_done()
    print("9600Ω ->", result)

    calc.configure(target=114.514, resistors=resistors, max_depth=3)
    result = calc.run_until_done()
    print("114.514Ω ->", result)

    calc.configure(target=191.981, resistors=resistors, max_depth=3)
    result = calc.run_until_done()
    print("191.981Ω ->", result)

if __name__ == "__main__":
    test_case()
