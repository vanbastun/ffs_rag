import requests
import json
from bs4 import BeautifulSoup
from pathlib import Path
import re


def fetch_faq_page():
    """Fetch the FAQ page from Fantasy Football Scout"""
    url = "https://www.fantasyfootballscout.co.uk/fantasy-football-faq-and-glossary"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching FAQ page: {e}")
        return None


def parse_faq_content(html_content):
    """Parse FAQ content from HTML and extract Q&A pairs"""
    soup = BeautifulSoup(html_content, "html.parser")
    faq_pairs = []
    
    # Process each paragraph element for regular FAQ questions
    for p in soup.find_all('p'):
        # Check if this paragraph contains a question (strong text)
        strong = p.find('strong')
        if strong:
            question = strong.get_text(strip=True)
            
            # Skip if this is part of Common Terms or Abbreviations (we'll handle those separately)
            if any(term in question.lower() for term in ['cleanie', 'shutout', 'differential', 'gameweek', 'bandwagon', 'position']):
                continue
            if any(abbrev in question.upper() for abbrev in ['FPL', 'PL', 'FFS', 'RMT', 'FT', 'ITB', 'GW', 'DGW', 'BGW', 'WC', 'BB', 'TC', 'FH', 'OOP', 'POO']):
                continue
            
            # Extract answer - get text after the strong tag, but stop at next strong tag
            answer_parts = []
            current_element = strong.next_sibling
            
            while current_element:
                if current_element.name == 'strong':
                    # Stop if we hit another question
                    break
                elif current_element.name == 'br':
                    # Skip br tags
                    pass
                elif hasattr(current_element, 'get_text'):
                    text = current_element.get_text(strip=True)
                    if text:
                        answer_parts.append(text)
                elif isinstance(current_element, str):
                    text = current_element.strip()
                    if text:
                        answer_parts.append(text)
                
                current_element = current_element.next_sibling
            
            answer = " ".join(answer_parts)
            
            # Clean up the answer
            answer = re.sub(r'\s+', ' ', answer).strip()
            
            if question and answer and len(answer) > 10:  # Filter out very short answers
                faq_pairs.append({
                    "question": question,
                    "answer": answer,
                    "section": "FAQ"
                })
    
    # Parse Common Terms section
    common_terms_heading = soup.find(['h2', 'h3'], string=re.compile(r'Common Terms', re.I))
    if common_terms_heading:
        # Find all paragraphs after the heading
        current = common_terms_heading.find_next('p')
        while current and current.name == 'p':
            # Look for <b> tags (terms) in this paragraph
            bold_tags = current.find_all('b')
            for bold in bold_tags:
                term = bold.get_text(strip=True)
                if term:
                    # Get the definition from the span or text after the bold tag
                    definition_parts = []
                    
                    # Check if there's a span with the definition
                    span = bold.find_next('span')
                    if span:
                        definition_parts.append(span.get_text(strip=True))
                    
                    # Also get any text after the span
                    for sibling in bold.next_siblings:
                        if sibling.name == 'span':
                            continue  # Already handled above
                        elif sibling.name == 'br':
                            break  # Stop at line breaks
                        elif hasattr(sibling, 'get_text'):
                            text = sibling.get_text(strip=True)
                            if text:
                                definition_parts.append(text)
                        elif isinstance(sibling, str):
                            text = sibling.strip()
                            if text:
                                definition_parts.append(text)
                    
                    definition = " ".join(definition_parts).strip()
                    # Remove leading dash and clean up
                    definition = re.sub(r'^[–-]\s*', '', definition).strip()
                    
                    if definition:
                        faq_pairs.append({
                            "question": f"What is {term}?",
                            "answer": definition,
                            "section": "Common Terms"
                        })
            
            current = current.find_next('p')
    
    # Parse Common Abbreviations section
    common_abbrev_heading = soup.find(['h2', 'h3'], string=re.compile(r'Common Abbreviations', re.I))
    if common_abbrev_heading:
        # Find all paragraphs after the heading
        current = common_abbrev_heading.find_next('p')
        while current and current.name == 'p':
            # Look for <b> tags (abbreviations) in this paragraph
            bold_tags = current.find_all('b')
            for bold in bold_tags:
                abbrev = bold.get_text(strip=True)
                if abbrev:
                    # Get the definition from the span or text after the bold tag
                    definition_parts = []
                    
                    # Check if there's a span with the definition
                    span = bold.find_next('span')
                    if span:
                        definition_parts.append(span.get_text(strip=True))
                    
                    # Also get any text after the span
                    for sibling in bold.next_siblings:
                        if sibling.name == 'span':
                            continue  # Already handled above
                        elif sibling.name == 'br':
                            break  # Stop at line breaks
                        elif hasattr(sibling, 'get_text'):
                            text = sibling.get_text(strip=True)
                            if text:
                                definition_parts.append(text)
                        elif isinstance(sibling, str):
                            text = sibling.strip()
                            if text:
                                definition_parts.append(text)
                    
                    definition = " ".join(definition_parts).strip()
                    # Remove leading dash and clean up
                    definition = re.sub(r'^[–-]\s*', '', definition).strip()
                    
                    if definition:
                        faq_pairs.append({
                            "question": f"What is {abbrev}?",
                            "answer": definition,
                            "section": "Common Abbreviations"
                        })
            
            current = current.find_next('p')
        
        # Also handle <strong> tags in abbreviations section
        current = common_abbrev_heading.find_next('p')
        while current and current.name == 'p':
            strong_tags = current.find_all('strong')
            for strong in strong_tags:
                abbrev = strong.get_text(strip=True)
                if abbrev:
                    # Get the definition from text after the strong tag
                    definition_parts = []
                    
                    for sibling in strong.next_siblings:
                        if sibling.name == 'br':
                            break  # Stop at line breaks
                        elif hasattr(sibling, 'get_text'):
                            text = sibling.get_text(strip=True)
                            if text:
                                definition_parts.append(text)
                        elif isinstance(sibling, str):
                            text = sibling.strip()
                            if text:
                                definition_parts.append(text)
                    
                    definition = " ".join(definition_parts).strip()
                    # Remove leading dash and clean up
                    definition = re.sub(r'^[–-]\s*', '', definition).strip()
                    
                    if definition:
                        faq_pairs.append({
                            "question": f"What is {abbrev}?",
                            "answer": definition,
                            "section": "Common Abbreviations"
                        })
            
            current = current.find_next('p')
    
    # Remove duplicates based on question
    seen_questions = set()
    unique_faq_pairs = []
    
    for pair in faq_pairs:
        if pair["question"] not in seen_questions:
            seen_questions.add(pair["question"])
            unique_faq_pairs.append(pair)
    
    return unique_faq_pairs


