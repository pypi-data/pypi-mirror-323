# Topsis

TOPSIS is based on the fundamental premise that the best solution has the shortest distance from the positive-ideal solution, and the longest distance from the negative-ideal one. Alternatives are ranked with the use of an overall index calculated based on the distances from the ideal solutions.

It takes 4 arguments :
1.Data.csv file
2.Weights
3.Impacts
4.Result file

Returns file with Topsis Score and Rank

## How to use it?

Open terminal and type pip install Topsis-shreya-102203070

To get started quickly, just use the following:

from topis_pckg.topsis import topsis
topsis('inputfilename','Weights','Impacts','Outputfilename')
make ensure the weights and impacts should be in ""

eg: "1,1,1,1,1" and "+,-,+,-,+"
