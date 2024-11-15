# How To Run

Clone the Repository on you local. It already contains all the required files such as the smart contracts and scripts to interact with the deployed contract. 

## Setup environment

1. Setup required conda environment using the following command: 
```bash
conda create environment.yml
```

2. Download node, npm and install ganache cli using them.

3. Download ganache GUI from their website and quickstart a workspace.

## Setup code files

1. Create a new brownie project using the following commands
```bash
brownie init
```

2. Compile the samrt contract after making any changes in the solidity file.
```bash
brownie compile
```

3. Add the ganache-gui network to the list of networks
```bash
bro
```

4. Run the script to interact with the deployed contract using the following command
```bash
brownie run .\scripts\combined_test.py --network ganache-local
```

**NOTE : Delete the `deployments` folder manually after making any changes (contract or new ganache workspace)**
