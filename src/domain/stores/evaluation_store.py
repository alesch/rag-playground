"""Storage for evaluation reports and metrics."""

from typing import Optional, List
from src.infrastructure.database.sqlite_client import SQLiteClient
from src.application.evaluation.evaluator import EvaluationReport, QuestionResult


class EvaluationStore:
    """Manages persistence of evaluation reports."""

    def __init__(self, db_client: SQLiteClient):
        self.db_client = db_client
        self.conn = db_client.conn

    def save_report(self, report: EvaluationReport) -> None:
        """Save an evaluation report with its question results."""
        cursor = self.conn.cursor()
        
        # Generate report ID
        report_id = f"eval-report-{report.run_id}"
        
        # Save report summary
        cursor.execute("""
            INSERT OR REPLACE INTO evaluation_reports 
            (id, run_id, ground_truth_run_id, mean_answer_relevancy)
            VALUES (?, ?, ?, ?)
        """, (
            report_id,
            report.run_id,
            report.gt_run_id,
            report.overall_metrics.get('mean_answer_relevancy')
        ))
        
        # Delete existing question results if replacing
        cursor.execute("""
            DELETE FROM evaluation_question_results WHERE report_id = ?
        """, (report_id,))
        
        # Save question results
        for q_id, result in report.results.items():
            cursor.execute("""
                INSERT INTO evaluation_question_results 
                (report_id, question_id, answer_relevancy)
                VALUES (?, ?, ?)
            """, (
                report_id,
                result.question_id,
                result.answer_relevancy
            ))
        
        self.conn.commit()

    def get_report(self, run_id: str) -> Optional[EvaluationReport]:
        """Retrieve an evaluation report by run ID."""
        cursor = self.conn.cursor()
        
        report_id = f"eval-report-{run_id}"
        
        # Get report summary
        cursor.execute("""
            SELECT * FROM evaluation_reports WHERE id = ?
        """, (report_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Get question results
        cursor.execute("""
            SELECT question_id, answer_relevancy 
            FROM evaluation_question_results 
            WHERE report_id = ?
        """, (report_id,))
        
        results = {}
        for q_row in cursor.fetchall():
            results[q_row['question_id']] = QuestionResult(
                question_id=q_row['question_id'],
                answer_relevancy=q_row['answer_relevancy']
            )
        
        return EvaluationReport(
            run_id=row['run_id'],
            gt_run_id=row['ground_truth_run_id'],
            results=results,
            overall_metrics={
                'mean_answer_relevancy': row['mean_answer_relevancy']
            }
        )

    def list_reports(self) -> List[EvaluationReport]:
        """List all evaluation reports."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT id FROM evaluation_reports ORDER BY evaluated_at DESC
        """)
        
        reports = []
        for row in cursor.fetchall():
            # Extract run_id from report_id format "eval-report-{run_id}"
            run_id = row['id'].replace('eval-report-', '')
            report = self.get_report(run_id)
            if report:
                reports.append(report)
        
        return reports
