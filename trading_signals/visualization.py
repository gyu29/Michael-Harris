import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import CHART_WIDTH, CHART_HEIGHT, CHART_BG_COLOR, CHART_PAPER_COLOR, CHART_FONT_COLOR

def plot_candlestick_with_signals(df, start_index=0, num_rows=100):
    df_subset = df.iloc[start_index:start_index + num_rows]
    
    fig = make_subplots(rows=1, cols=1)
    
    fig.add_trace(go.Candlestick(
        x=df_subset.index,
        open=df_subset['Open'],
        high=df_subset['High'],
        low=df_subset['Low'],
        close=df_subset['Close'],
        name='Candlesticks'),
        row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=df_subset.index, 
        y=df_subset['pointpos'], 
        mode="markers",
        marker=dict(size=10, color="MediumPurple", symbol='circle'),
        name="Entry Points"),
        row=1, col=1)
    
    fig.update_layout(
        width=CHART_WIDTH, 
        height=CHART_HEIGHT, 
        plot_bgcolor=CHART_BG_COLOR,
        paper_bgcolor=CHART_PAPER_COLOR,
        font=dict(color=CHART_FONT_COLOR),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        showlegend=True,
        legend=dict(
            x=0.01,
            y=0.99,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="white"
            ),
            bgcolor="black",
            bordercolor="gray",
            borderwidth=2
        )
    )
    
    fig.show()

def plot_backtest_results(results):
    # calculate aggregate metrics
    agg_returns = sum([r["Return [%]"] for r in results])
    num_trades = sum([r["# Trades"] for r in results])
    max_drawdown = min([r["Max. Drawdown [%]"] for r in results])
    avg_drawdown = sum([r["Avg. Drawdown [%]"] for r in results]) / len(results)
    win_rate = sum([r["Win Rate [%]"] for r in results]) / len(results)
    best_trade = max([r["Best Trade [%]"] for r in results])
    worst_trade = min([r["Worst Trade [%]"] for r in results])
    avg_trade = sum([r["Avg. Trade [%]"] for r in results]) / len(results)
    
    # make figure w/ metrics
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Aggregated Returns', 'Win Rate', 'Best Trade', 'Worst Trade', 'Avg Trade', 'Max Drawdown'],
        y=[agg_returns, win_rate, best_trade, worst_trade, avg_trade, max_drawdown],
        marker_color=['green', 'blue', 'green', 'red', 'purple', 'red']
    ))
    
    fig.update_layout(
        title='Backtest Results Summary',
        xaxis_title='Metric',
        yaxis_title='Value (%)',
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        plot_bgcolor=CHART_BG_COLOR,
        paper_bgcolor=CHART_PAPER_COLOR,
        font=dict(color=CHART_FONT_COLOR)
    )
    
    # text annotations with # of trades
    fig.add_annotation(
        x=0.5,
        y=0.9,
        text=f"Number of Trades: {num_trades}",
        showarrow=False,
        font=dict(size=14, color=CHART_FONT_COLOR),
        xref="paper",
        yref="paper"
    )
    
    fig.show()
