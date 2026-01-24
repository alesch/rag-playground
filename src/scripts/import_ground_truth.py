import re
from pathlib import Path
from typing import Dict, List

from src.database.sqlite_client import SQLiteClient
from src.domain.models import Run, RunConfig, AnswerSuccess
from src.domain.questionnaire_store import QuestionnaireStore
from src.domain.run_store import RunStore
from src.config import SQLITE_DB_PATH

def parse_notebooklm_ground_truth(content: str) -> Dict[str, str]:
    """Parse the NotebookLM export into a dictionary of {question_id: answer_text}."""
    qa_dict = {}
    # Split by **Q1.1:, **Q1.2:, etc.
    parts = re.split(r'\*\*Q(\d+\.\d+):', content)
    for i in range(1, len(parts), 2):
        q_label = "Q" + parts[i]
        body = parts[i+1]
        
        # Find where the question text ends and answer starts (marked by bold or just text)
        split_node = body.find('**')
        if split_node != -1:
            raw_answer = body[split_node+2:].strip()
            
            # The answer ends when the next section starts (### Section ...)
            answer_end = re.search(r'\n### .*', raw_answer, re.DOTALL)
            answer = raw_answer[:answer_end.start()].strip() if answer_end else raw_answer
            qa_dict[q_label] = answer
    return qa_dict

def main():
    db_path = str(SQLITE_DB_PATH)
    print(f"Connecting to database at {db_path}...")
    db_client = SQLiteClient(db_path)
    q_store = QuestionnaireStore(db_client)
    run_store = RunStore(db_client)
    
    # 1. Use existing questionnaire
    questionnaire_id = "sample_questionnaire"
    questionnaire = q_store.get_questionnaire(questionnaire_id)
    if not questionnaire:
        # Fallback to ingestion if missing to ensure we have questions
        questionnaire_src = Path("data/questionnaires/sample_questionnaire.md")
        if not questionnaire_src.exists():
            print(f"Error: Base questionnaire '{questionnaire_src}' not found. Cannot proceed.")
            return
        print(f"Questionnaire missing. Ingesting from {questionnaire_src}...")
        questionnaire, questions = q_store.import_from_markdown(questionnaire_src)
    else:
        print(f"✅ Questionnaire '{questionnaire_id}' found in database.")
        questions = q_store.get_questions(questionnaire_id)

    # 2. Parse NotebookLM output
    notebook_path = Path("tests/output-notebookLM.md")
    if not notebook_path.exists():
        print(f"Error: {notebook_path} not found.")
        return
        
    print(f"Parsing answers from {notebook_path}...")
    content = notebook_path.read_text(encoding='utf-8')
    parsed_answers = parse_notebooklm_ground_truth(content)
    
    # 3. Handle Ground Truth Run
    run_id = "ground_truth_notebooklm"
    existing_run = run_store.get_run(run_id)
    if not existing_run:
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
            description="Static reference output from NotebookLM"
        )
        run = Run(id=run_id, config=config, name="Ground Truth - NotebookLM")
        run_store.save_run(run)
    else:
        print(f"✅ Run '{run_id}' already exists.")
    
    # 4. Insert Answers
    print(f"Inserting ground truth answers...")
    found_count = 0
    for q_label, answer_text in parsed_answers.items():
        full_q_id = f"{questionnaire_id}:{q_label}"
        ans_id = f"ans-{run_id}-{q_label}"
        
        answer = AnswerSuccess(
            id=ans_id,
            run_id=run_id,
            question_id=full_q_id,
            answer_text=answer_text
        )
        run_store.save_answer(answer)
        found_count += 1
        
    print(f"\n✅ Ground truth import completed: {found_count}/{len(questions)} matched.")

if __name__ == "__main__":
    main()
