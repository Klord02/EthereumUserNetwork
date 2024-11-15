// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UserTransaction {

    uint public total_users;

    struct user {
        uint user_id;
        string user_name;
        uint user_balance;
        bool exists;
    }

    struct joint_account {
        mapping(uint => uint) balances;
        bool exists;
    }

    mapping(uint => user) public users;
    mapping(uint => mapping(uint => joint_account)) public joint_accounts;
    mapping(uint => uint[]) public network; 

    event debug1(string str1, uint uid);

    function getJointAccountBalances(uint u1, uint u2) public view returns (uint[] memory, uint[] memory) {
        uint id1 = u1 < u2 ? u1 : u2;
        uint id2 = u1 < u2 ? u2 : u1;

        require(joint_accounts[id1][id2].exists, "Joint account does not exist");

        uint[] memory tokenIds = new uint[](2);
        uint[] memory balances = new uint[](2);

        tokenIds[0] = id1;
        tokenIds[1] = id2;

        for (uint i = 0; i < tokenIds.length; i++) {
            balances[i] = joint_accounts[id1][id2].balances[tokenIds[i]];
        }

        return (tokenIds, balances);
    }

    function registerUser(uint user_id, string memory user_name) public {
        emit debug1("USER REGISTERED : ", user_id);
        require(! users[user_id].exists, "user already exists");
        users[user_id] = user(user_id, user_name, 0, true);
        total_users = total_users + 1;

    }

    function addBalance(uint user_id, uint balance) public {
        
        require(users[user_id].exists, "user does not exist");
        users[user_id].user_balance += balance;
    }

    function createAcc(uint u1, uint u2, uint bal1, uint bal2) public {

        require(u1 != u2, "user cannot create account with themselves");

        uint id1 = u1 < u2 ? u1 : u2;
        uint id2 = u1 < u2 ? u2 : u1;

        require(users[u1].exists, "user does not exist");
        require(users[u2].exists, "user does not exist");

        require(users[u1].user_balance >= bal1, "user has insufficient balance");
        require(users[u2].user_balance >= bal2, "user has insufficient balance");

        require(! joint_accounts[id1][id2].exists, "joint account already exists");

        network[u1].push(u2);
        network[u2].push(u1);

        joint_accounts[id1][id2].exists = true;
        joint_accounts[id1][id2].balances[id1] = bal1;
        joint_accounts[id1][id2].balances[id2] = bal2;

        users[u1].user_balance -= bal1;
        users[u2].user_balance -= bal2;
    }

    function findPath(uint sender, uint recipient, uint amount) public view returns (uint[] memory) {
        uint n = total_users;

        // Track visited nodes and store parent information for path reconstruction
        bool[] memory visited = new bool[](n);
        uint[] memory parent = new uint[](n);

        // Initialize parent array with a marker value for "no parent"
        for (uint i = 0; i < n; i++) {
            parent[i] = n; // Using `n` as a marker for nodes with no parent
        }

        // Use a dynamic queue array for flexibility
        uint[] memory queue = new uint[](n);
        uint head = 0;
        uint tail = 0;

        // Enqueue sender and mark it as visited
        queue[tail++] = sender;
        visited[sender] = true;

        // BFS loop
        while (head < tail) {
            uint curr = queue[head++]; // Dequeue

            // If we've reached the recipient, break out of the loop
            if (curr == recipient) {
                break;
            }

            // Explore neighbors of the current node
            for (uint i = 0; i < network[curr].length; i++) {
                uint neighbor = network[curr][i];
                // emit debug1("current user id : ", curr, "neighbor : ", neighbor);

                // Arrange IDs for joint account lookup between `curr` and `neighbor`
                uint id1 = curr < neighbor ? curr : neighbor;
                uint id2 = curr < neighbor ? neighbor : curr;

                // Check joint account existence, balance, and if neighbor is unvisited
                if (
                    joint_accounts[id1][id2].exists &&
                    joint_accounts[id1][id2].balances[curr] >= amount &&
                    !visited[neighbor]
                ) {
                    queue[tail++] = neighbor; // Enqueue neighbor
                    visited[neighbor] = true;
                    parent[neighbor] = curr; // Track the path
                }
            }
        }

        // If recipient was never reached, return an empty array
        if (!visited[recipient]) {
            return new uint[](0);  
        }

        // Calculate path length for initializing the result array
        uint pathLength = 1;
        for (uint p = recipient; p != sender; p = parent[p]) {
            pathLength++;
        }

        // Construct the path array in reverse order
        uint[] memory path = new uint[](pathLength);
        uint index = pathLength - 1;
        for (uint p = recipient; p != sender; p = parent[p]) {
            path[index--] = p;
        }
        path[0] = sender;

        return path;
    }


    function sendAmount(uint sender, uint recipient, uint amount) public {
        uint[] memory path = findPath(sender, recipient, amount);

        require(path.length > 0, "No valid path found");

        uint currentBalance = amount;

        for (uint i = 0; i < path.length - 1; i++) {
            uint node1 = path[i];
            uint node2 = path[i + 1];

            uint id1 = node1 < node2 ? node1 : node2;
            uint id2 = node1 < node2 ? node2 : node1;

            // require(joint_accounts[id1][id2].balances[node1] >= currentBalance, "Insufficient balance in joint account");

            joint_accounts[id1][id2].balances[node1] -= currentBalance;
            joint_accounts[id1][id2].balances[node2] += currentBalance;
        }

        // uint lastNode = path[path.length - 1];

        // require(joint_accounts[lastNode][recipient].balances[lastNode] >= currentBalance, "Insufficient balance for recipient");

        // joint_accounts[lastNode][recipient].balances[lastNode] -= currentBalance;
        // joint_accounts[lastNode][recipient].balances[recipient] += currentBalance;
    }

    function closeAccount(uint u1, uint u2) public {
        require(users[u1].exists, "User 1 does not exist");
        require(users[u2].exists, "User 2 does not exist");

        uint id1 = u1 < u2 ? u1 : u2;
        uint id2 = u1 < u2 ? u2 : u1;

        require(joint_accounts[id1][id2].exists, "Joint account does not exist");

        uint balance1 = joint_accounts[id1][id2].balances[id1];
        uint balance2 = joint_accounts[id1][id2].balances[id2];

        joint_accounts[u1][u2].exists = false;
        joint_accounts[u1][u2].balances[u1] = 0;
        joint_accounts[u1][u2].balances[u2] = 0;

        users[id1].user_balance += balance1;
        users[id2].user_balance += balance2;
    }
}