import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objs as go
import networkx as nx
import random
from collections import Counter
# Default Parameters
DEFAULT_N = 500
DEFAULT_K = 10
DEFAULT_REWIRE_PROB = 0.1
DEFAULT_INITIAL_INFECTED = 10

class SimulationModel:
    def __init__(self, n_nodes=500, k_neighbors=10, rewire_probability=0.1, initial_infected=10):
        self.n_nodes = n_nodes
        self.k_neighbors = k_neighbors
        self.rewire_probability = rewire_probability
        self.initial_infected = initial_infected
        self.reset()
    
    def reset(self):
        self.G = nx.watts_strogatz_graph(self.n_nodes, self.k_neighbors, self.rewire_probability)
        self.status = {node: "healthy" for node in self.G.nodes()}
        self.infection_days = {node: 0 for node in self.G.nodes()}
        
        infected_nodes = random.sample(list(self.G.nodes()), min(self.initial_infected, self.n_nodes))
        for node in infected_nodes:
            self.status[node] = "infected"
            self.infection_days[node] = 1
        
        nx.set_node_attributes(self.G, self.status, "status")
        self.pos = nx.spring_layout(self.G, seed=42,iterations=30,threshold=1e-4)
        self.day = 0
        self.stats_history = []
        self.update_stats()
    
    def update_stats(self):
        stats = Counter(self.status.values())
        stats_dict = {
            'day': self.day,
            'healthy': stats.get('healthy', 0),
            'infected': stats.get('infected', 0),
            'recovered': stats.get('recovered', 0),
            'vaccinated': stats.get('vaccinated', 0),
            'dead': stats.get('dead', 0)
        }
        self.stats_history.append(stats_dict)
        return stats_dict
        
    def spread_infection(self, infection_prob, recovery_days, daily_vaccination_rate, death_prob):
        new_infections = set()
        to_recover = set()
        to_die = set()
        
        for node, state in self.status.items():
            if state == "infected":
                if random.random() < death_prob:
                    to_die.add(node)
                    continue
                self.infection_days[node] += 1
                if self.infection_days[node] >= recovery_days:
                    to_recover.add(node)
                else:
                    for neighbor in self.G.neighbors(node):
                        if self.status[neighbor] == "healthy" and random.random() < infection_prob:
                            new_infections.add(neighbor)
        
        for node in new_infections:
            self.status[node] = "infected"
            self.infection_days[node] = 1
        for node in to_recover:
            self.status[node] = "recovered"
        for node in to_die:
            self.status[node] = "dead"
        
        healthy_nodes = [n for n, s in self.status.items() if s == "healthy"]
        num_to_vaccinate = int(len(healthy_nodes) * daily_vaccination_rate)
        if num_to_vaccinate > 0 and healthy_nodes:
            vaccinated_today = random.sample(healthy_nodes, min(num_to_vaccinate, len(healthy_nodes)))
            for node in vaccinated_today:
                self.status[node] = "vaccinated"
        
        nx.set_node_attributes(self.G, self.status, "status")
        self.day += 1
        return self.update_stats()

simulation = SimulationModel(DEFAULT_N, DEFAULT_K, DEFAULT_REWIRE_PROB, DEFAULT_INITIAL_INFECTED)

# Dash app
app = dash.Dash(__name__)
app.title = "UmbrellaX"

app.layout = html.Div([
    html.Div([
        html.H1("UmbrellaX: Disease Spread Simulation", style={"textAlign": "center", "color": "#2c3e50"}),
        
        html.Div([
            html.Div([
                html.H4("Simulation Parameters", style={"color": "#2c3e50"}),

                html.Label("Total Nodes"),
                dcc.Input(id='node-count', type='number', value=DEFAULT_N, min=10, max=5000, step=10),
                html.Button("Reset Simulation", id='reset-btn', n_clicks=0, style={
                    "padding": "6px 12px", "marginTop": "10px",
                    "backgroundColor": "#e67e22", "color": "white", "border": "none",
                    "borderRadius": "5px", "cursor": "pointer"
                }),
                html.Br(), html.Br(),

                html.Label("Infection Probability"),
                dcc.Slider(id='infection-slider', min=0, max=1, step=0.01, value=0.13,
                           marks={0: '0', 0.25: '0.25', 0.5: '0.5', 0.75: '0.75', 1: '1'}),

                html.Br(),
                html.Label("Recovery Days"),
                dcc.Input(id='recovery-input', type='number', value=5, min=1),

                html.Br(), html.Br(),
                html.Label("Daily Vaccination Rate"),
                dcc.Slider(id='vaccination-slider', min=0, max=0.05, step=0.001, value=0.005,
                           marks={0: '0%', 0.01: '1%', 0.03: '3%', 0.05: '5%'}),

                html.Br(),
                html.Label("Death Probability"),
                dcc.Slider(id='death-slider', min=0, max=0.1, step=0.001, value=0.01,
                           marks={0: '0%', 0.02: '2%', 0.05: '5%', 0.1: '10%'}),

                html.Br(),
                html.Label("Show Edges"),
                dcc.Checklist(id='toggle-edges', options=[{'label': '', 'value': 'show'}],
                              value=['show'], style={"display": "inline-block"}),

                html.Div([
                    html.Button("Next Day", id='next-day-btn', n_clicks=0, style={
                        "padding": "10px 20px", "marginTop": "20px",
                        "backgroundColor": "#27ae60", "color": "white",
                        "border": "none", "borderRadius": "6px"
                    }),
                ], style={"textAlign": "center"}),

                html.H4(id='day-counter', children=f"Day: {simulation.day}",
                        style={"textAlign": "center", "marginTop": "15px"}),
                
                html.Div(id='stats-display', style={
                    "backgroundColor": "#eee", "padding": "10px",
                    "borderRadius": "5px", "marginTop": "15px"
                }),

            ], style={"width": "30%", "padding": "10px", "backgroundColor": "#f5f5f5",
                      "borderRadius": "5px"}),
            
            html.Div([
                dcc.Graph(id='network-graph', style={"height": "70vh"})
            ], style={"width": "68%", "float": "right"}),

        ], style={"display": "flex", "justifyContent": "space-between"}),

        html.Div("© 2025 UmbrellaX", style={
            'textAlign': 'center', 'padding': '20px', 'fontSize': '13px',
            'color': '#7f8c8d', 'clear': 'both'
        })

    ], style={
        "maxWidth": "1200px", "margin": "auto", "padding": "20px",
        "fontFamily": "'Segoe UI', sans-serif", "backgroundColor": "#f9f9f9",
        "borderRadius": "10px", "boxShadow": "0px 0px 8px rgba(0,0,0,0.05)"
    })
])

