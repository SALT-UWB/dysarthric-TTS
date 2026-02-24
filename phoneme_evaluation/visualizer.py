import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List
from .analyzer import get_discriminative_phonemes, get_phoneme_diff_stats

def plot_phoneme_histograms(df: pd.DataFrame, phonemes: List[str], output_dir: Path):
    """
    Generates and saves histograms for the specified phonemes, stratified by Status and Sex.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    
    for ph in phonemes:
        ph_data = df[df['phoneme'] == ph]
        if ph_data.empty:
            continue
            
        g = sns.displot(
            data=ph_data, x="duration", hue="status", col="sex",
            kind="hist", kde=True, bins=30, height=5, aspect=1.2,
            palette={"HC": "green", "PD": "red"}
        )
        
        g.set_axis_labels("Duration (seconds)", "Count")
        g.fig.suptitle(f"Phoneme Duration Distribution: '{ph}'", y=1.05)
        
        safe_ph = "".join([c if c.isalnum() else "_" for c in ph])
        file_path = output_dir / f"hist_{safe_ph}.png"
        g.savefig(file_path, bbox_inches='tight')
        plt.close()

def plot_all_phonemes_boxplot(df: pd.DataFrame, output_path: Path):
    """
    Plots a 3-row figure: Boxplot, Cohen's d, and Sample Count.
    Ordered by absolute Cohen's d. Fixed Y-axis for duration.
    """
    # Calculate stats and order
    diff_stats = get_phoneme_diff_stats(df)
    if diff_stats.empty:
        print(f"Warning: No phonemes with enough data for Cohen's d calculation.")
        return

    top_phonemes_ordered = diff_stats['phoneme'].tolist()
    
    df_plot = df[df['phoneme'].isin(top_phonemes_ordered)].copy()
    df_plot['phoneme'] = pd.Categorical(df_plot['phoneme'], categories=top_phonemes_ordered, ordered=True)
    diff_stats['phoneme'] = pd.Categorical(diff_stats['phoneme'], categories=top_phonemes_ordered, ordered=True)
    
    fig, (ax_box, ax_d, ax_count) = plt.subplots(3, 1, figsize=(20, 18), sharex=True, 
                                               gridspec_kw={'height_ratios': [3, 1, 1]})
    sns.set_theme(style="whitegrid")
    
    # 1. Boxplot - Fixed Y axis from 0 to 0.25s
    sns.boxplot(
        data=df_plot, x="phoneme", y="duration", hue="status",
        palette={"HC": "green", "PD": "red"}, fliersize=1, ax=ax_box
    )
    ax_box.set_title("Phoneme Duration Distribution: PD vs HC (Ordered by |Cohen's d|)")
    ax_box.set_ylabel("Duration (seconds)")
    ax_box.set_xlabel("Phoneme")
    ax_box.set_ylim(0, 0.25)
    ax_box.tick_params(labelbottom=True)
    
    # 2. Cohen's d Barplot
    sns.barplot(data=diff_stats, x="phoneme", y="cohens_d", ax=ax_d, palette="vlag")
    ax_d.set_ylabel("Cohen's d")
    ax_d.set_xlabel("Phoneme")
    ax_d.axhline(0, color='black', linewidth=0.8)
    ax_d.axhline(0.2, color='gray', linestyle='--', alpha=0.5)
    ax_d.axhline(-0.2, color='gray', linestyle='--', alpha=0.5)
    ax_d.axhline(0.5, color='blue', linestyle='--', alpha=0.3)
    ax_d.axhline(-0.5, color='blue', linestyle='--', alpha=0.3)
    ax_d.tick_params(labelbottom=True)
    
    # 3. Count Plot
    counts = df_plot.groupby(['phoneme', 'status'], observed=True).size().reset_index(name='count')
    sns.barplot(data=counts, x="phoneme", y="count", hue="status", 
                palette={"HC": "green", "PD": "red"}, ax=ax_count)
    ax_count.set_ylabel("Sample Count")
    ax_count.set_xlabel("Phoneme")
    ax_count.get_legend().remove()
    
    # Rotate all labels
    for ax in [ax_box, ax_d, ax_count]:
        ax.tick_params(axis='x', rotation=90)
    
    plt.tight_layout()
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def plot_stratified_phonemes_boxplot(df: pd.DataFrame, output_path: Path):
    """
    Plots stratified boxplots for all phonemes with Cohen's d and count subplots.
    Fixed Y-axis for duration.
    """
    df_plot = df.copy()
    df_plot['group'] = df_plot['status'] + "_" + df_plot['sex']
    
    # Get global diff stats for ordering and d-plot
    diff_stats = get_phoneme_diff_stats(df)
    if diff_stats.empty:
        print(f"Warning: No phonemes with enough data for Cohen's d calculation.")
        return

    top_phonemes_ordered = diff_stats['phoneme'].tolist()
    
    df_plot['phoneme'] = pd.Categorical(df_plot['phoneme'], categories=top_phonemes_ordered, ordered=True)
    diff_stats['phoneme'] = pd.Categorical(diff_stats['phoneme'], categories=top_phonemes_ordered, ordered=True)
    
    palette = {
        "HC_M": "lightgreen",
        "HC_F": "darkgreen",
        "PD_M": "salmon",
        "PD_F": "darkred"
    }
    
    fig, (ax_box, ax_d, ax_count) = plt.subplots(3, 1, figsize=(24, 20), sharex=True, 
                                               gridspec_kw={'height_ratios': [3, 1, 1]})
    sns.set_theme(style="whitegrid")
    
    # 1. Boxplot (Stratified) - Fixed Y axis from 0 to 0.25s
    sns.boxplot(
        data=df_plot, x="phoneme", y="duration", hue="group",
        hue_order=["HC_M", "HC_F", "PD_M", "PD_F"],
        palette=palette, fliersize=0.5, ax=ax_box
    )
    ax_box.set_title("Phoneme Duration Distribution: Stratified by Status and Sex (Ordered by |Cohen's d|)")
    ax_box.set_ylabel("Duration (seconds)")
    ax_box.set_xlabel("Phoneme")
    ax_box.set_ylim(0, 0.25)
    ax_box.legend(title="Group (Status_Sex)")
    ax_box.tick_params(labelbottom=True)
    
    # 2. Cohen's d Barplot (Global PD vs HC)
    sns.barplot(data=diff_stats, x="phoneme", y="cohens_d", ax=ax_d, palette="vlag")
    ax_d.set_ylabel("Global Cohen's d")
    ax_d.set_xlabel("Phoneme")
    ax_d.axhline(0, color='black', linewidth=0.8)
    ax_d.axhline(0.2, color='gray', linestyle='--', alpha=0.5)
    ax_d.axhline(-0.2, color='gray', linestyle='--', alpha=0.5)
    ax_d.tick_params(labelbottom=True)
    
    # 3. Count Plot
    counts = df_plot.groupby(['phoneme', 'group'], observed=True).size().reset_index(name='count')
    sns.barplot(data=counts, x="phoneme", y="count", hue="group",
                hue_order=["HC_M", "HC_F", "PD_M", "PD_F"],
                palette=palette, ax=ax_count)
    ax_count.set_ylabel("Sample Count")
    ax_count.set_xlabel("Phoneme")
    ax_count.get_legend().remove()
    
    # Rotate all labels
    for ax in [ax_box, ax_d, ax_count]:
        ax.tick_params(axis='x', rotation=90)
    
    plt.tight_layout()
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
