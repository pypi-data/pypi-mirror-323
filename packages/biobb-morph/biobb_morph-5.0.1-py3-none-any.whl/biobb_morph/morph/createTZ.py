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

import copy
import csv
import os
import pathlib

import numpy as np
import numpy.linalg as la
import trimesh
from matplotlib.path import Path
from scipy.interpolate import splev, splprep
from scipy.spatial import ConvexHull
from stl import mesh

###


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------
def read_stl(file_path):
    # Load the STL file and return the mesh
    return mesh.Mesh.from_file(file_path)


def move_mesh(mesh, movement):
    # Move the mesh in the z-axis by the step amount
    mesh.vectors += np.array(movement)


def count_unique_vertices(mesh):
    # Reshape the vectors to a 2D array where each row is a vertex
    all_vertices = mesh.vectors.reshape(-1, 3)
    # Find the unique rows (vertices) and count them
    unique_vertices = np.unique(all_vertices, axis=0)
    return unique_vertices.shape[0]


def check_nodes_inside(inner_mesh, outer_mesh):
    # Create the faces array for inner and outer meshes.
    # Each face is a set of three consecutive integers because each set of three vertices form a triangle in the STL file.
    inner_faces = np.arange(inner_mesh.vectors.shape[0]) * 3
    inner_faces = np.column_stack((inner_faces, inner_faces + 1, inner_faces + 2))

    outer_faces = np.arange(outer_mesh.vectors.shape[0]) * 3
    outer_faces = np.column_stack((outer_faces, outer_faces + 1, outer_faces + 2))

    # Create trimesh objects for both meshes
    trimesh_inner = trimesh.Trimesh(
        vertices=inner_mesh.vectors.reshape(-1, 3), faces=inner_faces
    )
    trimesh_outer = trimesh.Trimesh(
        vertices=outer_mesh.vectors.reshape(-1, 3), faces=outer_faces
    )

    # Get the signed distances of all inner mesh vertices to the outer mesh surface
    signed_distances = trimesh_outer.nearest.signed_distance(trimesh_inner.vertices)

    # Count the number of vertices inside the outer mesh (positive signed distance)
    number_nodes_inside_count = np.sum(signed_distances > 0)

    # coordinates of the nodes inner mesh outside the outer mesh
    nodes_inside = trimesh_inner.vertices[signed_distances > 0]

    return number_nodes_inside_count, nodes_inside


def get_nodes(mesh):
    # Flatten the mesh.vectors to get a 2D array of nodes [n, 3]
    nodes = mesh.vectors.reshape(-1, 3)
    # Use np.unique to remove duplicates and return the unique nodes
    unique_nodes = np.unique(nodes, axis=0)
    return unique_nodes.tolist()


def project_onto_stlSurface(nodes, mesh_stl_file):
    # Load the STL file
    mesh = trimesh.load(mesh_stl_file)

    # Create an empty list to hold the projected points
    projected_points = []

    # For each node, find the nearest point on the mesh surface
    for node in nodes:
        point, _, _ = trimesh.proximity.closest_point(mesh, [node])
        projected_points.append(point[0])

    return projected_points


def project_onto_stlSurface_direction(nodes, mesh_stl_file, direction):
    # Load the STL file
    mesh = trimesh.load(mesh_stl_file)

    # Normalize the direction vector
    direction = np.array(direction)
    direction_norm = direction / np.linalg.norm(direction)

    # Create an empty list to hold the projected points
    projected_points = []

    # For each node, project along the given direction and find the intersection with the mesh
    for node in nodes:
        # Ray origin
        origin = np.array(node)
        # Ray direction, normalized
        vector = direction_norm

        # Perform ray-mesh intersection query
        locations, index_ray, index_tri = mesh.ray.intersects_location(
            ray_origins=[origin], ray_directions=[vector]
        )

        if len(locations) > 0:
            # If there are intersections, choose the closest point
            closest_point = locations[0]
            projected_points.append(closest_point)
        else:
            # If no intersection is found, add None or keep the original point (based on your use case)
            projected_points.append(
                None
            )  # or `projected_points.append(node)` to keep original

    return projected_points


