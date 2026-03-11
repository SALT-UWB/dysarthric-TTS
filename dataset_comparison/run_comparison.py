import argparse
import pandas as pd
import logging
from pathlib import Path
from .integrity import DataIntegrityChecker
from .embeddings import EmbeddingComparator
from .phonemes import PhonemeComparator
from .audio_utils import compare_durations
from .data_loader import load_metadata
from .constants import TASKS
from .utils import get_parallel_file, identify_task

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Compare reference and test datasets.")
    parser.add_argument("--ref", type=str, required=True, help="Path to reference dataset root")
    parser.add_argument("--test", type=str, required=True, help="Path to test dataset root")
    args = parser.parse_args()

    ref_root = Path(args.ref)
    test_root = Path(args.test)
    
    if not ref_root.exists():
        logger.error(f"Reference root not found: {ref_root}")
        return
    if not test_root.exists():
        logger.error(f"Test root not found: {test_root}")
        return

    # Generate dynamic reports directory name
    report_name = f"comparison_{ref_root.name}_{test_root.name}"
    reports_dir = Path("reports") / report_name
    reports_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Results will be saved to: {reports_dir}")
    
    try:
        metadata = load_metadata()
        logger.info(f"Loaded metadata for {len(metadata)} speakers.")
    except Exception as e:
        logger.error(f"Failed to load metadata: {e}")
        return

    logger.info("--- Phase 1: Data Integrity Check ---")
    checker = DataIntegrityChecker(ref_root, test_root)
    checker.check_parallelism()
    integrity_df = checker.get_report()
    
    if not integrity_df.empty:
        integrity_df['task'] = integrity_df['filename'].apply(identify_task)
        integrity_df = integrity_df.merge(metadata[['speaker_id', 'status']], on='speaker_id', how='left')
        integrity_df.to_csv(reports_dir / "comparison_integrity.csv", index=False)
        
        missing_count = integrity_df[~integrity_df['exists_in_test']].shape[0]
        txt_mismatch = integrity_df[integrity_df['transcription_match'] == False].shape[0]
        logger.info(f"Integrity Check Done. Missing: {missing_count}, Txt Mismatches: {txt_mismatch}")

    logger.info("--- Phase 2: Audio Duration Comparison ---")
    audio_results = []
    for task_dir in TASKS:
        ref_task_dir = ref_root / task_dir
        if not ref_task_dir.exists(): continue
            
        for ref_file in ref_task_dir.glob("*.wav"):
            test_file = get_parallel_file(ref_file, test_root)
            if test_file:
                try:
                    delta, sig = compare_durations(ref_file, test_file)
                    match = integrity_df[integrity_df['filename'] == ref_file.name]
                    spk = match['speaker_id'].iloc[0] if not match.empty else "unknown"
                    
                    audio_results.append({
                        "speaker_id": spk,
                        "filename": ref_file.name,
                        "task": identify_task(ref_file.name),
                        "duration_delta": delta,
                        "significant_diff": sig
                    })
                except Exception as e:
                    logger.error(f"Error comparing durations for {ref_file.name}: {e}")

    if audio_results:
        audio_df = pd.DataFrame(audio_results)
        audio_df.to_csv(reports_dir / "comparison_audio_durations.csv", index=False)
        sig_count = audio_df[audio_df['significant_diff']].shape[0]
        logger.info(f"Duration Check Done. Significant differences found: {sig_count}")

    logger.info("--- Phase 3: Embedding Comparison ---")
    try:
        emb_comp = EmbeddingComparator(ref_root, test_root)
        emb_comp.compare_embeddings()
        emb_df = emb_comp.get_report()
        if not emb_df.empty:
            emb_df = emb_df.merge(metadata[['speaker_id', 'status']], on='speaker_id', how='left')
            emb_df.to_csv(reports_dir / "comparison_embeddings.csv", index=False)
            
            emb_summary = emb_comp.get_speaker_summary(emb_df)
            emb_summary = emb_summary.merge(metadata[['speaker_id', 'status']], on='speaker_id', how='left')
            emb_summary.to_csv(reports_dir / "speaker_embedding_summary.csv", index=False)
            
            # Log aggregate stats
            group_means = emb_summary.groupby('status')['avg_cos_dist'].mean()
            task_means = emb_summary.groupby(['task', 'status'])['avg_cos_dist'].mean()
            task_means_euc = emb_summary.groupby(['task', 'status'])['avg_euc_dist'].mean()
            speaker_counts = emb_summary.groupby(['task', 'status'])['speaker_id'].nunique()
            file_counts = emb_df.groupby(['task', 'status'])['filename'].count()
            
            logger.info("Embedding Comparison Stats Breakdown:")
            for task in TASKS:
                if task in task_means.index.get_level_values(0):
                    logger.info(f"  Task: {task}")
                    for status in ['HC', 'PD']:
                        if (task, status) in task_means.index:
                            logger.info(f"    {status}: Cosine={task_means[task, status]:.4f}, Euclidean={task_means_euc[task, status]:.4f}, Speakers={speaker_counts[task, status]}, Files={file_counts[task, status]}")
            
            logger.info("Global Health Status Summary (Cosine):")
            for status in ['HC', 'PD']:
                if status in group_means.index:
                    logger.info(f"  {status}: Avg Cosine Dist={group_means[status]:.4f}")
    except Exception as e:
        logger.error(f"Error in embedding comparison: {e}")

    logger.info("--- Phase 4: Phoneme Comparison ---")
    ph_comp = PhonemeComparator()
    missing_csv_count = 0
    for task_dir in TASKS:
        ref_task_dir = ref_root / task_dir
        if not ref_task_dir.exists(): continue
        for ref_csv in ref_task_dir.glob("*.csv"):
            test_csv = get_parallel_file(ref_csv, test_root)
            if test_csv:
                try:
                    ph_comp.compare_alignments(ref_csv, test_csv, identify_task(ref_csv.name))
                except Exception as e:
                    logger.error(f"Error comparing alignments for {ref_csv.name}: {e}")
            else:
                logger.warning(f"Missing test alignment CSV for: {ref_csv.name}")
                missing_csv_count += 1
    
    ph_df = ph_comp.get_report()
    if not ph_df.empty:
        ph_df = ph_df.merge(metadata[['speaker_id', 'status']], on='speaker_id', how='left')
        ph_df.to_csv(reports_dir / "comparison_phonemes.csv", index=False)
        
        # Log phoneme stats
        avg_ph_delta = ph_df['duration_delta'].mean()
        missing_ph = ph_df['is_missing'].sum() if 'is_missing' in ph_df.columns else 0
        logger.info(f"Phoneme Check Done. Avg Delta: {avg_ph_delta:.4f}s, Missing Tokens: {missing_ph}, Missing Test CSVs: {missing_csv_count}")

    logger.info(f"Done. All reports generated in {reports_dir}/")

if __name__ == "__main__":
    main()
