import math
import sys
import pandas as pd
import numpy as np
import argparse

def topsis(data , weights =None, impacts=None, output=None):

    data = data.copy()
    extra = data.copy()
    
    row,cols = data.shape
    
    if weights != None:
        weights = weights.split(",")
    else :
        weights= []
        for i in range(cols-1):
            weights.append("1")
    if impacts !=None:
        impacts = impacts.split(",")
    else :
        impacts= []
        for i in range(cols-1):
            impacts.append("+")


    # Error of non-numeric types
    for i in weights:
        try:
            a = (float)(i)
        except ValueError:
            print("Please Enter a numeric type in weights")
            sys.exit()

    for i in impacts:
        if i == '+' or i== '-':
            continue
        else :
            print("Please Enter a '+' or '-' as an impact")
            sys.exit()


    # Handling all errors
            # Check for number of cols greater than equal to  3
    if cols <4 :
        print("Give a dataset with more columns")
        sys.exit()

    if  len(weights) != cols -1 :
        print("Number of Weights and columns don't match")
        sys.exit()

    if len(impacts) != cols -1:
        print("Number of impacts given don't match with number of columns")
        sys.exit()


    # Calculation of root mean square of all columns  and normalization of all rows
    Sum = []
    for i in data.columns[1:]:
        Sum.append(sum(data[i] * data[i]))

    Sum = np.array(Sum)
    rms = np.sqrt(Sum)

    for  index,col in enumerate(data.columns[1:]):
        data[col] = data[col] / rms[index]

    # Multiplying the weights to the data columns

    for index,col in enumerate(data.columns[1:]):
        data[col] = data[col] * (float)(weights[index])

    # Calculate Ideal Best and Ideal Worst
    IdealBest = []
    IdealWorst = []

    for index,col in enumerate(data.columns[1:]):
        if impacts[index] == '+':
            IdealBest.append(max(data[col]))
            IdealWorst.append(min(data[col]))
        if impacts[index] == '-':
            IdealBest.append(min(data[col]))
            IdealWorst.append(max(data[col]))


    # Calculate Eucledian distance from worst and negative as epos and eneg
    epos = []
    eneg = []

    for  i in range(row):
        valpos = 0
        valneg = 0
        for  index,col in enumerate(data.columns[1:]):
            valpos = valpos + (data.loc[i,col] - IdealBest[index])**2
            valneg = valneg + (data.loc[i,col] - IdealWorst[index])**2
        
        epos.append(math.sqrt(valpos))
        eneg.append(math.sqrt(valneg))

    # Calculate Performce Score
    Performance = []
    for i in range(row):
        Performance.append(round(eneg[i]/(epos[i]+eneg[i]),6))

    Rank = [ (int)(x) for x in pd.Series(Performance).rank(ascending=0) ] 
    data['Topsis Score'] = Performance
    data['Rank'] = Rank

    # Changing values of columns to previous
    for  index,col in enumerate(extra.columns[1:]):
        data[col] = extra[col]

    if output !=None:
        data.to_csv(output,index=False)

    return data




def main():
    ap = argparse.ArgumentParser(description='Calculate Rank of each row with TOPSIS')
    ap.add_argument('-f', '--filepath', type=str, required=True,  help='filepath of CSV file',dest='filepath')
    ap.add_argument('-i', '--impacts', type=str,  help="Imapact of each attribute Z('+', '-') of each column\n Default :'+,+,+,..'",dest= 'impacts')
    ap.add_argument('-w', '--Weights', type=str, help="Weights of each column of the given dataset \n Default: '1,1,1,1' ", dest= 'weights')
    ap.add_argument('-o', '--output', type=str, help='Name of file you want to enter results into', dest= 'output')

    args = ap.parse_args()
    try:
        data = pd.read_csv(args.filepath)
    except FileNotFoundError:
        print('file not present')
        sys.exit()

    dat = topsis(data, args.weights,args.impacts, args.output)
    print(dat)



if __name__ == '__main__':
    main()
