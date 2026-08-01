import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import os
from PIL import Image
import plotly.express as px

# Page Configuration

st.set_page_config(
    page_title = 'Global Economic Intelligence Platform', 
    page_icon="🌍",
    layout='wide',
    initial_sidebar_state="expanded"
)

# Sidebar Navigation
with st.sidebar:
    st.image("assets/logo.jpg", use_container_width=True)
    st.title('🌐 Global Economic Intelligence Platform')
    selected = option_menu(
        menu_title="Main Menu",
        options=[
            "Home",
            "Country Analysis",
            "GDP Trends",
            "Global Map",
            "Compare Countries",
            "Data Explorer",
            "About" 
        ],
        icons=[
            "house",
            "globe",
            "graph-up-arrow",
            "map",
            "arrow-left-right",
            "table",
            "info-circle"
        ],
        menu_icon="cast",
        default_index=0,
    )
 ################################################################   

# Data loading function inside app.py
@st.cache_data
def load_data():
    df = pd.read_csv("data/gdp_cleaned.csv")
    df.columns = df.columns.str.lower()

    aggregates_to_drop = [
        "Low & middle income", "Low income", "Lower middle income",
        "Upper middle income", "High income", "World", "IDA total",
        "IBRD only", "IDA & IBRD total", "IDA blend", "IDA only",
        "Other small states", "Pacific island small estates"
    ]

    # Filter out aggregates so only true countries remain in the dataset
    df = df[~df["country"].isin(aggregates_to_drop)]
    df = df.dropna(subset=["country_code"])

    # --- 🛠️ SAFEST REGION CLEANING FIX ---
    if "region" in df.columns:
        df["region"] = (
            df["region"]
            .astype(str)
            .str.replace("[", "", regex=False)
            .str.replace("]", "", regex=False)
            .str.replace("'", "", regex=False)
            .str.strip()
        )
        
        # Split on commas and take only the first element to fix "Asia, Asia"
        df["region"] = df["region"].apply(lambda x: str(x).split(",")[0].strip().title())
    else:
        df["region"] = "Global / Other"

    df["gdp"] = df['gdp_billions'] * 1e9
    df = df.sort_values(['country', 'year'])
    df['gdp_growth'] = df.groupby("country")['gdp'].pct_change() * 100

    return df



############################################

# Routing Pages Based on Selection
if selected == "Home":
    st.title("🌍 Global Economic Intelligence Platform")
    st.write("Welcome to your professional economic analytics dashboard.")
    st.markdown("### Empowering data-driven insights into worldwide macroeconomic trends.")

    col1, col2, = st.columns([2, 1])
    with col1:
        st.write("""
        This platform delivers comprehensive macroeconomic intelligence by analyzing GDP trajectories,
        growth rates, income brackets, and region distributions from 1960 to 2025.
        Designed for analysts, researchers, and policymakers to uncover actionable global economic insights.
        """)
    with col2:
        try:
            st.image("assets/world.jpg", caption="Global Connectivity", use_container_width=True)
        except:
            st.info("💡 Tip: Add a 'world.jpg' image to your 'assets/' folder to display it here.")
    st.markdown("---")
    st.subheader("🌍 Key Macroeconomic Highlights")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="Global GDP", value="$110 Trillion", delta="2025 Est.")
    m2.metric(label="Tracked Countries", value="190+", delta="World Bank Data")
    m3.metric(label="Historical Span", value="1960-2025", delta="65 Years") 
    m4.metric(label="Core Indicators", value="4 Main", delta="GDP, Growth, Income, Region")    

 ###########################################################################################################     

