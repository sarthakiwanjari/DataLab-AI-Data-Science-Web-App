import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from core.preprocessing import prepare_features

def run_clustering(df, clusters=3):
    if not 2 <= clusters <= 10:
        raise ValueError("Choose between 2 and 10 clusters.")
    data = df.dropna(axis=1, how="all").copy()
    if len(data) < clusters + 2:
        raise ValueError("Upload more rows than the number of requested clusters.")
    if data.shape[1] < 1:
        raise ValueError("No usable columns were found.")
    prep, _, _ = prepare_features(data)
    X = prep.fit_transform(data)
    if X.shape[1] == 0:
        raise ValueError("No usable features remain after preprocessing.")
    model = KMeans(n_clusters=clusters, random_state=42, n_init=10)
    labels = model.fit_predict(X)
    score = None
    if len(set(labels)) > 1 and len(data) > len(set(labels)) and len(data) <= 10000:
        score = round(float(silhouette_score(X, labels)), 4)
    counts = pd.Series(labels).value_counts().sort_index()
    return {
        "task": "Clustering", "algorithm": "K-Means", "clusters": int(clusters),
        "rows_clustered": int(len(data)), "cluster_counts": [
            {"cluster": f"Cluster {int(i)+1}", "count": int(n)} for i, n in counts.items()
        ],
        "silhouette_score": score,
        "note": "Clusters are mathematical groupings. Interpret them using domain context before making decisions."
    }
