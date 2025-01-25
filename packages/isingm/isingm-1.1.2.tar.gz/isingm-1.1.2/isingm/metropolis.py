# coding:utf-8

"""
@author: Pacidus

A module for the metropolis algorithm
"""

from isingm import lattice
import numpy as np

# Aliases
__perm__ = np.random.permutation
__random__ = np.random.rand
# End Aliases

# algorithm class
class algorithm(lattice):
    """
    Implementation of the Metropolis algorithm

    ### arguments:
    
    -   **for the arguments look the lattice class.**
    """

    def __init__(self, shape, *args, **kwargs):
        """
        Initialisation of the class algorithm
        """
        super().__init__(shape, *args, **kwargs)

        self.__On__ = 1 + int(self.__size__ * 0.01)

    def __sac__(self, choice):
        """
        Sum Adjacents Choice contribution of the hamiltionian

        ### arguments:

        - ##### choice:

        >   type: **tuple(numpy.array)**
        >
        >   is tuple of the coordinates of the spin chosen
        """

        # Aliases
        J = self.__J__
        n = choice[0].size
        adj = self.__adj__
        state = self.get_state()
        shape = self.__shape__
        a, d = adj.shape
        dim = range(d)
        nei = range(a)

        Sum = np.zeros(n)
        for j in nei:
            roll = choice[:]
            roll = tuple([(roll[k] + adj[j, k]) % shape[k] for k in dim])
            Sum += J[j] * state[roll]

        return Sum

    def __DH__(self, choice):
        """
        Compute the delta in energy for a set of spin flip 

        ### arguments:

        - ##### choice:

        >   type: **tuple(numpy.array)**
        >
        >   is tuple of the coordinates of the spin chosen
        """

        # Aliases
        B = self.__B__
        state = self.__state__
        sumadj = self.__sac__

        return 2 * state[choice] * (sumadj(choice) + B[choice])

    def __Ptrans__(self, choice):
        """
        Return the proba of transition

        ### arguments:

        - ##### choice:

        >   type: **tuple(numpy.array(int))**
        >
        >   is tuple of the coordinates of the spin chosen
        """

        # Aliases
        DH = self.__DH__(choice)

        # if the energy gap is negative set the proba to 1
        mask = DH <= 0
        DH[mask] = 0

        return np.exp(-self.__beta__ * DH)

    def step(self, n=0):
        """
        step apply the metropolis algorithm on n spin once


        ### arguments:

        #### Optional:
        
        - ##### n:

        >   type: **int**
        >
        >   n must be strictly positive is the size of the sample 
        """
        # Aliases
        size = self.__size__
        state = self.__state__
        shape = self.__shape__
        Ptrans = self.__Ptrans__

        if n <= 0:
            n = self.__On__

        # permute the indices of the lattice
        N = __perm__(size)[:n]

        # we convert the indices into coordinates
        choice = tuple()
        for i in shape:
            size /= i
            N1 = N % size
            choice += (((N - N1) / size).astype(int),)
            N = N1

        # we apply metropolis algorithm
        state[choice] *= 1 - 2 * (__random__(n) <= Ptrans(choice))