def project_onto_plane(nodes, centroid, plane):
    # The plane is (example): [1, 1, 0] xy plane
    # centroid [x, y, z] is the centroid (list of one coordinate) of the nodes where plane is based
    # The nodes are a list of coordinates
    # The function returns the projected points

    # Check if plane as two 1s and one 0
    if plane.count(1) != 2 or plane.count(0) != 1:
        raise ValueError("The plane must have two 1s and one 0")

    # the plane lives in the coordinates where the 1s, [1, 1, 0] xy plane
    # [0, 1, 1] yz plane
    # [1, 0, 1] xz plane

    # Create an empty list to hold the projected points
    projected_points = list()

    for node in nodes:
        if plane[2] == 0:
            projected_points.append([node[0], node[1], centroid[2]])
        elif plane[0] == 0:
            projected_points.append([centroid[0], node[1], node[2]])
        else:
            projected_points.append([node[0], centroid[1], node[2]])

    return projected_points


# Function to calculate the distance between two points
def point_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def resamplePoints(points, distance):
    """
    Resample a list of points to be approximately `distance` apart.

    :param points: A list of points (list of lists or 2D numpy array).
    :param distance: The distance at which to resample the points.
    :return: A list of resampled points.
    """

    # Transform the list of points to a 2D numpy array if it's not already
    if isinstance(points, list):
        points = np.array(points)

    # Resample points to be approximately `distance` apart
    resampled_points = [points[0]]
    for p in points[1:]:
        if point_distance(p, resampled_points[-1]) >= distance:
            resampled_points.append(p)

    return resampled_points


# Function to fit a spline to the points and resample it at a specified distance
def getContoursOfNodes(points, distance):
    # Transform the list of points to a 2D numpy array if is not already
    if isinstance(points, list):
        points = np.array(points)

    # Calculate the Convex Hull of the points
    hull = ConvexHull(points)
    hull_points = points[hull.vertices]

    # Close the loop
    hull_points = np.append(hull_points, [hull_points[0]], axis=0)

    # Fit a spline to the contour of the Convex Hull
    tck, u = splprep([hull_points[:, 0], hull_points[:, 1]], s=0, per=1)

    # Evaluate the spline over a dense range to get a smooth curve
    new_points_dense = splev(np.linspace(0, 1, 1000), tck)
    new_points_dense = np.column_stack(new_points_dense)

    # Resample points to be approximately `distance` apart
    resampled_points = resamplePoints(new_points_dense, distance)

    return resampled_points


def move_to_closest(contour_points, cloud_points):
    """
    For each point in contour_points, find the closest point in cloud_points
    and move the contour point to the position of the closest cloud point.

    :param contour_points: A list of lists representing the contour points.
    :param cloud_points: A list of lists representing the cloud points.
    :return: A list of lists representing the adjusted contour points.
    """
    # Convert lists to numpy arrays for efficient computation
    contour_points = np.array(contour_points)
    cloud_points = np.array(cloud_points)

    # Function to calculate the Euclidean distance between two points
    def euclidean_distance(point1, point2):
        return np.sqrt(np.sum((point1 - point2) ** 2))

    # Function to find the closest point in the cloud to a given contour point
    def find_closest_point(contour_point, cloud_points):
        distances = np.sqrt(((cloud_points - contour_point) ** 2).sum(axis=1))
        closest_point_index = np.argmin(distances)
        return cloud_points[closest_point_index]

    # Adjust each contour point to the position of the closest cloud point
    adjusted_contour_points = [
        find_closest_point(point, cloud_points) for point in contour_points
    ]

    return adjusted_contour_points


def splineLine_and_resample(points, distance):
    """
    Fit a spline to the given points and resample it at a specified distance.

    :param points: A list of points (list of lists or 2D numpy array).
    :param distance: The distance at which to resample the spline.
    :return: A list of resampled points along the spline.
    """

    # remove duplicates
    points = remove_duplicates(points)

    # Transform the list of points to a 2D numpy array if it's not already
    if isinstance(points, list):
        points = np.array(points)

    # Fit a spline to the contour
    tck, u = splprep([points[:, 0], points[:, 1]], s=0, per=1)

    # Evaluate the spline over a dense range to get a smooth curve
    new_points_dense = splev(np.linspace(0, 1, 1000), tck)
    new_points_dense = np.column_stack(new_points_dense)

    # Resample points to be approximately `distance` apart
    resampled_points = resamplePoints(new_points_dense, distance)

    return resampled_points


