from pathlib import Path
from .data_loader import load_all_data
from .analyzer import get_discriminative_phonemes
from .visualizer import plot_phoneme_histograms

def main():
    print("Loading data (including technical tokens)...")
    df = load_all_data(filter_technical=False)
    
    if df.empty:
        print("No data found!")
        return
        
    print("Identifying discriminative phonemes...")
    top_phonemes = get_discriminative_phonemes(df, top_n=10)
    print(f"Top 10 phonemes: {top_phonemes}")
    
    output_dir = Path("reports/plots/phonemes")
    all_boxplot_path = Path("reports/plots/phonemes_all_boxplot.png")
    print("Generating histograms...")
    plot_phoneme_histograms(df, top_phonemes, output_dir)
    print("Generating boxplot for all phonemes...")
    from .visualizer import plot_all_phonemes_boxplot
    plot_all_phonemes_boxplot(df, all_boxplot_path)

if __name__ == "__main__":
    main()
