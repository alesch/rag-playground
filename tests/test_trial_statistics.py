"""Tests for trial statistics calculation."""

import pytest
from scripts.calculate_trial_statistics import (
    calculate_statistics,
    get_trial_scores
)


class TestCalculateStatistics:
    """Tests for calculate_statistics function."""
    
    def test_calculates_mean_for_single_score(self):
        # Given
        scores = [0.85]
        
        # When
        stats = calculate_statistics(scores)
        
        # Then
        assert stats['mean'] == 0.85
        assert stats['stdev'] == 0.0  # Single value has no std dev
        assert stats['count'] == 1
    
    def test_calculates_mean_for_multiple_scores(self):
        # Given
        scores = [0.80, 0.85, 0.90]
        
        # When
        stats = calculate_statistics(scores)
        
        # Then
        assert stats['mean'] == pytest.approx(0.85, rel=1e-2)
        assert stats['count'] == 3
    
    def test_calculates_standard_deviation(self):
        # Given
        scores = [0.80, 0.85, 0.90]
        
        # When
        stats = calculate_statistics(scores)
        
        # Then
        assert stats['stdev'] > 0
        assert stats['stdev'] == pytest.approx(0.05, rel=1e-2)
    
    def test_finds_min_and_max(self):
        # Given
        scores = [0.70, 0.85, 0.95]
        
        # When
        stats = calculate_statistics(scores)
        
        # Then
        assert stats['min'] == 0.70
        assert stats['max'] == 0.95
    
    def test_handles_empty_list(self):
        # Given
        scores = []
        
        # When
        stats = calculate_statistics(scores)
        
        # Then
        assert stats['mean'] == 0.0
        assert stats['stdev'] == 0.0
        assert stats['count'] == 0
        assert stats['min'] == 0.0
        assert stats['max'] == 0.0
    
    def test_returns_all_required_fields(self):
        # Given
        scores = [0.85, 0.90]
        
        # When
        stats = calculate_statistics(scores)
        
        # Then
        assert 'mean' in stats
        assert 'stdev' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert 'count' in stats


class TestGetTrialScores:
    """Tests for get_trial_scores function."""
    
    def test_fetches_scores_from_database(self, mock_db_client):
        # Given
        mock_db_client.cursor_returns([
            (0.85,),
            (0.88,),
            (0.82,)
        ])
        
        # When
        scores = get_trial_scores(mock_db_client, "Baseline%", 3)
        
        # Then
        assert len(scores) == 3
        assert scores == [0.85, 0.88, 0.82]
    
    def test_uses_correct_sql_pattern(self, mock_db_client):
        # Given
        pattern = "Statistical - Baseline%"
        limit = 5
        
        # When
        get_trial_scores(mock_db_client, pattern, limit)
        
        # Then
        mock_db_client.assert_executed_with_params(pattern, limit)
    
    def test_returns_empty_list_when_no_results(self, mock_db_client):
        # Given
        mock_db_client.cursor_returns([])
        
        # When
        scores = get_trial_scores(mock_db_client, "NonExistent%", 3)
        
        # Then
        assert scores == []
    
    def test_orders_by_created_at_desc(self, mock_db_client):
        # Given
        mock_db_client.cursor_returns([
            (0.90,),  # Most recent
            (0.85,),
            (0.80,)   # Oldest
        ])
        
        # When
        scores = get_trial_scores(mock_db_client, "Test%", 3)
        
        # Then
        # Should return in order from database (already DESC)
        assert scores[0] == 0.90
        assert scores[2] == 0.80


# Fixtures

@pytest.fixture
def mock_db_client():
    """Mock database client for testing."""
    
    class MockCursor:
        def __init__(self):
            self._results = []
            self._executed_sql = None
            self._executed_params = None
        
        def execute(self, sql, params=None):
            self._executed_sql = sql
            self._executed_params = params
        
        def fetchall(self):
            return self._results
        
        def set_results(self, results):
            self._results = results
    
    class MockDBClient:
        def __init__(self):
            self._cursor = MockCursor()
            self.conn = self
        
        def cursor(self):
            return self._cursor
        
        def cursor_returns(self, results):
            """Helper to set cursor results."""
            self._cursor.set_results(results)
        
        def assert_executed_with_params(self, *expected_params):
            """Assert execute was called with expected params."""
            assert self._cursor._executed_params == expected_params
    
    return MockDBClient()
