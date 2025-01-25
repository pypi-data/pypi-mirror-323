import functools
import pandas as pd
import plotly.io as pio


# plotly template has maximum 10 basic colors for figure traces, so here we want to add more colors
plotly_template = pio.templates["plotly"]
pio.templates["draft"] = plotly_template
additional_colors = (
    "#ff057e",
    "#690f54",
    "#bf6524",
    "#176b15",
    "#0d0887",
    "#fde725",
    "#8a8678",
    "#a52c60",
    "#fcffa4",
)
basic_colors = pio.templates["draft"]["layout"]["colorway"]
pio.templates["draft"]["layout"]["colorway"] = basic_colors + additional_colors
pio.templates.default = "draft"


def figure_defaults(
    figure_options={
        "fix_xaxis": True,
        "calender": False,
        "Scatter_mode": False,
        "step": None,
    }
):
    def apply_figure_defaults(fig, options):
        def apply_trace_defaults(trace):
            if trace.type == "pie":
                trace.update(
                    textposition="inside",
                    textinfo="value+percent",
                    direction="clockwise",
                    sort=False,
                )
                fig.update_layout(
                    hiddenlabels=["Missing", "Missings"],
                )
            if trace.type == "scatter":
                if "groupby" in options and figure_options["fix_xaxis"]:
                    x_vals = get_complete_xaxis(options)
                    trace_c = pd.DataFrame({"x": trace.x, "y": trace.y})
                    trace_c["x"] = trace_c["x"].astype(str)
                    x_vals["x"] = x_vals["x"].astype(str)
                    trace_c = x_vals.merge(trace_c, on="x", how="left").fillna(0)
                    trace_c.update(x_vals.set_index("x", inplace=True))
                    fig.update_xaxes(
                        type="category", categoryorder="category ascending"
                    )
                    if "hovertext" in trace and type(trace) == "dict":
                        trace.update(
                            x=trace_c.index.astype(str).tolist(),
                        )
                    elif (
                        "hovertemplate" in trace
                        and type(trace["hovertemplate"]) == "list"
                    ):
                        trace.update(
                            x=trace_c.x,
                            y=trace_c.y.fillna(0),
                            text=trace_c.y.fillna(0),
                            hovertemplate=trace_c.hovertemplate.fillna(""),
                        )
                    else:
                        trace.update(x=trace_c.x, y=trace_c.y, text=trace_c.y)
                fig.update_layout(
                    hovermode="x",
                    hoverdistance=100,
                    spikedistance=1000,
                )
                fig.update_xaxes(
                    get_xaxis_layout(options),
                    linecolor="#BCCCDC",
                    showspikes=True,  # Show spike line for X-axis
                    # format spikelines
                    spikethickness=2,
                    spikedash="dot",
                    spikecolor="#999999",
                    spikemode="across",
                )
                fig.update_yaxes(
                    rangemode="tozero",
                    linecolor="#BCCCDC",
                    showgrid=True,
                    gridcolor="#BCCCDC",
                )
                if figure_options["Scatter_mode"]:
                    step = figure_options["step"]
                    trace.update(
                        textposition="top center",
                        # mode="lines+markers+text",
                    )
                    if int(min(trace.x)) < 0:
                        fig.update_xaxes(
                            range=[int(min(trace.x)), int(max(trace.x)) + 1],
                            dtick=step,
                            autorange=False,
                        )
                    else:
                        fig.update_xaxes(
                            range=[0, int(max(trace.x)) + 1],
                            dtick=step,
                            autorange=False,
                        )
                else:
                    trace.update(
                        textposition="top center",
                        mode="lines+markers+text",
                    )
                # if this is the only trace, edit range
                if len(fig.data) == 1:
                    fig.update_yaxes(
                        range=[0, round(max(trace.y) * 1.7, 0)],
                        autorange=False,
                    )
                if "benchmark" in options:
                    fig.add_hline(
                        y=options["benchmark"],
                        line_dash="dot",
                        line=dict(color="red"),
                        annotation_text="benchmark ({})".format(options["benchmark"]),
                    )
                    fig.update_yaxes(
                        range=[0, round(max(trace.y) * 2, 0)],
                        autorange=False,
                    )
            if trace.type == "bar":
                if "groupby" in options and figure_options["fix_xaxis"]:
                    x_vals = get_complete_xaxis(options)
                    trace_c = pd.DataFrame({"x": trace.x, "y": trace.y})
                    trace_c["x"] = trace_c["x"].astype(str)
                    x_vals["x"] = x_vals["x"].astype(str)
                    trace_c = x_vals.merge(trace_c, on="x", how="left").fillna(0)
                    trace_c.update(x_vals.set_index("x", inplace=True))
                    fig.update_xaxes(
                        type="category", categoryorder="category ascending"
                    )
                    if "hovertext" in trace and type(trace) == "dict":
                        trace.update(
                            x=trace_c.index.astype(str).tolist(),
                        )
                    elif (
                        "hovertemplate" in trace
                        and type(trace["hovertemplate"]) == "list"
                    ):
                        trace.update(
                            x=trace_c.x,
                            y=trace_c.y.fillna(0),
                            text=trace_c.y.fillna(0),
                            hovertemplate=trace_c.hovertemplate.fillna(""),
                        )
                    else:
                        trace.update(x=trace_c.x, y=trace_c.y, text=trace_c.y)
                trace.update(
                    textposition="auto",
                )
                fig.update_yaxes(
                    linecolor="#BCCCDC",
                    rangemode="tozero",
                    showgrid=True,
                    gridcolor="#BCCCDC",
                )
                fig.update_xaxes(get_xaxis_layout(options), linecolor="#BCCCDC")
            if trace.type == "box":
                fig.update_xaxes(get_xaxis_layout(options), linecolor="#BCCCDC")
                fig.update_yaxes(
                    rangemode="tozero",
                    linecolor="#BCCCDC",
                    showgrid=True,
                    gridcolor="#BCCCDC",
                )
            if trace.type == "histogram":
                fig.update_xaxes(linecolor="#BCCCDC")
                fig.update_yaxes(
                    rangemode="tozero",
                    linecolor="#BCCCDC",
                    showgrid=True,
                    gridcolor="#BCCCDC",
                )
            if trace.type == "treemap":
                trace.update(hovertemplate="%{label}<br>Count: %{value}")
                trace.update(root_color="white")
            if trace.type == "indicator":
                fig.update_layout(title=options["title"])
            return trace

        fig.for_each_trace(apply_trace_defaults)
        if fig.data[0].type == "treemap":
            fig.update_layout(
                title=options["title"],
                coloraxis={"colorscale": "ylorbr"},
            )
        elif fig.data[0].type == "heatmap":
            fig.update_layout(
                title=options["title"],
            )
            if figure_options["calender"]:
                fig.update_layout(
                    coloraxis={"colorscale": "blues"},
                )

        else:
            fig.update_layout(
                title=options["title"],
                plot_bgcolor="#FFF",
            )

        return fig

    def decorator_figure_defaults(func):
        @functools.wraps(func)
        def wrapper_figure_defaults(df, options):
            fig = func(df, options)
            if fig_is_empty(fig):
                return fig_empty_layout(fig, options)
            modified_fig = apply_figure_defaults(fig, options)
            return modified_fig

        return wrapper_figure_defaults

    return decorator_figure_defaults


