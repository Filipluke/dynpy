# Introduction

It's a module that allows to enginering calculations on dynamical systems. 

There are four main parts of the entire project:

- dynamics module

- mechanical models - lead of development and maintenance: Amadeusz Radomski (@amvdek); Grzegorz Długopolski (@grzegorzdl);

- symbolic and numeric solvers for ODE systems;

- reporting module.

Using the code below in Jupyter enviroment on Ongoing Project we can learn more about how to and what to use Python in engineering calculations:

    from dynpy.utilities.documents.document import IntroToCocalcGuide, UsageOfDynamicSystemsGuide
    IntroToCocalcGuide();

Run this code in the blank Jupyter you have created.
After running it you will see the guide in Output, i.e. a CELL-by-CELL (step-by-step) procedure
Next for an example, run the codes below and you will see how it works:

    from sympy import Symbol
    from dynpy.models.mechanics.pendulum import Pendulum
    
    Pendulum().preview()

You can preview the pendulum using such a function.
