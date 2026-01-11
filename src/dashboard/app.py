"""
Real-time dashboard for the multi-agent economy simulator.

Uses Dash (Plotly) for visualization.
"""

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from collections import deque
import threading
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.simulation import Simulation
from src.core.config import WORLD_WIDTH, WORLD_HEIGHT, GOODS


class Dashboard:
    """Dashboard for visualizing the simulation."""
    
    def __init__(self, simulation: Simulation):
        """Initialize dashboard with simulation."""
        self.sim = simulation
        self.app = dash.Dash(__name__)
        self.running = False
        
        # Data storage for charts
        self.price_history = {good: deque(maxlen=100) for good in GOODS}
        self.wealth_history = deque(maxlen=100)
        self.agent_count_history = deque(maxlen=100)
        self.tick_history = deque(maxlen=100)
        
        # Setup layout
        self._setup_layout()
        self._setup_callbacks()
    
    def _setup_layout(self):
        """Setup dashboard layout."""
        self.app.layout = html.Div([
            html.H1("🌍 Multi-Agent Economy Simulator", 
                   style={'textAlign': 'center', 'marginBottom': '30px'}),
            
            # Control panel
            html.Div([
                html.Button('Start', id='start-btn', n_clicks=0,
                           style={'margin': '10px', 'padding': '10px 20px'}),
                html.Button('Stop', id='stop-btn', n_clicks=0,
                           style={'margin': '10px', 'padding': '10px 20px'}),
                html.Button('Step', id='step-btn', n_clicks=0,
                           style={'margin': '10px', 'padding': '10px 20px'}),
                html.Div(id='status', style={'margin': '10px', 'fontSize': '18px'}),
                html.Div(id='tick-display', style={'margin': '10px', 'fontSize': '16px'}),
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),
            
            # Main grid
            html.Div([
                # Left column - World view
                html.Div([
                    html.H3("World Map"),
                    dcc.Graph(id='world-map', style={'height': '500px'}),
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                # Right column - Charts
                html.Div([
                    html.H3("Price Trends"),
                    dcc.Graph(id='price-chart', style={'height': '250px'}),
                    html.H3("Wealth & Agents"),
                    dcc.Graph(id='stats-chart', style={'height': '250px'}),
                ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            ]),
            
            # Stats panel
            html.Div([
                html.Div(id='agent-stats', style={'margin': '20px'}),
                html.Div(id='market-stats', style={'margin': '20px'}),
            ], style={'marginTop': '20px'}),
            
            # Auto-refresh interval
            dcc.Interval(
                id='interval-component',
                interval=500,  # Update every 500ms
                n_intervals=0,
                disabled=True
            ),
        ])
    
    def _setup_callbacks(self):
        """Setup Dash callbacks."""
        
        @self.app.callback(
            [Output('interval-component', 'disabled'),
             Output('status', 'children')],
            [Input('start-btn', 'n_clicks'),
             Input('stop-btn', 'n_clicks')]
        )
        def control_simulation(start_clicks, stop_clicks):
            ctx = dash.callback_context
            if not ctx.triggered:
                return True, "Status: Stopped"
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'start-btn':
                self.running = True
                return False, "Status: Running"
            elif button_id == 'stop-btn':
                self.running = False
                return True, "Status: Stopped"
            
            return True, "Status: Stopped"
        
        @self.app.callback(
            Output('step-btn', 'n_clicks'),
            [Input('step-btn', 'n_clicks')]
        )
        def step_simulation(n_clicks):
            if n_clicks > 0:
                self.sim.step(use_smart_decisions=True)
            return n_clicks
        
        @self.app.callback(
            [Output('world-map', 'figure'),
             Output('price-chart', 'figure'),
             Output('stats-chart', 'figure'),
             Output('tick-display', 'children'),
             Output('agent-stats', 'children'),
             Output('market-stats', 'children')],
            [Input('interval-component', 'n_intervals'),
             Input('step-btn', 'n_clicks')]
        )
        def update_dashboard(n_intervals, step_clicks):
            # Step simulation if running
            if self.running:
                self.sim.step(use_smart_decisions=True)
            
            # Get current state
            state = self.sim.get_state_summary()
            
            # Update history
            self.tick_history.append(state['tick'])
            self.wealth_history.append(state['total_wealth'])
            self.agent_count_history.append(state['num_agents'])
            
            for good in GOODS:
                self.price_history[good].append(state['prices'][good])
            
            # Create world map
            world_fig = self._create_world_map()
            
            # Create price chart
            price_fig = self._create_price_chart()
            
            # Create stats chart
            stats_fig = self._create_stats_chart()
            
            # Agent stats
            agent_stats = self._create_agent_stats()
            
            # Market stats
            market_stats = self._create_market_stats(state)
            
            tick_display = f"Tick: {state['tick']}"
            
            return world_fig, price_fig, stats_fig, tick_display, agent_stats, market_stats
    
    def _create_world_map(self):
        """Create world grid visualization."""
        # Terrain colors
        terrain_colors = {
            'plain': 'lightgreen',
            'farm': 'green',
            'mine': 'gray',
            'market': 'orange'
        }
        
        # Create grid
        fig = go.Figure()
        
        # Draw terrain
        for x in range(self.sim.world.width):
            for y in range(self.sim.world.height):
                cell = self.sim.world.get_cell(x, y)
                if cell:
                    color = terrain_colors.get(cell.terrain_type, 'white')
                    fig.add_trace(go.Scatter(
                        x=[x], y=[y],
                        mode='markers',
                        marker=dict(
                            size=15,
                            color=color,
                            line=dict(width=0.5, color='black')
                        ),
                        showlegend=False,
                        hovertext=f"{cell.terrain_type}",
                        hoverinfo='text'
                    ))
        
        # Draw agents
        agent_colors = {
            'consumer': 'blue',
            'producer': 'red',
            'trader': 'purple'
        }
        
        for agent in self.sim.agents.values():
            fig.add_trace(go.Scatter(
                x=[agent.x], y=[agent.y],
                mode='markers',
                marker=dict(
                    size=20,
                    color=agent_colors.get(agent.type, 'black'),
                    symbol='circle',
                    line=dict(width=2, color='white')
                ),
                name=agent.type,
                showlegend=True,
                hovertext=f"{agent.id}<br>Type: {agent.type}<br>Health: {agent.health:.1f}<br>Wealth: {agent.wealth:.1f}",
                hoverinfo='text'
            ))
        
        fig.update_layout(
            title="World Map (Agents on Terrain)",
            xaxis=dict(title="X", range=[-1, WORLD_WIDTH]),
            yaxis=dict(title="Y", range=[-1, WORLD_HEIGHT]),
            height=500,
            showlegend=True
        )
        
        return fig
    
    def _create_price_chart(self):
        """Create price trends chart."""
        fig = go.Figure()
        
        for good in GOODS:
            if len(self.price_history[good]) > 0:
                fig.add_trace(go.Scatter(
                    x=list(self.tick_history),
                    y=list(self.price_history[good]),
                    mode='lines+markers',
                    name=good.capitalize(),
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            title="Price Trends Over Time",
            xaxis=dict(title="Tick"),
            yaxis=dict(title="Price"),
            height=250,
            hovermode='x unified'
        )
        
        return fig
    
    def _create_stats_chart(self):
        """Create wealth and agent count chart."""
        fig = go.Figure()
        
        if len(self.wealth_history) > 0:
            fig.add_trace(go.Scatter(
                x=list(self.tick_history),
                y=list(self.wealth_history),
                mode='lines+markers',
                name='Total Wealth',
                yaxis='y',
                line=dict(color='green', width=2)
            ))
        
        if len(self.agent_count_history) > 0:
            fig.add_trace(go.Scatter(
                x=list(self.tick_history),
                y=list(self.agent_count_history),
                mode='lines+markers',
                name='Agent Count',
                yaxis='y2',
                line=dict(color='blue', width=2)
            ))
        
        fig.update_layout(
            title="Wealth & Agent Count",
            xaxis=dict(title="Tick"),
            yaxis=dict(title="Total Wealth", side='left'),
            yaxis2=dict(title="Agent Count", side='right', overlaying='y'),
            height=250,
            hovermode='x unified'
        )
        
        return fig
    
    def _create_agent_stats(self):
        """Create agent statistics display."""
        agents = list(self.sim.agents.values())
        
        if not agents:
            return html.Div("No agents alive")
        
        # Count by type
        type_counts = {}
        total_wealth = 0
        total_health = 0
        
        for agent in agents:
            type_counts[agent.type] = type_counts.get(agent.type, 0) + 1
            total_wealth += agent.wealth
            total_health += agent.health
        
        avg_wealth = total_wealth / len(agents)
        avg_health = total_health / len(agents)
        
        return html.Div([
            html.H4("Agent Statistics"),
            html.P(f"Total Agents: {len(agents)}"),
            html.P(f"Consumers: {type_counts.get('consumer', 0)}"),
            html.P(f"Producers: {type_counts.get('producer', 0)}"),
            html.P(f"Traders: {type_counts.get('trader', 0)}"),
            html.P(f"Average Wealth: {avg_wealth:.2f}"),
            html.P(f"Average Health: {avg_health:.2f}"),
        ])
    
    def _create_market_stats(self, state):
        """Create market statistics display."""
        return html.Div([
            html.H4("Market Statistics"),
            html.P(f"Food: Price={state['prices']['food']:.2f}, Qty={state['market_quantities']['food']:.1f}"),
            html.P(f"Ore: Price={state['prices']['ore']:.2f}, Qty={state['market_quantities']['ore']:.1f}"),
            html.P(f"Tools: Price={state['prices']['tools']:.2f}, Qty={state['market_quantities']['tools']:.1f}"),
            html.P(f"Total Wealth: {state['total_wealth']:.2f}"),
        ])
    
    def run(self, debug=True, port=8050):
        """Run the dashboard."""
        print(f"🚀 Starting dashboard on http://localhost:{port}")
        print("📊 Open your browser to see the visualization!")
        self.app.run_server(debug=debug, port=port)


def main():
    """Main function to run dashboard."""
    # Create simulation
    sim = Simulation(seed=42)
    
    # Create dashboard
    dashboard = Dashboard(sim)
    
    # Run dashboard
    dashboard.run()


if __name__ == "__main__":
    main()

