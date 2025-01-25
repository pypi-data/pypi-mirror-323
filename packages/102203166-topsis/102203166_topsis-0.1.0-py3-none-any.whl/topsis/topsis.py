import numpy as np

def topsis(data, weights, impacts):
    if len(weights) != data.shape[1] or len(impacts) != data.shape[1]:
        raise ValueError("Length of weights and impacts must match the number of criteria.")

    norm_data = data / np.sqrt((data**2).sum(axis=0))

    weighted_data = norm_data * weights

    ideal_best = []
    ideal_worst = []
    for i, impact in enumerate(impacts):
        if impact == '+':
            ideal_best.append(weighted_data[:, i].max())
            ideal_worst.append(weighted_data[:, i].min())
        elif impact == '-':
            ideal_best.append(weighted_data[:, i].min())
            ideal_worst.append(weighted_data[:, i].max())
        else:
            raise ValueError("Impacts should be '+' or '-'.")
    
    ideal_best = np.array(ideal_best)
    ideal_worst = np.array(ideal_worst)
 
    dist_best = np.sqrt(((weighted_data - ideal_best)**2).sum(axis=1))
    dist_worst = np.sqrt(((weighted_data - ideal_worst)**2).sum(axis=1))
  
    scores = dist_worst / (dist_best + dist_worst)
    return scores
