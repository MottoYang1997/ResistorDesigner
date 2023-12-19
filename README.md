# ResistorDesigner
A Resistor Network Designer with Dynamic Programming

## How to Run

In the project folder, type
~~~ bash
python resistor_designer.py
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

## Key Parameters in the Program
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
