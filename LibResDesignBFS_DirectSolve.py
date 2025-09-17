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
from collections import deque
class Decision:
    """表示一次操作，包含类型和电阻值"""
    def __init__(self, action: str, res: float):
        self.action = action  # "serial" 或 "parallel"
        self.res = res
    def __str__(self):
        return f"{self.action} {self.res:.3f}Ω"
    def __repr__(self):
        return self.__str__()
    def forward_propagate(self, prev_res: float) -> float:
        """正向计算：在已有电阻 prev_res 的基础上，加上/并上一个电阻"""
        if self.action == "serial":
            return prev_res + self.res
        else:  # parallel
            return (prev_res * self.res) / (prev_res + self.res) if (prev_res + self.res) != 0 else math.inf
class ResistorCalculator:
    """电阻网络搜索器（基于 BFS 搜索解空间）"""
    def __init__(self, available_resistors, error=1e-3):
        self.resistors = available_resistors   # 可用电阻列表
        self.error = error                     # 容错范围
    def _evaluate_chain(self, chain):
        """给定一条决策链，计算总电阻"""
        val = 0.0
        for d in chain:
            val = d.forward_propagate(val)
        return val
    def solve(self, target, max_depth=3):
        """
        搜索最优解：
          - 若找到误差范围内的解，返回最少电阻数量的方案
          - 若没有精确命中，返回所有搜索中误差最小的方案
        """
        queue = deque([(0.0, [])])  # (当前电阻值, 决策链)
        best_chain = []
        best_val = None
        best_error = float("inf")
        while queue:
            _, chain = queue.popleft()
            depth = len(chain)
            if depth >= max_depth:
                continue
            for r in self.resistors:
                # 第一步只能串联，避免 0Ω // R = 0Ω 的无效状态
                valid_actions = ["serial"] if depth == 0 else ["serial", "parallel"]
                for action in valid_actions:
                    decision = Decision(action, r)
                    new_chain = chain + [decision]
                    val = self._evaluate_chain(new_chain)
                    err = abs(val - target)
                    # 更新最佳近似解
                    if err < best_error:
                        best_error = err
                        best_chain = new_chain
                        best_val = val
                    # 命中目标（早停）
                    if err <= self.error:
                        return self._format_result(target, new_chain, val, exact=True)
                    queue.append((val, new_chain))
        # 没有精确解，返回最接近的
        return self._format_result(target, best_chain, best_val, exact=False, best_error=best_error)
    def _format_result(self, target, chain, value, exact=False, best_error=None):
        """格式化输出"""
        steps = []
        cur = 0.0
        for d in chain:
            prev = cur
            cur = d.forward_propagate(cur)
            act = "Serial" if d.action == "serial" else "Parallel"
            steps.append(f"{prev:.3f}Ω --{act}{d.res:.3f}Ω--> {cur:.3f}Ω")
        note = "精确解" if exact else f"近似解 (误差 {best_error:.3f}Ω)" if value is not None else "未找到解"
        return {
            "target": target,
            "chain": chain,
            "result": value,
            "depth": len(chain),
            "steps": steps,
            "note": note
        }


# ---------------- 测试 ----------------
if __name__ == "__main__":
    # E6 系列 × 常见倍率
    res_list = [r * s for r in [1.0, 1.5, 2.2, 3.3, 4.7, 6.8] for s in [1e1, 1e2, 1e3, 1e5]]
    calc = ResistorCalculator(res_list, error=1e-3)

    # 例1：精确命中
    res1 = calc.solve(960, max_depth=5)
    print(res1["note"])
    print("\n".join(res1["steps"]))

    # 例2：近似结果
    res2 = calc.solve(114.514, max_depth=4)
    print(res2["note"])
    print("\n".join(res2["steps"]))

    # 例3：更大的目标
    res3 = calc.solve(1919.81, max_depth=5)
    print(res3["note"])
    print("\n".join(res3["steps"]))
