from typing import List, Dict, Tuple, Optional
import torch
from .data_loader import EmbeddingFile, Centroid
from .utils import calculate_centroid, calculate_cosine_distance
from .constants import GROUP_DDK

class WavLMAnalyzer:
    def __init__(self, embeddings: List[EmbeddingFile]):
        self.embeddings = embeddings
        self.speaker_centroids: Dict[str, Dict[str, Centroid]] = {}
        self.group_centroids: Dict[str, Dict[str, Dict[str, Centroid]]] = {}
        self.versions = sorted(list(set(e.dataset_version for e in embeddings)))
        # Map speaker to metadata
        self.speaker_meta = {e.speaker_id: {'sex': e.sex, 'age': e.age, 'hy': e.hy} for e in embeddings}
        self._initialize_centroids()
        
        self.all_group_centroids: List[Centroid] = []
        for ver in self.group_centroids:
            for sid in self.group_centroids[ver]:
                for gid in self.group_centroids[ver][sid]:
                    self.all_group_centroids.append(self.group_centroids[ver][sid][gid])

    def _initialize_centroids(self):
        """Calculates all group and speaker centroids per version."""
        by_ver_speaker: Dict[str, Dict[str, List[torch.Tensor]]] = {}
        by_ver_speaker_group: Dict[str, Dict[str, Dict[str, List[torch.Tensor]]]] = {}
        
        for e in self.embeddings:
            ver = e.dataset_version
            if ver not in by_ver_speaker:
                by_ver_speaker[ver] = {}
                by_ver_speaker_group[ver] = {}
                self.speaker_centroids[ver] = {}
                self.group_centroids[ver] = {}
                
            if e.speaker_id not in by_ver_speaker[ver]:
                by_ver_speaker[ver][e.speaker_id] = []
                by_ver_speaker_group[ver][e.speaker_id] = {}
            
            if e.group != GROUP_DDK:
                by_ver_speaker[ver][e.speaker_id].append(e.vector)
            
            if e.group not in by_ver_speaker_group[ver][e.speaker_id]:
                by_ver_speaker_group[ver][e.speaker_id][e.group] = []
            
            by_ver_speaker_group[ver][e.speaker_id][e.group].append(e.vector)
            
        for ver in self.versions:
            for sid, vectors in by_ver_speaker[ver].items():
                if not vectors: continue
                vec = calculate_centroid(vectors)
                meta = self.speaker_meta.get(sid, {'sex': 'M', 'age': 0.0, 'hy': '0'})
                self.speaker_centroids[ver][sid] = Centroid(
                    type='speaker', speaker_id=sid, group_id=None, vector=vec, 
                    sex=meta['sex'], age=meta['age'], hy=meta['hy'], dataset_version=ver
                )
            
            for sid, groups in by_ver_speaker_group[ver].items():
                self.group_centroids[ver][sid] = {}
                meta = self.speaker_meta.get(sid, {'sex': 'M', 'age': 0.0, 'hy': '0'})
                for gid, vectors in groups.items():
                    vec = calculate_centroid(vectors)
                    self.group_centroids[ver][sid][gid] = Centroid(
                        type='group', speaker_id=sid, group_id=gid, vector=vec, 
                        sex=meta['sex'], age=meta['age'], hy=meta['hy'], dataset_version=ver
                    )

    def get_hierarchical_distances(self, embedding: EmbeddingFile) -> Dict[str, float]:
        ver = embedding.dataset_version
        sid = embedding.speaker_id
        gid = embedding.group
        dist_group = calculate_cosine_distance(embedding.vector, self.group_centroids[ver][sid][gid].vector)
        dist_speaker = 1.0
        if sid in self.speaker_centroids[ver]:
            dist_speaker = calculate_cosine_distance(embedding.vector, self.speaker_centroids[ver][sid].vector)
        return {'dist_own_group': dist_group, 'dist_own_speaker': dist_speaker}

    def find_nearest_speaker_centroid(self, embedding: EmbeddingFile) -> Tuple[str, float]:
        ver = embedding.dataset_version
        min_dist = float('inf')
        nearest_sid = None
        for sid, centroid in self.speaker_centroids[ver].items():
            if sid == embedding.speaker_id: continue
            dist = calculate_cosine_distance(embedding.vector, centroid.vector)
            if dist < min_dist:
                min_dist, nearest_sid = dist, sid
        return nearest_sid, min_dist

    def find_nearest_group_centroid(self, embedding: EmbeddingFile) -> Tuple[str, str, float]:
        ver = embedding.dataset_version
        min_dist = float('inf')
        nearest_sid, nearest_gid = None, None
        for sid, groups in self.group_centroids[ver].items():
            if sid == embedding.speaker_id: continue
            for gid, centroid in groups.items():
                dist = calculate_cosine_distance(embedding.vector, centroid.vector)
                if dist < min_dist:
                    min_dist, nearest_sid, nearest_gid = dist, sid, gid
        return nearest_sid, nearest_gid, min_dist

    def classify_to_nearest_group(self, embedding: EmbeddingFile) -> Centroid:
        min_dist = float('inf')
        nearest_centroid = None
        for centroid in self.all_group_centroids:
            dist = calculate_cosine_distance(embedding.vector, centroid.vector)
            if dist < min_dist:
                min_dist, nearest_centroid = dist, centroid
        return nearest_centroid
