import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, normalize,  PowerTransformer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn import metrics
from scipy.spatial.distance import cdist
import numpy as np
from kneed import KneeLocator
from statistics import mean
import os 

def langs_to_num(row):
    row = eval(row)
    row = [i for a,i in enumerate(row) if i!='']
    return len(row)

def analyse(username, repo):
    df = pd.read_csv(f'./data/{username}/{repo}.csv', index_col=0) 

    # Шаг 1: Подготовка данных
    # Проверка и очистка данных:
    # Так как количество языков недостаточно, чтобы выявить направление специализации разработчика, 
    # то переведем данный признак в численное количество приобретенных навыков.

    df['Languages'] = df['Languages'].apply(langs_to_num)
    df = df.drop(['FirstDataActivity'], axis=1)
    df = df.drop(['LastDataActivity'], axis=1)

    # Удалять дубликаты, обрабатывать пропуски нам не нужно. Перейдем к корреляции признаков.
    # Стоит обратить внимание на признаки с высокой корреляцией — тёмно-красные и тёмно-синие клетки. 
    # Близость к единице означает сильно выраженную положительную линейную зависимость, а близость к -1 — сильно выраженную отрицательную зависимость.

    # Заметна очень высокая положительная корреляция между притоком и оттоком кода. 
    # Возьмем разницу этих признаков и получим значение новых строчек кода в проекте, которые не изменялись.

    df['Add-Del'] = (df['Additions'] - df['Deletions'])
    df = df.drop(['Additions', 'Deletions'], axis=1)

    scaling=StandardScaler()
    scaling.fit(df)
    scaled_data=scaling.transform(df)

    X_normalized = normalize(scaled_data)
    X_normalized = pd.DataFrame(X_normalized)

    # Шаг 2: Предварительный анализ данных

    pt = PowerTransformer()
    pt.fit(X_normalized)
    X_transformed = pt.transform(X_normalized)
    X_transformed = pd.DataFrame(X_transformed)
    
    principal=PCA(n_components=3)
    principal.fit(X_transformed)
    x=principal.transform(X_transformed)

    distortions = []
    inertias = []
    K = range(1, 20)

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

    kmeans = KMeans(n_clusters=num_of_clusters, \
				init='k-means++', random_state=42)
    y_kmeans = kmeans.fit_predict(x)

    clusters_info = pd.DataFrame(columns=df.columns)

    if not os.path.exists(f'./data/{username}/web'): 
        os.makedirs(f'./data/{username}/web')
    else:
        for filename in os.listdir(f'./data/{username}/web'):
            file_path = os.path.join(f'./data/{username}/web', filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f'Ошибка при удалении файла {file_path}. {e}')

    for cluster in np.unique(y_kmeans):
        cluster_df = df[y_kmeans == cluster]
        
        sns.set(style='white')
        cluster_df.set_index(cluster_df.index).plot(kind='bar', stacked= True)
        cluster_info = {'Cluster': cluster}
        for col in df.columns:
            cluster_info[col] = str(min(cluster_df[col])) + ' - ' + str(max(cluster_df[col]))
        
        clusters_info.loc[len(clusters_info)] = cluster_info

        plt.ylabel('Number of actions')
        plt.xlabel('Login of programmer')
        plt.title(f'Cluster {cluster}')
        plt.savefig(f'./data/{username}/web/cluster_{cluster}.png')
        plt.close()
    
    clusters_info.to_csv(f'./data/{username}/web/clusters_info.csv', index=False)