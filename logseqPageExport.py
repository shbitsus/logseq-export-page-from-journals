import os
import sys
import re
import datetime
from pathlib import Path

# ==================== CONFIGURATION ====================
# Paths to your local Logseq directories
# JOURNALS_DIR = r"/home/user/Documents/LogSeq/journals" 
# JOURNALS_DIR = r"C:\Users\YourName\Documents\Logseq\journals" 
JOURNALS_DIR = Path.home() / "Documents/LogSeq/journals"
PAGES_DIR = Path.home() / "Documents/LogSeq/pages"
# =======================================================

def find_case_insensitive_page(pages_dir, page_name):
    """Finds the page markdown file on Linux by matching lowercase names."""
    if not pages_dir.exists():
        return None
        
    target_filename = f"{page_name.lower()}.md"
    for entry in os.scandir(pages_dir):
        if entry.is_file() and entry.name.lower() == target_filename:
            return Path(entry.path)
    return None

def extract_linked_blocks(file_path, tag):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    clean_tag = tag.replace("[", "").replace("]", "").lower()
    
    extracted_content = []
    inside_target_block = False
    target_indent = -1

    for line in lines:
        stripped = line.lstrip()
        if not stripped or not stripped.startswith("- "):
            continue
            
        indent_level = len(line) - len(stripped)

        if not inside_target_block:
            if clean_tag in line.lower():
                inside_target_block = True
                target_indent = indent_level
                extracted_content.append(line)
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
    if len(sys.argv) < 2:
        print("Error: Missing target tag parameter.")
        print("Usage: python export_logseq.py <tag_or_page_name>")
        print("Example: python export_logseq.py fastmail")
        sys.exit(1)
        
    raw_tag = sys.argv[1]
    
    search_tag = raw_tag if raw_tag.startswith("[[") else f"[[{raw_tag}]]"
    safe_filename_tag = raw_tag.replace("[", "").replace("]", "").replace(" ", "_")

    # 1. Read and prepend the core Page file text if it exists
    page_content = ""
    matched_page_path = find_case_insensitive_page(PAGES_DIR, raw_tag)
    
    if matched_page_path and matched_page_path.exists():
        print(f"Found core page file: {matched_page_path.name}")
        with open(matched_page_path, "r", encoding="utf-8") as f:
            page_content = f.read().strip()
            if page_content:
                page_content = f"# Core Page: {raw_tag}\n\n{page_content}\n\n"
    else:
        print(f"⚠️ Note: No core page file found for '{raw_tag}' in {PAGES_DIR}. Skipping prepend.")

    # 2. Extract references from Journal files
    if not JOURNALS_DIR.exists():
        print(f"Error: The directory '{JOURNALS_DIR}' does not exist. Check configuration.")
        return

    journal_files = sorted(list(JOURNALS_DIR.glob("*.md")))
    journal_output = []

    for file_path in journal_files:
        date_str = file_path.stem.replace("_", "-")
        blocks = extract_linked_blocks(file_path, search_tag)
        if blocks:
            journal_output.append(f"# {date_str}\n\n{blocks}\n")

    # 3. Assemble and export to Current Working Directory
    if page_content or journal_output:
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H")
        output_filename = f"{safe_filename_tag}_{timestamp}.md"
        output_file = Path.cwd() / output_filename
        
        full_markdown_payload = page_content + "\n".join(journal_output)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_markdown_payload.strip() + "\n")
        print(f"✅ Success! Output saved to your current directory: {output_file}")
    else:
        print(f"⚠️ No contents or journal block hierarchies found for '{search_tag}'")

if __name__ == "__main__":
    main()
