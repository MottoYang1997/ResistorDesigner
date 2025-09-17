# ResistorDesigner
A Resistor Network Designer with Dynamic Programming and BFS.

## How to Run (GUI)

You can also run the **graphical interface** built with Tkinter:

~~~bash
python Ex01.gui.py
~~~

### GUI Features

- **Target Resistance**: Enter the resistance value you want to achieve.
- **Maximum Depth**: The search depth — larger values try more resistor combinations.
- **Error Threshold**: Allowed deviation (tolerance) between target and result.

---

### Adding Resistors

- **E‑Series (batch add)**:
  Use the dropdowns to select a resistor **series** (E6, E12, E24) and a **scale factor** (1, 10, 100, 1k, etc.), then click **Add E-Series**.
- **Manual Add**:
  Enter a resistance value and click **Add** to insert it into the resistor library.
- **Edit/Delete/Clear**:
  Select a resistor and use the buttons to modify or remove it.

---

### Running the Calculation

1. Set **Target Resistance**, **Max Depth**, and **Error Threshold**.
2. Ensure you have resistors listed in the **Resistor Library**.
3. Click **Run Calculation**.
   - The program will iteratively search for the best resistor network.
   - Intermediate results appear in the output panel.
4. Click **Stop** at any time to end the search early.

---

### Output Panel

The output shows:
- **Current best candidate** (closest resistance found).
- **Depth of combination**.
- **Number of search calls performed**.
- **Final result path**: step‑by‑step resistor network (serial/parallel).

Example (simplified):
```
计算开始: 目标 960Ω, 深度=5
候选: 960.000Ω
深度: 3
搜索次数: 152
串联 330Ω → 并联 680Ω → 串联 150Ω → 960Ω
搜索完成！
最佳结果: 960.000Ω
```

---


## How to Run (Command Line)

In the project folder, type
~~~ bash
python Ex00.resistor_designer_hjb.py
~~~

Below is a sample output from the program.

~~~
Worst Case Total Calculations: 46656
Target Resistance (ohm): 123.456
Solution may be better if considering a decision length longer than 3.
---- begin from 0 ohm ----
serial 22.0 ohm
serial 68.0 ohm
serial 33.0 ohm
---- circuit complete ----
Result: 123.0 ohm
~~~

### Key Parameters in the Program
+ scale_list
  + Scales of the available resistor
+ res_6_list
  + Standard E6 resistor values
+ max_decision_chain_length
  + Maximum Dynamic Programming Depth and maximum number of resistors used. The worst-case number of search cases grow **exponentially** with this parameter.
+ decision_list
  + You can also append your available resistors into decision_list with the following template.

~~~ python
my_res = 123.0
decision_list.append(Decision("serial", my_res))
decision_list.append(Decision("parallel", my_res))
~~~

## License

This project is licensed under the GNU GPL v3.