def save_faq_json(faq_pairs, output_path):
    """Save FAQ pairs as JSON"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(faq_pairs, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(faq_pairs)} FAQ pairs to {output_path}")


def main():
    """Main function to fetch, parse and save FAQ data"""
    print("Fetching FAQ page...")
    html_content = fetch_faq_page()
    
    if not html_content:
        print("Failed to fetch FAQ page")
        return
    
    print("Parsing FAQ content...")
    faq_pairs = parse_faq_content(html_content)
    
    if not faq_pairs:
        print("No FAQ pairs found")
        return
    
    # Save as JSON
    output_path = "/home/ubuser/ffs_rag/data/raw/faq_ffs.json"
    save_faq_json(faq_pairs, output_path)
    
    # Also save raw HTML for reference
    raw_html_path = "/home/ubuser/ffs_rag/data/raw/faq_ffs_raw.html"
    with open(raw_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Saved raw HTML to {raw_html_path}")
    
    # Print sample pairs
    print("\nSample FAQ pairs:")
    for i, pair in enumerate(faq_pairs[:5]):
        print(f"{i+1}. Q: {pair['question']}")
        print(f"   A: {pair['answer'][:100]}...")
        print(f"   Section: {pair['section']}")
        print()


if __name__ == "__main__":
    main()
    