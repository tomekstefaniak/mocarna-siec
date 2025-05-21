import networkx as nx
import numpy as np
import random

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
    # Początkowe przepustowości (będą skalowane później)
    for u, v in G.edges:
        if (u, v) in ring_edges or (v, u) in ring_edges:
            G.edges[u, v]['base_capacity'] = 200_000_000
        else:
            G.edges[u, v]['base_capacity'] = 300_000_000
        G.edges[u, v]['capacity'] = G.edges[u, v]['base_capacity']
        G.edges[u, v]['actual_flow'] = 0

    N = np.zeros((20, 20), dtype=int)
    for i in range(20):
        for j in range(20):
            if i != j:
                N[i][j] = random.randint(100, 1000)
            else:
                N[i][j] = 0
    return G, N

def set_capacities(G, multiplier):
    for u, v in G.edges:
        G.edges[u, v]['capacity'] = int(G.edges[u, v]['base_capacity'] * multiplier)

def calculate_actual_flow(G, N):
    G_directed = nx.DiGraph()
    for u, v in G.edges:
        G_directed.add_edge(u, v, capacity=G.edges[u, v]['capacity'], actual_flow=0)
        G_directed.add_edge(v, u, capacity=G.edges[u, v]['capacity'], actual_flow=0)
    for i in range(20):
        for j in range(20):
            if i != j and N[i][j] > 0:
                flow_value = N[i][j]
                source, sink = i + 1, j + 1
                while flow_value > 0:
                    try:
                        path = nx.shortest_path(G_directed, source, sink, weight='actual_flow')
                        residual_capacity = float('inf')
                        for k in range(len(path) - 1):
                            u, v = path[k], path[k + 1]
                            residual = G_directed.edges[u, v]['capacity'] - G_directed.edges[u, v]['actual_flow']
                            residual_capacity = min(residual_capacity, residual)
                        flow_to_add = min(flow_value, residual_capacity)
                        if flow_to_add <= 0:
                            break
                        for k in range(len(path) - 1):
                            u, v = path[k], path[k + 1]
                            G_directed.edges[u, v]['actual_flow'] += flow_to_add
                        flow_value -= flow_to_add
                    except nx.NetworkXNoPath:
                        break
    for u, v in G.edges:
        flow = G_directed.edges[u, v]['actual_flow'] if (u, v) in G_directed.edges else 0
        flow += G_directed.edges[v, u]['actual_flow'] if (v, u) in G_directed.edges else 0
        G.edges[u, v]['actual_flow'] = flow

def calculate_delay(G, N, m):
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
            T = calculate_delay(G_sub, N, m)
            if T < T_max:
                success_count += 1
    reliability = success_count / num_simulations
    return reliability

def experiment_increasing_capacity():
    G, N = create_network()
    p = 0.9
    T_max = 10
    m = 1000
    num_simulations = 500  # Możesz zwiększyć dla większej dokładności
    multipliers = [0.25, 0.5, 0.75, 1, 1.5, 2, 3, 5]
    results = []

    print("Mnożnik przepustowości | Niezawodność Pr[T < T_max]")
    print("--------------------------------------------")
    for mult in multipliers:
        set_capacities(G, mult)
        calculate_actual_flow(G, N)
        reliability = simulate_network_reliability(G, N, p, T_max, m, num_simulations)
        print(f"{mult:>20}x | {reliability:>10.4f}")
        results.append((mult, reliability))
    return results

def main():
    experiment_increasing_capacity()

if __name__ == "__main__":
    main()