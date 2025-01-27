## TOPSIS

Python package which allows one to modify a data set by adding TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) scores and ranks to it.

## Setup 
Install the package using the following command: 
# pip install Topsis_Mandar_102203163

In order to use the package include the following in your python program : 
# import topsis as tp

## Features 
The package currently consists of the following function: 
# topsis(inputFileName : str, weights : str, impacts : str, resultFileName : str) 

- inputFileName : name of your input (.csv) file. For example : "train.csv"
- weights : weights to be applied to each feature of the data set. The number of weights must be equal to the number of features. It must also contain the weights separated by commas in a string. For example, for a data set consisting of 4 features, weights = "1,2,1,1"
- impacts : ideal value for each feature of the data set. The number of impacts must be equal to the number of features. If the value is "+", then a higher value is preferable in the feature. Similarly, if the value if --s "-", then a lower value is more preferable in the feature. Its value must contain the values separated by commas in a string. For example, for a data set consisting of 5 features, impacts = "+,-,+,+"
- resultFileName : File name in which the updated data set containing the respective TOPSIS scores and Ranks must be saved. For example : "train-result.csv". 








