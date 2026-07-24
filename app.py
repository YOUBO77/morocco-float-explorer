import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

st.set_page_config(page_title="Morocco Path Explorer", layout="wide")

# Load data
scenario_df      = pd.read_csv("scenario_df.csv")
trend_slopes     = pd.read_csv("trend_slopes.csv")
feature_imp      = pd.read_csv("feature_importance.csv")
morocco_metrics  = pd.read_csv("morocco_metrics.csv")
clusters         = pd.read_csv("clusters.csv")

try:
    probabilities = pd.read_csv("probabilities.csv")["probability"].tolist()
except:
    probabilities = []


# Helpers
def slope_color(indicator, slope):
    if indicator == "Reserves":
        return "green" if slope > 0 else "red" if slope < 0 else "gray"
    else:
        return "green" if slope < 0 else "red" if slope > 0 else "gray"


# Tabs

tab1, tab2 = st.tabs(["Scenario Explorer", "Methodology & Visualizations"])

# TAB 1 — Scenario Explorer

with tab1:
    st.title("Morocco Float: Interactive Scenario Explorer")

    # -- Scenario selector --
    scenario_options = scenario_df["Scenario"].unique()
    selected_scenario = st.selectbox(
        "Select an Economic Scenario:", scenario_options, index=0
    )
    filtered_data = scenario_df[scenario_df["Scenario"] == selected_scenario]
    prob = filtered_data["P(Success)"].values[0]
    risk = filtered_data["Risk"].values[0]

    # -- Top KPIs --
    k1, k2, k3 = st.columns(3)
    k1.metric("Predicted Probability", f"{prob:.1%}",
              help="Bootstrap 90% CI: 30.2% – 78.0%")
    k2.metric("Risk Level", risk)
    if selected_scenario == "Base":
        k3.metric("Cluster", "Success Floaters",
                  help="Ward hierarchical clustering on pre-float trends + levels")
    else:
        k3.metric("Cluster", "Peer-derived",
                  help="Counterfactual trajectory swapped from peer country")

    st.divider()

    # -- Morocco Pre-Float Metrics (all 8 features) --
    st.subheader("Morocco Pre-Float Macroeconomic Profile")
    m = morocco_metrics.set_index("Metric")["Value"].to_dict()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Inflation Trend",  f"{m.get('Inflation_trend', 0):.2f}%/yr",
              help="Negative = improving (falling inflation)")
    c2.metric("Debt Trend",       f"{m.get('Debt_trend', 0):.2f} pts/yr",
              help="Negative = deleveraging")
    c3.metric("Exchange Trend",   f"{m.get('Exchange_trend', 0):.3f} LCU/USD/yr",
              help="Negative = stability / appreciation")
    c4.metric("Reserves Trend",   f"{m.get('Reserves_trend', 0):.2e} USD/yr",
              help="Positive = building reserves")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Inflation Mean (3yr)", f"{m.get('Inflation_mean', 0):.2f}%")
    c6.metric("Debt Mean (3yr)",      f"{m.get('Debt_mean', 0):.2f}% GNI")
    c7.metric("Exchange Mean (3yr)",  f"{m.get('Exchange_mean', 0):.2f} LCU/USD")
    c8.metric("Reserves Mean (3yr)",  f"{m.get('Reserves_mean', 0):.2e} USD")

    st.divider()

    # -- Scenario comparison chart --
    risk_colors = {"Low": "#e74c3c", "Medium": "#f1c40f", "High": "#2ecc71"}

    fig = go.Figure(data=[go.Bar(
        x=scenario_df["Scenario"],
        y=scenario_df["P(Success)"],
        marker=dict(
            color=[risk_colors[r] for r in scenario_df["Risk"]],
            line=dict(
                width=[4 if s == selected_scenario else 0 for s in scenario_df["Scenario"]],
                color=["black" if s == selected_scenario else "rgba(0,0,0,0)"
                       for s in scenario_df["Scenario"]]
            )
        ),
        text=scenario_df["P(Success)"].apply(lambda x: f"{x:.1%}"),
        textposition="auto"
    )])

    fig.add_hline(y=0.5, line_dash="dash", line_color="gray",
                  annotation_text="50% Threshold", annotation_position="top right")
    fig.update_layout(
        title="Scenario Comparison: Probability of Successful Float",
        yaxis=dict(range=[0, 1.1], title="P(Success)"),
        xaxis_title="Economic Scenario",
        template="plotly_white",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Full Scenario Data"):
        display_df = filtered_data[["Scenario", "Source", "P(Success)", "Risk"]].copy()
        display_df["P(Success)"] = display_df["P(Success)"].apply(lambda x: f"{x:.1%}")
        st.dataframe(display_df, hide_index=True, use_container_width=True)

    with st.expander("Methodology & Limitations"):
        st.markdown("""
        **Data:** 6 historical currency floats (Egypt 2016, Ghana 2023, Nigeria 2023,
        Poland 2000, Georgia 2019, Morocco 2026)

        **Method:** Theil-Sen trend slopes → Ward hierarchical clustering →
        Random Forest (n=5 peers, 8 features) → Bootstrap CIs (1,000 iterations)

        **Key Insight:** Trajectory matters more than level for policy events.
        Morocco's improving trends cluster with European success cases.

        **Limitations:**
        - Small sample (n=6) limits predictive precision
        - 3-year pre-float window may miss structural breaks
        - Poland debt imputed; Nigeria exchange rate uses official rate
        - No causal inference — descriptive pattern matching only

        **Uncertainty:** Bootstrap 90% CI for Base scenario: 30.2% – 78.0%
        """)


# TAB 2 — Methodology & Visualizations (all interactive)

with tab2:
    st.header("Methodology Visualizations")

    # -- Interactive Trend Slopes --
    st.subheader("Pre-Float Trajectory Slopes by Country")
    indicators = {
        "Inflation":      {"title": "Inflation Trend (% per Year)",      "unit": "%/yr"},
        "Debt":           {"title": "Debt Trend (% of GNI per Year)",    "unit": "pts/yr"},
        "Exchange rate":  {"title": "Exchange Rate Trend (LCU/USD/yr)","unit": "LCU/USD/yr"},
        "Reserves":       {"title": "Reserves Trend (USD per Year)",     "unit": "USD/yr"}
    }
    panel_map = {"Inflation": (1,1), "Debt": (1,2), "Exchange rate": (2,1), "Reserves": (2,2)}

    fig_slopes = make_subplots(
        rows=2, cols=2,
        subplot_titles=[v["title"] for v in indicators.values()]
    )

    for indicator, (row, col) in panel_map.items():
        df_panel = trend_slopes[trend_slopes["Indicator"] == indicator].copy()

        # Sort: Morocco first, then peers by distance to Morocco
        morocco_slope = df_panel.loc[df_panel["Country"] == "Morocco", "Trend slope"].values[0]
        df_panel["distance"] = (df_panel["Trend slope"] - morocco_slope).abs()
        df_panel = pd.concat([
            df_panel[df_panel["Country"] == "Morocco"],
            df_panel[df_panel["Country"] != "Morocco"].sort_values("distance")
        ])

        colors  = [slope_color(indicator, s) for s in df_panel["Trend slope"]]
        symbols = ["star" if c == "Morocco" else "circle" for c in df_panel["Country"]]
        sizes   = [16 if c == "Morocco" else 12 for c in df_panel["Country"]]

        fig_slopes.add_trace(go.Scatter(
            x=df_panel["Country"],
            y=df_panel["Trend slope"],
            mode="markers+text",
            text=df_panel["Country"],
            textposition="top center",
            marker=dict(color=colors, symbol=symbols, size=sizes,
                        line=dict(width=1, color="black")),
            showlegend=False
        ), row=row, col=col)

        fig_slopes.add_hline(y=0, line_dash="dash", line_color="black", line_width=1,
                             row=row, col=col)
        fig_slopes.update_xaxes(showticklabels=False, row=row, col=col)
        fig_slopes.update_yaxes(title_text=indicators[indicator]["unit"], row=row, col=col)

    fig_slopes.update_layout(
        height=850,
        template="plotly_white",
        title_text="Green = Favorable  |  Red = Unfavorable  |  Star = Morocco",
        title_x=0.5
    )
    st.plotly_chart(fig_slopes, use_container_width=True)

    st.divider()

    # -- Hierarchical Clustering --
    st.subheader("Hierarchical Clustering Dendrogram")
    st.markdown("""
    Morocco clusters with Poland and Georgia (**Success Floaters**) at a lower linkage
    distance than with Egypt / Ghana / Nigeria (**Crisis Floaters**).
    """)
    st.image("Dendrogram.png", use_container_width=True)

    st.markdown("**Cluster Assignments:**")
    st.dataframe(
        clusters.rename(columns={"Country Name": "Country", "cluster_labels": "Cluster"}),
        hide_index=True,
        use_container_width=True
    )

    st.divider()

    # -- Interactive Feature Importance --
    st.subheader("Random Forest Feature Importance")
    fig_imp = px.bar(
        feature_imp.sort_values("Importance", ascending=True),
        x="Importance",
        y="Feature",
        orientation="h",
        color="Importance",
        color_continuous_scale="Inferno",
        text=feature_imp.sort_values("Importance", ascending=True)["Importance"].apply(lambda x: f"{x:.3f}")
    )
    fig_imp.update_layout(
        yaxis_title="",
        xaxis_title="Importance Score",
        template="plotly_white",
        coloraxis_showscale=False,
        height=450
    )
    st.plotly_chart(fig_imp, use_container_width=True)

    st.divider()

    # -- Bootstrap Distribution --
    if probabilities:
        st.subheader("Bootstrap Distribution")
        fig_boot = go.Figure(data=[go.Histogram(
            x=probabilities,
            nbinsx=30,
            marker_color="#3498db",
            opacity=0.85
        )])
        fig_boot.add_vline(x=0.5, line_dash="dash", line_color="gray",
                           annotation_text="50% Threshold")
        fig_boot.add_vline(x=np.mean(probabilities), line_dash="dot", line_color="red",
                           annotation_text=f"Mean: {np.mean(probabilities):.1%}")
        fig_boot.update_layout(
            title="Morocco P(Success) Across 1,000 Bootstrap Samples",
            xaxis_title="Probability of Success",
            yaxis_title="Count",
            template="plotly_white",
            bargap=0.1
        )
        st.plotly_chart(fig_boot, use_container_width=True)
    else:
        st.info("Bootstrap probabilities not loaded.")
