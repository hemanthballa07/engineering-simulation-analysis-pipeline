import os
import sys
import json
import argparse
import jsonschema
from pathlib import Path
from datetime import datetime

# Add project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Imports from previous days
from scripts.extract_metrics import extract_run_metrics
from scripts.validate_metrics import validate_run_metrics
from ai.prompt_templates import SYSTEM_PROMPT, build_user_prompt
from ai.azure_openai_client import EngineeringAIClient

# Imports from Day 6
from observability.logging import get_logger, log_event
from observability.context import RequestContext
from observability.timing import Timer

logger = get_logger(__name__)

INSIGHTS_SCHEMA_PATH = os.path.join(project_root, 'ai', 'insights_schema.json')

def load_insights_schema():
    with open(INSIGHTS_SCHEMA_PATH, 'r') as f:
        return json.load(f)

def generate_mock_insights(metrics_payload):
    """Returns deterministic mock insights for CI/CD."""
    run_id = metrics_payload.get("run_id", "mock_run")
    return json.dumps({
        "executive_summary": f"MOCK SUMMARY: Run {run_id} was stable.",
        "best_variant": {
            "run_id": run_id,
            "reason": "Mock stability check passed.",
            "key_metrics": {"stability_ratio": 0.05}
        },
        "tradeoffs": ["Mock Tradeoff A vs B"],
        "anomalies_or_risks": [],
        "recommended_next_experiments": ["Decrease dt"],
        "confidence_score": 1.0,
        "confidence_justification": "Mock Mode Deterministic"
    })

def generate_insights_for_run(run_dir, client, output_dir=None, mock=False):
    """
    Orchestrates the insight generation flow for a single run.
    """
    run_path = Path(run_dir)
    run_id = run_path.name
    
    # Start tracing context given run_id
    with RequestContext(run_id=run_id):
        log_event(logger, "ai_generation_start", f"Processing Run: {run_id}")

        with Timer("metrics_extraction_and_validation", description="Extraction & Validation"):
            # 1. Extract Metrics
            try:
                metrics_payload = extract_run_metrics(run_dir)
            except Exception as e:
                logger.error(f"Metrics extraction failed: {e}")
                return False

            # 2. Validate Metrics
            is_valid, errors = validate_run_metrics(metrics_payload)
            if not is_valid:
                log_event(logger, "metrics_validation_failed", f"Validation errors: {errors}", errors=errors)
                return False

        # 3. Construct Prompt
        user_prompt = build_user_prompt(metrics_payload)
        
        # 4. Generate Audit Artifact
        audit_data = {
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "model_config": {
                "temperature": 0.0,
                "deployment": "MOCK" if mock else client.deployment_name
            },
            "system_prompt": SYSTEM_PROMPT,
            "user_prompt": user_prompt
        }
        
        if output_dir:
            out_path = Path(output_dir)
        else:
            out_path = run_path / "insights"
            
        out_path.mkdir(parents=True, exist_ok=True)
        
        prompt_file = out_path / f"{run_id}.prompt.json"
        with open(prompt_file, "w") as f:
            json.dump(audit_data, f, indent=2)
            
        # 5. Call AI (or Mock)
        with Timer("ai_inference", description="AI Model Inference"):
            try:
                if mock:
                    log_event(logger, "ai_mock_mode", "Generating mock insights")
                    raw_response = generate_mock_insights(metrics_payload)
                else:
                    log_event(logger, "ai_live_mode", f"Calling AI Model ({client.deployment_name})")
                    raw_response = client.generate_chat_completion(SYSTEM_PROMPT, user_prompt)
                
                # Parse JSON
                insights_json = json.loads(raw_response)
                
                # 6. Validate Output Schema
                schema = load_insights_schema()
                jsonschema.validate(instance=insights_json, schema=schema)
                
                # 7. Save Artifacts
                # JSON
                insights_file = out_path / f"{run_id}.insights.json"
                with open(insights_file, "w") as f:
                    json.dump(insights_json, f, indent=2)
                    
                # Markdown
                md_file = out_path / f"{run_id}.insights.md"
                with open(md_file, "w") as f:
                    f.write(f"# Engineering Insights: {run_id}\n\n")
                    f.write(f"**Confidence**: {insights_json.get('confidence_score')} ({insights_json.get('confidence_justification')})\n\n")
                    f.write(f"## Executive Summary\n{insights_json.get('executive_summary')}\n\n")
                    
                    best = insights_json.get('best_variant', {})
                    f.write(f"## Best Variant Anlaysis\n")
                    f.write(f"- **Outcome**: {best.get('reason')}\n")
                    f.write(f"- **Key Metrics**: {best.get('key_metrics')}\n\n")
                    
                    f.write("## Trade-offs\n")
                    for t in insights_json.get('tradeoffs', []):
                        f.write(f"- {t}\n")
                        
                    f.write("\n## Recommendations\n")
                    for r in insights_json.get('recommended_next_experiments', []):
                        f.write(f"- {r}\n")
                
                log_event(logger, "ai_generation_success", f"Insights saved to {out_path}")
                return True

            except json.JSONDecodeError:
                log_event(logger, "ai_generation_failed", "Invalid JSON from AI")
                return False
            except jsonschema.ValidationError as e:
                log_event(logger, "ai_generation_failed", f"Schema validation error: {e.message}")
                return False
            except Exception as e:
                log_event(logger, "ai_generation_failed", f"Error: {e}")
                return False

def main():
    parser = argparse.ArgumentParser(description="Generate AI Insights for runs.")
    parser.add_argument("--run-dir", type=str, help="Single run directory to process")
    parser.add_argument("--batch-dir", type=str, help="Directory containing multiple runs")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no API calls)")
    
    args = parser.parse_args()
    
    client = None
    if not args.mock:
        try:
            client = EngineeringAIClient()
        except Exception:
            sys.exit(1)
            
        if not client.client:
            logger.error("Skipping generation: No AI credentials found.")
            sys.exit(1)
    else:
        # Mock client placeholder if needed, or just pass None since we use 'mock' flag
        client = None

    if args.run_dir:
        generate_insights_for_run(args.run_dir, client, mock=args.mock)
        
    elif args.batch_dir:
        batch_path = Path(args.batch_dir)
        for d in batch_path.iterdir():
            if d.is_dir() and (d / "metadata.json").exists():
                generate_insights_for_run(str(d), client, mock=args.mock)
    else:
        print("Please provide --run-dir or --batch-dir")
        sys.exit(1)

if __name__ == "__main__":
    main()
