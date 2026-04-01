"""ML pipeline design team — Data Science."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="ml_pipeline",
    description="Designs an end-to-end ML pipeline from feature engineering through deployment and monitoring.",
    category="Data Science",
    tags=["machine learning", "mlops", "pipeline", "model", "feature engineering", "deployment"],
    agents=[
        AgentSpec(
            name="ML Problem Framer",
            role="Problem formulation and baseline specialist",
            instructions=(
                "You are an ML product manager. Frame the ML problem correctly: "
                "business objective → ML objective mapping (maximize revenue? minimize churn?), "
                "supervised / unsupervised / reinforcement learning classification, "
                "label definition and quality assessment, "
                "baseline model (what is a simple heuristic or rule-based baseline to beat?), "
                "success metric selection (accuracy, AUC, precision, recall, F1, RMSE, NDCG — justify choice), "
                "and offline vs. online evaluation strategy."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Feature Engineer",
            role="Feature design and data transformation specialist",
            instructions=(
                "You are a feature engineering specialist. Design: "
                "raw features available and their quality assessment, "
                "derived features (transformations, interactions, aggregations), "
                "temporal features (lag features, rolling statistics, recency/frequency/monetary), "
                "categorical encoding strategy (one-hot, target encoding, embeddings), "
                "feature scaling approach, "
                "feature selection methodology (permutation importance, SHAP, RFE), "
                "and a feature store design recommendation."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Model Architect",
            role="Algorithm selection and training pipeline specialist",
            instructions=(
                "You are a machine learning engineer. Design: "
                "algorithm candidates with trade-off analysis (linear models vs. tree-based vs. neural), "
                "training pipeline architecture (data loading, preprocessing, training loop), "
                "hyperparameter search strategy (grid, random, Bayesian), "
                "cross-validation design (stratified k-fold, time-series split for temporal data), "
                "class imbalance handling strategy, "
                "regularization approach, "
                "and compute resource requirements."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="MLOps Engineer",
            role="Model deployment, monitoring, and lifecycle specialist",
            instructions=(
                "You are an MLOps engineer. Design: "
                "model serving architecture (REST API, batch inference, streaming), "
                "model registry and versioning approach, "
                "A/B testing framework for model rollout, "
                "data drift and model drift monitoring (which metrics to track, alert thresholds), "
                "retraining trigger strategy (scheduled vs. performance-triggered), "
                "and the full CI/CD pipeline for ML (from experiment to production)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "Which algorithm class best balances performance, interpretability, and maintainability for this use case?",
        "Gradient boosting (XGBoost/LightGBM): excellent tabular performance, moderate interpretability",
        "Neural network / deep learning: best for unstructured data, requires more data and compute",
        "Linear/logistic regression: fully interpretable, fast, often competitive with proper feature engineering",
        "Ensemble of simpler models: reliability over peak performance, easier to debug",
    ],
    expected_outputs=[
        "ML problem framing and success metrics",
        "Baseline model definition",
        "Feature engineering plan",
        "Algorithm comparison and recommendation",
        "Training pipeline architecture",
        "MLOps deployment architecture",
        "Drift monitoring strategy",
        "Retraining trigger policy",
    ],
))
