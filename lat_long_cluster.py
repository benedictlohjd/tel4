import pandas as pd
from k_means_constrained import KMeansConstrained

df = pd.read_csv("joined_lat_long.csv")

lat_long = df[["WS1_Postal_lat", "WS1_Postal_long"]]

clf = KMeansConstrained(
    n_clusters = len(lat_long)//4,  
    size_min=4,    
    size_max=5,    
    random_state=0 
)

res = clf.fit_predict(lat_long)

df['cluster_id'] = res

# df.to_csv('clusters.csv', index = False)
