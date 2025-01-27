# PBLgrupo6
# Preprocessing library PBL group 6

### Prerequisites

For this code, the following libreries are required:
 - numpy
 - pandas
 - scipy
 - sys
 - time



### How to use
These are the steps you need to follow to clean your dataset:
1. Introduce your path in the class. --> ex:  Variable = libreria.DataAnalysis(path).
2. Read your data with pandas:
- CSV: use the function Variable.csv().
- Excel: usa the function Variable.excel().
3. Start cleaning your dataset using Variable.analyze().
4. Visualize the dataframe using the function Variable.visualize()
5. Save the dataframe using Variable.save()

If you want to see this information while running the code, use the function Variable.info()

Extra:
These analysis criteria can be changed:
- variable 1 = Percentage of empty data to recommend deleting the column (0.3 by default) 
- variable 2 = Normal distribution displacement to assume skewed distribution (0.05 by default)
To do so, create a file named 'values.txt' with the values separated with commas and without any space. Example: "0.3,0.05"

The separation character for the csv can be changed by introducing a diferent character in the function.

## Code example:

import libreriaclases as lb

Data1=lb.DataAnalysis('example.csv')

Data1.csv(sep = ',')

Data1.analyze()
