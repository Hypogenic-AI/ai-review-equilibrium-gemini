import pdfplumber
import glob
import os

pdf_files = sorted(glob.glob("papers/*.pdf"))
output_file = "papers_summary.txt"

with open(output_file, "w", encoding="utf-8") as out:
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        out.write(f"\n{'='*80}\nPROCESSING: {filename}\n{'='*80}\n\n")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Read first 5 pages (Abstract, Intro, Methods usually)
                pages_to_read = min(5, len(pdf.pages))
                text = ""
                for i in range(pages_to_read):
                    page_text = pdf.pages[i].extract_text()
                    if page_text:
                        text += page_text + "\n"
                out.write(text)
        except Exception as e:
            out.write(f"ERROR reading {filename}: {e}\n")

print(f"Extracted text to {output_file}")