def create_filtered_stl(mesh_file, filteredCoord, output_file):
    # Load the original mesh
    original_mesh = mesh.Mesh.from_file(mesh_file)

    # Convert mesh coordinates to a 2D numpy array
    all_coords_array = np.array(original_mesh.vectors).reshape(-1, 3).round(decimals=6)

    # Obtain the filtered indices
    filtered_indices = []
    for fc in filteredCoord:
        fc_rounded = np.round(fc, decimals=6)
        indices = np.where((all_coords_array == fc_rounded).all(axis=1))[0]
        filtered_indices.extend(indices)

    # Find faces that contain the filtered nodes
    filtered_faces = []
    for i in range(len(original_mesh.vectors)):
        if any(
            np.isin(original_mesh.vectors[i].reshape(-1, 3), filteredCoord).all(axis=1)
        ):
            filtered_faces.append(i)

    # Create the submesh
    submesh_faces = original_mesh.vectors[filtered_faces]
    submesh = mesh.Mesh(np.zeros(submesh_faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(submesh_faces):
        submesh.vectors[i] = f

    # Save the submesh
    submesh.save(output_file)


def find_perimeter_nodes(mesh_file):
    # Load the mesh
    my_mesh = mesh.Mesh.from_file(mesh_file)

    # Create a dictionary to count edge occurrences
    edge_dict = {}

    # Iterate through each face and process its edges
    for face in my_mesh.vectors:
        for i in range(3):
            # Create an edge as a tuple of vertex indices, sorted
            edge = tuple(sorted([tuple(face[i]), tuple(face[(i + 1) % 3])]))

            # Count occurrences of the edge
            if edge in edge_dict:
                edge_dict[edge] += 1
            else:
                edge_dict[edge] = 1

    # Extract unique edges (those that occur only once)
    unique_edges = [edge for edge, count in edge_dict.items() if count == 1]

    # Extract nodes from these unique edges
    perimeter_nodes = np.unique(
        [node for edge in unique_edges for node in edge], axis=0
    )

    return perimeter_nodes


def find_centroid(nodes):
    # Convert the list of nodes to a 2D numpy array if is not already
    if isinstance(nodes, list):
        nodes = np.array(nodes)

    # Calculate the centroid
    centroid = np.mean(nodes, axis=0)

    # convert to list
    centroid = centroid.tolist()

    return centroid


def find_closest_node_to_centroid_in_stl(stl_file):
    # Load the mesh from the STL file
    my_mesh = mesh.Mesh.from_file(stl_file)

    # Extract the nodes (vertices) from the mesh
    # my_mesh.vectors is a 3D array: [faces, vertices, coordinates]
    nodes = np.unique(my_mesh.vectors.reshape(-1, 3), axis=0)

    # Calculate the centroid
    centroid = find_centroid(nodes)

    # convert centroid to numpy array
    centroid = np.array(centroid)

    # Find the node closest to the centroid
    distances = np.linalg.norm(nodes - centroid, axis=1)
    closest_node_index = np.argmin(distances)
    closest_node = nodes[closest_node_index]

    return closest_node


def get_representative_normal(stl_file):
    # Load the mesh from the STL file
    my_mesh = mesh.Mesh.from_file(stl_file)

    # Normalize the normals to unit vectors
    normals = my_mesh.normals
    norms = np.linalg.norm(normals, axis=1)
    unit_normals = normals / norms[:, np.newaxis]

    # Calculate the representative normal as the average of the unit normals
    representative_normal = np.mean(unit_normals, axis=0)
    norm = np.linalg.norm(representative_normal)
    if norm != 0:
        representative_normal /= norm  # Normalize the representative normal

    return representative_normal


def rotation_matrix_from_vectors(vec1, vec2):
    """Find the rotation matrix that aligns vec1 to vec2
    :param vec1: A 3d "source" vector
    :param vec2: A 3d "destination" vector
    :return mat: A transform matrix (3x3) which when applied to vec1, aligns it with vec2.
    """
    a, b = (
        (vec1 / np.linalg.norm(vec1)).reshape(3),
        (vec2 / np.linalg.norm(vec2)).reshape(3),
    )
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s**2))
    return rotation_matrix


