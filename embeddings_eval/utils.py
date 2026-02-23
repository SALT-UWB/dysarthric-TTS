import numpy as np
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None # Define as None to avoid UnboundLocalError

def calculate_cosine_distance(vec1, vec2):
    """Calculates cosine distance (1 - cosine similarity)."""
    if HAS_TORCH and isinstance(vec1, torch.Tensor) and isinstance(vec2, torch.Tensor):
        import torch.nn.functional as F
        # Similarity between vectors
        similarity = F.cosine_similarity(vec1.unsqueeze(0), vec2.unsqueeze(0)).item()
        return 1.0 - float(similarity)
    
    # Fallback to numpy
    v1 = np.array(vec1).flatten()
    v2 = np.array(vec2).flatten()
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 1.0 # Max distance if one vector is zero
    similarity = np.dot(v1, v2) / (norm1 * norm2)
    return 1.0 - float(similarity)

def calculate_centroid(vectors):
    """Calculates the mean vector (centroid) of a list of vectors."""
    if not vectors:
        return None
    
    if HAS_TORCH and isinstance(vectors[0], torch.Tensor):
        stacked = torch.stack(vectors)
        return torch.mean(stacked, dim=0)
    
    # Fallback to numpy
    return np.mean(vectors, axis=0)
