import argparse
import os

from .analyzer import WavLMAnalyzer
from .data_loader import load_embeddings
from .reporter import WavLMReporter

def main():
    parser = argparse.ArgumentParser(description="PC-GITA WavLM Embedding Evaluation")
    parser.add_argument("--input_dir", type=str, 
                        default="datalocal/PC-GITA_v260210_24kHz/speaker_embeddings/wavLM",
                        help="Directory containing .pt embedding files")
    parser.add_argument("--output_dir", type=str, default="reports",
                        help="Directory to save CSV reports")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        
    print(f"Loading embeddings from {args.input_dir}...")
    embeddings = load_embeddings(args.input_dir)
    print(f"Loaded {len(embeddings)} embeddings.")
    
    print("Analyzing hierarchical distances...")
    analyzer = WavLMAnalyzer(embeddings)
    reporter = WavLMReporter(analyzer)
    
    print("Generating detailed report...")
    detailed_df = reporter.generate_detailed_report()
    detailed_path = os.path.join(args.output_dir, "wavlm_detailed_distances.csv")
    detailed_df.to_csv(detailed_path, index=False)
    print(f"Saved detailed report to {detailed_path}")
    
    print("Generating summary reports...")
    summaries = reporter.generate_summary_reports(detailed_df)
    
    for status, df in summaries.items():
        summary_path = os.path.join(args.output_dir, f"wavlm_summary_{status}.csv")
        df.to_csv(summary_path, index=False)
        print(f"Saved {status} summary to {summary_path}")

if __name__ == "__main__":
    main()
