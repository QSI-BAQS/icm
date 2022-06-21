**Testing what gate decomposition that introduces ancillas would look like in Cirq**

For this the ICM form of circuits is being implemented.
*Fault-Tolerant High Level Quantum Circuits: Form, Compilation and Description*
https://arxiv.org/abs/1509.02004

The insertion of ancilla performs many updates on the subsequent gates 
from the circuit. Therefore, this code uses a `SplitQubit` as introduced in:
*Faster manipulation of large quantum circuits using wire label reference
diagrams* https://arxiv.org/abs/1811.06011

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
