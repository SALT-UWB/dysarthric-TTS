import argparse
import logging
from pathlib import Path
import pandas as pd
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_ddk_source(file_path: Path) -> dict[str, list[dict]]:
    """
    Parses DDK source files (DDK1.txt etc.) which have sections per file:
    AVPEPUDEA0003
    Start End Transcription
    0 0.631 Petaka
    ...
    """
    transcripts = {}
    current_code = None
    
    if not file_path.exists():
        logger.warning(f"Source file {file_path} not found.")
        return {}

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # Check if line is a file code (e.g., AVPEPUDEA0003)
        if re.match(r'^[A-Z]{10}\d{4}$', line):
            current_code = line
            transcripts[current_code] = []
            i += 1
            # Skip header line "Start End Transcription" if it exists
            if i < len(lines) and "Start" in lines[i]:
                i += 1
            continue
        
        if current_code:
            parts = line.split()
            if len(parts) >= 3:
                try:
                    start = float(parts[0])
                    end = float(parts[1])
                    text = " ".join(parts[2:])
                    transcripts[current_code].append({
                        'start': start,
                        'end': end,
                        'text': text
                    })
                except ValueError:
                    pass
        i += 1
        
    return transcripts

def process_ddk(
    input_dir: str,
    mapping_path: str,
    metadata_dir: str,
    lowercase: bool = True
) -> None:
    input_path = Path(input_dir)
    mapping_file = Path(mapping_path)
    meta_path = Path(metadata_dir)
    
    if not mapping_file.exists():
        logger.error(f"Mapping file not found: {mapping_file}")
        return

    # Load mapping: CODE;CODE4JHU;Code BD-Parkinson;...
    mapping_df = pd.read_csv(mapping_file, sep=';')
    # Create lookup: Code BD-Parkinson -> CODE
    lookup = dict(zip(mapping_df['Code BD-Parkinson'], mapping_df['CODE']))
    
    # Load DDK source transcripts
    ddk_sources = {
        'DDK1': parse_ddk_source(meta_path / "DDK1.txt"),
        'DDK2': parse_ddk_source(meta_path / "DDK2.txt"),
        'DDK3': parse_ddk_source(meta_path / "DDK3.txt")
    }
    
    wav_files = list(input_path.glob("*.wav"))
    logger.info(f"Found {len(wav_files)} WAV files in {input_dir}")
    
    count = 0
    for wav_file in wav_files:
        # Example name: 001PD_S1_DDK1.wav
        parts = wav_file.stem.split('_')
        if len(parts) < 3:
            continue
            
        speaker_id = parts[0]
        ddk_type = parts[2] # DDK1, DDK2, or DDK3
        
        # 1. Map speaker_id (001PD) to code (AVPE...)
        code = lookup.get(speaker_id)
        if not code:
            logger.warning(f"No mapping found for speaker {speaker_id} ({wav_file.name})")
            continue
            
        # 2. Get segments for this code and DDK type
        source_data = ddk_sources.get(ddk_type, {})
        segments = source_data.get(code)
        
        if not segments:
            logger.warning(f"No transcript found for {code} in {ddk_type} ({wav_file.name})")
            continue
            
        # 3. Join with comma logic
        words = []
        prev_end = None
        
        for seg in segments:
            word = seg['text']
            if lowercase:
                word = word.lower()
                
            if prev_end is not None:
                gap = seg['start'] - prev_end
                if gap > 0.200: # > 200ms
                    words.append(",")
            
            words.append(word)
            prev_end = seg['end']
            
        # 4. Finalize string
        # Clean up spaces around commas
        transcript = " ".join(words).replace(" ,", ",")
        # Ensure it ends with a period
        if not transcript.endswith("."):
            transcript += "."
            
        # Write to file
        output_txt = wav_file.with_suffix('.txt')
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(transcript)
        count += 1
        
    logger.info(f"Successfully generated {count} transcription files.")

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate DDK transcriptions.")
    parser.add_argument("--input_dir", type=str, default="datalocal/v260210_24kHz/ddk",
                        help="Directory with DDK wav files")
    parser.add_argument("--mapping_path", type=str, default="datalocal/v260210_24kHz/_metadata/PCGITAtoPD_mapping.csv",
                        help="Path to speaker mapping CSV")
    parser.add_argument("--metadata_dir", type=str, default="datalocal/v260210_24kHz/_metadata",
                        help="Directory containing DDK1.txt, DDK2.txt, DDK3.txt")
    parser.add_argument("--no_lowercase", action="store_true",
                        help="Do not convert text to lowercase")
    
    args = parser.parse_args()
    
    process_ddk(
        input_dir=args.input_dir,
        mapping_path=args.mapping_path,
        metadata_dir=args.metadata_dir,
        lowercase=not args.no_lowercase
    )

if __name__ == "__main__":
    main()
