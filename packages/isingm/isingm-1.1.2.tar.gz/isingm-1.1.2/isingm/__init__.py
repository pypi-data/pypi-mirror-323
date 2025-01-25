# coding:utf-8

"""
@author: Pacidus

A module for the Ising model
"""

__version__ = "1.1.2"

import numpy as np

# Aliases
__perm__ = np.random.permutation
__random__ = np.random.rand
# End Aliases

# Useful functions:
def __gen_adj__(dim):
    """
    Generates the simplest isotropic adjacency vector
    for a given dimension.

    ### arguments:

    - #### dim:

    >   type: **int** > 0
    >
    >   Is the dimension of the lattice.
    """
    adj = []
    Dim = range(dim)
    direction = range(2)

    for i in direction:
        for j in Dim:
            vec = [0] * dim
            vec[j] = i * 2 - 1
            adj.append(vec)
    return np.array(adj)


# End Useful fonctions


# lattice class
class lattice:
    """
    This is the main place of the Ising model,
    we have to initialize it with a tuple of the lattice shape that can be of any dimension or size.
    The lattice can be initialized with a random state (you can choose the state ratio up) or all in a state 1 or -1.

    ### arguments:

    - ##### shape:

    >   type: **tuple(int)**
    >
    >   The shape of the lattice is tested for 1 to 4 dimension.
    >   Every values of shape must be > 0 

    #### Optionnal:

    - ##### all:

    >    type: **int** == 1 or -1
    >
    >    Set the state at all 1 or -1 it overpass the r parrameter.

    - ##### r: 

    >   type: **float** in [0, ..., 1]
    >
    >  Set a random state with a ratio r of 1 in the lattice (default r = 0.5).

    - ##### adj: 

    >   type: **numpy.array**
    >
    >   A vector of vector: is the representation of the spin interaction.
    >
    >   |  0  |  J  |  0  |
    >   | --- | --- | --- |
    >   |**J**|**#**|**J**| 
    >   |**0**|**J**|**0**| 
    >
    >   Will be written as [[1,0],[-1,0],[0,1],[0,-1]]
    >   
    >   As default it's the left right up down direct neighbor matrix will be genereted (whatever this mean in 4 or more dimensions).

    - ##### J:

    >   type: **numpy.array** or **float**
    >
    >   Is the interraction between spins, 
    >   if J is an array he as to be the same length than adj.
    >
    >   (you can choose to make anisotropic iteractions !!)

    - ##### B:
    
    >   type: **numpy.array** or **float**
    >
    >   Is the magnetic field imposed on the lattice,
    >   if B is an array he as to have the same shape of the lattice

    - ##### beta:

    >   type: **float**
    >
    >   Beta is 1/(Kb * T) with T the absolute temp,
    >   and Kb is the Boltzmann constant.
    """

    # Private functions

    def __init__(self, shape, *args, **kwargs):
        """
        Initialisation of the class lattice.
        """

        # Init the private propriety of the lattice
        self.__dim__ = len(shape)
        self.__shape__ = shape
        self.__state__ = np.empty(shape)

        self.__size__ = self.__state__.size

        # Optional Parameters

        # set the state of the lattice
        if "all" in kwargs:
            self.all(kwargs["all"])
        elif "r" in kwargs:
            self.randomize(kwargs["r"])
        else:
            self.randomize()

        # set the adjacency vector
        if "adj" in kwargs:
            self.__adj__ = kwargs["adj"]
        else:
            self.__adj__ = __gen_adj__(self.__dim__)

        # set the iteraction values
        self.__J__ = np.ones(self.__adj__.shape[0])
        if "J" in kwargs:
            self.__J__ *= kwargs["J"]

        # set the values of the magnetic field
        self.__B__ = np.zeros(shape)
        if "B" in kwargs:
            self.__B__ += kwargs["B"]

        # set the beta values
        self.__beta__ = 1
        if "beta" in kwargs:
            self.__beta__ = kwargs["beta"]

    def __sum_adj__(self):
        """
        Sum the contributions of the "adjacent" part of the hamiltonian,
        for all the elements of the lattice.
        """
        # Aliases
        J = self.__J__
        adj = self.__adj__

        # set the itterator
        n, d = adj.shape
        dim = range(d)
        neigh = range(n)

        # init the sum
        Sum = np.zeros(self.__shape__)

        for a in neigh:  # For each adjacent
            roll = self.get_state()
            for j in dim:  # For each dimension
                roll = np.roll(roll, adj[a, j], axis=j)
            Sum += J[a] * roll

        return Sum

    def __eq__(self, value):
        """
        Define equality (useful for testing).
        """
        return self.__state__ == value

    # Public functions

    def randomize(self, ratio=0.5):
        """
        Randomize th lattice state with a given ratio of up state.

        ### arguments:

        #### Optionnal:
        
        - ##### ratio:

        >   type: **float** in [0, ..., 1]
        >
        >   The ratio of up state. 
        """

        # Aliases
        dim = range(self.__dim__)
        size = self.__size__
        state = self.__state__
        shape = self.__shape__
        closest_ratio = int(size * ratio)

        # set the random state
        state[...] = 1 - 2 * (__random__(*shape) > ratio)

        # correct the randomness to match the ratio
        val = closest_ratio - (self == 1).sum()
        if val != 0:
            flips = abs(val)
            sign = val / flips

            # Find the spin we have to flip
            mask = np.where(self == -sign)
            n = mask[0].size

            # choose witch ones where gonna flip
            choice = __perm__(n)[:flips]

            # construct the indices tuple
            indices = tuple([[mask[d][choice]] for d in dim])

            # and we flip them
            state[indices] = sign

    def all(self, state):
        """
        Set all the lattice to the same state.

        ### arguments:
        
        - ##### state:

        >   type: **int** == -1 or 1
        >
        >   Value of the spin site.
        """

        self.__state__[...] = state

    def mag(self):
        """
        Compute the magnetization of the lattice.

        ### returns:

        - ##### Magnetization
        
        >   type: **float** 
        >
        >   Magnetization of the lattice.
        """
        return self.__state__.mean()

    def hamiltonian(self):
        """
        Compute the Halmitonian of each spin.
        
        ### returns:

        - ##### local_Hamiltonian:
        
        >   type: **numpy array** 
        >
        >   The Hamiltonian calculated for each spin.
        """
        return -self.__state__ * (self.__sum_adj__() + self.__B__)

    def H(self):
        """
        Compute the Hamiltonian of the lattice.

        ### returns:

        - ##### Hamiltonian
        
        >   type: **float** 
        >
        >   Hamiltonian of the lattice.
        """
        return self.hamiltonian().sum()

    def mH(self):
        """
        Compute the mean value of the Hamiltonian.

        ### returns:

        - ##### <H>
        
        >   type: **float** 
        >
        >   Mean value of the Hamiltonian.
        """
        return self.hamiltonian().mean()

    # All the get fonction
    
    def get_shape(self):
        """
        Method to get the shape of the lattice
        
        ### returns:
        
        - ##### shape:
        
        >   type: **tuple(float)**
        > 
        >   Return the shape of the lattice
        """
        
        return self.__size__
    
    def get_size(self):
        """
        Method to get the size of the lattice
        
        ### returns:
        
        - ##### size:
        
        >   type: **float**
        > 
        >   Return the size of the lattice
        """
        
        return self.__size__

    def get_state(self):
        """
        Method to get the state of the lattice.

        ### returns:

        - ##### state:
        
        >   type: **numpy array** 
        >
        >   Return the copy of the state.
        """
        return self.__state__.copy()

    def get_beta(self):
        """
        Method to get beta.

        ### returns:

        - ##### beta:
        
        >   type: **float** 
        >
        >   Return beta.
        """
        return self.__beta__

    def get_B(self):
        """
        Method to get the magnetic field.

        ### returns:

        - ##### B:
        
        >   type: **numpy array** 
        >
        >   Return the magnetic field.
        """
        return self.__B__

    # All the set fonction

    def set_state(self, state):
        """
        Method to set the state of the lattice.

        ### arguments:

        - ##### state:
        
        >   type: **numpy array** 
        >
        >   The new state.
        """
        self.__state__ = state.copy()

    def set_beta(self, beta):
        """
        Method to set beta.

        ### arguments:

        - ##### beta:
        
        >   type: **float** 
        >
        >   The new beta.
        """
        self.__beta__ = beta

    def set_B(self, B):
        """
        Method to set the magnetic field.

        ### arguments:

        - ##### B:
        
        >   type: **numpy array**
        >
        >   The new Magnetic field.
        """
        self.__B__ = B