elif selected == "Country Analysis":
    st.title("🌍 Individual Country Intelligence")
    st.write("Deconstruct a singular nation's historical economic trajectory, expansion speed, and systemic classification.")

    # Load the data
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.stop()

    # Country selectors and filters
    col_select1, col_select2 = st.columns([2, 1])

    with col_select1:
        # Get unique list of countries
        valid_countries_df = df[df["country_code"].notnull()]
        country_list = sorted(valid_countries_df["country"].unique())

        # Default selection (e.g., Japan if available, else first item)
        default_idx = country_list.index("Japan") if "Japan" in country_list else 0
        selected_country = st.selectbox("Choose Target Country:", country_list, index=default_idx)

    # Filter data for the chosen country
    country_df = df[df["country"] == selected_country].sort_values("year")

    if country_df.empty:
        st.warning(f"No data available for {selected_country}.")
    else:
        # Extract latest metrics for KPI calculations
        latest_row = country_df.iloc[-1]
        latest_year = int(latest_row["year"])
        latest_gdp = latest_row['gdp']
        avg_growth = country_df['gdp_growth'].mean()
        income_group = latest_row['income_group']
        region = latest_row.get("region")

        # Calculate previous year metric to give recruiters an elegant dynamic delta
        if len(country_df) > 1:
            prev_gdp = country_df.iloc[-2]['gdp']
            gdp_delta_pct = ((latest_gdp - prev_gdp) / prev_gdp) * 100
            gdp_delta_str = f"{gdp_delta_pct:+.2f}% YoY"
        else:
            gdp_delta_str = None

        st.markdown("---")

        # KPI cards
        st.subheader(f"📊 {selected_country} - Key Structural Indicators ({latest_year})")
        Kpi1, Kpi2, Kpi3, Kpi4 = st.columns(4)

        # Helper function to format large number cleanly
        def format_gdp(val):
            if val >= 1e12:
                return f"${val / 1e12:.2f}T"
            elif val >= 1e9:
                return f"${val / 1e9:.2f}B"
            elif val >= 1e6:
                return f"${val / 1e6:.2f}M"
            return f"${val:,.0f}"

        with Kpi1:
            st.metric(label="Latest Nominal GDP", value=format_gdp(latest_gdp), delta=gdp_delta_str)
        with Kpi2:
            # Dynamic delta changes color based on positive or negative historical average expansion speed
            st.metric(label="Historical Growth Velocity", value=f"{avg_growth:.2f}%" if pd.notna(avg_growth) else "N/A", delta="Avg Tracked Speed", delta_color="normal")
        with Kpi3:
            st.metric(label="World Bank Income Tier", value=str(income_group))
        with Kpi4:
            st.metric(label="Geographic Macro Region", value=str(region))

        st.markdown("---")

        # --- RECRUITER WOW-FACTOR: DUAL VISUALIZATION INTERFACE ---
        st.subheader("📈 Macroeconomic Trend Deconstruction")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("#### **GDP Production Scale over Time**")
            # Smooth area chart showing macro compounding asset expansion
            fig_gdp = px.area(
                country_df,
                x="year",
                y="gdp_billions",
                title=f"{selected_country} - Total GDP Volume ($ Billions)",
                labels={"gdp_billions": "GDP ($ Billions)", "year": "Year"},
                template="plotly_dark"
            )
            fig_gdp.update_traces(line_color="#00cc96", fillcolor="rgba(0, 204, 150, 0.2)")
            fig_gdp.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=380, hovermode="x unified")
            st.plotly_chart(fig_gdp, use_container_width=True)

        with chart_col2:
            st.markdown("#### **Annual Expansion & Contraction Speed**")
            
            # Setup conditional color tags: Green for growth years, Crimson Red for market crashes/recessions
            country_df["growth_type"] = country_df["gdp_growth"].apply(lambda x: "Expansion" if x >= 0 else "Contraction")
            
            fig_growth = px.bar(
                country_df.dropna(subset=["gdp_growth"]),
                x="year",
                y="gdp_growth",
                color="growth_type",
                color_discrete_map={"Expansion": "#00cc96", "Contraction": "#ff4b4b"},
                title=f"{selected_country} - YoY GDP Growth Percentage (%)",
                labels={"gdp_growth": "Growth Rate (%)", "year": "Year", "growth_type": "Market State"},
                template="plotly_dark"
            )
            fig_growth.update_layout(
                margin=dict(l=20, r=20, t=40, b=20), 
                height=380, 
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_growth, use_container_width=True)

        # --- SCANNABLE INSIGHT FOOTER ---
        st.markdown("---")
        st.markdown("### 🧭 Strategic Intelligence Observations")
        obs_col1, obs_col2 = st.columns(2)
        with obs_col1:
            st.markdown(
                """
                **1. Structural Volatility Analysis**
                * The **Growth Percentage Bar Chart** clearly exposes structural shocks.
                * Look for down-spikes representing global economic stress events.
                * Long consecutive green bars indicate consistent domestic stability.
                """
            )
        with obs_col2:
            st.markdown(
                """
                **2. Production Milestones**
                * The **GDP Volume Area Chart** maps the speed of capital accumulation.
                * Rapid curve steepening indicates transition into advanced industrial phases.
                * Stagnating flat regions highlight middle-income traps or structural plateaus.
                """
            )


 #########################################################################################################       

