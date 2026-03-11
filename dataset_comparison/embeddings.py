import torch
import torch.nn.functional as F
import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Dict
from .data_loader import load_embedding
from .utils import extract_speaker_id, identify_task
from .constants import TASKS

logger = logging.getLogger(__name__)

class EmbeddingComparator:
    def __init__(self, ref_root: Path, test_root: Path):
        self.ref_emb_root = ref_root / "speaker_embeddings" / "wavLM"
        self.test_emb_root = test_root / "speaker_embeddings" / "wavLM"
        self.results = []

    def calculate_distances(self, ref_emb: torch.Tensor, test_emb: torch.Tensor) -> Dict[str, float]:
        """
        Calculates both Cosine and Euclidean distances between two embeddings.
        """
        ref_emb = ref_emb.flatten()
        test_emb = test_emb.flatten()
        
        # Cosine Distance (1 - similarity)
        sim = F.cosine_similarity(ref_emb.unsqueeze(0), test_emb.unsqueeze(0))
        cos_dist = 1.0 - sim.item()
        
        # Euclidean Distance
        euc_dist = torch.norm(ref_emb - test_emb, p=2).item()
        
        return {
            "cosine_distance": cos_dist,
            "euclidean_distance": euc_dist
        }

    def compare_embeddings(self):
        """
        Iterates through embeddings in the reference root and matches them in test.
        """
        if not self.ref_emb_root.exists():
            logger.error(f"Reference embedding root missing: {self.ref_emb_root}")
            return
        if not self.test_emb_root.exists():
            logger.error(f"Test embedding root missing: {self.test_emb_root}")
            return

        logger.info(f"Comparing embeddings in {self.ref_emb_root.name}")
        for ref_file in self.ref_emb_root.glob("*.pt"):
            test_file = self.test_emb_root / ref_file.name
            
            if test_file.exists():
                try:
                    ref_val = load_embedding(ref_file)
                    test_val = load_embedding(test_file)
                    dists = self.calculate_distances(ref_val, test_val)
                    
                    task = identify_task(ref_file.name)

                    self.results.append({
                        "speaker_id": extract_speaker_id(ref_file),
                        "filename": ref_file.name,
                        "task": task,
                        "cosine_distance": dists["cosine_distance"],
                        "euclidean_distance": dists["euclidean_distance"]
                    })
                except Exception as e:
                    logger.error(f"Error processing embedding {ref_file.name}: {e}")
            else:
                logger.debug(f"Missing test embedding for {ref_file.name}")

    def get_report(self) -> pd.DataFrame:
        return pd.DataFrame(self.results)

    def get_speaker_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregates distances by speaker and task.
        """
        if df.empty:
            return pd.DataFrame()
        
        summary = df.groupby(['speaker_id', 'task']).agg({
            'cosine_distance': ['mean', 'std'],
            'euclidean_distance': ['mean', 'std']
        }).reset_index()
        
        # Flatten columns
        summary.columns = [
            'speaker_id', 'task', 
            'avg_cos_dist', 'std_cos_dist',
            'avg_euc_dist', 'std_euc_dist'
        ]
        return summary
