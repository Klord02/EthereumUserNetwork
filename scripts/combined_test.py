print("Importing...")
import os
import shutil
from brownie import UserTransaction, accounts
print("Imported")

def main():
    deployments_path = "./build/deployments/"
    exists = os.path.exists(deployments_path)
    if exists:
        print(exists)
        shutil.rmtree(deployments_path)
        os.makedirs(deployments_path, exist_ok=True)

    admin = accounts[0]
    print("admin address: ", admin)
    contract_address = UserTransaction.deploy({"from" : admin})
    print("Transaction address: ", contract_address)

    print("=================================================================")
    
    # Fetch the deployed contract
    deployed_contract = UserTransaction.at(contract_address)

    # Create 10 users
    for i in range(0, 10):
        tx = deployed_contract.registerUser(i, f"User{i}",{"from": admin})
        tx.wait(1)

        events = tx.events
        if "debug1" in events:
            emitted_event = events["debug1"]
            print(f"Event for User {i}: {emitted_event}")
        else:
            print(f"No debug1 event for User {i}")

        tx = deployed_contract.addBalance(i, 500)

    total_users = deployed_contract.total_users()
    print("Total Users:", total_users)
    
    print("=================================================================")

    # Create joint accounts
    # for i in range(0, 10):
    #     for j in range(0,10):
    #         try:
    #             tx = deployed_contract.createAcc(i, j, 20, 20,{"from": admin})
    #             tx.wait(1)

    #             (tokens, balances) = deployed_contract.getJointAccountBalances(i, j)
    #             print(f"Tokens: {tokens}, balances: {balances}")
                
    #         except Exception as e:
    #             print(f"i={i}, j={j}, e={e}")
    
    # Create accounts manually
    tx = deployed_contract.createAcc(0, 1, 20, 20,{"from": admin})
    tx.wait(1)
    (tokens, balances) = deployed_contract.getJointAccountBalances(0, 1)
    print(f"Tokens: {tokens}, balances: {balances}")
    
    tx = deployed_contract.createAcc(1, 2, 5, 20,{"from": admin})
    tx.wait(1)
    (tokens, balances) = deployed_contract.getJointAccountBalances(1, 2)
    print(f"Tokens: {tokens}, balances: {balances}")

    tx = deployed_contract.createAcc(1, 3, 15, 20,{"from": admin})
    tx.wait(1)
    (tokens, balances) = deployed_contract.getJointAccountBalances(1, 3)
    print(f"Tokens: {tokens}, balances: {balances}")

    tx = deployed_contract.createAcc(2, 4, 10, 20,{"from": admin})
    tx.wait(1)
    (tokens, balances) = deployed_contract.getJointAccountBalances(2, 4)
    print(f"Tokens: {tokens}, balances: {balances}")

    tx = deployed_contract.createAcc(3, 4, 10, 20,{"from": admin})
    tx.wait(1)
    (tokens, balances) = deployed_contract.getJointAccountBalances(3, 4)
    print(f"Tokens: {tokens}, balances: {balances}")

    print("=================================================================")

    # Check BFS path
    sender = 0
    recipient = 4
    amount = 10

    path = deployed_contract.findPath(sender, recipient, amount)
    print(f"Path from {sender} to {recipient}: {path}")

    print("=================================================================")

    sender = 0
    recipient = 4
    amount = 10

    tx = deployed_contract.sendAmount(sender, recipient, amount, {"from": admin})
    tx.wait(1)
    print(f"Amount sent from {sender} to {recipient}")
    
    for i in range(len(path)-1):
        u1 = path[i]
        u2 = path[i+1]
        
        (tokens, balances) = deployed_contract.getJointAccountBalances(u1, u2)
        print(f"Tokens: {tokens}, balances: {balances}")