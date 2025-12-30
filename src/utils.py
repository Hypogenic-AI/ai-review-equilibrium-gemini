import os
import pandas as pd
import glob

def load_iclr_data(data_dir="datasets/AI-Scientist-ICLR", limit=None):
    """
    Loads the ICLR data: ratings and paths to parsed text files.
    """
    ratings_path = os.path.join(data_dir, "ratings_subset.tsv")
    parsed_dir = os.path.join(data_dir, "iclr_parsed")
    
    # Load ratings
    try:
        df = pd.read_csv(ratings_path, sep="\t")
    except FileNotFoundError:
        print(f"Error: Ratings file not found at {ratings_path}")
        return pd.DataFrame()

    # Get available text files
    txt_files = glob.glob(os.path.join(parsed_dir, "*.txt"))
    # Map paper ID (filename stem) to full path
    # Filenames in iclr_parsed seem to be the paper IDs
    id_to_path = {os.path.splitext(os.path.basename(f))[0]: f for f in txt_files}
    
    # Filter dataframe to only include papers we have text for
    # The dataframe likely has a column for paper ID. Let's inspect it first.
    # Assuming the first column or a column named 'forum' or 'id' is the key.
    # If the column mapping fails, we will need to inspect the TSV structure.
    
    # Let's quickly verify the columns in a separate step or assume standard OpenReview format
    # Usually 'forum' is the ID.
    
    # For now, let's just add a 'file_path' column based on the index or ID column
    
    available_papers = []
    for idx, row in df.iterrows():
        # The TSV uses 'paper_id' as the key
        paper_id = str(row.get('paper_id', ''))
        
        if paper_id and paper_id in id_to_path:
            row['text_path'] = id_to_path[paper_id]
            available_papers.append(row)
    
    if available_papers:
        df_filtered = pd.DataFrame(available_papers)
    else:
        # Fallback: maybe the filenames don't match 'forum'. 
        # Let's return the raw list of text files if dataframe matching fails
        # so we can at least run on *some* papers.
        print("Warning: Could not match TSV rows to text files. Using random text files.")
        files = list(id_to_path.values())[:limit] if limit else list(id_to_path.values())
        return pd.DataFrame({'text_path': files, 'forum': [os.path.splitext(os.path.basename(f))[0] for f in files]})

    if limit:
        df_filtered = df_filtered.head(limit)
        
    return df_filtered

def read_paper_text(file_path, max_tokens=15000):
    """
    Reads paper text and truncates if necessary.
    Simple char truncation for now (approx 4 chars/token).
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Rough truncation to avoid massive context
    max_chars = max_tokens * 4
    if len(text) > max_chars:
        text = text[:max_chars] + "\n...[TRUNCATED]..."
        
    return text
