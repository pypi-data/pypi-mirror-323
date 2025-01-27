#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 ___  ___  ________     ___    ___ ___  ___  ________     ___    ___ ___    ___  _______  ________
|\  \|\  \|\   __  \   |\  \  /  /|\  \|\  \|\   __  \   |\  \  /  /|\  \  /  /|/  ___  \|\_____  \
\ \  \\\  \ \  \|\  \  \ \  \/  / | \  \\\  \ \  \|\  \  \ \  \/  / | \  \/  / /__/|_/  /\|____|\ /_
 \ \   __  \ \   __  \  \ \    / / \ \   __  \ \   __  \  \ \    / / \ \    / /|__|//  / /     \|\  \
  \ \  \ \  \ \  \ \  \  /     \/   \ \  \ \  \ \  \ \  \  /     \/   /     \/     /  /_/__   __\_\  \
   \ \__\ \__\ \__\ \__\/  /\   \    \ \__\ \__\ \__\ \__\/  /\   \  /  /\   \    |\________\|\_______\
    \|__|\|__|\|__|\|__/__/ /\ __\    \|__|\|__|\|__|\|__/__/ /\ __\/__/ /\ __\    \|_______|\|_______|
                       |__|/ \|__|                       |__|/ \|__||__|/ \|__|


"""

#*************************************************************************************************
#******    Program that move the central point (id=71143) to coordinates (0,0,0)            ******
#******    auth: Estefano Muñoz-Moya                                                        ******
#******    webPage: https://estefano23.github.io/                                           ******
#******    github: estefano23                                                               ******
#******    email: estefano.munoz.moya@gmail.com                                             ******
#*************************************************************************************************


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
# introduction
# ------------

#libraries
from __future__ import print_function
import os
import argparse
import csv
import numpy as np
###

# read the file L4-L5_noBEP.txt that contains four columns, the id and the x,y,z values. Save it in a dictionary
nodes = dict()
with open('L4-L5_noBEP.txt', 'r') as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        nodes[int(row[0])] = [float(row[1]), float(row[2]), float(row[3])]

# take the node 71143 and move it to the (0,0,0) coordinates, and translate the other nodes
centralNode = nodes[71143]
for key in nodes:
    nodes[key] = [nodes[key][0] - centralNode[0], nodes[key][1] - centralNode[1], nodes[key][2] - centralNode[2]]

# save the new coordinates in a new file
stringFormat = '{},{:.8f},{:.8f},{:.8f}'
stringFormat += '\n'

with open('L4-L5_noBEP_corrected.txt', 'w') as f:
    for key in nodes:
        f.write(stringFormat.format(key, nodes[key][0], nodes[key][1], nodes[key][2]))

# save the same file, but without the index
stringFormat = '{:.8f},{:.8f},{:.8f}'
stringFormat += '\n'
with open('L4-L5_noBEP_noIndex_corrected.txt', 'w') as f:
    for key in nodes:
        f.write(stringFormat.format(nodes[key][0], nodes[key][1], nodes[key][2]))

# read the file AFTemplate.txt and save the first column in a list
with open('AFTemplate.txt', 'r') as f:
    reader = csv.reader(f, delimiter=',')
    templateAF = list()
    for row in reader:
        templateAF.append(int(row[0]))

# do the same with the file NPTemplate.txt
with open('NPTemplate.txt', 'r') as f:
    reader = csv.reader(f, delimiter=',')
    templateNP = list()
    for row in reader:
        templateNP.append(int(row[0]))

# save the new coordinates in a new file
stringFormat = '{},{:.8f},{:.8f},{:.8f}'
stringFormat += '\n'

with open('AF_noBEP_corrected.txt', 'w') as f:
    for key in templateAF:
        f.write(stringFormat.format(
            key, nodes[key][0], nodes[key][1], nodes[key][2]))

with open('NP_noBEP_corrected.txt', 'w') as f:
    for key in templateNP:
        f.write(stringFormat.format(
            key, nodes[key][0], nodes[key][1], nodes[key][2]))

# save the same file, but without the index
stringFormat = '{:.8f},{:.8f},{:.8f}'
stringFormat += '\n'
with open('AF_noBEP_noIndex_corrected.txt', 'w') as f:
    for key in templateAF:
        f.write(stringFormat.format(nodes[key][0], nodes[key][1], nodes[key][2]))

with open('NP_noBEP_noIndex_corrected.txt', 'w') as f:
    for key in templateNP:
        f.write(stringFormat.format(nodes[key][0], nodes[key][1], nodes[key][2]))

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
# read the file AFTemplateWCEP.txt and save the first column in a list
with open('AFTemplateWCEP.txt', 'r') as f:
    reader = csv.reader(f, delimiter=',')
    templateAF = list()
    for row in reader:
        templateAF.append(int(row[0]))

# do the same with the file NPTemplate.txt
with open('NPTemplateWCEP.txt', 'r') as f:
    reader = csv.reader(f, delimiter=',')
    templateNP = list()
    for row in reader:
        templateNP.append(int(row[0]))

# save the new coordinates in a new file
stringFormat = '{},{:.8f},{:.8f},{:.8f}'
stringFormat += '\n'

with open('AFWCEP_noBEP_corrected.txt', 'w') as f:
    for key in templateAF:
        f.write(stringFormat.format(
            key, nodes[key][0], nodes[key][1], nodes[key][2]))

with open('NPWCEP_noBEP_corrected.txt', 'w') as f:
    for key in templateNP:
        f.write(stringFormat.format(
            key, nodes[key][0], nodes[key][1], nodes[key][2]))

# save the same file, but without the index
stringFormat = '{:.8f},{:.8f},{:.8f}'
stringFormat += '\n'
with open('AFWCEP_noBEP_noIndex_corrected.txt', 'w') as f:
    for key in templateAF:
        f.write(stringFormat.format(
            nodes[key][0], nodes[key][1], nodes[key][2]))

with open('NPWCEP_noBEP_noIndex_corrected.txt', 'w') as f:
    for key in templateNP:
        f.write(stringFormat.format(
            nodes[key][0], nodes[key][1], nodes[key][2]))
