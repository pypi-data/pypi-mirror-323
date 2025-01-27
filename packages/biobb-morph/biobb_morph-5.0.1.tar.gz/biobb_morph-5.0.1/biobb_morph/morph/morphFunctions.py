#!/usr/bin/python
# -*- coding: utf-8 -*-

#
#  ___  ___  ________     ___    ___ ___  ___  ________     ___    ___ ___    ___  _______  ________
# |\  \|\  \|\   __  \   |\  \  /  /|\  \|\  \|\   __  \   |\  \  /  /|\  \  /  /|/  ___  \|\_____  \
# \ \  \\\  \ \  \|\  \  \ \  \/  / | \  \\\  \ \  \|\  \  \ \  \/  / | \  \/  / /__/|_/  /\|____|\ /_
#  \ \   __  \ \   __  \  \ \    / / \ \   __  \ \   __  \  \ \    / / \ \    / /|__|//  / /     \|\  \
#   \ \  \ \  \ \  \ \  \  /     \/   \ \  \ \  \ \  \ \  \  /     \/   /     \/     /  /_/__   __\_\  \
#    \ \__\ \__\ \__\ \__\/  /\   \    \ \__\ \__\ \__\ \__\/  /\   \  /  /\   \    |\________\|\_______\
#     \|__|\|__|\|__|\|__/__/ /\ __\    \|__|\|__|\|__|\|__/__/ /\ __\/__/ /\ __\    \|_______|\|_______|
#                        |__|/ \|__|                       |__|/ \|__||__|/ \|__|
#          01001000 01100001 01111000 01001000 01100001 01111000 01111000 00110010 00110011
#

# ***************************************************************
# ******    Functions used in the main program morph.py    ******
# ******    auth: Estefano Muñoz-Moya                      ******
# ******    webPage: https://estefano23.github.io/         ******
# ******    github: estefano23                             ******
# ******    email: estefano.munoz.moya@gmail.com           ******
# ***************************************************************


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
# introduction
# ------------

# libraries
from __future__ import print_function

import csv
import itertools
import math
import os
import subprocess
from statistics import mean, median

import meshio  # type: ignore
import numpy as np

###

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
# define functions for rigid and non-rigid registrations

# Rigid


def defFuncRigid(
    targetFile, sourceFile, outPutFileName, nLoops, lenTarget, lenSource, bcpdCommand
):
    nLoops = str(nLoops)
    lenTarget = str(lenTarget)
    lenSource = str(lenSource)

    if int(lenTarget) == int(lenSource):
        funcBCPD = [
            bcpdCommand,
            "-x",
            targetFile,
            "-y",
            sourceFile,
            "-o",
            outPutFileName,
            "-l",
            "1e9",
            "-b",
            "2.0",
            "-w",
            "0.1",
            "-J",
            "300",
            "-K",
            "70",
            "-p",
            "-d",
            "5",
            "-e",
            "0.3",
            "-f",
            "0.3",
            "-g",
            "3",
            "-c",
            "1e-15",
            "-n",
            nLoops,
            "-ux",
            "-Db," + lenTarget + ",1",
            "-sY",
        ]
    else:
        funcBCPD = [
            bcpdCommand,
            "-x",
            targetFile,
            "-y",
            sourceFile,
            "-o",
            outPutFileName,
            "-l",
            "1e9",
            "-b",
            "2.0",
            "-w",
            "0.1",
            "-J",
            "300",
            "-K",
            "70",
            "-p",
            "-d",
            "5",
            "-e",
            "0.3",
            "-f",
            "0.3",
            "-g",
            "3",
            "-c",
            "1e-15",
            "-n",
            nLoops,
            "-ux",
            "-Dx," + lenTarget + ",1",
            "-Dy," + lenSource + ",1",
            "-sY",
        ]

    return funcBCPD