elif selected == "GDP Trends":
    st.title("📈 Historical GDP Trajectories")
    st.write("Analyze and compare macroeconomic growth timelines across eras.")

    try:
        df = load_data()
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.stop()


    # --- 🛠️ SAFE AND AGGRESSIVE AGGREGATE FILTERING (FIXED) ---
    aggregates_to_ban = [
        "income", "total", "only", "blend", "world", 
        "europe &", "america &", "east asia",
          
    ]
    
    # Parentheses added around both conditions to force correct operator order
    for word in aggregates_to_ban:
        df = df[
            (~df["country"].str.lower().str.contains(word, na=False)) | 
            (df["country"].str.lower().str.contains("united states", na=False))
        ]

    # --- 2. Interactive Filters ---
    st.markdown("### 🎛️ Analysis Controls")
    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        all_regions = sorted(df["region"].unique())
        # FIX: Set default=all_regions so all continents load instantly, showing the USA immediately!
        selected_regions = st.multiselect(
            "Filter by Continents:", 
            options=all_regions, 
            default=all_regions 
        )


    trend_df = df[df["region"].isin(selected_regions)]

    with filter_col2:
        min_year, max_year = int(df["year"].min()), int(df["year"].max())
        start_yr, end_yr = st.slider(
            "Select Timeframe Range:", 
            min_value=min_year, 
            max_value=max_year, 
            value=(min_year, max_year)
        )

    trend_df = trend_df[(trend_df["year"] >= start_yr) & (trend_df["year"] <= end_yr)]

    if trend_df.empty:
        st.warning("No data points found matching selected criteria.")
    else:
        # --- 3. Summary Performance Context Cards ---
        st.markdown("---")
        st.markdown("### 📊 Period Summary Metrics")
        
        top_country_row = trend_df.loc[trend_df["gdp_billions"].idxmax()]
        total_gdp_period = trend_df[trend_df["year"] == end_yr]["gdp_billions"].sum()
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(
                label=f"Peak Era Economy ({top_country_row['year']})", 
                value=f"{top_country_row['country']}", 
                delta=f"${top_country_row['gdp_billions']:,.0f}B"
            )
        with c2:
            st.metric(
                label=f"Combined Selected GDP ({end_yr})", 
                value=f"${total_gdp_period/1000:.2f}T" if total_gdp_period >= 1000 else f"${total_gdp_period:,.0f}B"
            )
        with c3:
            avg_growth_rate = trend_df["gdp_growth"].mean()
            st.metric(
                label="Average Growth Rate (Era)", 
                value=f"{avg_growth_rate:.2f}%" if pd.notna(avg_growth_rate) else "N/A"
            )

        # --- 4. Refined Charting Layout with Clean Legend Placement ---
        st.markdown("---")
        st.markdown("### 📈 Longitudinal GDP Growth Trajectories")
        
        # Isolate the top 8 actual countries to maximize legibility 
        top_economies = trend_df[trend_df["year"] == end_yr].nlargest(8, "gdp_billions")["country"].tolist()
        chart_df = trend_df[trend_df["country"].isin(top_economies)].sort_values("year")

        fig_trends = px.line(
            chart_df,
            x="year",
            y="gdp_billions",
            color="country",
            title=f"Macroeconomic Trajectories of Top Economies ({start_yr} - {end_yr})",
            labels={"gdp_billions": "Nominal GDP (USD Billions)", "year": "Year", "country": "Country"},
            template="plotly_dark"
        )

        # Layout adjustments to prevent title/legend collision
        fig_trends.update_layout(
            hovermode="x unified",
            xaxis=dict(
                rangeslider=dict(visible=True),
                type="linear",
                showgrid=True,
                gridcolor="#2c304d"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#2c304d"
            ),
            # Clean layout fix: Moves the legend block safely to the right panel 
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            ),
            margin=dict(l=40, r=150, t=80, b=40),
            height=600
        )
        
        fig_trends.update_traces(line=dict(width=3))
        st.plotly_chart(fig_trends, use_container_width=True)

        st.markdown("### 🧭 Key Insights for Recruiters")
        st.markdown(
            """
            - **Market Dominance**: The line graph isolates the largest valid country economies inside your selection to guarantee visual fidelity.
            - **Macro Shocks Visibility**: Scrub the timeline slider at the bottom to zoom into specific eras like the 2008 crash or 2020 shifts.
            """
        )


