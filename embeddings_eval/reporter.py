import os
import pandas as pd
from tqdm.auto import tqdm
from typing import List, Dict
from collections import Counter
from .data_loader import EmbeddingFile
from .analyzer import WavLMAnalyzer
from .constants import STATUS_PD, STATUS_HC

class WavLMReporter:
    def __init__(self, analyzer: WavLMAnalyzer):
        self.analyzer = analyzer

    def generate_detailed_report(self, calculate_samples: bool = False) -> pd.DataFrame:
        """Generates a row-per-sample report."""
        rows = []
        desc = "Calculating distances (sample vs centroids)"
        for e in tqdm(self.analyzer.embeddings, desc=desc):
            hier_dists = self.analyzer.get_hierarchical_distances(e)
            near_sid_gc, near_gid_gc, near_gc_dist = self.analyzer.find_nearest_group_centroid(e)
            
            row = {
                'file': os.path.basename(e.path),
                'speaker id': e.speaker_id,
                'status': e.health_status,
                'sex': e.sex,
                'group': e.group,
                'dist own group centroid': hier_dists['dist_own_group'],
                'dist own speaker centroid': hier_dists['dist_own_speaker'],
                'nearest other group centroid id': f"{near_sid_gc}_{near_gid_gc}",
                'nearest other group centroid dist': near_gc_dist
            }
            rows.append(row)
        return pd.DataFrame(rows)

    def generate_classification_report(self) -> pd.DataFrame:
        """
        Performs classification of each sample to the nearest group centroid.
        Identifies TOP 5 intruders for each speaker-group pair.
        """
        results = []
        desc = "Classifying samples to centroids"
        for e in tqdm(self.analyzer.embeddings, desc=desc):
            nearest_centroid = self.analyzer.classify_to_nearest_group(e)
            is_correct = (nearest_centroid.speaker_id == e.speaker_id)
            
            results.append({
                'speaker_id': e.speaker_id,
                'status': e.health_status,
                'source_group': e.group,
                'assigned_speaker': nearest_centroid.speaker_id,
                'assigned_group': nearest_centroid.group_id,
                'is_correct': is_correct
            })
            
        df = pd.DataFrame(results)
        
        final_rows = []
        for (sid, gid), group_data in df.groupby(['speaker_id', 'source_group']):
            total = len(group_data)
            correct = group_data['is_correct'].sum()
            accuracy = (correct / total) * 100
            status = group_data['status'].iloc[0]
            
            # Find TOP 5 intruders
            wrong_assignments = group_data[group_data['is_correct'] == False]
            intruder_list = []
            if not wrong_assignments.empty:
                counts = Counter(wrong_assignments.apply(lambda x: f"{x['assigned_speaker']}_{x['assigned_group']}", axis=1))
                top_5 = counts.most_common(5)
                intruder_list = [f"{name} ({count/total*100:.1f}%)" for name, count in top_5]
            
            final_rows.append({
                'speaker id': sid,
                'group': gid,
                'status': status,
                'total samples': total,
                'correct samples': correct,
                'accuracy %': accuracy,
                'top 5 intruders': ", ".join(intruder_list)
            })
            
        return pd.DataFrame(final_rows)

    def generate_aggregated_classification_report(self, class_df: pd.DataFrame) -> pd.DataFrame:
        """Aggregates classification results by Status (HC/PD) and Group."""
        agg = class_df.groupby(['status', 'group']).agg({
            'total samples': 'sum',
            'correct samples': 'sum'
        }).reset_index()
        agg['accuracy %'] = (agg['correct samples'] / agg['total samples']) * 100
        return agg

    def generate_summary_reports(self, detailed_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Generates summary tables (Mean/Var) for PD and HC groups."""
        summaries = {}
        for status in [STATUS_PD, STATUS_HC]:
            subset = detailed_df[detailed_df['status'] == status]
            if subset.empty:
                summaries[status] = pd.DataFrame()
                continue
            
            summary = subset.groupby(['speaker id', 'group']).agg({
                'dist own group centroid': ['mean', 'var'],
                'dist own speaker centroid': ['mean', 'var']
            }).reset_index()
            
            summary.columns = ['speaker id', 'group', 'dist group mean', 'dist group var', 'dist speaker mean', 'dist speaker var']
            
            extra_rows = []
            ver = self.analyzer.versions[0]
            for _, row in summary.iterrows():
                sid, gid = row['speaker id'], row['group']
                c_vec = self.analyzer.group_centroids[ver][sid][gid].vector
                dummy = EmbeddingFile(path="", speaker_id=sid, health_status=status, session="", group=gid, vector=c_vec, sex='M', dataset_version=ver)
                near_sid_gc, near_gid_gc, near_gc_dist = self.analyzer.find_nearest_group_centroid(dummy)
                extra_rows.append({'centroid nearest other group': f"{near_sid_gc}_{near_gid_gc}", 'centroid nearest other group dist': near_gc_dist})
            
            summary = pd.concat([summary, pd.DataFrame(extra_rows)], axis=1)
            summaries[status] = summary
        return summaries