# non-Rigid
def defFuncNonRigid(
    targetFile,
    sourceFile,
    outPutFileName,
    lambdaVal,
    betaVal,
    nLoops,
    lenTarget,
    lenSource,
    bcpdCommand,
):
    lambdaVal = str(lambdaVal)
    betaVal = str(betaVal)
    nLoops = str(nLoops)
    lenTarget = str(lenTarget)
    lenSource = str(lenSource)

    if int(lenTarget) == int(lenSource):
        funcBCPD = [
            bcpdCommand,
            "-x",
            targetFile,
            "-y",
            sourceFile,
            "-o",
            outPutFileName,
            "-l",
            lambdaVal,
            "-b",
            betaVal,
            "-w",
            "0.0000001",
            "-J",
            "300",
            "-K",
            "70",
            "-p",
            "-d",
            "7",
            "-e",
            "0.15",
            "-f",
            "0.2",
            "-g",
            "0.1",
            "-c",
            "1e-15",
            "-n",
            nLoops,
            "-uy",
            "-Db," + lenTarget + ",1",
            "-sY",
        ]
    else:
        funcBCPD = [
            bcpdCommand,
            "-x",
            targetFile,
            "-y",
            sourceFile,
            "-o",
            outPutFileName,
            "-l",
            lambdaVal,
            "-b",
            betaVal,
            "-w",
            "0.0000001",
            "-J",
            "300",
            "-K",
            "70",
            "-p",
            "-d",
            "7",
            "-e",
            "0.15",
            "-f",
            "0.2",
            "-g",
            "0.1",
            "-c",
            "1e-15",
            "-n",
            nLoops,
            "-uy",
            "-Dx," + lenTarget + ",1",
            "-Dy," + lenSource + ",1",
            "-sY",
        ]

    return funcBCPD


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
# excecuting the BCPD registrations

# Rigid


def defRigid(nameMorph, numberIVD, patientID, funcRigid, outPutFileName, pathOut):
    print(
        "-------------------------------------------------------------------------------"
    )
    print("")
    print("Rigid registratio of the " + nameMorph + ": " + numberIVD + " " + patientID)
    print("")
    # print the bcpd function
    print(funcRigid)
    print("")
    morphingFunc = subprocess.run(funcRigid)
    print(
        "-------------------------------------------------------------------------------"
    )
    print(" ")
    # moving the temporal file to pathOut folder
    files = [
        filename for filename in os.listdir(".") if filename.startswith(outPutFileName)
    ]
    for filename in files:
        morphingFunc = subprocess.run(["mv", filename, pathOut])
    print("The rigid files of the " + nameMorph + " were move to: " + pathOut)
    print("")


# non-Rigid


def defNonRigid(nameMorph, numberIVD, patientID, funcNonRigid, outPutFileName, pathOut):
    print(
        "-------------------------------------------------------------------------------"
    )
    print("")
    print(
        "Non-Rigid registratio of the " + nameMorph + ": " + numberIVD + " " + patientID
    )
    print("")
    print(funcNonRigid)
    print("")
    morphingFunc = subprocess.run(funcNonRigid)
    print(
        "-------------------------------------------------------------------------------"
    )
    print(" ")
    # moving the temporal file to pathOut folder
    files = [
        filename for filename in os.listdir(".") if filename.startswith(outPutFileName)
    ]
    for filename in files:
        morphingFunc = subprocess.run(["mv", filename, pathOut])
    print("The " + nameMorph + " files were move to: " + pathOut)
    print("")


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
# obtaining the coordinates of the node 71143 from the morphed file without indexing


def ObtainCentroid(fileIn, pathIn, nodes, index):
    print(
        "-------------------------------------------------------------------------------"
    )
    print("Obtaining the coordinates of the node 71143 of the morphed model")
    print("")

    # index
    # entire mesh: 71143

    nodesCoord = dict()

    with open(os.path.join(pathIn, fileIn), "r") as f:
        reader = csv.reader(f, delimiter="\t")
        count = 0
        for row in reader:
            nodesCoord[nodes[count]] = row
            count += 1
    f.close()

    coordCentralNode = nodesCoord[index]

    return coordCentralNode


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
# creating inputs files (.inp)


def createInpFile(
    nameMorph,
    numberIVD,
    patientID,
    fileIn,
    fileOut,
    pathIn,
    pathOut,
    inpTemplatePath,
    nodes,
    stringFormat,
    coordCentralNode,
):
    print(
        "-------------------------------------------------------------------------------"
    )
    print(
        "Creating "
        + nameMorph
        + " model in a .inp file of "
        + numberIVD
        + " "
        + patientID
    )
    print("")

    nodesCoord = dict()

    with open(os.path.join(pathIn, fileIn), "r") as f:
        reader = csv.reader(f, delimiter="\t")
        count = 0
        for row in reader:
            nodesCoord[nodes[count]] = row
            count += 1
    f.close()

    # store the coordinates and the index in the dictionary nodesCoord and rest the value of coordCentralNode

    for key, value in nodesCoord.items():
        nodesCoord[key] = [
            float(value[0]) - float(coordCentralNode[0]),
            float(value[1]) - float(coordCentralNode[1]),
            float(value[2]) - float(coordCentralNode[2]),
        ]

    nodesOn3dFileOutPath = os.path.join(pathOut, fileOut)

    with open(nodesOn3dFileOutPath, "w") as filenodesOn3dOut:
        with open(inpTemplatePath) as f:
            lines = f.readlines()
        count = 1
        for line in lines:
            if count == 58:
                for inode in sorted(nodes):
                    filenodesOn3dOut.write(
                        stringFormat.format(inode, *nodesCoord[inode])
                    )
            filenodesOn3dOut.write(line)
            count += 1
    filenodesOn3dOut.close()


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Cheking failed elements in the final .inp file


