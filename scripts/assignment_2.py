import os
import shutil
import random
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from brownie import UserTransaction, accounts


def ClearCache():
    deployments_path = "./build/deployments/"
    exists = os.path.exists(deployments_path)
    if exists:
        print(exists)
        shutil.rmtree(deployments_path)
        os.makedirs(deployments_path, exist_ok=True)

def DeployContract():
    admin = accounts[0]
    print("admin address: ", admin)
    contract_address = UserTransaction.deploy({"from" : admin})
    print("Transaction address: ", contract_address)
    print("=================================================================")
    return UserTransaction.at(contract_address)

def CreatePowerLawNetwork(n, m):
    '''
    Using Barabasi Albert model to create Power Law ordered networks.
    Starting with m fully connected nodes add nodes one by one
    Each new node will make m edges with existing set of nodes
    such that probability of making connection depends on degree of node
    '''

    # Storing Edges as a list of tuples [(n1, n2), (n2, n3)]
    edges = []

    # Keeping track of degree of each node
    degree_dict = {}
    for i in range(n):
        degree_dict[i] = 0 # Initially degree for each node is 0 since nothing is connected

    # fully connect first m nodes
    for i in range(m):
        for j in range(i+1, m):
            edges.append((i,j))
        degree_dict[i] = m - 1 
    
    # Simulate nodes coming in one by one with mentioned property
    for i in range(m, n):
        # Create a list of existing node indices in which node index is repeated as many times as its degree
        if m==1 and i==1:
            choice_list = [0]
        else:
            choice_list = []
            for j in range(i-1):
                choice_list += [j] * degree_dict[j]
        
        # Randomly choose first m elements from choice list
        random.shuffle(choice_list)
        chosen_indices = choice_list[:m]

        # Connect the new node to the chosen nodes
        for j in chosen_indices:
            edges.append((i,j))
            degree_dict[i] += 1
            degree_dict[j] += 1
    
    # Save graph of index vs degree
    fig = plt.figure()
    plt.scatter(degree_dict.keys(), degree_dict.values())
    plt.title("Index vs Degree")
    plt.xlabel("Index")
    plt.ylabel("Degree")
    plt.savefig("./results/node_index_vs_degree.png", dpi=300, format='png') 
    plt.close(fig)
    
    # Save graph of degree vs P(degree)
    degree_freq = {}
    for i in range(n):
        degree = degree_dict[i]
        if degree not in degree_freq:
            degree_freq[degree] = 1
        else:
            degree_freq[degree] += 1

    degrees = np.array(list(degree_freq.keys()))
    degree_freq = np.array(list(degree_freq.values()))
    degree_prob = degree_freq / sum(degree_freq)

    fig = plt.figure()
    plt.scatter(degrees, degree_prob)
    plt.title("Degree vs P(Degree)")
    plt.xlabel("Degree")
    plt.ylabel("P(Degree)")
    plt.savefig("./results/degree_vs_proba.png", dpi=300, format='png') 
    plt.close(fig)

    return edges 

def CreateUsers(deployed_contract, n):
    # Create n users
    admin = accounts[0]
    for i in range(0, n):
        tx = deployed_contract.registerUser(i, f"User{i}",{"from": admin})
        tx.wait(1)
        tx = deployed_contract.addBalance(i, 50000) # Add a huge balance to allow many edges

    total_users = deployed_contract.total_users()
    print("Total Users:", total_users)

def CreateJointAccounts(deployed_contract, edges):
    '''
    If e is no. of edges then sample e balances from exponential distribution
    and create joint accounts using sampled balances distributed equally
    '''

    e = len(edges)
    balances = np.random.exponential(scale=10, size=e) # Mean 10
    print(balances)
    admin = accounts[0]

    for i, edge in enumerate(edges):
        (n1, n2) = edge

        try:
            tx = deployed_contract.createAcc(n1, n2, balances[i], 20,{"from": admin})
            tx.wait(1)
    
        except Exception as ex:
            print(f"i={n1}, j={n2}, e={ex}")

def TestTransactions(deployed_contract, n, t, every_k_transactions):
    '''
    For t transactions randomly pick any 2 out of 0 to n-1 indices and transfer money
    Keep track of ratio of successful transactions after every 100 iterations
    '''
    admin = accounts[0]
    success_ratios = []

    successes = 0
    for i in range(t):
        print("Transaction no. ", i+1)
        # Every k iterations reset counter and append success ratio
        if i!=0 and i % every_k_transactions == 0:
            success_ratios.append(float(successes/(i)))
            

        indices = random.sample(range(n), 2)
        sender = indices[0]
        reciever = indices[1]
        print(f"Sender: {sender}, Reciever: {reciever}")

        try:
            tx = deployed_contract.sendAmount(sender, reciever, 1, {"from": admin})
            tx.wait(1)
            successes += 1
            print("Successful")
        except Exception as ex:
            print("Failed: ", ex)

    # Save the graph of success ratios
    fig = plt.figure()
    plt.plot(list(range(len(success_ratios))), success_ratios)
    plt.title(f"Success Ratios every {every_k_transactions} transactions")
    plt.xlabel(f"transactions (in {every_k_transactions}s)")
    plt.ylabel("Success Ratio")
    plt.savefig("./results/success_ratios.png", dpi=300, format='png') 
    plt.close(fig)

def main():
    # Clear any cache of previous runs
    ClearCache()

    # Deploy the created smart contract
    deployed_contract = DeployContract()

    # Create 100 Users
    n = 100
    CreateUsers(deployed_contract, n)

    # Create power law network structure
    m = 2
    edges = CreatePowerLawNetwork(n, m)

    # Using the network structure created, create joint accounts and assign balances
    CreateJointAccounts(deployed_contract, edges)

    # Test Transactions
    transactions = 1001
    TestTransactions(deployed_contract, n, transactions, 100)
    

# if __name__ == "__main__":
#     edges = CreatePowerLawNetwork(100, 2)
#     print(len(edges))