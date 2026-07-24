#Page  config
st.set_page_config(page_title="Morocco Path Explorer", layout="wide")

tab1, tab2 = st.tabs(["Scenario Explorer", "Methodology & Visualizations"])
with tab1:
  st.title(" Morocco Float: Interactive scenario Explorer")
  # The dropdown menu
  scenario_options = scenario_df["Scenario"].unique()
  selected_scenario = st.selectbox("Select an Economic Scenario:",
                                 scenario_options,
                                 index=0 # Default to first option
                                 )
  # Filtering the data based on selection
  filtered_data = scenario_df[scenario_df["Scenario"] == selected_scenario]

  #Geting values for display
  prob = filtered_data["P(Success)"].values[0]
  risk = filtered_data["Risk"].values[0]

  # Displaying metrics
  col1, col2 = st.columns(2)
  col1.metric("Predicted Probability", f"{prob:.1%}", help="Bootstrap 90% CI: 30.2% - 78.0%")
  col2.metric("Risk level", risk)

  # Dynamic chart
  risk_colors = {"Low": "#e74c3c", "Medium": "#f1c40f", "High": "#2ecc71"}
  fig = go.Figure(data=[go.Bar(
      x=scenario_df["Scenario"],
      y=scenario_df["P(Success)"],
      marker_color=[risk_colors[r] for r in scenario_df["Risk"]],marker =dict(
          color=[risk_colors[r] for r in scenario_df["Risk"]], line=dict(
              width=[4 if s == selected_scenario else 0 for s in scenario_df["Scenario"]],
              color=["black" if s == selected_scenario else "rgba(0,0,0,0)" for s in scenario_df["Scenario"]])),
      text=scenario_df["P(Success)"].apply(lambda x: f"{x:.1%}"),
      textposition="auto"
      )])
  fig.add_hline(y=0.5, line_dash="dash", line_color="gray")
  fig.update_layout(title="Scenario Comparison", yaxis=dict(range=[0, 1.1]), template="plotly_white")
  st.plotly_chart(fig, use_container_width=True)
  # Show details
  with st.expander("View Full Scenario Data"):
    display_df = filtered_data[["Scenario", "Source", "P(Success)", "Risk"]].copy()
    display_df["P(Success)"] = display_df["P(Success)"].apply(lambda x: f"{x:.1%}")
    st.dataframe(display_df, hide_index=True)
  with st.expander("Methodology & Limitations"):
    st.markdown("""
      **Data:** 6 historical currency floats (Egypt, Ghana, Nigeria, Poland, Georgia, Morocco)
      **Method:** Theil-Sen trend slopes → hierarchical clustering → Random Forest → bootstrap CIs
      **Limitations:**
      - Small sample (n=6) limits predictive precision
      - 3-year pre-float window may not capture full trajectory
      - Poland debt imputed; Nigeria exchange rate uses official rate

      **Uncertainty:** Bootstrap 90% CI for Base scenario: 30.2% - 78.0%
      """)

with tab2:
  st.subheader("Pre-Float Trajectory Slopes")
  st.image("trajectory_slope.png")

  st.subheader("Hierarchical Clustering Dendrogram")
  st.image("Dendrogram.png")

  st.subheader("Random Forest Feature Importance")
  st.image("feature_importance.png")

  with st.expander("Bootstrap Distribution"):
    fig_boot = go.Figure(data=[go.Histogram(x=probabilities, nbinsx=30)])
    fig_boot.add_vline(x=0.5, line_dash="dash", line_color="gray")
    fig_boot.update_layout(title="Morocco P(Success) Across 1000 Bootstrap Samples",
                           xaxis_title="Probability", yaxis_title="Count")
    st.plotly_chart(fig_boot)
