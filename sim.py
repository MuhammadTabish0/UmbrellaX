import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import random

# --- Load and Analyze Real-World COVID Probabilities ---
def load_covid_data(csv_path):
    df = pd.read_csv(csv_path, parse_dates=['date'])
    df = df[df['location'] == 'India']  # Or any specific location
    df = df.sort_values('date')
    df['positive_rate_calc'] = df['new_cases'] / df['new_tests']
    return df['positive_rate_calc'].mean(skipna=True)  # Use average as infection probability

# --- Generate Synthetic Social Network ---
def generate_social_network(n=3000, k=10, p=0.05):
    return nx.watts_strogatz_graph(n=n, k=k, p=p)

# --- Visualization ---
def draw_network(G, infected_nodes, step):
    color_map = ['red' if node in infected_nodes else 'green' for node in G.nodes()]
    plt.figure(figsize=(10, 10))
    nx.draw_spring(G, node_color=color_map, node_size=10, edge_color='gray', with_labels=False)
    plt.title(f"Disease Spread Simulation - Step {step}")
    plt.axis('off')
    plt.show()

# --- Disease Spread Simulation ---
def simulate_disease_spread(G, initial_infected, infection_prob, steps=10):
    infected = set(initial_infected)
    infection_history = [set(infected)]

    for step in range(steps):
        new_infected = set(infected)
        for node in infected:
            for neighbor in G.neighbors(node):
                if neighbor not in infected:
                    if random.random() < infection_prob:
                        new_infected.add(neighbor)
        infected = new_infected
        infection_history.append(set(infected))
        draw_network(G, infected, step + 1)

    return infection_history

# --- Main Execution ---
def main():
    # Step 1: Estimate infection probability from real data
    # For demonstration, we use a constant; replace with real data if needed.
    # infection_prob = load_covid_data('covid_data.csv')
    infection_prob = 0.05  # ~5% infection chance on contact

    # Step 2: Generate Network
    G = generate_social_network(n=100, k=10, p=0.05)

    # Step 3: Randomly select initial infected individuals
    initial_infected = random.sample(list(G.nodes()), 5)

    # Step 4: Simulate
    simulate_disease_spread(G, initial_infected, infection_prob, steps=10)

if __name__ == '__main__':
    main()
