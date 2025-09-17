import json
import re
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup


def fetch_faq_page() -> str:
    """Fetch the FAQ page from Fantasy Football Scout"""
    url = "https://www.fantasyfootballscout.co.uk/fantasy-football-faq-and-glossary"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching FAQ page: {e}")
        return ""


def parse_faq_content(html_content: str) -> list[dict[str, Any]]:
    """Parse FAQ content from HTML and extract Q&A pairs"""
    soup = BeautifulSoup(html_content, "html.parser")
    faq_pairs = []

    # Sequential scanning approach - track current section as we go through h2 and p tags
    current_heading = None
    all_tags = soup.find_all(["h2", "p"])

    i = 0
    while i < len(all_tags):
        tag = all_tags[i]

        if tag.name == "h2":
            # Start a new section
            current_heading = tag.get_text(strip=True)
        elif tag.name == "p" and current_heading is not None:
            # Skip "Join Our Leagues" section
            if current_heading == "Join Our Leagues":
                i += 1
                continue

            # Check if this paragraph has bold elements
            bold_elements = tag.find_all(["strong", "b"])

            # For abbreviations/terms section, process all bold elements
            if current_heading and (
                "Terms" in current_heading or "Abbreviations" in current_heading
            ):
                for bold_element in bold_elements:
                    question = bold_element.get_text(strip=True)
                    if question:  # Skip if empty
                        # Extract answer for this abbreviation
                        answer_parts = []
                        current_element = bold_element.next_sibling

                        while current_element:
                            if current_element.name in ["strong", "b"]:
                                # Stop if we hit another abbreviation
                                break
                            elif current_element.name == "br":
                                # Skip br tags
                                pass
                            elif hasattr(current_element, "get_text"):
                                text = current_element.get_text(strip=True)
                                if text:
                                    answer_parts.append(text)
                            elif isinstance(current_element, str):
                                text = current_element.strip()
                                if text:
                                    answer_parts.append(text)

                            current_element = current_element.next_sibling

                        answer = " ".join(answer_parts)
                        answer = re.sub(r"^[-–]\s*", "", answer).strip()
                        answer = re.sub(r"\s+", " ", answer).strip()

                        if question and answer and len(answer) > 1:
                            formatted_question = f"What is {question}?"
                            faq_pairs.append(
                                {
                                    "question": formatted_question,
                                    "answer": answer,
                                    "section": current_heading,
                                }
                            )
            elif bold_elements and bold_elements[0].parent == tag:
                # This is a regular question paragraph - only process the first bold element
                bold_element = bold_elements[0]
                question = bold_element.get_text(strip=True)

                # Extract answer from current paragraph
                answer_parts = []
                current_element = bold_element.next_sibling

                while current_element:
                    if current_element.name in ["strong", "b"]:
                        # Stop if we hit another question
                        break
                    elif current_element.name == "br":
                        # Skip br tags
                        pass
                    elif current_element.name == "a":
                        # Replace link text with full URL
                        href = current_element.get("href", "")
                        if href:
                            answer_parts.append(f"({href})")
                        else:
                            answer_parts.append(current_element.get_text(strip=True))
                    elif hasattr(current_element, "get_text"):
                        text = current_element.get_text(strip=True)
                        if text:
                            answer_parts.append(text)
                    elif isinstance(current_element, str):
                        text = current_element.strip()
                        if text:
                            answer_parts.append(text)

                    current_element = current_element.next_sibling

                # Now check if there are consecutive paragraphs that continue the answer
                j = i + 1
                while j < len(all_tags) and all_tags[j].name == "p":
                    next_p = all_tags[j]
                    # If next paragraph doesn't start with bold (no new question), it's part of the answer
                    next_bold = next_p.find(["strong", "b"])
                    if not next_bold or next_bold.parent != next_p:
                        # This paragraph continues the answer
                        next_text = next_p.get_text(strip=True)
                        if next_text:
                            answer_parts.append(next_text)
                        j += 1
                    else:
                        break

                # Move i to the last paragraph we processed
                i = j - 1

                answer = " ".join(answer_parts)

                # Clean up the answer - remove leading dash
                answer = re.sub(r"^[-–]\s*", "", answer).strip()
                answer = re.sub(r"\s+", " ", answer).strip()

                if question and answer and len(answer) > 3:
                    faq_pairs.append(
                        {"question": question, "answer": answer, "section": current_heading}
                    )

        i += 1

    # Remove duplicates based on question
    seen_questions = set()
    unique_faq_pairs = []

    for pair in faq_pairs:
        if pair["question"] not in seen_questions:
            seen_questions.add(pair["question"])
            unique_faq_pairs.append(pair)

    return unique_faq_pairs


def save_faq_json(faq_pairs: list[dict[str, Any]], output_path: str) -> None:
    """Save FAQ pairs as JSON"""
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path_obj, "w", encoding="utf-8") as f:
        json.dump(faq_pairs, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(faq_pairs)} FAQ pairs to {output_path}")


def main() -> None:
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
    output_path = "/home/ubuser/r2/ffs_rag/data/raw/faq_ffs.json"
    save_faq_json(faq_pairs, output_path)

    # Also save raw HTML for reference
    raw_html_path = "/home/ubuser/r2/ffs_rag/data/raw/faq_ffs_raw.html"
    with open(raw_html_path, "w", encoding="utf-8") as f:
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
