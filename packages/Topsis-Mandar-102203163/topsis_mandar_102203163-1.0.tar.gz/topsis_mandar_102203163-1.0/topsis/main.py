import pandas as pd 
from pandas.api.types import is_numeric_dtype
from scipy.stats import rankdata
import numpy as np
def topsis(inputFileName : str, weights : str, impacts : str, resultFileName : str):
    
    try:
        data = pd.read_csv(inputFileName)
    except: 
        raise Exception('file not found')

    if (data.shape[1] < 3):
        print('Three or more columns required')
        exit(1)

    data = data.iloc[:, 1:]

    for name in np.array(data.columns):
        if not is_numeric_dtype(data[name]):
            raise Exception('only numeric values allowed')

    data = data.values 
    rows = data.shape[0]
    columns = data.shape[1]
    norm = []
    for j in range(columns):
        rootsum = 0
        for i in range(rows):
            rootsum = rootsum + (data[i][j]) ** 2
        rootsum = np.sqrt(rootsum)
    
        data[:, j] = data[:, j] / rootsum

    weights = weights.replace(' ', '')
    try:
        weights = np.array([int(item) for item in weights.split(',')])
    except:
        raise Exception('invalid input')
    if(len(weights) != columns):
        raise Exception('number of weights should be valid and equal to number of columns, check if the separators are correct(use commas)')
    for j in range(columns):
        data[:, j] = data[:, j] * weights[j]

    impacts = impacts.split(',') 
    allowed = {'+', '-'}
    if(not np.isin(impacts, list(allowed)).all()):
        raise Exception('invalid input')
    if(len(impacts) != columns):
        raise Exception('number of impacts should be equal to number of columns, check if the separators are correct')

    vjpos = []
    vjneg = []

    for j in range(columns):
        if (impacts[j] == "+"): 
            vjpos.append(max(data[:, j]))
            vjneg.append(min(data[:, j]))
        else:
            vjpos.append(min(data[:, j]))
            vjneg.append(max(data[:, j]))

    vjpos = np.float64(vjpos)
    vjneg = np.float64(vjneg)

    spos = []
    sneg = []
    for i in range(rows): 
        distpos = 0
        distneg = 0
        for j in range(columns):
            distpos = distpos + (data[i][j] - vjpos[j]) ** 2
            distneg = distneg + (data[i][j] - vjneg[j]) ** 2
        distpos = np.sqrt(distpos)
        distneg = np.sqrt(distneg)
        spos.append(distpos)
        sneg.append(distneg)

    spos = np.float64(spos)
    sneg = np.float64(sneg)

    scores = []
    for i in range(rows): 
        p = sneg[i] / (spos[i] + sneg[i])
        p = round(p, 3)
        scores.append(p)

    scores = np.float64(scores)
 
    ranks = len(scores) - rankdata(scores).astype(int) + 1

    data = pd.read_csv(inputFileName) 
    data['Topsis Score'] = scores 
    data['Rank'] = ranks 
    data.to_csv(resultFileName, index = False)