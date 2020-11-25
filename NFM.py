'''
Author information:
Joey R. Muffoletto
University of Texas at Austin
Autonomous Systems Group
jrmuff@utexas.edu
'''

import csv

with open('data/scn_UAM_testNewVT.trp', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)