def get_complete_xaxis(options):
    start_date = options["start_date"] if ("start_date" in options) else "2009-04-01"
    end_date = (
        options["end_date"]
        if ("end_date" in options)
        else pd.to_datetime("today").strftime("%Y-%m-%d")
    )
    frequant = options["groupby"] if "groupby" in options else "y"
    return pd.DataFrame(
        {
            "x": pd.period_range(
                start=start_date,
                end=end_date,
                freq=frequant,
            )
        },
    )


def get_xaxis_layout(options):
    xaxis_layout = {"showgrid": False, "dtick": 1}
    if "groupby" in options:
        if options["groupby"] == "6M":
            xaxis_layout["type"] = "category"
        elif options["groupby"] == "m":
            xaxis_layout["dtick"] = "M1"
            xaxis_layout["type"] = "date"
        elif options["groupby"] == "w":
            df = get_complete_xaxis(options)
            xaxis_layout["range"] = [str(df["x"].min()), str(df["x"].max())]

    return xaxis_layout


def get_ordered_age_groups(fig):
    """
    This function shows the age groups in specific order
    ["Neonates","Infants","1 to 2 Years","Older","Adults"]
    """
    return fig.update_xaxes(
        categoryorder="array",
        categoryarray=["Neonates", "Infants", "1 to 2 Years", "Older", "Adults"],
    )


def fig_is_empty(fig):
    """
    check check for every track in fig sum list of Y axis
    input: fig (object)
    output: True if figure data is empty(sum of Y axis == 0)
            False if figure data is NOT empty (sum of Y aixs > 0)
    """
    if len(fig.data) == 0:
        return True
    if fig.data[0].type in ["histogram", "box"]:
        return False
    elif fig.data[0].type == "heatmap":
        return (
            sum(sum(x) if isinstance(x, list) else x for x in list(fig.data[0].z)) == 0
        )
    elif fig.data[0].type in ["bar", "scatter"]:
        return sum(sum(x.y) for x in fig.data) == 0
    elif fig.data[0].type == "pie":
        return sum(fig.data[0].values) == 0


def fig_empty_layout(fig, options):
    """
    change empty figure layout to show clear text to end user
    input: fig(object) with empty data
    return fig(object) with text and no (xaxis,yaxis)
    """
    fig.update_traces(visible=False, selector=dict(type="scatter"))

    fig.update_layout(
        title={"text": options["title"]},
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": "No data related found during that period",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16},
            }
        ],
    )
    return fig
