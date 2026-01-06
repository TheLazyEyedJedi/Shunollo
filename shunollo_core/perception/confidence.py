"""
confidence.py - Statistical Certainty
-------------------------------------
Provides mathematical tools for agent verification.
Move away from "I saw this 5 times" to "I am 95% confident".
"""
import math

def calculate_wilson_score(positive: int, total: int, z: float = 1.96) -> float:
    """
    Calculate the lower bound of the Wilson Score Interval.
    Used for rating systems with small sample sizes.
    
    :param positive: Number of positive outcomes (Success/True Positive)
    :param total: Total number of trials
    :param z: Z-statistic (1.96 for 95% confidence)
    :return: Lower bound probability (0.0 - 1.0)
    """
    if total == 0:
        return 0.0
        
    phat = positive / total
    
    # Wilson Score Interval Formula
    # (phat + z*z/(2*n) - z * sqrt((phat*(1-phat) + z*z/(4*n))/n)) / (1 + z*z/n)
    
    n = total
    numerator = phat + (z*z) / (2*n) - z * math.sqrt((phat * (1 - phat) + (z*z) / (4*n)) / n)
    denominator = 1 + (z*z) / n
    
    return max(0.0, numerator / denominator)
