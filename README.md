# ICM
## What is it?

`icm` provides python code for compiling a quantum circuit to a fault-tolerant version of the circuit, specifically [the ICM format](https://arxiv.org/abs/1509.02004). The ICM format consists of 3 layers of computation which together can represent any quantum circuit. 
1. Initialization - Here we initialize the qubit states we will need for our computation. Namely |0>, |+>, and magic states. 
2. CNOT - A series of CNOT gates that perform most of the computation
3. Measurement - Measuring in the Z or X eigenbases is used to implement single qubit gates in the sequence. 

In addition to the usual implementation of ICM, we have also implemented (*Faster manipulation of large quantum circuits using wire label reference diagrams*)[https://arxiv.org/abs/1811.06011] which cuts down on the number of gates added to the circuit when adding ancilla qubits. 

## How to Use?

First, install the package by navigating to the main directory in your terminal and running `pip install -e .`.

Circuits are provided to the compiler in the form of (Cirq)[https://quantumai.google/cirq] circuits and returns fault-tolerant implementations of that cirq circuit.

Simply call the `icm_converter` function with the circuit you want to put in ICM form and the list of gates that the circuit is composed of. You will then receive an equivalent circuit in ICM form.

## Development
To keep our repository clean and functional, we have implemented style checks and
tests. We expect that contributors will follow these standards when contributing.

### Installation
To make sure you have all the tools to run style checks, you should run
`pip install -e "[.dev]"` to make sure all those tools are installed. You might
also want to run `install pre-commit` to make sure that pre-commit checks are 
set up.

### Pre-commit
Pre-commit checks your code whenever you make a commit to make sure you are
following style rules. This makes sure all our commits are clean and functional.