def generate_traces(show_edges=False):
    traces = []

    if show_edges:
        edge_x, edge_y = [], []
        for edge in simulation.G.edges():
            x0, y0 = simulation.pos[edge[0]]
            x1, y1 = simulation.pos[edge[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
        traces.append(go.Scattergl(x=edge_x, y=edge_y, line=dict(width=0.2, color='#ccc'),
                                   hoverinfo='none', mode='lines'))

    node_x, node_y, node_colors, node_text = [], [], [], []
    color_map = {
        "healthy": "green", "infected": "red", "recovered": "blue",
        "vaccinated": "purple", "dead": "black"
    }

    for node in simulation.G.nodes():
        x, y = simulation.pos[node]
        node_x.append(x)
        node_y.append(y)
        status = simulation.status[node]
        node_colors.append(color_map[status])
        node_text.append(f"Node {node} - {status}")

    traces.append(go.Scattergl(x=node_x, y=node_y, text=node_text, mode='markers',
                               hoverinfo='text', marker=dict(color=node_colors, size=4)))
    return traces

@app.callback(
    Output('network-graph', 'figure'),
    Output('day-counter', 'children'),
    Output('stats-display', 'children'),
    Input('next-day-btn', 'n_clicks'),
    Input('reset-btn', 'n_clicks'),
    Input('toggle-edges', 'value'),
    State('infection-slider', 'value'),
    State('recovery-input', 'value'),
    State('vaccination-slider', 'value'),
    State('death-slider', 'value'),
    State('node-count', 'value')
)
def update_output(next_day_clicks, reset_clicks, toggle_edges,
                  infection_prob, recovery_days, vaccination_rate, death_prob,
                  node_count):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'reset-btn':
        simulation.__init__(n_nodes=node_count, k_neighbors=DEFAULT_K,
                            rewire_probability=DEFAULT_REWIRE_PROB,
                            initial_infected=DEFAULT_INITIAL_INFECTED)
    elif triggered_id == 'next-day-btn':
        simulation.spread_infection(infection_prob, recovery_days,
                                    vaccination_rate, death_prob)

    show_edges = 'show' in toggle_edges
    traces = generate_traces(show_edges)

    stats = simulation.stats_history[-1]
    stats_display = html.Div([
        html.P(f"Healthy: {stats['healthy']} ({stats['healthy']/simulation.n_nodes*100:.1f}%)"),
        html.P(f"Infected: {stats['infected']} ({stats['infected']/simulation.n_nodes*100:.1f}%)"),
        html.P(f"Recovered: {stats['recovered']} ({stats['recovered']/simulation.n_nodes*100:.1f}%)"),
        html.P(f"Vaccinated: {stats['vaccinated']} ({stats['vaccinated']/simulation.n_nodes*100:.1f}%)"),
        html.P(f"Dead: {stats['dead']} ({stats['dead']/simulation.n_nodes*100:.1f}%)")
    ])

    fig = go.Figure(data=traces, layout=go.Layout(
        title='<b>Network Visualization</b>', title_font=dict(size=20, color='#2c3e50'),
        showlegend=False, hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        annotations=[dict(text="Green=Healthy | Red=Infected | Blue=Recovered | Purple=Vaccinated | Black=Dead",
                          showarrow=False, xref="paper", yref="paper",
                          x=0.01, y=-0.01, font=dict(size=12, color="#555"))],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    ))

    return fig, f"Day: {simulation.day}", stats_display

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