################################################################################################################    

elif selected == "Global Map":
    st.title("🗺️ Geographic Macroeconomic Overview")
    st.write("Examine the spatial distribution of global wealth and production density across hemispheres.")

    # 1. Load the data safely
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.stop()    

    # --- 2. Advanced Controls (Year and Scale Toggles) ---
    st.markdown("### 🎛️ Map Controls")
    ctrl_col1, ctrl_col2 = st.columns(2)
    
    with ctrl_col1:
        # Dynamically fetch available years for recruiters to slide through time
        available_years = sorted(df['year'].unique(), reverse=True)
        selected_year = st.selectbox("Select Target Year:", available_years, index=0)
    
    with ctrl_col2:
        # Crucial Recruiter Feature: Toggle between linear and log scale to handle wealth variance
        scale_type = st.radio(
            "Color Scaling Type:",
            options=["Standard (Linear)", "Enhanced Variance (Logarithmic)"],
            horizontal=True,
            help="Logarithmic scaling prevents dominant super-economies from washing out smaller nations."
        )

    # Filter data for selected parameters
    df_latest = df[(df['year'] == selected_year) & df['country_code'].notna()].copy()

    # Calculate color parameters based on user selection
    if scale_type == "Enhanced Variance (Logarithmic)":
        import numpy as np
        # Avoid log(0) issues by forcing a tiny positive lower bound
        df_latest['color_value'] = np.log10(df_latest['gdp_billions'].clip(lower=0.1))
        colorbar_title = "GDP Scale<br>(Log10 Billions)"
    else:
        df_latest['color_value'] = df_latest['gdp_billions']
        colorbar_title = "GDP<br>Billions ($)"

    # --- 3. Optimized Choropleth Implementation ---
    fig = px.choropleth(
        df_latest,
        locations='country_code',
        color='color_value',
        hover_name='country',
        hover_data={
            "region": True,
            "gdp_billions": ":,.0f",
            "color_value": False
        },
        color_continuous_scale=px.colors.sequential.Viridis, # Cleaner, high-contrast palette
        projection="natural earth",
        template="plotly_dark"
    )

    # 4. Refine layout parameters (Removed duplicate title string completely)
    fig.update_layout(
        geo=dict(
            showframe=False, 
            showcoastlines=True,
            coastlinecolor="#2c304d",
            showland=True,
            landcolor="#1a1c2e",
            showcountries=True,
            countrycolor="#4b507d",
            bgcolor="#0e1117",
            showocean=True,
            oceancolor="#071633"
        ),
        coloraxis_colorbar=dict(
            title=colorbar_title,
            thickness=15,
            len=0.65,
            outlinewidth=0,
            ticks="outside"
        ),
        margin=dict(l=0, r=0, t=10, b=0), # Shaved top margin since title is handled natively
        height=550,
    )

    # Clean custom tooltip presentation
    fig.update_traces(
        hovertemplate=
        "<b>%{hovertext}</b><br><br>" +
        "Region: %{customdata[0]}<br>" +
        "Nominal GDP: <b>$%{customdata[1]}B US</b><extra></extra>"
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. Actionable Scannable Text Summary ---
    st.markdown("---")
    st.markdown(f"### 🧭 Spatial Intelligence Observations ({selected_year})")
    
    obs_col1, obs_col2 = st.columns(2)
    with obs_col1:
        st.markdown(
            """
            **1. Geographic Wealth Concentration**
            * The map highlights severe clustering of production scale within specific hubs.
            * The **Standard Scale** layout emphasizes the massive gap between superpowers and developing regions.
            * Toggle the timeline selector above to observe global wealth shifts over recent decades.
            """
        )
    with obs_col2:
        st.markdown(
            """
            **2. Regional Variance Resolution**
            * Switching to **Enhanced Variance (Logarithmic)** makes regional variance visible.
            * This mathematical transformation reveals the economic distribution of mid-tier economies.
            * Unshaded land masses represent data exceptions or localized regional aggregates that were bypassed.
            """
        )

  #######################################################################################################################    

# Add fallback placeholders for remaining empty routes so Streamlit compiles correctly
elif selected == "Compare Countries":
    st.title("📊 Cross-Border Economic Correlation Matrix")
    st.write("Perform multi-dimensional benchmarking to evaluate growth efficiency, risk factor volatility, and historical resilience between two chosen economies.")

    try:
        df = load_data()
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.stop()

    # --- 1. Symmetrical Dual Selection Dropdowns ---
    st.markdown("### 🎛️ Select Comparison Assets")
    col_filter1, col_filter2 = st.columns(2)

    with col_filter1:
        st.markdown("#### **🏳️‍🌈 Asset Profile A**")
        region_list_a = sorted(df["region"].unique())
        selected_region_a = st.selectbox("Filter Continent (A):", region_list_a, key="reg_a")
        
        filtered_df_a = df[df["region"] == selected_region_a]
        country_list_a = sorted(filtered_df_a["country"].unique())
        default_idx_a = country_list_a.index("Japan") if "Japan" in country_list_a else 0
        selected_country_a = st.selectbox("Target Nation (A):", country_list_a, index=default_idx_a, key="cnt_a")

    with col_filter2:
        st.markdown("#### **🏳️‍🌈 Asset Profile B**")
        region_list_b = sorted(df["region"].unique())
        selected_region_b = st.selectbox("Filter Continent (B):", region_list_b, key="reg_b")
        
        filtered_df_b = df[df["region"] == selected_region_b]
        country_list_b = sorted(filtered_df_b["country"].unique())
        default_idx_b = country_list_b.index("Germany") if "Germany" in country_list_b else 0
        selected_country_b = st.selectbox("Target Nation (B):", country_list_b, index=default_idx_b, key="cnt_b")

    # Isolate data frames for individual metrics calculations
    df_a = df[df["country"] == selected_country_a].sort_values("year")
    df_b = df[df["country"] == selected_country_b].sort_values("year")

    if df_a.empty or df_b.empty:
        st.warning("Please choose valid country targets to compile the comparison matrix.")
    else:
        # --- 2. Live Metrics Benchmark Cards ---
        st.markdown("---")
        st.markdown("### 📊 Head-to-Head Structural Summary")
        
        latest_a = df_a.iloc[-1]
        latest_b = df_b.iloc[-1]
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(
                label="Current Nominal GDP Volume",
                value=f"{selected_country_a}: ${latest_a['gdp_billions']:,.1f}B",
                delta=f"{selected_country_b}: ${latest_b['gdp_billions']:,.1f}B",
                delta_color="off" 
            )
        with m2:
            st.metric(
                label="Historical Expansion Velocity (Avg)",
                value=f"{selected_country_a}: {df_a['gdp_growth'].mean():.2f}%",
                delta=f"{selected_country_b}: {df_b['gdp_growth'].mean():.2f}%",
                delta_color="off"
            )
        with m3:
            st.metric(
                label="World Bank Classification",
                value=f"{selected_country_a}: {latest_a['income_group']}",
                delta=f"{selected_country_b}: {latest_b['income_group']}",
                delta_color="off"
            )

        # --- 3. The Showstopper Visualization Interface ---
        st.markdown("---")
        st.markdown("### 📊 Advanced Correlation Dashboard")
        
        chart_col1, chart_col2 = st.columns(2)
        
        # Merge both datasets for multi-variable plotting
        compare_df = pd.concat([df_a, df_b]).sort_values("year")
        
        with chart_col1:
            st.markdown("#### **Growth Velocity vs Economic Scale Matrix**")
            # Scatter Plot: Removes timeline linear tracking to isolate efficiency clustering
            fig_scatter = px.scatter(
                compare_df,
                x="gdp_billions",
                y="gdp_growth",
                color="country",
                size="gdp_billions",
                hover_data=["year"],
                title="Economic Scale vs YoY Expansion Speed",
                labels={"gdp_billions": "GDP Scale ($ Billions)", "gdp_growth": "YoY Growth Rate (%)"},
                template="plotly_dark"
            )
            fig_scatter.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig_scatter.update_traces(marker=dict(opacity=0.75, line=dict(width=1, color="white")))
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with chart_col2:
            st.markdown("#### **Decadal Distribution Comparison**")
            # Select key anchor points over time to prevent a messy layout
            decades = [1970, 1980, 1990, 2000, 2010, 2020]
            bar_df = compare_df[compare_df["year"].isin(decades)].copy()
            
            # Bar Chart: Grouped breakdown comparing specific structural time brackets
                       # Bar Chart: Grouped breakdown comparing specific structural time brackets
            fig_bar = px.bar(
                bar_df,
                x="year",
                y="gdp_billions",
                color="country",
                barmode="group",  # <-- FIXED: Changed from bgroupmode to barmode
                title="Structural GDP Volume by Decade",
                labels={"gdp_billions": "GDP Volume ($ Billions)", "year": "Decade Milestone"},
                template="plotly_dark"
            )
            fig_bar.update_layout(
                barmode="group",
                margin=dict(l=20, r=20, t=40, b=20),
                height=400,
                xaxis=dict(type='category'), # Forces specific decade labels instead of a slider range
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_bar, use_container_width=True)


        # --- 4. Actionable Scannable Text Summary ---
        st.markdown("---")
        st.markdown("### 🧭 Cross-Border Benchmark Insights")
        
        obs_col1, obs_col2 = st.columns(2)
        with obs_col1:
            st.markdown(
                """
                **1. Efficiency vs Scale Dynamics**
                * The **Scatter Plot Matrix** drops the simple timeline view to cross-reference volume against pure expansion speed.
                * Clusters high on the Y-axis indicate periods of efficient, high-speed development.
                * Clusters further to the right display massive production volume, often accompanied by stabilized, slower growth rates.
                """
            )
        with obs_col2:
            st.markdown(
                """
                **2. Decadal Structural Shifts**
                * The **Decadal Bar Graph** filters out the continuous line trends, isolating specific structural intervals instead.
                * Comparing the height differences between paired bars reveals when competitive shifts or catch-up growth cycles occurred.
                """
            )

############################################################################################################################

elif selected == "Data Explorer":
    st.title("🗂️ Global Macroeconomic Repository Explorer")
    st.write("Query, filter, and extract custom slices of the master macroeconomic ledger using granular parameters.")

    try:
        df = load_data()
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.stop()

    # --- 1. Advanced Structural Query Filters ---
    st.markdown("### 🎛️ Query Criteria Builders")
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        # Multi-select region picker
        available_regions = sorted(df["region"].unique())
        selected_regions = st.multiselect(
            "Filter Regions:", 
            options=available_regions, 
            default=available_regions
        )

    # Apply initial region filter
    explorer_df = df[df["region"].isin(selected_regions)]

    with filter_col2:
        # Dynamic country list based on chosen regions
        available_countries = sorted(explorer_df["country"].unique())
        selected_countries = st.multiselect(
            "Filter Specific Countries:", 
            options=available_countries, 
            default=available_countries[:5] if len(available_countries) >= 5 else available_countries,
            help="Leave empty or modify selections to scope down rows."
        )

    if selected_countries:
        explorer_df = explorer_df[explorer_df["country"].isin(selected_countries)]

    with filter_col3:
        # Metric bounding thresholds
        min_gdp, max_gdp = float(df["gdp_billions"].min()), float(df["gdp_billions"].max())
        gdp_range = st.slider(
            "GDP Threshold Scope ($ Billions):",
            min_value=min_gdp,
            max_value=max_gdp,
            value=(min_gdp, max_gdp)
        )

    # Final dataframe adjustments
    explorer_df = explorer_df[
        (explorer_df["gdp_billions"] >= gdp_range[0]) & 
        (explorer_df["gdp_billions"] <= gdp_range[1])
    ].sort_values(["country", "year"], ascending=[True, False])

    # --- 2. Live Data Quality and Profile Summaries ---
    st.markdown("---")
    st.markdown("### 📊 Dataset Integrity Profile")
    
    stat1, stat2, stat3 = st.columns(3)
    with stat1:
        st.metric(label="Rows Returned", value=f"{len(explorer_df):,}")
    with stat2:
        # Compute exact active memory usage to show advanced technical awareness
        memory_usage_kb = explorer_df.memory_usage(deep=True).sum() / 1024
        st.metric(label="RAM Allocation Footprint", value=f"{memory_usage_kb:.2f} KB")
    with stat3:
        # Add a download link for recruiters to test export tools
        csv_data = explorer_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Cleaned CSV Slice",
            data=csv_data,
            file_name="macro_custom_slice.csv",
            mime="text/csv",
            use_container_width=True
        )

    # --- 3. Clean Interactive Table Rendering ---
    st.markdown("---")
    st.markdown("### 📋 Dynamic Query Result Ledger")
    
    if explorer_df.empty:
        st.warning("No rows matched your exact structural query constraints. Loosen filter boundaries.")
    else:
        # Present clean column ordering for recruiter eyes
        display_cols = ["year", "country", "country_code", "region", "gdp_billions", "gdp_growth", "income_group"]
        
        # Round decimals inside display view for extreme polish
        formatted_df = explorer_df[display_cols].copy()
        formatted_df["gdp_billions"] = formatted_df["gdp_billions"].round(2)
        formatted_df["gdp_growth"] = formatted_df["gdp_growth"].round(2)
        
        # Display high-utility interactive data frame
        st.dataframe(
            formatted_df,
            use_container_width=True,
            hide_index=True
        )