def count_matching_coordinates_and_remove_matches(list1, list2):
    # Function to round only the z coordinate to a specified number of decimal places
    def round_z(coord, decimals):
        x, y, z = coord
        return (x, y, round(z, decimals))

    # Convert list1 to a set of tuples with z coordinate rounded for efficient lookup
    list1_set = set(round_z(coord, 0) for coord in list1)

    # Count how many coordinates in list1 (with rounded z) are present in list2
    match_count = sum(1 for coord in list2 if round_z(coord, 0) in list1_set)

    # Create a new list from list2 without the coordinates found in list1
    list2_without_matches = [
        coord for coord in list2 if round_z(coord, 0) not in list1_set
    ]

    return list2_without_matches, match_count


def remove_duplicates(lst):
    # transform it into a list if is not
    if isinstance(lst, np.ndarray):
        lst = lst.tolist()

    seen = set()
    new_lst = []
    for item in lst:
        item_tuple = tuple(item)  # Convert sublist to tuple for hashability
        if item_tuple not in seen:
            seen.add(item_tuple)
            new_lst.append(item)
    return new_lst


def remove_points_inside_contour(points, contour):
    # Create a Path object from the contour
    path = Path(contour)

    # Convert points to a Nx2 numpy array if it's not already in that form
    points_array = np.array(points)

    # Use the contains_points method to test which points are inside the contour
    mask = path.contains_points(points_array)

    # Get the indices of points that are outside the contour
    outside_indices = np.where(~mask)[0]

    # Get the inside indices
    inside_indices = np.where(mask)[0]

    # Get the points that are outside the contour using the indices
    outside_points = points_array[outside_indices]

    return outside_points.tolist(), outside_indices.tolist(), inside_indices.tolist()


