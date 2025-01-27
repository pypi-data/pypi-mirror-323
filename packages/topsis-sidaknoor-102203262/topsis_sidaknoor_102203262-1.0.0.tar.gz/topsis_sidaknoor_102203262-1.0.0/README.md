# topsis-sidaknoor-102203262
It is a command line package that gives rank and score to a row based on value , weights and impacts given. It uses the TOPSIS( The Technique for Order of Preference by Similarity to Ideal Solution ) under the hood to do these calculations.

## Installation
```python
pip install -i https://test.pypi.org/simple/ topsis-sidak-102203262
```

## How to use it
Syntax :
 ```python
    topsis -f=[filepath] -w=[weights] -i=[impacts] -o=[output]
```
### Arguments
1.  filepath : str  : a file containing data on which you want to perform topsis. This should include first column as a string column while others as numeric values only.

2. weights : str : Importance you want to give to each feature. Note should be a numeric values seperated by a comma(","). By default , weights="1,1,1,...."

3. impacts : str : Sign given regarding if you want more or less of feature. Should be '+' or '-' separated by a comma(","). By default , impacts="+,+,+,..."

4. output : str : A filename in str if you want result to be saved in working directory. If not passed , by default None.

Returns:  A pd.DataFrame with original values plus two columns of Topsis Score and Rank

# LICENSE
This repository is licensed under MIT LICENSE.
See LICENSE for more info. 