#######################################################################################################################################    

elif selected == "About":
    st.title("ℹ️ About This Project")
    st.write("Learn about the purpose of this project, the tools used, and the person behind the dashboard.")

    st.markdown("---")

    # --- 1. Strategic Portfolio Split Layout ---
    col_about1, col_about2 = st.columns([2, 1])

    with col_about1:
        st.markdown("## 🎯 Platform Objective")
        st.markdown(
            """
            The **Global Economic Intelligence Platform** was built to turn raw, fragmented macroeconomic records 
            into structured, actionable business intelligence. Covering data from **1960 through 2025**, 
            the dashboard automates data cleaning, standardizes political boundaries, and handles highly skewed wealth 
            distributions to give researchers and analysts a clear view of global trends.
            """
        )

        st.markdown("## 📌 What This Project Does")
        st.markdown("""
        - Cleaned missing and inconsistent data.
        - Standardized country names and regions for accurate analysis.
        - Created interactive charts and maps to explore economic trends.
        - Added filters so users can compare countries, regions, and indicators easily.
        - Used logarithmic scaling where necessary to better visualize very large differences between countries."""
        )

    with col_about2:
        st.markdown("### 👩‍💻 About the Author")
        # Visual profile wrapper card
        st.image("assets/profile.png", width=300)  
        st.info(
            """
            **Mylene Gadeau**  
            *Data Analyst*  

            I enjoy cleaning, analyzing, and visualizing data to uncover meaningful insights. This project demonstrates my skills in Python, SQL, data cleaning, exploratory analysis, and dashboard development.
            """
        )
        
        st.markdown(
    """
    * 💼 **LinkedIn Profile**: [nicole-gadeau](www.linkedin.com/in/nicole-gadeau)
    * 💻 **Project Repository**: [https://github.com/mylenegadeau-lang/Global-Economic-Intelligence-Platform](https://github.com/mylenegadeau-lang/Global-Economic-Intelligence-Platform)
    * 📧 **Direct Inquiry**: [Send Email](mailto:mylenegadeau@example.com)
    """
        )



    # --- 2. Live Technical Stack Breakdown Matrix ---
    st.markdown("---")
    st.markdown("### 🛠️ Production Stack Dependencies")
    
    tech1, tech2, tech3, tech4 = st.columns(4)
    with tech1:
        st.markdown("#### **🐍 Python Core**")
        st.caption("Used to clean the data, perform calculations, and build the dashboard..")
    with tech2:
        st.markdown("#### **🐼 Pandas Library**")
        st.caption("Used to organize, clean, and analyze the dataset.")
    with tech3:
        st.markdown("#### **📊 Plotly Engine**")
        st.caption("Used to create interactive charts and maps.")
    with tech4:
        st.markdown("#### **🌍 Country Converter**")
        st.caption("Used to match countries with their regions and continents for accurate visualizations.")

    st.markdown("---")
    st.caption("🚀 Platform Version 1.2.0 • Maintained with strict performance standards.")



