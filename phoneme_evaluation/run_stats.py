from pathlib import Path
from .data_loader import load_all_data
from .reporter import generate_full_report

def main():
    print("Loading data and alignments...")
    df = load_all_data()
    
    if df.empty:
        print("No data found!")
        return
        
    output_path = Path("reports/phoneme_stats_summary.csv")
    wide_path = Path("reports/phoneme_stats_wide.csv")
    print(f"Generating statistics for {len(df)} phoneme samples...")
    generate_full_report(df, output_path)
    generate_wide_report(df, wide_path)

if __name__ == "__main__":
    main()
