from copy import deepcopy

from sklearn.metrics import average_precision_score, accuracy_score, roc_auc_score
from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve
import numpy as np


def find_best_threshold(y_true, y_pred):
    "We assume first half is real 0, and the second half is fake 1"

    N = y_true.shape[0]

    if y_pred[0:N//2].max() <= y_pred[N//2:N].min(): # perfectly separable case
        return (y_pred[0:N//2].max() + y_pred[N//2:N].min()) / 2 

    best_acc = 0 
    best_thres = 0 
    for thres in y_pred:
        temp = deepcopy(y_pred)
        temp[temp>=thres] = 1 
        temp[temp<thres] = 0 

        acc = (temp == y_true).sum() / N  
        if acc >= best_acc:
            best_thres = thres
            best_acc = acc 
    
    return best_thres


def find_best_acc_threshold(y_true, y_pred):
    thresholds = np.linspace(0, 1, 100)
    best_accuracy = 0
    best_threshold = 0

    for threshold in thresholds:
        accuracy = accuracy_score(y_true, y_pred > threshold)
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_threshold = threshold

    return best_threshold

 
def calculate_for_threshold(y_true, y_pred, thres):
    r_acc = accuracy_score(y_true[y_true==0], y_pred[y_true==0] > thres)
    f_acc = accuracy_score(y_true[y_true==1], y_pred[y_true==1] > thres)
    acc = accuracy_score(y_true, y_pred > thres)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred > thres).ravel()

    ppv = tp / (tp + fp) if (tp + fp) != 0 else 0  # Positive Predictive Value
    npv = tn / (tn + fn) if (tn + fn) != 0 else 0  # Negative Predictive Value
    tpr = tp / (tp + fn) if (tp + fn) != 0 else 0  # Recall (True Positive Rate)
    tnr = tn / (fp + tn) if (fp + tn) != 0 else 0  # True Negative Rate

    return { 
        'r_acc': r_acc, 'f_acc': f_acc, 'acc': acc, 
        'tn': tn, 'fp': fp, 'fn': fn, 'tp': tp, 
        'ppv': ppv, 'npv': npv, 'tpr': tpr, 'tnr': tnr 
    }   


def calculate_performance_metrics(y_true, y_pred, find_thres=False):

    metrics = { }

    # Get AP / precision - recall AUC
    metrics['ap'] = average_precision_score(y_true, y_pred)

    # Get ROC AUC   
    metrics['roc_auc'] = roc_auc_score(y_true, y_pred)

    metrics['roc_curve'] = roc_curve(y_true, y_pred, drop_intermediate=True)
    metrics['precision_recall_curve'] = precision_recall_curve(y_true, y_pred, drop_intermediate=True)
            
    # Acc based on 0.5
    metrics['threshold_05'] = calculate_for_threshold(y_true, y_pred, 0.5)

    if not find_thres:
        return metrics

    # Acc based on the best thres - oracle
    metrics['best_threshold'] = find_best_acc_threshold(y_true, y_pred)
    metrics['oracle_threshold'] = calculate_for_threshold(y_true, y_pred, metrics['best_threshold'])

    return metrics

