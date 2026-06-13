import os
import sys
import re
import datetime
from pathlib import Path

# ==================== CONFIGURATION ====================
# path to your local Logseq "journals" folder:
# JOURNALS_DIR = r"C:\Users\YourName\Documents\Logseq\journals" 
JOURNALS_DIR = r"/home/user/Documents/LogSeq/journals" 
# =======================================================

def extract_linked_blocks(file_path, tag):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Match raw page reference formats like [[mypage]] or #mypage or mypage
    # Stripping brackets for flexible loose text matching
    clean_tag = tag.replace("[", "").replace("]", "").lower()
    
    extracted_content = []
    inside_target_block = False
    target_indent = -1

    for line in lines:
        stripped = line.lstrip()
        if not stripped or not stripped.startswith("- "):
            continue
            
        indent_level = len(line) - len(stripped)

        # Case 1: Looking for a new parent block containing the tag
        if not inside_target_block:
            if clean_tag in line.lower():
                inside_target_block = True
                target_indent = indent_level
                extracted_content.append(line)
        # Case 2: Currently inside a target block's tree
        else:
            if indent_level <= target_indent:
                if clean_tag in line.lower():
                    target_indent = indent_level
                    extracted_content.append(line)
                else:
                    inside_target_block = False
            else:
                extracted_content.append(line)

    return "".join(extracted_content)

def main():
    # 1. Parse target tag parameter from command line
    if len(sys.argv) < 2:
        print("Error: Missing target tag parameter.")
        print("Usage: python logseqPageExport.py <tag_or_page_name>")
        print("Example: python logseqPageExport.py mypage")
        sys.exit(1)
        
    raw_tag = sys.argv[1]
    
    # 2. Form search tag string (supports loose inputs like "mypage" or "[[mypage]]")
    search_tag = raw_tag if raw_tag.startswith("[[") else f"[[{raw_tag}]]"
    safe_filename_tag = raw_tag.replace("[", "").replace("]", "").replace(" ", "_")

    journals_path = Path(JOURNALS_DIR)
    if not journals_path.exists():
        print(f"Error: The directory '{JOURNALS_DIR}' does not exist. Check script line 8.")
        return

    # 3. Read and sort journal markdown files
    journal_files = sorted(list(journals_path.glob("*.md")))
    final_output = []

    for file_path in journal_files:
        date_str = file_path.stem.replace("_", "-")
        blocks = extract_linked_blocks(file_path, search_tag)
        if blocks:
            final_output.append(f"# {date_str}\n\n{blocks}\n")

    # 4. Generate dynamic output timestamp: Tag_YYYYMMDD-HH.md
    if final_output:
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H")
        output_filename = f"{safe_filename_tag}_{timestamp}.md"
        # output_file = journals_path.parent / output_filename
        output_file = Path.cwd() / output_filename
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_output))
        print(f"✅ Success! Compiled file saved to: {output_file}")
    else:
        print(f"No block hierarchies found containing '{search_tag}'")

if __name__ == "__main__":
    main()
