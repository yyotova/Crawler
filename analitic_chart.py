import plotly.graph_objects as go


def show_chart(range_time, visited):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=range_time,
        y=visited
    ))

    fig.update_layout(
        autosize=False,
        width=800,
        height=900,
        yaxis=dict(
            title_text="Visited websites",
            tickmode="array",
            titlefont=dict(size=30)
        ),
        xaxis=dict(
            title_text='Time ranges',
            tickmode="array",
            titlefont=dict(size=30)
        )
    )

    fig.show()
