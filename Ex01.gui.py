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

import tkinter as tk
from tkinter import ttk, messagebox
from LibResDesignBFS import ResistorCalculator

# --- E 系列定义 ---
E_SERIES = {
    "E6": [1.0, 1.5, 2.2, 3.3, 4.7, 6.8],
    "E12": [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2],
    "E24": [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4,
            2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2,
            6.8, 7.5, 8.2, 9.1]
}
SCALE_FACTORS = {
    "1": 1,
    "10": 10,
    "100": 100,
    "1k": 1e3,
    "10k": 1e4,
    "100k": 1e5,
}


class ResistorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("电阻组合计算器 © YimingYang 2025")

        # --- 顶部输入区 ---
        frm_top = ttk.Frame(root)
        frm_top.pack(fill="x", padx=5, pady=5)

        ttk.Label(frm_top, text="目标电阻:").pack(side="left")
        self.target_var = tk.StringVar()
        ttk.Entry(frm_top, textvariable=self.target_var, width=10).pack(side="left", padx=2)

        ttk.Label(frm_top, text="最大深度:").pack(side="left")
        self.depth_var = tk.IntVar(value=3)
        ttk.Spinbox(frm_top, from_=1, to=6, textvariable=self.depth_var, width=5).pack(side="left", padx=2)

        ttk.Label(frm_top, text="误差阈值:").pack(side="left")
        self.error_var = tk.DoubleVar(value=1e-2)
        ttk.Entry(frm_top, textvariable=self.error_var, width=8).pack(side="left", padx=2)

        # --- 批量添加 E 系列 ---
        frm_batch = ttk.LabelFrame(root, text="批量添加 E 系列")
        frm_batch.pack(fill="x", padx=5, pady=5)

        self.eseries_var = tk.StringVar(value="E6")
        ttk.Combobox(frm_batch, textvariable=self.eseries_var, values=list(E_SERIES.keys()), width=5).pack(side="left", padx=2)

        self.scale_var = tk.StringVar(value="10")
        ttk.Combobox(frm_batch, textvariable=self.scale_var, values=list(SCALE_FACTORS.keys()), width=5).pack(side="left", padx=2)

        ttk.Button(frm_batch, text="添加E系列", command=self.add_eseries).pack(side="left", padx=5)

        # --- 电阻管理区 ---
        frm_res = ttk.LabelFrame(root, text="电阻库")
        frm_res.pack(fill="x", padx=5, pady=5)

        self.resistor_listbox = tk.Listbox(frm_res, height=8, selectmode="extended")
        self.resistor_listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frm_res, command=self.resistor_listbox.yview)
        self.resistor_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="left", fill="y")

        frm_res_btns = ttk.Frame(frm_res)
        frm_res_btns.pack(side="left", fill="y", padx=5)

        self.add_var = tk.StringVar()
        ttk.Entry(frm_res_btns, textvariable=self.add_var, width=10).pack(pady=2)
        ttk.Button(frm_res_btns, text="添加", command=self.add_resistor).pack(pady=2)
        ttk.Button(frm_res_btns, text="修改", command=self.edit_resistor).pack(pady=2)
        ttk.Button(frm_res_btns, text="删除", command=self.del_resistor).pack(pady=2)
        ttk.Button(frm_res_btns, text="全部清空", command=lambda: self.resistor_listbox.delete(0, "end")).pack(pady=2)
        
        # --- 计算控制区 ---
        frm_ctrl = ttk.Frame(root)
        frm_ctrl.pack(fill="x", padx=5, pady=5)

        ttk.Button(frm_ctrl, text="运行计算", command=self.run_calc).pack(side="left", padx=5)
        ttk.Button(frm_ctrl, text="停止", command=self.stop_calc).pack(side="left", padx=5)

        ttk.Label(frm_ctrl, text="步进n:").pack(side="left", padx=5)
        self.step_var = tk.IntVar(value=500)
        ttk.Spinbox(frm_ctrl, from_=1, to=5000, textvariable=self.step_var, width=8).pack(side="left")

        # --- 输出结果 ---
        self.output_text = tk.Text(root, height=15)
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)

        # 状态变量
        self.calc = None
        self.searching = False
        self.target_val = None

    # ---- 功能实现 ----
    def add_resistor(self):
        try:
            val = float(self.add_var.get())
            self.resistor_listbox.insert("end", val)
        except ValueError:
            messagebox.showerror("错误", "请输入合法的数字电阻值！")

    def edit_resistor(self):
        sel = self.resistor_listbox.curselection()
        if not sel:
            return
        try:
            val = float(self.add_var.get())
            self.resistor_listbox.delete(sel[0])
            self.resistor_listbox.insert(sel[0], val)
        except ValueError:
            messagebox.showerror("错误", "请输入合法的数字电阻值！")

    def del_resistor(self):
        sel = self.resistor_listbox.curselection()
        for i in reversed(sel):
            self.resistor_listbox.delete(i)

    def add_eseries(self):
        series = self.eseries_var.get()
        scale = SCALE_FACTORS[self.scale_var.get()]
        for r in E_SERIES[series]:
            self.resistor_listbox.insert("end", r * scale)

    def stop_calc(self):
        self.searching = False
        self.output_text.insert("end", "用户已停止计算。\n")

    def run_calc(self):
        if self.searching:
            messagebox.showinfo("提示", "计算正在进行中...")
            return

        try:
            self.target_val = float(self.target_var.get())
        except ValueError:
            messagebox.showerror("错误", "请输入合法的目标电阻！")
            return

        depth = self.depth_var.get()
        error = self.error_var.get()
        resistors = [float(self.resistor_listbox.get(i)) for i in range(self.resistor_listbox.size())]

        if not resistors:
            messagebox.showwarning("警告", "请至少添加一个电阻！")
            return

        # 初始化计算器对象
        self.calc = ResistorCalculator(available_resistors = resistors, error=error)
        self.calc.config(self.target_val, depth)
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", f"计算开始: 目标 {self.target_val}Ω, 深度={depth}\n")
        self.searching = True

        self.root.after(50, self.step_calc)

    def step_calc(self):
        if not self.searching or self.calc is None:
            return

        n = self.step_var.get()
        done, result = self.calc.step_n(n)

        if result:  # 每次更新最佳结果
            self.output_text.delete("1.0", "end")
            self.output_text.insert("end",
                f"候选: {result['result']:.3f}Ω\n深度: {result['depth']}, {result['note']}\n搜索次数: {result["search_calls"]}\n"
            )

        if done:
            self.output_text.insert("end", "\n搜索完成！\n")
            self.output_text.insert("end", f"搜索次数: {result["search_calls"]}\n")
            self.output_text.insert("end", f"最佳结果: {result['result']:.3f}Ω\n")
            for s in result['path_steps']:
                self.output_text.insert("end", s + "\n")
            self.searching = False
            return

        # 继续下一批
        self.root.after(50, self.step_calc)


if __name__ == "__main__":
    root = tk.Tk()
    gui = ResistorGUI(root)
    root.mainloop()
