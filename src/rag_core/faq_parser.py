import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class FAQItem:
    question: str
    answer: str
    section: str


class FAQParser:
    """Parser for FAQ files with section blocks and Q&A format"""
    
    def __init__(self):
        self.section_pattern = re.compile(r'^<([^>]+)>(?:</\1>)?$')
        self.question_pattern = re.compile(r'^(.+\?)$')
    
    def parse_faq_file(self, file_path: str) -> List[FAQItem]:
        """Parse FAQ file and return list of FAQ items"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_faq_content(content)
    
    def parse_faq_content(self, content: str) -> List[FAQItem]:
        """Parse FAQ content string and return list of FAQ items"""
        lines = content.split('\n')
        faq_items = []
        current_section = ""
        current_question = ""
        current_answer_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check for section markers
            section_match = self.section_pattern.match(line)
            if section_match:
                # Save previous Q&A if exists
                if current_question and current_answer_lines:
                    faq_items.append(FAQItem(
                        question=current_question,
                        answer='\n'.join(current_answer_lines).strip(),
                        section=current_section
                    ))
                
                # Start new section
                current_section = section_match.group(1)
                current_question = ""
                current_answer_lines = []
                continue
            
            # Check for question (ends with ?)
            if line.endswith('?'):
                # Save previous Q&A if exists
                if current_question and current_answer_lines:
                    faq_items.append(FAQItem(
                        question=current_question,
                        answer='\n'.join(current_answer_lines).strip(),
                        section=current_section
                    ))
                
                # Start new question
                current_question = line
                current_answer_lines = []
                continue
            
            # If we have a question, this line is part of the answer
            if current_question:
                current_answer_lines.append(line)
        
        # Don't forget the last Q&A
        if current_question and current_answer_lines:
            faq_items.append(FAQItem(
                question=current_question,
                answer='\n'.join(current_answer_lines).strip(),
                section=current_section
            ))
        
        return faq_items
    
    def faq_items_to_chunks(self, faq_items: List[FAQItem]) -> List[Dict[str, Any]]:
        """Convert FAQ items to chunks for vector storage"""
        chunks = []
        
        for i, item in enumerate(faq_items):
            # Create a combined text for the chunk
            combined_text = f"Q: {item.question}\nA: {item.answer}"
            
            # Create metadata
            metadata = {
                "source_id": f"faq_{i}",
                "question": item.question,
                "answer": item.answer,
                "section": item.section,
                "type": "faq",
                "lang": "en"
            }
            
            chunks.append({
                "text": combined_text,
                "metadata": metadata
            })
        
        return chunks
