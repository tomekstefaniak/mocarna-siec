
import networkx as nx
import matplotlib.pyplot as plt
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

    # Przypisanie przepustowości c(e)
    for u, v in G.edges:
        if (u, v) in ring_edges:
            G.edges[u, v]['capacity'] = 2000000  # 2 Mbps dla krawędzi pierścienia
        else:
            G.edges[u, v]['capacity'] = 3000000  # 3 Mbps dla dodatkowych krawędzi

        G.edges[u, v]['actual_flow'] = 0  # Przepływ a(e) początkowo 0

    # Przypisanie przykładowych przepływów (w pakietach/s)
    flow_values = {
        (1, 2): 300,   # 300 pakietów/s
        (2, 3): 200,   # 200 pakietów/s
        (1, 11): 400,  # 400 pakietów/s
        (5, 15): 250,  # 250 pakietów/s
        (20, 1): 500   # 500 pakietów/s
    }

    for u, v in flow_values.keys():
        G.edges[u, v]['actual_flow'] = flow_values[(u, v)]

    # Tworzenie macierzy N (20x20)
    N = np.zeros((20, 20))

    N[1 - 1][3 - 1] = 500
    N[1 - 1][11 - 1] = 400
    N[5 - 1][15 - 1] = 250
    N[20 - 1][1 - 1] = 500

    return G, N

def calculate_delay(G, N, m):
    """
    Oblicza średnie opóźnienie T według wzoru:
    T = (1/G) * SUM_e( a(e) / (c(e)/m - a(e)) )
    """
    G_total = np.sum(N)  # Suma wszystkich elementów macierzy N
    if G_total == 0:
        return float('inf')  # Unikamy dzielenia przez 0

    delay_sum = 0
    for u, v in G.edges:
        a_e = G.edges[u, v]['actual_flow']  # Przepływ a(e) w pakietach/s
        c_e = G.edges[u, v]['capacity']     # Przepustowość c(e) w bitach/s
        if c_e / m <= a_e:  # Sprawdzamy, czy denominator nie jest ujemny lub zerowy
            return float('inf')
        delay_sum += a_e / (c_e / m - a_e)

    T = (1 / G_total) * delay_sum
    return T

def simulate_network_reliability(G, N, p, T_max, m, num_simulations = 1000):
    """
    Szacuje niezawodność sieci metodą Monte Carlo.
    Zwraca prawdopodobieństwo, że T < T_max w nierozspójnionej sieci.
    """
    success_count = 0
    for _ in range(num_simulations):
        # Tworzenie podgrafu z losowo uszkodzonymi krawędziami
        G_sub = G.copy()
        edges_to_remove = []
        for u, v in G.edges:
            if random.random() > p:  # Uszkadzamy krawędź z prawdopodobieństwem 1-p
                edges_to_remove.append((u, v))
        G_sub.remove_edges_from(edges_to_remove)

        # Sprawdzamy, czy podgraf jest spójny
        if nx.is_connected(G_sub):
            # Obliczamy opóźnienie T
            T = calculate_delay(G_sub, N, m)
            if T < T_max:
                success_count += 1

    # Prawdopodobieństwo sukcesu
    reliability = success_count / num_simulations
    return reliability

def main():
    # Parametry
    G, N = create_network()
    p = 0.9           # Prawdopodobieństwo nieuszkodzenia krawędzi
    T_max = 0.001     # Maksymalne dopuszczalne opóźnienie (w sekundach)
    m = 1000          # Średnia wielkość pakietu w bitach (np. 1000 bitów)
    num_simulations = 1000  # Liczba symulacji Monte Carlo

    # Obliczenie niezawodności
    reliability = simulate_network_reliability(G, N, p, T_max, m, num_simulations)
    
    # Wyświetlenie wyniku
    print(f"Parametry:")
    print(f"  Prawdopodobieństwo nieuszkodzenia krawędzi (p): {p}")
    print(f"  Maksymalne opóźnienie (T_max): {T_max} s")
    print(f"  Średnia wielkość pakietu (m): {m} bitów")
    print(f"  Liczba symulacji: {num_simulations}")
    print(f"Oszacowana niezawodność sieci: {reliability:.4f}")
    
    # Opcjonalnie: oblicz T dla oryginalnej sieci
    T = calculate_delay(G, N, m)
    print(f"Średnie opóźnienie w oryginalnej sieci (T): {T:.6f} s")

if __name__ == "__main__":
    main()
