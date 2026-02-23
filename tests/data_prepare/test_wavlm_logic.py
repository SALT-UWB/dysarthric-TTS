import pytest
import torch
import numpy as np
from embeddings_eval.utils import calculate_centroid, calculate_cosine_distance
from embeddings_eval.data_loader import EmbeddingFile
from embeddings_eval.analyzer import WavLMAnalyzer

def test_calculate_centroid():
    v1 = torch.tensor([1.0, 0.0])
    v2 = torch.tensor([0.0, 1.0])
    centroid = calculate_centroid([v1, v2])
    expected = torch.tensor([0.5, 0.5])
    assert torch.allclose(centroid, expected)

def test_calculate_cosine_distance():
    v1 = torch.tensor([1.0, 0.0])
    v2 = torch.tensor([1.0, 0.0])
    # Similarity 1.0 -> Distance 0.0
    assert calculate_cosine_distance(v1, v2) == pytest.approx(0.0)
    
    v3 = torch.tensor([0.0, 1.0])
    # Similarity 0.0 -> Distance 1.0
    assert calculate_cosine_distance(v1, v3) == pytest.approx(1.0)

def test_analyzer_centroids():
    # Setup mock embeddings
    e1 = EmbeddingFile(path="p1", speaker_id="001PD", health_status="PD", session="S1", group="ddk", vector=torch.tensor([1.0, 0.0]))
    e2 = EmbeddingFile(path="p2", speaker_id="001PD", health_status="PD", session="S1", group="ddk", vector=torch.tensor([0.0, 1.0]))
    e3 = EmbeddingFile(path="p3", speaker_id="002HC", health_status="HC", session="S1", group="ddk", vector=torch.tensor([1.0, 1.0]))
    
    analyzer = WavLMAnalyzer([e1, e2, e3])
    
    # Check speaker centroids
    assert "001PD" in analyzer.speaker_centroids
    assert "002HC" in analyzer.speaker_centroids
    assert torch.allclose(analyzer.speaker_centroids["001PD"].vector, torch.tensor([0.5, 0.5]))
    
    # Check group centroids
    assert analyzer.group_centroids["001PD"]["ddk"].group_id == "ddk"
    assert torch.allclose(analyzer.group_centroids["001PD"]["ddk"].vector, torch.tensor([0.5, 0.5]))

def test_analyzer_distances():
    e1 = EmbeddingFile(path="p1", speaker_id="001PD", health_status="PD", session="S1", group="ddk", vector=torch.tensor([1.0, 0.0]))
    e2 = EmbeddingFile(path="p2", speaker_id="001PD", health_status="PD", session="S1", group="ddk", vector=torch.tensor([0.0, 1.0]))
    e3 = EmbeddingFile(path="p3", speaker_id="002HC", health_status="HC", session="S1", group="ddk", vector=torch.tensor([1.0, 1.0]))
    
    analyzer = WavLMAnalyzer([e1, e2, e3])
    
    # Distances for e1
    dists = analyzer.get_hierarchical_distances(e1)
    # Own group/speaker centroid is [0.5, 0.5]. 
    # Cosine similarity between [1,0] and [0.5, 0.5] is 1/sqrt(2) approx 0.707
    # Distance is 1 - 0.707 = 0.293
    assert dists['dist_own_group'] == pytest.approx(1.0 - 1.0/np.sqrt(2))
    
    # Nearest other speaker for e1 is 002HC
    nearest_sid, dist = analyzer.find_nearest_other(e1)
    assert nearest_sid == "002HC"
    # [1,0] vs [1,1] -> sim = 1/sqrt(2)
    assert dist == pytest.approx(1.0 - 1.0/np.sqrt(2))
