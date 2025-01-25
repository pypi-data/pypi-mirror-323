![wheel](https://img.shields.io/pypi/wheel/isingm?style=plastic)
![implementation](https://img.shields.io/pypi/implementation/isingm)
![python](https://img.shields.io/pypi/pyversions/isingm)
![downloads](https://img.shields.io/pypi/dm/isingm)

# Ising
A pythonic implementation of the Ising model.

Check the example for more.


## Lattice
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

## Methods

### randomize(self, ratio=0.5)
Randomize th lattice state with a given ratio of up state.

### arguments:

#### Optionnal:

- ##### ratio:

>   type: **float** in [0, ..., 1]
>
>   The ratio of up state.

### all(self, state)
Set all the lattice to the same state.

### arguments:

- ##### state:

>   type: **int** == -1 or 1
>
>   Value of the spin site.

### H(self)
Compute the Hamiltonian of the lattice.

### returns:

- ##### Hamiltonian

>   type: **float** 
>
>   Hamiltonian of the lattice.

### hamiltonian(self)
Compute the Halmitonian of each spin.

### returns:

- ##### local_Hamiltonian:

>   type: **numpy array** 
>
>   The Hamiltonian calculated for each spin.

### mH(self)
Compute the mean value of the Hamiltonian.

### returns:

- ##### <H>

>   type: **float** 
>
>   Mean value of the Hamiltonian.

### mag(self)
Compute the magnetization of the lattice.

### returns:

- ##### Magnetization

>   type: **float** 
>
>   Magnetization of the lattice.

### get_B(self)
Method to get the magnetic field.

### returns:

- ##### B:

>   type: **numpy array** 
>
>   Return the magnetic field.

### get_beta(self)
Method to get beta.

### returns:

- ##### beta:

>   type: **float** 
>
>   Return beta.

### get_shape(self)
Method to get the shape of the lattice

### returns:

- ##### shape:

>   type: **tuple(float)**
> 
>   Return the shape of the lattice

### get_size(self)
Method to get the size of the lattice

### returns:

- ##### size:

>   type: **float**
> 
>   Return the size of the lattice

### get_state(self)
Method to get the state of the lattice.

### returns:

- ##### state:

>   type: **numpy array** 
>
>   Return the copy of the state.


### set_B(self, B)
Method to set the magnetic field.

### arguments:

- ##### B:

>   type: **numpy array**
>
>   The new Magnetic field.

### set_beta(self, beta)
Method to set beta.

### arguments:

- ##### beta:

>   type: **float** 
>
>   The new beta.

### set_state(self, state)
Method to set the state of the lattice.

### arguments:

- ##### state:

>   type: **numpy array** 
>
>   The new state.





## Metropolis.algorithm
Is the class who solve the Ising model with the **Metropolis algorithm**

Implementation of the Metropolis algorithm

### arguments:

-   **for the arguments look the lattice class.**

## Methods

### step(self, n=0):

step apply the metropolis algorithm on n spin once

### arguments:

#### Optional:

- ##### n:

>   type: **int**
>
>   n must be strictly positive is the size of the sample 
