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
from collections import deque


class Decision:
    def __init__(self, action: str, res: float):
        self.action = action
        self.res = res

    def __str__(self):
        return f"{self.action} {self.res:.3f} Ω"

    def __repr__(self):
        return self.__str__()

    def forward_propagate(self, res):
        """正向计算：已知已有电阻res，新增一个电阻组合"""
        if self.action == "serial":
            return res + self.res
        else:  # parallel
            return (res * self.res) / (res + self.res)


def approx_equal(a, b, error=1e-6):
    return abs(a - b) < error

class ResistorCalculator:
    def __init__(self, available_resistors, error=1.0):
        self.resistors = available_resistors
        self.error = error
        self.reset()
    def reset(self):
        self.target = None
        self.max_depth = 3
        self.decision_list = []
        self.queue = deque()
        self.visited = set()
        self.finished = False
        self.solution_found = False
        self.result_value = None
        self.result_chain = []
        self.call_count = 0
        # 用于记录最接近解
        self.best_chain = []
        self.best_error = float("inf")
        self.best_value = None

    def config(self, target, max_depth):
        self.reset()
        self.target = target
        self.max_depth = max_depth
        self.queue.append( (0.0, []) )

    def solve(self, target, max_depth=3):
        self.config(target, max_depth)
        return self.run_until_done()
    
    def step_n(self, n=1):
        for _ in range(n):
            if not self.queue or self.finished:
                self.finished = True
                return True, self.get_result()
            current, chain = self.queue.popleft()
            depth = len(chain)
            self.call_count += 1
            if depth >= self.max_depth:
                continue
            for res in self.resistors:
                # 第一层只串联，避免 0Ω // R = 0Ω 的问题
                actions = ["serial"] if depth == 0 else ["serial", "parallel"]
                for action in actions:
                    decision = Decision(action, res)
                    new_chain = chain + [decision]
                    # forward 计算
                    test_val = 0.0
                    for d in new_chain:
                        test_val = d.forward_propagate(test_val)
                    err = abs(test_val - self.target)
                    # 更新最佳解
                    if err < self.best_error:
                        self.best_error = err
                        self.best_chain = new_chain
                        self.best_value = test_val
                    # 命中（在容差内）
                    if err <= self.error:
                        self.solution_found = True
                        self.finished = True
                        self.result_value = test_val
                        self.result_chain = new_chain
                        return True, self.get_result()
                    # 否则入队
                    self.queue.append((test_val, new_chain))
        # 还没结束
        return False, self.get_result()
    
    def run_until_done(self):
        while not self.finished and self.queue:
            self.step_n(1)
        return self.get_result()
    def get_result(self):
        if self.solution_found:
            chain = self.result_chain
            val = self.result_value
            note = "精确解"
        else:
            chain = self.best_chain
            val = self.best_value
            if val is not None:
                note = f"近似解 (误差 {self.best_error:.3f}Ω)"
            else:
                note = "未找到解"
        steps = []
        if chain:
            current = 0.0
            for d in chain:
                prev = current
                current = d.forward_propagate(current)
                action_txt = "串联" if d.action == "serial" else "并联"
                steps.append(f"{prev:g}Ω\t\t\t--{action_txt}{d.res:g}Ω-->\t\t\t{current:g}Ω")
        return {
            "target": self.target,
            "finished": self.finished,
            "solution_found": self.solution_found,
            "result": val,
            "chain": chain,
            "depth": len(chain),
            "path_steps": steps,
            "note": note,
            "search_calls": self.call_count
        }


if __name__ == "__main__":
    # res_list = [100, 150, 220, 330]  # 可选电阻
    res_list = [r * s for r in [1.0, 1.5, 2.2, 3.3, 4.7, 6.8] for s in [1e1, 1e2, 1e3, 1e5]]
    calc = ResistorCalculator(res_list, error=0.001)
    # 例 1: 
    res1 = calc.solve(960, max_depth=5)
    print(res1["note"])       # "精确解"
    print(res1["path_steps"]) # 展示具体组合
    # 例 2: 
    res2 = calc.solve(114.514, max_depth=4)
    print(res2["note"])       # "近似解 (误差 0.xxxΩ)"
    print(res2["path_steps"])
    # 例 3: 
    res2 = calc.solve(1919.81, max_depth=3)
    print(res2["note"])       # "近似解 (误差 0.xxxΩ)"
    print(res2["path_steps"])
