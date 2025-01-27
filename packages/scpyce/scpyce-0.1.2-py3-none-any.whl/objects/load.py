"""
Contains the object classes for point load objects of the structural model.
"""

import numpy as np
from objects import element # pylint: disable=import-error

class PointLoad:
    """
    Creates a point load object from a node defining the location and the 6 degrees
    of freedom representing the load applications.

    Parameters:
    node (node object): The node location of the load.
    fx (bool): The load value in the x direction.
    fy (bool): The load value in the y direction.
    fz (bool): The load values in the z direction.
    mx (bool): The moment load value about the x axis.
    my (bool): The moment load value about the y axis.
    mz (bool): The moment load value about the z axis.

    Returns:
    point load object: The defined point load object.
    """
    # pylint: disable=too-many-arguments
    # Eight is reasonable in this case.

    def __init__(self,
                 node : element.Node,
                 fx : float,
                 fy : float,
                 fz : float,
                 mx : float,
                 my : float,
                 mz : float
                 ):

        self.node = node
        self.fx = fx
        self.fy = fy
        self.fz = fz
        self.mx = mx
        self.my = my
        self.mz = mz

    def __str__(self):
        """
        Returns a string representing the object.
        
        Parameters: 
        None

        Returns:
        string: String object representing the load object.
        """

        output_string = []

        if abs(self.fx) > 0:
            output_string.append(f'Fx = {self.fx}kN')
        if abs(self.fy) > 0:
            output_string.append(f'Fy = {self.fy}kN')
        if abs(self.fz) > 0:
            output_string.append(f'Fz = {self.fz}kN')
        if abs(self.mx) > 0:
            output_string.append(f'Mx = {self.mx}kN')
        if abs(self.my) > 0:
            output_string.append(f'My = {self.my}kN')
        if abs(self.mz) > 0:
            output_string.append(f'Mz = {self.mz}kN')

        return '\n'.join(output_string)

    def __list__(self):
        """
        Returns an array with the object variables.
        
        Parameters: 
        None

        Returns:
        numpy array: Array object representing the load object.
        """

        return np.array([self.fx,
                         self.fy,
                         self.fz,
                         self.mx,
                         self.my,
                         self.mz])
