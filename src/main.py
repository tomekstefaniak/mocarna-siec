
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

def create_network():
    # Tworzenie grafu skierowanego
    G = nx.DiGraph()

    # Dodanie wierzchołków (1 do 20)
    G.add_nodes_from(range(1, 21))

    # Dodanie krawędzi pierścienia
    ring_edges = [(i, i+1) for i in range(1, 20)] + [(20, 1)]
    G.add_edges_from(ring_edges)

    # Dodanie dodatkowych krawędzi przechodzących wewnątrz pierścienia
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

G, N = create_network()

# # Weryfikacja liczby wierzchołków i krawędzi
# print(f"Liczba wierzchołków: {G.number_of_nodes()}")
# print(f"Liczba krawędzi: {G.number_of_edges()}")

# # Zapisanie wizualizacji grafu | Wersja bez etykiet
# pos = nx.circular_layout(G)  # Układ pierścieniowy dla czytelności
# nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10, arrowsize=15)
# # plt.title("Graf prezentujący topologię sieci")
# plt.savefig("imgs/graf.png")

# Zapisanie wizualizacji grafu | Wersja bez etykiet
plt.figure(figsize=(12, 12))  # Większy rozmiar
pos = nx.circular_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10, arrowsize=15)
# Przygotowanie etykiet dla krawędzi
edge_labels = {(u, v): f"{G.edges[u, v]['actual_flow']}/{G.edges[u, v]['capacity']}" for u, v in G.edges}
# Rysowanie etykiet na krawędziach
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

plt.tight_layout()
plt.savefig("imgs/graf.png")

# Wyświetlenie macieży natężeń strumienia pakietów
print(N)