def checkFailedElem(
    outPutFileFailedElem,
    outPutFileMorphedIVD,
    pathInp,
    pathTemplate,
    numberIVD,
    patientID,
    gap,
    abaqusCommand,
):
    print(
        "-------------------------------------------------------------------------------"
    )
    print("")
    print("Cheking if there are failed elements in " + numberIVD + " " + patientID)
    print("")
    cwd = os.getcwd()
    nodesOn3dFileOutPath = os.path.join(cwd, pathInp, outPutFileMorphedIVD)

    if abaqusCommand == "gmsh":
        lenFailedElem = check_zero_volume_elements_Gmesh(
            nodesOn3dFileOutPath, pathInp, pathTemplate
        )

    else:
        nameDic = list()
        name = outPutFileMorphedIVD.split(".")[0]
        nameDic.append(nodesOn3dFileOutPath)
        nameDic.append(name)
        nameDicFile = numberIVD + "_" + patientID + "_" + "nameDicFile.txt"

        lenFailedElem = int()

        with open(nameDicFile, "w") as filenameDicOut:
            for line in nameDic:
                filenameDicOut.write(line + "\n")
        filenameDicOut.close()

        # funcFailedElem = ['LANG=en_US.utf8 abaqus cae noGUI="failedElem.py"']
        funcFailedElem = [
            abaqusCommand,
            "cae",
            "noGUI={}".format(cwd + "/sources/functions/failedElem.py"),
            "--",
            nameDicFile,
        ]

        print(funcFailedElem)
        print("")
        morphingFunc = subprocess.run(funcFailedElem)
        print("")

        lenFailedElem = int()

        with open(nameDicFile, "r") as filenodesOn3dOut:
            for line in filenodesOn3dOut:
                lenFailedElem = int(line)

        morphingFunc = subprocess.run(["rm", nameDicFile])

    # file with the name of the inp file on the input folder that contains the number of failed elements and the gap value
    header = "NfailedElem, gap"

    with open(os.path.join(pathInp, outPutFileFailedElem), "w") as filenodesOn3dOut:
        filenodesOn3dOut.write(header + "\n")
        filenodesOn3dOut.write(str(lenFailedElem) + "," + str(gap))

    if lenFailedElem == 0:
        print("The .inp file doesn't have failed elements, it's ready to be simulated")

    elif lenFailedElem > 0:
        print("There are " + str(lenFailedElem) + " failed elements")
        print("the morphing process for the merged file need to be repeated")
    print("")

    return lenFailedElem