def procedure(
    nodeDistance, moveTo, fileAF, fileNP, movement, nodesAF, nodesNP, contourNP, plane
):
    # read the meshes to be edited
    meshAF = read_stl(fileAF)  # The larger mesh (pink)
    meshNP = read_stl(fileNP)  # The smaller mesh (blue)

    # get the nodes of the two meshes
    temp_nodesAF = get_nodes(meshAF)

    # create a list with the nodes of the top and bottom of the NP
    nodesNP_top = list()

    # count the number of nodes in the NP mesh
    numberNodesNP = count_unique_vertices(meshNP)  # Number of nodes in the smaller mesh

    # ----------------------------------------------------------------------------------
    # Superior-Inferior movement
    print(
        "Starting the projection of the contour of the NP to the surface of the NP and the AF"
    )
    print(
        "------------------------------------------------------------------------------------"
    )
    print("")

    # Obtain the unitary vector of movement
    movement_unitary = np.array(movement) / la.norm(movement)

    print(
        "The contour of the NP is projected to the surface of the NP and the AF in the direction of the movement"
    )
    print("direction of the movement: ", movement_unitary)
    print("")

    # proyect the contourNP to the surface of the meshAF in the direction of the movement
    contourNP_projected_AF = project_onto_stlSurface_direction(
        contourNP, fileAF, movement_unitary
    )
    # proyect the contourNP to the surface of the meshNP in the direction of the movement
    contourNP_projected_NP = project_onto_stlSurface_direction(
        contourNP, fileNP, movement_unitary
    )

    # calculate the nodes between contourNP and contourNP_projected_AF that should be separated by a distance of nodeDistance
    nodes_between = list()

    for start, end in zip(contourNP_projected_NP, contourNP_projected_AF):
        # Calculate the total distance between the start and end points
        total_distance = la.norm(end - start)

        # Calculate the number of intervals
        num_intervals = np.floor(total_distance / nodeDistance).astype(int)

        # Generate the nodes
        if num_intervals > 0:
            # The +1 accounts for the fact that linspace includes both start and end points
            intermediate_nodes = np.linspace(
                start, end, num=num_intervals + 1, endpoint=True
            )

            # Exclude the start and end nodes and add each node to the list
            for node in intermediate_nodes[1:-1]:
                nodes_between.append(node)

    # project the nodesAF to the plane, considering centroid [0, 0, 0]
    nodesAF_projected = project_onto_plane(nodesAF, [0, 0, 0], plane)
    # project the nodesNP to the plane, considering centroid [0, 0, 0]
    nodesNP_projected = project_onto_plane(nodesNP, [0, 0, 0], plane)

    # check the index of the plane that is 0
    index = plane.index(0)

    # remove the index from the nodesAF_projected
    for node in nodesAF_projected:
        del node[index]
    # remove the index from the nodesNP_projected
    for node in nodesNP_projected:
        del node[index]

    # create a contourNP_plane
    contourNP_plane = copy.deepcopy(contourNP)
    for node in contourNP_plane:
        del node[index]

    # remove the nodesAF_projected that are inside the contourNP
    nodesAF_projected, index_outside_AF, index_inside_AF = remove_points_inside_contour(
        nodesAF_projected, contourNP_plane
    )
    # remove the nodesNP_projected that are inside the contourNP
    nodesNP_projected, index_outside_NP, index_inside_NP = remove_points_inside_contour(
        nodesNP_projected, contourNP_plane
    )

    # Find the centroid of the contourNP
    centroid_contourNP = find_centroid(contourNP)

    # move centroid_contourNP to [0, 0, 0] aswell the nodesAF and nodesNP
    nodesAF = np.array(nodesAF)
    nodesAF = nodesAF - centroid_contourNP
    nodesAF = nodesAF.tolist()
    nodesNP = np.array(nodesNP)
    nodesNP = nodesNP - centroid_contourNP
    nodesNP = nodesNP.tolist()

    # remove from index_inside the indices of nodesAF ones that are in the direction of the movement separated by variable plane
    nodesNP_top = list()
    for node_index, node in enumerate(nodesAF):
        # Only proceed if the index is in index_outside
        # delete the index of the node in index_inside, only if it's also in index_inside
        side = np.dot(node, movement_unitary)
        if side < 0 and node_index in index_inside_AF:
            index_inside_AF.remove(node_index)
        elif side > 0 and node_index in index_inside_AF:
            nodesNP_top.append(node)

    # do the same for the nodesNP
    for node_index, node in enumerate(nodesNP):
        # Only proceed if the index is in index_outside
        # delete the index of the node in index_inside, only if it's also in index_inside
        side = np.dot(node, movement_unitary)
        if side < 0 and node_index in index_inside_NP:
            index_inside_NP.remove(node_index)

    # remove from nodesAF the nodes with the index_inside
    nodesAF = [i for j, i in enumerate(nodesAF) if j not in index_inside_AF]

    # remove from nodesNP the nodes with the index_inside
    nodesNP = [i for j, i in enumerate(nodesNP) if j not in index_inside_NP]

    # return the centroid_contourNP to the original position
    nodesAF = np.array(nodesAF)
    nodesAF = nodesAF + centroid_contourNP
    nodesAF = nodesAF.tolist()
    nodesNP = np.array(nodesNP)
    nodesNP = nodesNP + centroid_contourNP
    nodesNP = nodesNP.tolist()
    nodesNP_top = np.array(nodesNP_top)
    nodesNP_top = nodesNP_top + centroid_contourNP
    nodesNP_top = nodesNP_top.tolist()

    # add to nodesNP the nodes_between
    nodesNP.extend(nodes_between)

    # remove duplicates for the three lists
    nodesAF = remove_duplicates(nodesAF)
    nodesNP = remove_duplicates(nodesNP)

    # # plot the contourNP and the contourNP_projected_AF, and the nodes_between, and the nodesAF
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection="3d")
    # ax.scatter(*zip(*contourNP), color='r')
    # ax.scatter(*zip(*contourNP_projected_AF), color="b")
    # ax.scatter(*zip(*nodes_between), color="g")
    # ax.scatter(*zip(*nodesAF), color="m")
    # ax.scatter(*zip(*nodesNP_top), color="y")
    # ax.scatter(*zip(*nodesNP), color="c")
    # plt.show()

    # get the closest node to the centroid of the top NP
    closest_node = find_centroid(nodesNP_top)
    # into numpy array
    closest_node = np.array(closest_node)

    # get the vector that translate the closest node to the point moveTo
    moveVec = moveTo - closest_node

    print("Representative Normal and the closest node to the centroid of the top NP")
    print("closest_node: ", closest_node)
    print("Vector that translate the closest node to the point moveTo")
    print("moveVec: ", moveVec)
    print("")

    return (
        nodesAF,
        nodesNP,
        nodesNP_top,
        nodes_between,
        moveVec,
        closest_node,
    )


