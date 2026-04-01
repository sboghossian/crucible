"""Dataset exploration and profiling team — Data Science."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="dataset_explorer",
    description="Profiles, cleans, and develops analytical hypotheses for a dataset, producing an EDA report and analysis plan.",
    category="Data Science",
    tags=["data science", "eda", "exploratory data analysis", "data quality", "statistics", "python"],
    agents=[
        AgentSpec(
            name="Data Profiler",
            role="Statistical summary and data quality specialist",
            instructions=(
                "You are a data scientist specializing in exploratory data analysis. For the described dataset, produce: "
                "schema documentation (column names, data types, descriptions), "
                "statistical summary (for numeric columns: mean, median, std, min, max, skewness; "
                "for categorical: cardinality, top values, mode), "
                "missing data analysis (which columns, what pattern: MCAR, MAR, or MNAR?), "
                "outlier detection approach (IQR, z-score, domain knowledge thresholds), "
                "and data freshness / temporal coverage assessment."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Quality Engineer",
            role="Data cleaning and validation specialist",
            instructions=(
                "You are a data quality engineer. Produce: "
                "data quality issues inventory (nulls, duplicates, inconsistent formats, impossible values), "
                "cleaning strategy for each issue (imputation method, deduplication logic, normalization), "
                "validation rules to enforce (business logic constraints), "
                "data lineage questions (where did this data come from, what transformations were applied?), "
                "and a data quality score framework (dimensions: completeness, accuracy, consistency, timeliness)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Hypothesis Generator",
            role="Analytical hypothesis and research question specialist",
            instructions=(
                "You are an analytical strategist. Based on the dataset description, generate: "
                "10 analytical hypotheses worth testing (business questions the data can answer), "
                "key relationships to explore (which variable pairs are likely correlated?), "
                "segmentation hypotheses (which groups behave differently?), "
                "anomaly investigation directions (what anomalies are most business-relevant?), "
                "and a prioritized analysis roadmap (which questions to answer first and why)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Visualization Planner",
            role="Data visualization and storytelling specialist",
            instructions=(
                "You are a data visualization specialist. Design: "
                "EDA visualization plan (which chart type for which question: histogram, scatter, heatmap, box plot), "
                "distribution visualizations for key variables, "
                "correlation analysis approach (Pearson, Spearman, or Cramér's V for categorical), "
                "time series decomposition approach if temporal data is present, "
                "Python code outline (pandas, matplotlib/seaborn/plotly) for the 5 most important EDA charts, "
                "and a dashboard layout for communicating findings to stakeholders."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "What analytical question should be prioritized given the dataset's characteristics?",
        "Descriptive analysis (understand what is currently happening before hypothesizing why)",
        "Predictive analysis (identify variables that predict the key outcome metric)",
        "Anomaly detection (find the outliers, they often contain the most actionable insights)",
        "Segmentation (find natural clusters that behave differently)",
    ],
    expected_outputs=[
        "Dataset schema documentation",
        "Statistical summary per column",
        "Data quality issues inventory with cleaning strategy",
        "10 analytical hypotheses ranked by business value",
        "EDA visualization plan with chart specifications",
        "Python code outline for top 5 EDA charts",
        "Prioritized analysis roadmap",
    ],
))
