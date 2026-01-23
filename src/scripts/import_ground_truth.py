import re
from pathlib import Path
from typing import Dict, List

from src.database.sqlite_client import SQLiteClient
from src.domain.models import Questionnaire, Question, Run, RunConfig, AnswerSuccess
from src.domain.questionnaire_store import QuestionnaireStore
from src.domain.run_store import RunStore
from src.config import SQLITE_DB_PATH

def parse_notebooklm_ground_truth(content: str) -> Dict[str, Dict[str, str]]:
    """
    Parse the NotebookLM export into a dictionary of {question_id: {question: text, answer: text}}.
    Reuses logic from scripts/generatecsv.py but keeps citations in text.
    """
    qa_dict = {}
    # Split by **Q1.1:, **Q1.2:, etc.
    parts = re.split(r'\*\*Q(\d+\.\d+):', content)
    
    for i in range(1, len(parts), 2):
        q_label = "Q" + parts[i]
        body = parts[i+1]
        
        # Find where the question text ends and answer starts (marked by bold or just text)
        # NotebookLM often has "Question text? ** Answer text"
        split_node = body.find('**')
        
        if split_node != -1:
            q_text = body[:split_node].strip()
            # Remove any trailing " " or ":"
            q_text = re.sub(r'[\s:]+$', '', q_text)
            
            raw_answer = body[split_node+2:].strip()
            
            # The answer ends when the next section starts (### Section ...)
            answer_end = re.search(r'\n### .*', raw_answer, re.DOTALL)
            if answer_end:
                answer = raw_answer[:answer_end.start()].strip()
            else:
                answer = raw_answer
            
            qa_dict[q_label] = {
                'question_text': q_text,
                'answer_text': answer
            }
    return qa_dict

def main():
    db_path = str(SQLITE_DB_PATH)
    print(f"Initializing database at {db_path}...")
    db_client = SQLiteClient(db_path)
    
    q_store = QuestionnaireStore(db_client)
    run_store = RunStore(db_client)
    
    # 1. Ensure Questionnaire exists
    questionnaire_id = "sample_questionnaire"
    questionnaire = q_store.get_questionnaire(questionnaire_id)
    if not questionnaire:
        print(f"Creating questionnaire '{questionnaire_id}'...")
        questionnaire = Questionnaire(
            id=questionnaire_id,
            name="Compliance Questionnaire 1.0",
            description="Sample compliance questions for testing RAG performance.",
            source_file="data/questionnaires/sample_questionnaire.md"
        )
        q_store.save_questionnaire(questionnaire)
    
    # 2. Parse NotebookLM output
    notebook_path = Path("tests/output-notebookLM.md")
    if not notebook_path.exists():
        print(f"Error: {notebook_path} not found.")
        return
        
    print(f"Parsing {notebook_path}...")
    content = notebook_path.read_text(encoding='utf-8')
    parsed_data = parse_notebooklm_ground_truth(content)
    
    # 3. Ensure Questions exist
    print("Ensuring questions exist in database...")
    questions = []
    for q_id, data in parsed_data.items():
        full_q_id = f"{questionnaire_id}:{q_id}"
        q = Question(
            id=full_q_id,
            questionnaire_id=questionnaire_id,
            question_id=q_id,
            text=data['question_text']
        )
        questions.append(q)
    
    q_store.save_questions(questions)
    
    # 4. Create Run for Ground Truth
    run_id = "ground_truth_notebooklm"
    existing_run = run_store.get_run(run_id)
    if existing_run:
        print(f"Target run '{run_id}' already exists. Skipping run creation.")
    else:
        print(f"Creating ground truth run '{run_id}'...")
        config = RunConfig(
            id="notebooklm_config",
            name="NotebookLM Reference Configuration",
            llm_model="NotebookLM",
            llm_temperature=0,
            retrieval_top_k=0,
            similarity_threshold=0,
            chunk_size=0,
            chunk_overlap=0,
            embedding_model="NotebookLM",
            embedding_dimensions=0,
            description="Static reference output from NotebookLM (Web Interface)"
        )
        run = Run(id=run_id, config=config, name="Ground Truth - NotebookLM")
        run_store.save_run(run)
    
    # 5. Insert Answers
    print(f"Inserting {len(parsed_data)} answers for run '{run_id}'...")
    for q_id, data in parsed_data.items():
        ans_id = f"ans-{run_id}-{q_id}"
        answer = AnswerSuccess(
            id=ans_id,
            run_id=run_id,
            question_id=f"{questionnaire_id}:{q_id}",
            answer_text=data['answer_text']
        )
        run_store.save_answer(answer)
        
    print("\n✅ Ground truth import completed successfully!")

if __name__ == "__main__":
    main()