def mainProgramTZ(fileIn, nodeDistance, moveTo, movement, plane, reduce_param):
    # read the fileIn
    # first line is fileAF and second line is fileNP
    with open(fileIn, "r") as f:
        fileAF = f.readline().strip()
        fileNP = f.readline().strip()

    # check the path of fileIn using os.path
    pathFiles = os.path.dirname(fileIn)

    # add the path to the files
    fileAF = os.path.join(pathFiles, fileAF)
    fileNP = os.path.join(pathFiles, fileNP)

    print("fileAF: ", fileAF)

    filenameAF = str(pathlib.Path(fileAF).stem)
    print("filenameAF: ", filenameAF)
    filenameNP = str(pathlib.Path(fileNP).stem)

    # get the numberIVD
    numberIVD = filenameAF.split("_")[1]

    # get the patient
    patient = filenameAF.split("_")[3]

    # read the meshes to be edited
    meshAF = read_stl(fileAF)  # The larger mesh (pink)
    meshNP = read_stl(fileNP)  # The smaller mesh (blue)

    # count the number of nodes in the two meshes
    numbertemp_nodesAF = count_unique_vertices(
        meshAF
    )  # Number of nodes in the larger mesh
    numberNodesNP = count_unique_vertices(meshNP)  # Number of nodes in the smaller mesh

    # to print in terminal
    # program presentation with argparse selections
    print("")
    print("")
    print("                              Create Transition Zone of the IVD")
    print("                              ---------------------------------")
    print("")

    print(f"AF: {filenameAF}")
    print(f"NP: {filenameNP}")
    print(f"The movement of the outer mesh is {movement}")
    print(f"Distance between two nodes of the mesh: {nodeDistance}")
    print(f"Translation of the AF and NP: {moveTo}")
    print(f"Number of nodes in the NP: {numberNodesNP}")
    print(f"Number of nodes in the AF: {numbertemp_nodesAF}")
    print("")

    nodesAF = get_nodes(meshAF)
    nodesNP = get_nodes(meshNP)

    # create a list with the nodes of the top and bottom NP
    nodesNP_top = list()
    nodesNP_bottom = list()

    # Project the nodes of the NP to the plane
    # nodesNP to a list
    centroid_NP = find_centroid(nodesNP)

    # project the NP points to the plane
    projected_point_NP = project_onto_plane(nodesNP, centroid_NP, plane)

    # create a list only with the components with 1s in the plane for the projected_point_NP
    projected_point_NP_2D = list()

    for node in projected_point_NP:
        if plane[2] == 0:
            projected_point_NP_2D.append([node[0], node[1]])
        elif plane[0] == 0:
            projected_point_NP_2D.append([node[1], node[2]])
        else:
            projected_point_NP_2D.append([node[0], node[2]])

    # Create a contour of the projected points
    contourNP = getContoursOfNodes(projected_point_NP_2D, nodeDistance)

    # move the countourNP to closest node in projected_point_NP to increase the accuracy
    contourNP = move_to_closest(contourNP, projected_point_NP_2D)

    # Now create a spline line of the contourNP and resample it at a specified distance to increase the accuracy
    contourNP = splineLine_and_resample(contourNP, nodeDistance)

    # Find the centroid of the contourNP
    centroid_contourNP = find_centroid(contourNP)

    # create a temporary copy of the contourNP
    contourNP_temp = copy.deepcopy(contourNP)

    # reduce the size of the contourNP by 0.7, considering the centroid as the center
    contourNP = np.array(contourNP)
    contourNP = (contourNP - centroid_contourNP) * reduce_param + centroid_contourNP

    # resample the contourNP at a specified distance
    contourNP = resamplePoints(contourNP, nodeDistance)

    # pass from 2D to 3D, using the z coordinate of the centroid of the NP
    contourNP = [[x, y, centroid_NP[2]] for x, y in contourNP]

    print("Contour of the NP was created to create the transition zone")
    print("Space between the nodes of the contour: ", nodeDistance)
    print("Reduce the size of the contour by: ", reduce_param)
    print("")

    # # Plot 3D and 2D if needed
    # # plot the projected points_NP (list of coordintes)
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection="3d")
    # ax.scatter(*zip(*projected_point_NP), color='r')
    # ax.scatter(*zip(*nodesNP), color="b")
    # # plot the centroid
    # ax.scatter(*centroid_NP, color="m")
    # plt.show()

    # # plot a new 2D figure of projected_point_NP_2D
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # ax.scatter(*zip(*projected_point_NP_2D), color='r')
    # # add the contour as points
    # ax.scatter(*zip(*contourNP), color="b")
    # # plot the centroid
    # ax.scatter(*centroid_contourNP, color="m")
    # plt.show()

    # make the values in movement positive and then negative
    movement = [abs(i) for i in movement]

    # try to complete this function, if not, reduce_param =+ -0.1
    success = False
    while not success:
        try:
            (
                nodesAF,
                nodesNP,
                nodesNP_bottom,
                nodes_between,
                moveVec,
                closest_node,
            ) = procedure(
                nodeDistance,
                moveTo,
                fileAF,
                fileNP,
                movement,
                nodesAF,
                nodesNP,
                contourNP,
                plane,
            )

            success = True  # If procedure() completes without raising an exception

        except:
            reduce_param -= 0.1

            print("**EXCEPTION**")
            print("The reduce_param was reduced by 0.1")
            print("reduce_param: ", reduce_param)
            print("")

            # reduce the size of the contourNP by 0.7, considering the centroid as the center
            contourNP = np.array(contourNP_temp)
            contourNP = (
                contourNP - centroid_contourNP
            ) * reduce_param + centroid_contourNP

            # resample the contourNP at a specified distance
            contourNP = resamplePoints(contourNP, nodeDistance)

            # pass from 2D to 3D, using the z coordinate of the centroid of the NP
            contourNP = [[x, y, centroid_NP[2]] for x, y in contourNP]

            (
                nodesAF,
                nodesNP,
                nodesNP_bottom,
                nodes_between,
                moveVec,
                closest_node,
            ) = procedure(
                nodeDistance,
                moveTo,
                fileAF,
                fileNP,
                movement,
                nodesAF,
                nodesNP,
                contourNP,
                plane,
            )

            success = True  # If procedure() completes without raising an exception

    # After the loop
    if success:
        print("Procedure completed successfully.")
        print(
            "---------------------------------------------------------------------------------------------------------------------------------------------"
        )
        print("")
    else:
        print("Unable to complete the procedure after adjustments.")
        print(
            "---------------------------------------------------------------------------------------------------------------------------------------------"
        )
        print("")

    # make the values in movement negative
    movement = [-i for i in movement]

    success = False
    while not success:
        try:
            (
                nodesAF,
                nodesNP,
                nodesNP_top,
                nodes_between,
                moveVec2,
                closest_node2,
            ) = procedure(
                nodeDistance,
                moveTo,
                fileAF,
                fileNP,
                movement,
                nodesAF,
                nodesNP,
                contourNP,
                plane,
            )

            success = True  # If procedure() completes without raising an exception

        except:
            reduce_param -= 0.1

            print("**EXCEPTION**")
            print("The reduce_param was reduced by 0.1")
            print("reduce_param: ", reduce_param)
            print("")

            # reduce the size of the contourNP by 0.7, considering the centroid as the center
            contourNP = np.array(contourNP_temp)
            contourNP = (
                contourNP - centroid_contourNP
            ) * reduce_param + centroid_contourNP

            # resample the contourNP at a specified distance
            contourNP = resamplePoints(contourNP, nodeDistance)

            # pass from 2D to 3D, using the z coordinate of the centroid of the NP
            contourNP = [[x, y, centroid_NP[2]] for x, y in contourNP]

            (
                nodesAF,
                nodesNP,
                nodesNP_top,
                nodes_between,
                moveVec2,
                closest_node2,
            ) = procedure(
                nodeDistance,
                moveTo,
                fileAF,
                fileNP,
                movement,
                nodesAF,
                nodesNP,
                contourNP,
                plane,
            )

            success = True  # If procedure() completes without raising an exception

    # After the loop
    if success:
        print("Procedure completed successfully.")
        print(
            "---------------------------------------------------------------------------------------------------------------------------------------------"
        )
        print("")
    else:
        print("Unable to complete the procedure after adjustments.")
        print(
            "---------------------------------------------------------------------------------------------------------------------------------------------"
        )
        print("")

    # Create nodesTZ
    nodesTZ = copy.deepcopy(nodesNP)

    # create the final nodesNP --> nodesTZ + nodesNP_top + nodesNP_bottom
    # add nodesNP_top
    nodesNP.extend(nodesNP_top)
    # add nodesNP_bottom
    nodesNP.extend(nodesNP_bottom)

    # add to nodesAF the nodesTZ
    nodesAF.extend(nodesTZ)

    # create nodes for toRigid
    nodesToRid = nodesAF.copy()
    # add nodesNP_top
    nodesToRid.extend(nodesNP_top)
    # add nodesNP_bottom
    nodesToRid.extend(nodesNP_bottom)

    # remove duplicates for the three lists
    nodesAF = remove_duplicates(nodesAF)
    nodesNP = remove_duplicates(nodesNP)
    nodesToRid = remove_duplicates(nodesToRid)

    # to numpy
    nodesAF = np.array(nodesAF)
    nodesNP = np.array(nodesNP)
    nodesToRid = np.array(nodesToRid)

    # translate the nodesAF, nodesNP, and nodesToRid with moveVec
    nodesAF = nodesAF + moveVec
    nodesNP = nodesNP + moveVec
    nodesToRid = nodesToRid + moveVec

    # convert the nodesAF, nodesNP, and nodesToRid to list
    nodesAF = nodesAF.tolist()
    nodesNP = nodesNP.tolist()
    nodesToRid = nodesToRid.tolist()

    # # plot the contourNP and the contourNP_projected_AF, and the nodes_between, and the nodesAF
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection="3d")
    # ax.scatter(*zip(*nodesAF), color="m")
    # ax.scatter(*zip(*nodesNP), color="c")
    # plt.show()

    # create a txt with the coordinates of the nodes of the two meshes, separated by a comma: csv
    # names
    fileAF_out = "IVD_" + numberIVD + "_nodesOnSurface_AF_" + patient + ".txt"
    fileNP_out = "IVD_" + numberIVD + "_nodesOnSurface_NP_" + patient + ".txt"
    fileToRid_out = "IVD_" + numberIVD + "_nodesOnSurface_toRigid_" + patient + ".txt"
    fileInfo = "IVD_" + numberIVD + "_info_" + patient + ".txt"

    # Create the folder to save the files called results if it does not exist
    resultPath = "textToBcpd"
    if not os.path.exists(resultPath):
        os.makedirs(resultPath)

    print("resultPath: ", resultPath)
    print("fileAF_out: ", fileAF_out)

    # x,y,z
    with open(os.path.join(resultPath, fileAF_out), "w") as f:
        writer = csv.writer(f)
        writer.writerows(nodesAF)
    with open(os.path.join(resultPath, fileNP_out), "w") as f:
        writer = csv.writer(f)
        writer.writerows(nodesNP)
    with open(os.path.join(resultPath, fileToRid_out), "w") as f:
        writer = csv.writer(f)
        writer.writerows(nodesToRid)

    # write the info file with the names of the files
    # fileAF_out
    # fileNP_out
    # fileToRid_out
    with open(os.path.join(resultPath, fileInfo), "w") as f:
        f.write(fileAF_out + "\n")
        f.write(fileNP_out + "\n")
        f.write(fileToRid_out + "\n")

    # The new FileIn
    fileIn = os.path.join(resultPath, fileInfo)

    return fileIn
