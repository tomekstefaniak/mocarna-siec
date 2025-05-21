
import networkx as nx
import numpy as np
import random
from tabulate import tabulate

def create_network():
    G = nx.Graph()
    G.add_nodes_from(range(1, 21))
    ring_edges = [(i, i+1) for i in range(1, 20)] + [(20, 1)]
    G.add_edges_from(ring_edges)
    additional_edges = [
        (1, 11), (2, 12), (3, 13), (4, 14), (5, 15),
        (6, 16), (7, 17), (8, 18), (9, 19)
    ]

    G.add_edges_from(additional_edges)

    for u, v in G.edges:
        if (u, v) in ring_edges or (v, u) in ring_edges:
            G.edges[u, v]['capacity'] = 200000000
        else:
            G.edges[u, v]['capacity'] = 300000000
        G.edges[u, v]['actual_flow'] = 0

    N = np.zeros((20, 20), dtype=int)

    for i in range(20):
        for j in range(20):
            if i != j:
                N[i][j] = random.randint(100, 1000)
            else:
                N[i][j] = 0
    
    return G, N

def calculate_actual_flow(G, N):
    """
    Calculates edge weights as the sum of packet flows from i to j, distributing
    flows across multiple paths while respecting edge capacity constraints.
    """
    # Create a directed graph for flow calculations to handle undirected edges
    G_directed = nx.DiGraph()
    for u, v in G.edges:
        G_directed.add_edge(u, v, capacity=G.edges[u, v]['capacity'], actual_flow=0)
        G_directed.add_edge(v, u, capacity=G.edges[u, v]['capacity'], actual_flow=0)

    # Process each source-sink pair
    for i in range(20):
        for j in range(20):
            if i != j and N[i][j] > 0:
                flow_value = N[i][j]
                source, sink = i + 1, j + 1

                # Continue finding augmenting paths until flow is satisfied or no path exists
                while flow_value > 0:
                    try:
                        # Find shortest path in terms of current flow to avoid saturated edges
                        path = nx.shortest_path(G_directed, source, sink, weight='actual_flow')
                        # Calculate residual capacity along the path
                        residual_capacity = float('inf')
                        for k in range(len(path) - 1):
                            u, v = path[k], path[k + 1]
                            residual = G_directed.edges[u, v]['capacity'] - G_directed.edges[u, v]['actual_flow']
                            residual_capacity = min(residual_capacity, residual)

                        # Allocate as much flow as possible up to flow_value
                        flow_to_add = min(flow_value, residual_capacity)
                        if flow_to_add <= 0:
                            break  # No more capacity available

                        # Update flows along the path
                        for k in range(len(path) - 1):
                            u, v = path[k], path[k + 1]
                            G_directed.edges[u, v]['actual_flow'] += flow_to_add

                        flow_value -= flow_to_add

                    except nx.NetworkXNoPath:
                        break  # No more paths available

    # Aggregate flows back to undirected graph
    for u, v in G.edges:
        # Sum flows in both directions (u,v) and (v,u) since G is undirected
        flow = G_directed.edges[u, v]['actual_flow'] if (u, v) in G_directed.edges else 0
        flow += G_directed.edges[v, u]['actual_flow'] if (v, u) in G_directed.edges else 0
        G.edges[u, v]['actual_flow'] = flow

def calculate_delay(G, N, m):
    """
    Calculates average delay T according to the formula:
    T = (1/G) * SUM_e( a(e) / (c(e)/m - a(e)) )
    """
    G_total = np.sum(N)
    if G_total == 0:
        return float('inf')
    delay_sum = 0
    for u, v in G.edges:
        a_e = G.edges[u, v]['actual_flow']
        c_e = G.edges[u, v]['capacity']
        if c_e / m <= a_e:
            return float('inf')
        delay_sum += a_e / (c_e / m - a_e)
    T = (1 / G_total) * delay_sum
    return T

def simulate_network_reliability(G, N, p, T_max, m, num_simulations=1000):
    """
    Estimates network reliability using Monte Carlo simulation.
    Returns the probability that T < T_max in a connected network.
    """
    success_count = 0
    for _ in range(num_simulations):
        G_sub = G.copy()
        edges_to_remove = []

        for u, v in G.edges:
            if random.random() > p:
                edges_to_remove.append((u, v))

        G_sub.remove_edges_from(edges_to_remove)

        if nx.is_connected(G_sub):
            calculate_actual_flow(G_sub, N)

        if nx.is_connected(G_sub):
            T = calculate_delay(G_sub, N, m)
            if T < T_max:
                success_count += 1

    reliability = success_count / num_simulations

    return reliability

def add_random_edge(G):
    """
    Adds a random edge between two non-adjacent nodes in the graph.
    The new edge's capacity is set to the average capacity of all existing edges.
    Returns the modified graph.
    """
    nodes = list(G.nodes())
    possible_edges = []
    
    # Find all possible edges that don't exist yet
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            u = nodes[i]
            v = nodes[j]
            if not G.has_edge(u, v):
                possible_edges.append((u, v))
    
    if not possible_edges:
        print("No possible edges to add - graph is complete!")
        return G
    
    # Calculate average capacity of existing edges
    capacities = [data['capacity'] for u, v, data in G.edges(data=True)]
    avg_capacity = int(np.mean(capacities)) if capacities else 300000000
    
    # Add a random edge with average capacity
    u, v = random.choice(possible_edges)
    G.add_edge(u, v, capacity=avg_capacity, actual_flow=0)
    print(f"Added new edge: ({u}, {v}) with capacity {avg_capacity} (average)")
    return G

def main():
    # Create base network
    G, N = create_network()
    
    # Simulation parameters
    p = 0.9
    T_max = 10
    m = 1000
    num_simulations = 300
    
    # Prepare table data
    table_headers = ["Iteration", "Edges Count", "Added Edge", "Reliability"]
    table_data = []
    
    # Initial simulation
    reliability = simulate_network_reliability(G, N, p, T_max, m, num_simulations)
    table_data.append([0, G.number_of_edges(), "Initial network", f"{reliability:.4f}"])
    
    # Run 5 iterations adding random edges and testing reliability
    for i in range(1, 21):
        G = add_random_edge(G)
        reliability = simulate_network_reliability(G, N, p, T_max, m, num_simulations)
        added_edge = list(G.edges())[-1]  # Get the last added edge
        table_data.append([i, G.number_of_edges(), added_edge, f"{reliability:.4f}"])
    
    # Print beautiful table
    print("\nNetwork Reliability Simulation Results")
    print(f"Parameters: p={p}, T_max={T_max}, m={m}, simulations={num_simulations}")
    print(tabulate(table_data, headers=table_headers, tablefmt="grid"))
    
    # # Print some network statistics
    # print("\nFinal Network Statistics:")
    # print(f"- Nodes: {G.number_of_nodes()}")
    # print(f"- Edges: {G.number_of_edges()}")
    # print(f"- Average degree: {sum(dict(G.degree()).values()) / G.number_of_nodes():.2f}")

if __name__ == "__main__":
    main()
