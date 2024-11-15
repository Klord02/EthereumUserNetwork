# How To Run

## Clone the Repository 
```bash
git clone https://github.com/Klord02/EthereumUserNetwork.git
```
It already contains all the required files such as the smart contracts and scripts to interact with the deployed contract. 

## Setup environment

1. Setup required conda environment using the following command: 
```bash
conda env create -f environment.yml
```

2. Download node, and npm

3. Download ganache GUI from their website and quickstart a workspace.

## Setup code files

### 1. If starting from scratch, create a new brownie project using the following commands
```bash
brownie init
```
**Note this is not required if cloned the repo**

### 2. Compile the samrt contract after making any changes in the solidity file.
```bash
brownie compile
```

### 3. Add the ganache-gui network to the list of networks
```bash
brownie networks add Ethereum ganache-local host=http://127.0.0.1:7545 chainid=5777
```

### 4. Run the script to interact with the deployed contract using the following command
```bash
brownie run .\scripts\combined_test.py --network ganache-local
```

**NOTE : Delete the `deployments` folder manually after making any changes (contract or new ganache workspace)**
