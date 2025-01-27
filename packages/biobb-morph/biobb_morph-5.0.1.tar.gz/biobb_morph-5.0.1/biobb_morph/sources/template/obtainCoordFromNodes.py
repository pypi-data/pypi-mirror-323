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

#********************************************************************
#******    Obtain coordinates from nodes                       ******
#******    auth: Estefano Muñoz-Moya                           ******
#******    webPage: https://estefano23.github.io/              ******
#******    github: estefano23                                  ******
#******    email: estefano.munoz.moya@gmail.com                ******
#********************************************************************


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
# introduction
# ------------

#libraries
from __future__ import print_function
import numpy as np
###

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------
# code
#-----------------

coordFile = 'L4-L5_shell_coords.txt'
nodesFile = 'nodesCEPupper_down.txt'
newFile = 'templateCEPupper_down.txt'

# read the file coordFile
# extract the coordinates of the nodes: id, x, y, z
# the values are separated by commas
coord = dict()
with open(coordFile, 'r') as f:
    for line in f:
        if line.startswith('#'):
            continue
        else:
            line = line.split(',')
            coord[int(line[0])] = [float(line[1]), float(line[2]), float(line[3])]
        
# read the nodesFile and extract the nodes
nodes = list()
with open(nodesFile, 'r') as f:
    for line in f:
        if line.startswith('#'):
            continue
        else:
            line = line.split()
            nodes.append(int(line[0]))
            
# create the newFile with the coordinates of the nodes
# the id is in nodes
# the coordinates are in coord
# the format is: id, x, y, z
# separated by commas
with open(newFile, 'w') as f:
    for inode, node in enumerate(nodes):
        f.write(str(node) + ',' + str(coord[node][0]) + ',' + str(coord[node][1]) + ',' + str(coord[node][2]) + '\n')