def check_zero_volume_elements_Gmesh(
    fileINP, pathInp, pathTemplate, volume_threshold=0.2e-1
):
    def calculate_tetrahedron_volume(p0, p1, p2, p3):
        """Calculate the volume of a tetrahedron given its four vertices."""
        mat = np.array([p1 - p0, p2 - p0, p3 - p0])
        return abs(np.linalg.det(mat)) / 6.0

    def calculate_hexahedron_volume(points):
        """Calculate the volume of a hexahedron by decomposing it into five tetrahedrons."""
        volume = (
            calculate_tetrahedron_volume(points[0], points[1], points[3], points[4])
            + calculate_tetrahedron_volume(points[1], points[2], points[3], points[6])
            + calculate_tetrahedron_volume(points[1], points[4], points[5], points[6])
            + calculate_tetrahedron_volume(points[3], points[4], points[6], points[7])
            + calculate_tetrahedron_volume(points[1], points[3], points[4], points[6])
        )
        return volume

    # Read the nodes from the .inp file
    nodesTot, nodeOrder = readCoordFromFile(fileINP, 57, 83538, ",")

    # read the correspondingNodesFebAbqs.txt file
    nodesFeb = dict()
    nodeOrder = list()
    with open(os.path.join(pathTemplate, "correspondingNodesFebAbqs.txt"), "r") as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            nodesFeb[int(row[0])] = nodesTot[int(row[1])]
            nodeOrder.append(int(row[0]))
        f.close()

    # get the name of the file without extension
    name = fileINP.split(".")[0]

    # Gmsh file
    gmshFile = os.path.join(pathInp, name + ".msh")

    # string format
    stringFormat = "{} {:.8f} {:.8f} {:.8f}"
    stringFormat += "\n"

    with open(gmshFile, "w") as filenodesOn3dOut:
        with open(os.path.join(pathTemplate, "template_L4-L5.msh")) as f:
            lines = f.readlines()
        count = 1
        for line in lines:
            if count == 6:
                for inode in sorted(nodeOrder):
                    filenodesOn3dOut.write(stringFormat.format(inode, *nodesFeb[inode]))
            filenodesOn3dOut.write(line)
            count += 1

    """Check for zero-volume elements in a .mesh file."""
    # Read the mesh file
    mesh = meshio.read(gmshFile)
    lenFailedElem = 0

    for cell_block in mesh.cells:
        if cell_block.type == "hexahedron":
            print("Hexahedron")
            for i, element in enumerate(cell_block.data):
                points = mesh.points[element]
                volume = calculate_hexahedron_volume(points)
                if volume < volume_threshold:
                    lenFailedElem += 1

        elif cell_block.type == "tetra":
            print("Tetrahedron")
            for i, element in enumerate(cell_block.data):
                p0, p1, p2, p3 = [mesh.points[node] for node in element]
                volume = calculate_tetrahedron_volume(p0, p1, p2, p3)
                if volume < volume_threshold:
                    lenFailedElem += 1

    if lenFailedElem == 0:
        print("No zero-volume elements found.")
    else:
        print(f"Found {lenFailedElem} zero-volume elements.")
    print("")

    return lenFailedElem


def readCoordFromFile(file, l1, l2, delM):
    # read the file .inp from the line l1 to the line l2
    # store the data in a dictionary called nodesTot
    # the dictionary is nodeId: [x, y, z]
    with open(file, "r") as f:
        reader = csv.reader(f, delimiter=delM)
        nodesTot = dict()
        nodeOrder = list()
        for row in itertools.islice(reader, l1, l2):
            nodesTot[int(row[0])] = [float(row[1]), float(row[2]), float(row[3])]
            nodeOrder.append(int(row[0]))
        f.close()

    return nodesTot, nodeOrder


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Cheking the accuracy of the morphing process
# Hausdorff distance between 3D grids (Euclidean distance)


def bbox(array, point, radius):
    a = array[
        np.where(
            np.logical_and(
                array[:, 0] >= point[0] - radius, array[:, 0] <= point[0] + radius
            )
        )
    ]
    b = a[
        np.where(
            np.logical_and(a[:, 1] >= point[1] - radius, a[:, 1] <= point[1] + radius)
        )
    ]
    c = b[
        np.where(
            np.logical_and(b[:, 2] >= point[2] - radius, b[:, 2] <= point[2] + radius)
        )
    ]
    return c


def hausdorff(surface_a, surface_b):
    # Taking two arrays as input file, the function is searching for the Hausdorff distane of "surface_a" to "surface_b"
    dists = []

    l = len(surface_a)
    print("the model has " + str(l) + " nodes")
    print("")
    try:
        # Python 2
        xrange
    except NameError:
        # Python 3, xrange is now named range
        xrange = range

    for i in xrange(l):
        # walking through all the points of surface_a
        dist_min = 1000.0
        radius = 0
        b_mod = np.empty(shape=(0, 0, 0))

        # increasing the cube size around the point until the cube contains at least 1 point
        while b_mod.shape[0] == 0:
            b_mod = bbox(surface_b, surface_a[i], radius)
            radius += 0.5

        # to avoid getting false result (point is close to the edge, but along an axis another one is closer),
        # increasing the size of the cube
        b_mod = bbox(surface_b, surface_a[i], radius * math.sqrt(3))

        for j in range(len(b_mod)):
            # walking through the small number of points to find the minimum distance
            dist = np.linalg.norm(surface_a[i] - b_mod[j])
            if dist_min > dist:
                dist_min = dist

        dists.append(dist_min)

        maxDist = np.max(dists)
        avg = mean(dists)
        meanVal = median(dists)

    return maxDist, avg, meanVal
