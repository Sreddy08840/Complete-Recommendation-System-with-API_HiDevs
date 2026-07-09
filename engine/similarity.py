
"""
Similarity algorithms for recommendation systems.

This module provides implementations of:
- Cosine Similarity
- Jaccard Similarity
- Pearson Correlation
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine_similarity


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.

    Cosine similarity measures the cosine of the angle between two vectors,
    ranging from -1 (opposite) to 1 (exact same direction).

    Args:
        vec_a: First input vector (1D numpy array)
        vec_b: Second input vector (1D numpy array)

    Returns:
        Cosine similarity score between vec_a and vec_b

    Examples:
        >>> import numpy as np
        >>> a = np.array([1, 2, 3])
        >>> b = np.array([4, 5, 6])
        >>> cosine_similarity(a, b)
        0.9746318371790309
    """
    # Reshape vectors to 2D for sklearn
    vec_a_2d = vec_a.reshape(1, -1)
    vec_b_2d = vec_b.reshape(1, -1)
    return float(sk_cosine_similarity(vec_a_2d, vec_b_2d)[0][0])


def jaccard_similarity(set_a: set, set_b: set) -> float:
    """
    Compute Jaccard similarity between two sets.

    Jaccard similarity is the size of the intersection divided by
    the size of the union of two sets, ranging from 0 (no overlap)
    to 1 (identical sets).

    Args:
        set_a: First input set
        set_b: Second input set

    Returns:
        Jaccard similarity score between set_a and set_b

    Examples:
        >>> a = {1, 2, 3}
        >>> b = {2, 3, 4}
        >>> jaccard_similarity(a, b)
        0.5
    """
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union != 0 else 0.0


def pearson_correlation(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute Pearson correlation coefficient between two arrays.

    Pearson correlation measures linear correlation between two variables,
    ranging from -1 (perfect negative correlation) to 1 (perfect positive
    correlation), with 0 indicating no linear correlation.

    Args:
        x: First input array (1D numpy array)
        y: Second input array (1D numpy array)

    Returns:
        Pearson correlation coefficient between x and y

    Examples:
        >>> import numpy as np
        >>> x = np.array([1, 2, 3, 4, 5])
        >>> y = np.array([2, 4, 6, 8, 10])
        >>> pearson_correlation(x, y)
        1.0
    """
    # Compute mean of x and y
    mean_x = np.mean(x)
    mean_y = np.mean(y)

    # Compute covariance and standard deviations
    covariance = np.sum((x - mean_x) * (y - mean_y))
    std_x = np.sqrt(np.sum((x - mean_x) ** 2))
    std_y = np.sqrt(np.sum((y - mean_y) ** 2))

    # Avoid division by zero
    if std_x == 0 or std_y == 0:
        return 0.0

    return covariance / (std_x * std_y)


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("Similarity Algorithms - Example Usage")
    print("=" * 60)

    # Cosine similarity example
    print("\n--- Cosine Similarity ---")
    a = np.array([1, 2, 3, 4, 5])
    b = np.array([2, 4, 6, 8, 10])
    c = np.array([5, 4, 3, 2, 1])
    print(f"Vector a: {a}")
    print(f"Vector b: {b}")
    print(f"Vector c: {c}")
    print(f"Cosine(a, b): {cosine_similarity(a, b):.4f}")
    print(f"Cosine(a, c): {cosine_similarity(a, c):.4f}")

    # Jaccard similarity example
    print("\n--- Jaccard Similarity ---")
    set1 = {1, 2, 3, 4, 5}
    set2 = {4, 5, 6, 7, 8}
    set3 = {1, 2, 3}
    print(f"Set 1: {set1}")
    print(f"Set 2: {set2}")
    print(f"Set 3: {set3}")
    print(f"Jaccard(set1, set2): {jaccard_similarity(set1, set2):.4f}")
    print(f"Jaccard(set1, set3): {jaccard_similarity(set1, set3):.4f}")

    # Pearson correlation example
    print("\n--- Pearson Correlation ---")
    x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    y = np.array([2, 4, 5, 8, 10, 11, 14, 16, 18, 20])
    z = np.array([10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
    print(f"x: {x}")
    print(f"y: {y}")
    print(f"z: {z}")
    print(f"Pearson(x, y): {pearson_correlation(x, y):.4f}")
    print(f"Pearson(x, z): {pearson_correlation(x, z):.4f}")
