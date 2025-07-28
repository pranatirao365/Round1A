import os
import fitz  # PyMuPDF
import json
import re
from collections import defaultdict

def is_heading_text(text):
    """Check if text looks like a heading based on patterns"""
    if not text or len(text.strip()) < 2:
        return False
    
    # Remove common non-heading patterns
    text_clean = text.strip()
    
    # Skip page numbers, dates, footers, etc.
    if re.match(r'^\d+$', text_clean):  # Just numbers
        return False
    if re.match(r'^\d+/\d+/\d+$', text_clean):  # Dates
        return False
    if len(text_clean) < 3:  # Too short
        return False
    
    # Check for heading patterns
    # All caps (common for headings)
    if text_clean.isupper() and len(text_clean) > 2:
        return True
    
    # Title case with reasonable length
    if text_clean.istitle() and 3 <= len(text_clean) <= 100:
        return True
    
    # Contains numbering (1. Introduction, Chapter 2, etc.)
    if re.match(r'^[\d\.\s]+[A-Z]', text_clean):
        return True
    
    # Common heading words
    heading_words = ['introduction', 'conclusion', 'chapter', 'section', 'appendix', 
                    'references', 'bibliography', 'index', 'abstract', 'summary']
    if any(word in text_clean.lower() for word in heading_words):
        return True
    
    return False

def extract_title_and_headings(pdf_path):
    """Extract title and headings with improved detection"""
    doc = fitz.open(pdf_path)
    
    # Collect all text blocks with metadata
    text_blocks = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get text blocks with detailed information
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            text_blocks.append({
                                "text": text,
                                "size": span["size"],
                                "flags": span["flags"],  # Bold, italic, etc.
                                "font": span["font"],
                                "page": page_num + 1,
                                "bbox": span["bbox"],  # Position on page
                                "is_bold": bool(span["flags"] & 2**4),  # Bold flag
                                "is_italic": bool(span["flags"] & 2**1),  # Italic flag
                            })
    
    if not text_blocks:
        return {"title": "Unknown Title", "outline": []}
    
    # Extract title (usually largest text on first page, or from metadata)
    first_page_blocks = [b for b in text_blocks if b["page"] == 1]
    
    # Try to get title from PDF metadata first
    title = doc.metadata.get("title", "")
    if not title or title == "Unknown":
        # Find largest text on first page that looks like a title
        if first_page_blocks:
            # Sort by font size and position (top of page)
            first_page_blocks.sort(key=lambda x: (-x["size"], x["bbox"][1]))
            
            for block in first_page_blocks[:5]:  # Check top 5 largest texts
                if is_heading_text(block["text"]) and len(block["text"]) > 3:
                    title = block["text"]
                    break
            
            # If no good title found, use the largest text
            if not title or len(title) < 3:
                title = first_page_blocks[0]["text"]
    
    # Extract headings using multiple criteria
    headings = []
    
    # Group by font size and analyze patterns
    size_groups = defaultdict(list)
    for block in text_blocks:
        if is_heading_text(block["text"]):
            size_groups[block["size"]].append(block)
    
    # Sort font sizes (largest first)
    font_sizes = sorted(size_groups.keys(), reverse=True)
    
    # Assign heading levels based on font size hierarchy
    heading_levels = {}
    for i, size in enumerate(font_sizes[:3]):  # Top 3 font sizes
        if i == 0:
            heading_levels[size] = "H1"
        elif i == 1:
            heading_levels[size] = "H2"
        elif i == 2:
            heading_levels[size] = "H3"
    
    # Create headings list
    for block in text_blocks:
        if (is_heading_text(block["text"]) and 
            block["size"] in heading_levels and
            block["text"] != title):  # Don't include title as heading
            
            headings.append({
                "level": heading_levels[block["size"]],
                "text": block["text"],
                "page": block["page"]
            })
    
    # Sort headings by page number and then by level
    headings.sort(key=lambda x: (x["page"], x["level"]))
    
    return {
        "title": title,
        "outline": headings
    }

def main():
    """Main function following challenge requirements"""
    # Use challenge-specified paths
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        print("Available directories:", os.listdir("/app"))
        return
    
    # Process all PDFs in input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            
            try:
                result = extract_title_and_headings(pdf_path)
                
                # Create output filename
                output_filename = filename.rsplit(".", 1)[0] + ".json"
                output_path = os.path.join(output_dir, output_filename)
                
                # Write JSON output
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                    
                print(f"Processed: {filename} -> {output_filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                # Create a basic output even if there's an error
                basic_result = {
                    "title": "Error Processing Document",
                    "outline": []
                }
                output_filename = filename.rsplit(".", 1)[0] + ".json"
                output_path = os.path.join(output_dir, output_filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(basic_result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()