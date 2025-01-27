"""
This module contains the functions for the geometrical manipulation of vectors.
"""
import math
import numpy as np

def magnitude(vector):
    """
    Returns the magnitude of a vector.
    
    Parameters:
    vector (vector_3d): The vector to calcaute the magnitude of.

    Returns:
    float: The magnitude of the vector
    """

    return math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)


def unit(vector):
    """
    Returns a vector whose magnitude is 1 orientated to the input vector.
    
    Parameters:
    vector (vector_3d): The vector to derive the unit vector from.

    Returns:
    vector (vector_3d): The resultant unit vector.
    """

    unit_vec = np.array([vector[0] / magnitude(vector),
                        vector[1] / magnitude(vector),
                        vector[2] / magnitude(vector)]
                        )
    

    return unit_vec

def gram_schmit(vector_1, vector_2):
    """
    Creates an orthogonal vector to the first vector in a plane defined by both vectors.

    Parameters:
    vector_1 (vector_3d): The first vector defining the plane.
    vector_2 (vector_3d): The second vector defining the plane.

    Returns:
    vector (vector_3d): The resultant orthogonal vector.
    """

    return vector_2 - (np.dot(np.dot(vector_2,vector_1),vector_1))

def is_parallel(vector_1, vector_2):
    """
    Checks whether two vectors are parallel.

    Parameters:
    vector_1 (vector_3d): The first vector to compare.
    vector_2 (vector_3d): The second vector to compare.

    Returns:
    bool: 'true' if vectors are parallel and 'false' if
    vectors are not parallel.
    """
    return magnitude(np.cross(vector_1,vector_2)) == 0

def length(point_1, point_2):
    """
    Gets the length of a vector between two points.
    
    Parameters:
    point_1 (vector_3d): A vector representing a point to
                         calculate length from.
    point_2 (vector_3d): A vector representing a point to
                         calculate length to.

    Returns:
    float: The length of the line.
    
    """

    return math.sqrt((point_1[0] - point_2[0])**2
                     + (point_1[1] - point_2[1])**2
                     + (point_1[2] - point_2[2])**2
                     )

def unit_x():
    """
    Returns a unit vector oriented to the x-axis.
    
    Parameters:
    None

    Returns:
    A unit vector in aligned to the x-axis.    
    """

    return np.array([1,0,0])

def unit_y():
    """
    Returns a unit vector oriented to the y-axis.
    
    Parameters:
    None

    Returns:
    A unit vector in aligned to the y-axis.  
    """

    return np.array([0,1,0])

def unit_z():
    """
    Returns a unit vector oriented to the z-axis
    
    Parameters:
    None

    Returns:
    A unit vector in aligned to the z-axis. 
    """

    return np.array([0,0,1])
