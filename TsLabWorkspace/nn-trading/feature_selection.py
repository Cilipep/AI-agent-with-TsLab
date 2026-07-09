"""Feature selection for reducing dimensionality."""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif, SelectKBest


def select_features_correlation(X: pd.DataFrame, y: pd.Series, max_features: int = 80) -> list:
    """Select features based on correlation with target."""
    corr = X.corrwith(y).abs()
    corr = corr.sort_values(ascending=False)
    return corr.head(max_features).index.tolist()


def select_features_importance(X: pd.DataFrame, y: pd.Series, max_features: int = 80) -> list:
    """Select features using Random Forest importance."""
    rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    importance = pd.Series(rf.feature_importances_, index=X.columns)
    importance = importance.sort_values(ascending=False)
    return importance.head(max_features).index.tolist()


def select_features_mutual_info(X: pd.DataFrame, y: pd.Series, max_features: int = 80) -> list:
    """Select features using mutual information."""
    mi = mutual_info_classif(X, y, random_state=42)
    mi_series = pd.Series(mi, index=X.columns)
    mi_series = mi_series.sort_values(ascending=False)
    return mi_series.head(max_features).index.tolist()


def select_features_combined(X: pd.DataFrame, y: pd.Series, max_features: int = 80) -> list:
    """Combine multiple selection methods for robust feature set."""
    # Get top features from each method (take top 120 from each)
    corr_features = set(select_features_correlation(X, y, min(120, len(X.columns))))
    importance_features = set(select_features_importance(X, y, min(120, len(X.columns))))
    mi_features = set(select_features_mutual_info(X, y, min(120, len(X.columns))))

    # Score: how many methods selected each feature
    all_features = list(set(list(corr_features) + list(importance_features) + list(mi_features)))
    scores = {}
    for f in all_features:
        score = (f in corr_features) + (f in importance_features) + (f in mi_features)
        scores[f] = score

    # Sort by score, then by importance
    sorted_features = sorted(scores.keys(), key=lambda x: (scores[x], x), reverse=True)
    return sorted_features[:max_features]


def apply_feature_selection(X_train: pd.DataFrame, y_train: pd.Series,
                           X_val: pd.DataFrame, max_features: int = 80) -> tuple:
    """Apply feature selection and return selected columns."""
    selected = select_features_combined(X_train, y_train, max_features)
    return X_train[selected], X_val[selected], selected
