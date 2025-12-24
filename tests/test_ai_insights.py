import pytest
import json
import os
from unittest.mock import MagicMock, patch
from scripts.generate_ai_insights import generate_insights_for_run, EngineeringAIClient

# Sample valid metrics payload (subset)
VALID_METRICS = {
    "run_id": "run_test_ai",
    "parameter_set": {"alpha": 0.1, "nx": 50},
    "performance_metrics": {
        "max_temperature": 0.5,
        "min_temperature": 0.0,
        "mean_temperature": 0.2,
        "stability_ratio": 0.1
    },
    "quality_metrics": {"converged": True, "steps": 100},
    "execution_metrics": {"timestamp": "2025-01-01T00:00:00", "platform": "Test"}
}

# Sample valid AI response
VALID_AI_RESPONSE = json.dumps({
    "executive_summary": "Test summary.",
    "best_variant": {
        "run_id": "run_test_ai",
        "reason": "Stable and fast.",
        "key_metrics": {"max_temp": 0.5}
    },
    "tradeoffs": ["Tradeoff A vs B"],
    "anomalies_or_risks": [],
    "recommended_next_experiments": ["Try alpha=0.2"],
    "confidence_score": 0.95,
    "confidence_justification": "Clear data."
})

@pytest.fixture
def mock_client():
    client = MagicMock(spec=EngineeringAIClient)
    client.deployment_name = "test-deploy"
    client.generate_chat_completion.return_value = VALID_AI_RESPONSE
    return client

@pytest.fixture
def mock_run_dir(tmp_path):
    run_dir = tmp_path / "run_test_ai"
    run_dir.mkdir()
    
    # Write necessary artifacts for extract_metrics to work
    # We need to mock metadata.json and metrics.json properly as extract_metrics reads them
    # OR we can mock extract_metrics. Let's mock extract_metrics to keep this test focused on the AI flow.
    return str(run_dir)

@patch("scripts.generate_ai_insights.extract_run_metrics")
@patch("scripts.generate_ai_insights.validate_run_metrics")
def test_generate_insights_success(mock_validate, mock_extract, mock_client, mock_run_dir):
    """Test successful generation flow."""
    # Setup mocks
    mock_extract.return_value = VALID_METRICS
    mock_validate.return_value = (True, [])
    
    # Execute
    result = generate_insights_for_run(mock_run_dir, mock_client)
    
    assert result is True
    
    # Check artifacts created
    out_dir = os.path.join(mock_run_dir, "insights")
    assert os.path.exists(os.path.join(out_dir, "run_test_ai.prompt.json"))
    assert os.path.exists(os.path.join(out_dir, "run_test_ai.insights.json"))
    assert os.path.exists(os.path.join(out_dir, "run_test_ai.insights.md"))
    
    # Verify AI call
    mock_client.generate_chat_completion.assert_called_once()

@patch("scripts.generate_ai_insights.extract_run_metrics")
@patch("scripts.generate_ai_insights.validate_run_metrics")
def test_generate_insights_invalid_metrics(mock_validate, mock_extract, mock_client, mock_run_dir):
    """Test that AI is NOT called if metrics validation fails."""
    mock_extract.return_value = VALID_METRICS
    mock_validate.return_value = (False, ["Physics Error"])
    
    result = generate_insights_for_run(mock_run_dir, mock_client)
    
    assert result is False
    mock_client.generate_chat_completion.assert_not_called()

@patch("scripts.generate_ai_insights.extract_run_metrics")
@patch("scripts.generate_ai_insights.validate_run_metrics")
def test_generate_insights_bad_ai_schema(mock_validate, mock_extract, mock_client, mock_run_dir):
    """Test handling of invalid JSON from AI."""
    mock_extract.return_value = VALID_METRICS
    mock_validate.return_value = (True, [])
    
    # AI returns valid JSON but invalid against our schema (missing fields)
    mock_client.generate_chat_completion.return_value = json.dumps({"foo": "bar"})
    
    result = generate_insights_for_run(mock_run_dir, mock_client)
    
    assert result is False
    # Should verify audit prompt still exists even if output failed? 
    # Current logic saves prompt before calling AI, so yes.
    out_dir = os.path.join(mock_run_dir, "insights")
    assert os.path.exists(os.path.join(out_dir, "run_test_ai.prompt.json"))
