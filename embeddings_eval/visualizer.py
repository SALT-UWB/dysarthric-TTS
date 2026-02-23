import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib.lines import Line2D
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from .analyzer import WavLMAnalyzer
from .constants import (
    COLOR_M_PD, COLOR_M_HC, COLOR_F_PD, COLOR_F_HC,
    STATUS_PD, STATUS_HC, SEX_F,
    SYMBOL_SAMPLE,
    SYMBOL_SPEAKER_CENTROID,
    GROUP_MARKERS,
    ALL_GROUPS
)

class WavLMVisualizer:
    def __init__(self, analyzer: WavLMAnalyzer):
        self.analyzer = analyzer
        self.embeddings_matrix = torch.stack([e.vector for e in analyzer.embeddings]).cpu().numpy()
        self.speaker_ids = [e.speaker_id for e in analyzer.embeddings]
        self.statuses = [e.health_status for e in analyzer.embeddings]
        self.groups = [e.group for e in analyzer.embeddings]
        self.sexes = [e.sex for e in analyzer.embeddings]

    def _get_color(self, status: str, sex: str) -> str:
        if sex == SEX_F:
            return COLOR_F_PD if status == STATUS_PD else COLOR_F_HC
        return COLOR_M_PD if status == STATUS_PD else COLOR_M_HC

    def plot_speaker_comparison(self, speaker_ids: list[str], method: str = 'pca'):
        """Plots samples with gender-aware colors and hierarchical connections."""
        ver = self.analyzer.versions[0]
        sample_indices = [i for i, sid in enumerate(self.speaker_ids) if sid in speaker_ids]
        if not sample_indices:
            print(f"No data found for speakers: {speaker_ids}")
            return
            
        all_vecs = []
        meta = [] # (type, sid, gid, color, marker)
        sample_map, group_centroid_map, speaker_centroid_map = {}, {}, {}
        
        # Samples
        for idx in sample_indices:
            sid, gid, sex, status = self.speaker_ids[idx], self.groups[idx], self.sexes[idx], self.statuses[idx]
            color = self._get_color(status, sex)
            marker = GROUP_MARKERS.get(gid, SYMBOL_SAMPLE)
            curr_idx = len(all_vecs)
            all_vecs.append(self.embeddings_matrix[idx])
            meta.append(('sample', sid, gid, color, marker))
            key = (sid, gid)
            if key not in sample_map: sample_map[key] = []
            sample_map[key].append(curr_idx)
            
        # Group Centroids
        for sid in speaker_ids:
            if sid in self.analyzer.group_centroids[ver]:
                for gid, centroid in self.analyzer.group_centroids[ver][sid].items():
                    status = STATUS_PD if STATUS_PD in sid else STATUS_HC
                    color = self._get_color(status, centroid.sex)
                    marker = GROUP_MARKERS.get(gid, SYMBOL_SAMPLE)
                    group_centroid_map[(sid, gid)] = len(all_vecs)
                    all_vecs.append(centroid.vector.cpu().numpy())
                    meta.append(('group_centroid', sid, gid, color, marker))
                    
        # Speaker Centroids
        for sid in speaker_ids:
            if sid in self.analyzer.speaker_centroids[ver]:
                c = self.analyzer.speaker_centroids[ver][sid]
                status = STATUS_PD if STATUS_PD in sid else STATUS_HC
                color = self._get_color(status, c.sex)
                speaker_centroid_map[sid] = len(all_vecs)
                all_vecs.append(c.vector.cpu().numpy())
                meta.append(('speaker_centroid', sid, None, color, SYMBOL_SPEAKER_CENTROID))
                
        matrix = np.array(all_vecs)
        if method.lower() == 'pca':
            reducer = PCA(n_components=2)
        else:
            reducer = TSNE(n_components=2, random_state=42, init='pca', 
                          learning_rate='auto', perplexity=min(30, len(matrix)-1))
        projections = reducer.fit_transform(matrix)
        
        plt.figure(figsize=(14, 10))
        # Lines
        for sid in speaker_ids:
            for gid in ALL_GROUPS:
                key = (sid, gid)
                if key in sample_map and key in group_centroid_map:
                    gx, gy = projections[group_centroid_map[key]]
                    for s_idx in sample_map[key]:
                        sx, sy = projections[s_idx]
                        plt.plot([sx, gx], [sy, gy], color='gray', linewidth=0.2, alpha=0.2)
            if sid in speaker_centroid_map:
                sx, sy = projections[speaker_centroid_map[sid]]
                for gid in ALL_GROUPS:
                    key = (sid, gid)
                    if key in group_centroid_map:
                        gx, gy = projections[group_centroid_map[key]]
                        plt.plot([gx, sx], [gy, sy], color='gray', linewidth=0.5, alpha=0.3)

        # Markers
        for i, (x, y) in enumerate(projections):
            m_type, sid, gid, color, marker = meta[i]
            if m_type == 'sample':
                plt.scatter(x, y, c=color, marker=marker, alpha=0.2, s=30)
            elif m_type == 'group_centroid':
                plt.scatter(x, y, c=color, marker=marker, s=150, edgecolors='black', linewidth=0.8)
            elif m_type == 'speaker_centroid':
                plt.scatter(x, y, c=color, marker=marker, s=400, edgecolors='black', linewidth=1.2)
                plt.text(x + 0.01, y + 0.01, sid, fontsize=12, fontweight='bold')
                
        plt.title(f"Hierarchical Comparison by Gender ({method.upper()})", fontsize=15)
        
        # Legend construction
        legend_elements = [
            Line2D([0], [0], color='w', label='-- STATUS & GENDER --'),
            Line2D([0], [0], color=COLOR_M_PD, lw=4, label='PD Male'),
            Line2D([0], [0], color=COLOR_F_PD, lw=4, label='PD Female'),
            Line2D([0], [0], color=COLOR_M_HC, lw=4, label='HC Male'),
            Line2D([0], [0], color=COLOR_F_HC, lw=4, label='HC Female'),
            Line2D([0], [0], color='w', label=''),
            Line2D([0], [0], color='w', label='-- SYMBOLS --'),
            Line2D([0], [0], marker=SYMBOL_SPEAKER_CENTROID, color='w', label='Global Centroid',
                   markerfacecolor='gray', markersize=12, markeredgecolor='black'),
        ]
        
        # Add Group specific markers to legend
        for gid in ALL_GROUPS:
            marker = GROUP_MARKERS.get(gid, SYMBOL_SAMPLE)
            legend_elements.append(
                Line2D([0], [0], marker=marker, color='w', label=f'Group: {gid}',
                       markerfacecolor='gray', markersize=10, markeredgecolor='black')
            )
            
        plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        plt.grid(True, alpha=0.15)
        plt.tight_layout()
        plt.show()

    def plot_centroids(self, method: str = 'pca', save_path: str | None = None):
        all_sids = list(self.analyzer.speaker_centroids[self.analyzer.versions[0]].keys())
        self.plot_speaker_comparison(all_sids, method=method)
