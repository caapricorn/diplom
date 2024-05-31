import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, normalize,  PowerTransformer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import cdist
import numpy as np
from kneed import KneeLocator
from statistics import mean
from utils import repo_exist, clean_user_data
import sys

def langs_to_num(row):
    row = eval(row)
    row = [i for a,i in enumerate(row) if i!='']
    return len(row)

def normalization(df):
    scaling=StandardScaler()
    scaling.fit(df)
    scaled_data=scaling.transform(df)

    X_normalized = normalize(scaled_data)
    X_normalized = pd.DataFrame(X_normalized)

    pt = PowerTransformer()
    pt.fit(X_normalized)
    X_transformed = pt.transform(X_normalized)
    X_transformed = pd.DataFrame(X_transformed)
    
    principal=PCA(n_components=3)
    principal.fit(X_transformed)
    x=principal.transform(X_transformed)
    return x

def elbow_method(x):
    distortions = []
    inertias = []
    K = range(1, len(x))

    for k in K:
        kmeanModel = KMeans(n_clusters=k).fit(x)
        distortions.append(sum(np.min(cdist(x, kmeanModel.cluster_centers_,
                                            'euclidean'), axis=1)) / x.shape[0])
        inertias.append(kmeanModel.inertia_)

    knee_locator_distortion = KneeLocator(K, distortions, curve='convex', direction='decreasing')
    knee_locator_inertia = KneeLocator(K, inertias, curve='convex', direction='decreasing')

    optimal_k_distortion = knee_locator_distortion.elbow
    optimal_k_inertia = knee_locator_inertia.elbow
    num_of_clusters = round(mean([optimal_k_distortion, optimal_k_inertia]))
    return num_of_clusters

def silhouette_analysis(x, key):
    range_n_clusters = range(3, len(x))
    silhouette_scores = []

    for n_clusters in range_n_clusters:
        if key == 'hierarchy':
            linked = linkage(x, method='ward')
            cluster_labels = fcluster(linked, n_clusters, criterion='maxclust')
        elif key == 'spectral':
            n_neighbors = min(n_clusters + 1, len(x) - 1)
            spectral = SpectralClustering(n_clusters=n_clusters, affinity='nearest_neighbors', n_neighbors=n_neighbors, assign_labels='kmeans')
            cluster_labels = spectral.fit_predict(x)
        silhouette_avg = silhouette_score(x, cluster_labels)
        silhouette_scores.append(silhouette_avg)

    optimal_clusters = range_n_clusters[np.argmax(silhouette_scores)]
    return optimal_clusters

def result_of_clustering(df, clusters, method, folder_name):
    clusters_info = pd.DataFrame(columns=df.columns)
    clean_user_data(f'./data/{folder_name}/web/{method}')
    for cluster in np.unique(clusters):
        cluster_df = df[clusters == cluster]
        
        sns.set(style='white')
        cluster_df.set_index(cluster_df.index).plot(kind='bar', stacked= True)
        cluster_info = {'Cluster': cluster}
        for col in df.columns:
            cluster_info[col] = str(min(cluster_df[col])) + ' - ' + str(max(cluster_df[col]))
        
        clusters_info.loc[len(clusters_info)] = cluster_info

        plt.ylabel('Number of actions')
        plt.xlabel('Login of programmer')
        plt.title(f'Cluster {cluster}')
        plt.savefig(f'./data/{folder_name}/web/{method}/cluster_{cluster}.png')
        plt.close()
    
    clusters_info.to_csv(f'./data/{folder_name}/web/{method}/clusters_info.csv', index=False)

def kmeans_clustering(num_of_clusters, x, df, folder_name):
    kmeans = KMeans(n_clusters=num_of_clusters, \
				init='k-means++', random_state=42)
    y_kmeans = kmeans.fit_predict(x)
    result_of_clustering(df, y_kmeans, 'K-means кластеризация', folder_name)

def hierarchy_clustering(x, df, folder_name):
    linked = linkage(x, method='ward')
    num_of_clusters = silhouette_analysis(x, 'hierarchy')
    cluster_labels = fcluster(linked, num_of_clusters, criterion='maxclust')
    result_of_clustering(df, cluster_labels, 'Иерархическая кластеризация', folder_name)

def spectral_clustering(x, df, folder_name):
    num_of_clusters = silhouette_analysis(x, 'spectral')
    n_neighbors = min(num_of_clusters + 1, len(x) - 1)
    spectral = SpectralClustering(n_clusters=num_of_clusters, affinity='nearest_neighbors', n_neighbors=n_neighbors, assign_labels='kmeans')
    labels = spectral.fit_predict(x)
    result_of_clustering(df, labels, 'Спектральная кластеризация', folder_name)

def analyse(username, repo, log = lambda x: print(x)):
    url = f'https://api.github.com/repos/{username}/{repo}'
    folder_name = f'{username}-{repo}'
    if not repo_exist(url, log):
        sys.exit(0)

    df = pd.read_csv(f'./data/{folder_name}/csv/data.csv', index_col=0) 

    df['Languages'] = df['Languages'].apply(langs_to_num)
    df = df.drop(['FirstDataActivity'], axis=1)
    df = df.drop(['LastDataActivity'], axis=1)

    x = normalization(df)

    num_of_clusters = elbow_method(x)

    clean_user_data(f'./data/{folder_name}/web')

    kmeans_clustering(num_of_clusters, x, df, folder_name) 

    hierarchy_clustering(x, df, folder_name)

    spectral_clustering(x, df, folder_name)