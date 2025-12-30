from datasets import load_dataset
import os
import json

def download_and_save(dataset_id, save_name):
    print(f"Downloading {dataset_id}...")
    try:
        # Trust remote code is sometimes needed for some datasets
        dataset = load_dataset(dataset_id, trust_remote_code=True)
        save_path = os.path.join("datasets", save_name)
        dataset.save_to_disk(save_path)
        print(f"Saved {dataset_id} to {save_path}")
        
        # Save sample
        sample_path = os.path.join(save_path, "sample.json")
        # Try to get 'train' split, else first available
        split = list(dataset.keys())[0]
        samples = dataset[split][:3]
        
        # Convert to list of dicts if needed (dataset slicing returns dict of lists usually)
        # Actually dataset[:3] returns a dict of lists {col: [val1, val2, val3]}
        # We want list of dicts for readability
        keys = samples.keys()
        sample_list = []
        for i in range(len(list(keys)[0])): # Assuming all cols have same length
             item = {k: samples[k][i] for k in keys}
             sample_list.append(item)

        with open(sample_path, "w") as f:
            json.dump(sample_list, f, indent=2, default=str)
        print(f"Saved sample to {sample_path}")
        
    except Exception as e:
        print(f"Failed to download {dataset_id}: {e}")

if __name__ == "__main__":
    download_and_save("qanastek/ICLR-OpenReview", "ICLR-OpenReview")
    download_and_save("tasksource/peer-read", "peer-read-tasksource")
