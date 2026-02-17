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
            
        # Check if line is a file code (e.g., AVPEPUDEA0001)
        # Relaxed regex: starts with letters, ends with digits, e.g. AVPEPUDEA0001
        if re.match(r'^[A-Z]+\d+$', line):
            current_code = line
            transcripts[current_code] = []
            i += 1
            # Skip header line if it follows (case insensitive check)
            if i < len(lines) and "start" in lines[i].lower() and "transcription" in lines[i].lower():
                i += 1
            continue
        
        if current_code:
            # Handle both tabs and spaces
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
    lowercase: bool = True,
    pause_threshold_ms: float = 200.0
) -> None:
    input_path = Path(input_dir)
    mapping_file = Path(mapping_path)
    meta_path = Path(metadata_dir)
    
    # ... (skipping unchanged code)
    
    wav_files = list(input_path.glob("*.wav"))
    logger.info(f"Found {len(wav_files)} WAV files in {input_dir}")
    
    pause_threshold_sec = pause_threshold_ms / 1000.0
    
    count = 0
    # ... (skipping to the loop logic)
            if prev_end is not None:
                gap = seg['start'] - prev_end
                if gap > pause_threshold_sec:
                    words.append(",")
                    has_long_pause = True
            
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
        
        # Log details
        pause_info = " [LONG PAUSE DETECTED -> COMMA ADDED]" if has_long_pause else ""
        logger.info(f"Processed {wav_file.name}: {transcript}{pause_info}")
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
    parser.add_argument("--pause_threshold_ms", type=float, default=200.0,
                        help="Gap threshold in ms to insert a comma (default: 200.0)")
    
    args = parser.parse_args()
    
    process_ddk(
        input_dir=args.input_dir,
        mapping_path=args.mapping_path,
        metadata_dir=args.metadata_dir,
        lowercase=not args.no_lowercase,
        pause_threshold_ms=args.pause_threshold_ms
    )

if __name__ == "__main__":
    main()
