import re
import csv
import os

def clean_text(text):
    if not text:
        return ""
    
    # Remove Markdown Bold/Italic (**text**, *text*, __text__)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    
    # Remove Markdown Links [text](url) -> text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    
    # Remove Inline Code `text` -> text
    text = re.sub(r'`(.*?)`', r'\1', text)
    
    # Remove Headers (### Header) -> Header
    text = re.sub(r'#+\s*', '', text)
    
    # Remove backslash escapes (\.) -> .
    text = text.replace('\.', '.')
    
    return text.strip()

def remove_citations(text):
    if not text:
        return ""
    
    # Remove trailing citation numbers often seen in NotebookLM (e.g., "text 1, 2." or "text 1.")
    # Look for sequence of numbers and commas/spaces at the very end
    text = re.sub(r'\s+\d+(?:,\s*\d+)*\.?$', '', text)
    
    # Remove bracketed citations like [1], [1, 2]
    text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
    
    return text.strip()

def parse_llama_file(content):
    qa_dict = {}
    chunks = content.split('======================================================================')
    for chunk in chunks:
        q_match = re.search(r'\[\d+/50\] (Q\d+\.\d+):\s*(.*?)\n-+', chunk, re.DOTALL)
        a_match = re.search(r'ANSWER:\s*(.*?)\s*SOURCES:', chunk, re.DOTALL)
        s_match = re.search(r'SOURCES:\s*(.*)', chunk, re.DOTALL)
        if q_match and a_match:
            q_id = q_match.group(1).strip()
            q_text = q_match.group(2).strip()
            answer = a_match.group(1).strip()
            
            sources_text = s_match.group(1).strip() if s_match else ""
            sources = [s.strip('- ').strip() for s in sources_text.split('\n') if s.strip()]
            
            # Clean the answer
            cleaned_answer = remove_citations(clean_text(answer))
            
            qa_dict[q_id] = {
                'question': q_text,
                'answer': cleaned_answer,
                'sources': ", ".join(sources),
                'word_count': len(cleaned_answer.split())
            }
    return qa_dict

def parse_notebooklm_file(content):
    qa_dict = {}
    parts = re.split(r'\*\*Q(\d+\.\d+):', content)
    
    for i in range(1, len(parts), 2):
        q_id = "Q" + parts[i]
        body = parts[i+1]
        
        split_node = body.find('**')
        
        if split_node != -1:
            q_text = body[:split_node].strip()
            raw_answer = body[split_node+2:].strip()
            
            answer_end = re.search(r'\n### .*', raw_answer, re.DOTALL)
            if answer_end:
                answer = raw_answer[:answer_end.start()].strip()
            else:
                answer = raw_answer
            
            # Extract citations before cleaning
            citations = re.findall(r'\b\d+\b', answer)
            valid_citations = sorted(list(set([c for c in citations if c.isdigit() and int(c) < 100])))
            
            # Clean the answer
            cleaned_answer = remove_citations(clean_text(answer))
            
            qa_dict[q_id] = {
                'question': clean_text(q_text),
                'answer': cleaned_answer,
                'sources': ", ".join(valid_citations),
                'word_count': len(cleaned_answer.split())
            }
    return qa_dict

def main():
    base_dir = "tests"
    llama_path = os.path.join(base_dir, "output-llama3.2.md")
    notebook_path = os.path.join(base_dir, "output-notebookLM.md")
    output_csv = "model_comparison.csv"
    
    try:
        with open(llama_path, 'r', encoding='utf-8') as f:
            llama_content = f.read()
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = f.read()
    except Exception as e:
        print(f"Error reading files: {e}")
        return

    print("Parsing Llama...")
    llama_data = parse_llama_file(llama_content)
    
    print("Parsing NotebookLM...")
    notebook_data = parse_notebooklm_file(notebook_content)
    
    all_keys = set(llama_data.keys()) | set(notebook_data.keys())
    
    def sort_key(k):
        try:
            parts = k[1:].split('.')
            return [int(p) for p in parts]
        except:
            return [999,999]
    
    sorted_keys = sorted(all_keys, key=sort_key)
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'ID', 
            'Question', 
            'Llama Answer', 
            'NotebookLM Answer', 
            'Llama Status', 
            'NotebookLM Status', 
            'Llama Words', 
            'NotebookLM Words', 
            'Llama Sources', 
            'NotebookLM Citations', 
            'Precision [MANUAL]', 
            'Contradiction [MANUAL]'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for key in sorted_keys:
            l = llama_data.get(key, {'question': 'N/A', 'answer': 'N/A', 'sources': '', 'word_count': 0})
            n = notebook_data.get(key, {'question': 'N/A', 'answer': 'N/A', 'sources': '', 'word_count': 0})
            
            question_text = n['question'] if n['question'] != 'N/A' else l['question']
            
            writer.writerow({
                'ID': key,
                'Question': question_text,
                'Llama Answer': l['answer'],
                'NotebookLM Answer': n['answer'],
                'Llama Status': "Failed" if "cannot find" in l['answer'].lower() else "Success",
                'NotebookLM Status': "Failed" if "cannot find" in n['answer'].lower() else "Success",
                'Llama Words': l['word_count'],
                'NotebookLM Words': n['word_count'],
                'Llama Sources': l['sources'],
                'NotebookLM Citations': n['sources'],
                'Precision [MANUAL]': '',
                'Contradiction [MANUAL]': ''
            })
            
    print(f"Created clean {output_csv} with {len(sorted_keys)} rows.")

if __name__ == "__main__":
    main()