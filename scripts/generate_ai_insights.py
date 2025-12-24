import os
import sys
import json
import argparse
import logging
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

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INSIGHTS_SCHEMA_PATH = os.path.join(project_root, 'ai', 'insights_schema.json')

def load_insights_schema():
    with open(INSIGHTS_SCHEMA_PATH, 'r') as f:
        return json.load(f)

def generate_insights_for_run(run_dir, client, output_dir=None):
    """
    Orchestrates the insight generation flow for a single run.
    """
    run_path = Path(run_dir)
    run_id = run_path.name
    logger.info(f"Processing Run: {run_id}")

    # 1. Extract Metrics (using Day 3 logic)
    try:
        metrics_payload = extract_run_metrics(run_dir)
    except Exception as e:
        logger.error(f"Metrics extraction failed for {run_id}: {e}")
        return False

    # 2. Validate Metrics (Safety Gate)
    is_valid, errors = validate_run_metrics(metrics_payload)
    if not is_valid:
        logger.error(f"Metrics validation failed for {run_id}. AI will NOT run. Errors: {errors}")
        return False

    # 3. Construct Prompt
    user_prompt = build_user_prompt(metrics_payload)
    
    # 4. Generate Audit Artifact (Prompt)
    audit_data = {
        "run_id": run_id,
        "timestamp": datetime.utcnow().isoformat(),
        "model_config": {
            "temperature": 0.0,
            "deployment": client.deployment_name
        },
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }
    
    # Determine output paths
    if output_dir:
        out_path = Path(output_dir)
    else:
        out_path = run_path / "insights"
        
    out_path.mkdir(parents=True, exist_ok=True)
    
    prompt_file = out_path / f"{run_id}.prompt.json"
    with open(prompt_file, "w") as f:
        json.dump(audit_data, f, indent=2)
    logger.info(f"Audit: Prompt saved to {prompt_file}")

    # 5. Call AI
    try:
        logger.info(f"Calling AI Model ({client.deployment_name})...")
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
        
        logger.info(f"Success: Insights saved to {out_path}")
        return True

    except json.JSONDecodeError:
        logger.error("AI returned invalid JSON.")
        return False
    except jsonschema.ValidationError as e:
        logger.error(f"AI output schema validation failed: {e.message}")
        return False
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate AI Insights for runs.")
    parser.add_argument("--run-dir", type=str, help="Single run directory to process")
    parser.add_argument("--batch-dir", type=str, help="Directory containing multiple runs")
    
    args = parser.parse_args()
    
    # Initialize Client once
    try:
        client = EngineeringAIClient()
    except Exception:
        sys.exit(1)
        
    if not client.client:
        logger.error("Skipping generation: No AI credentials found.")
        sys.exit(1)

    if args.run_dir:
        generate_insights_for_run(args.run_dir, client)
        
    elif args.batch_dir:
        batch_path = Path(args.batch_dir)
        for d in batch_path.iterdir():
            if d.is_dir() and (d / "metadata.json").exists():
                generate_insights_for_run(str(d), client)
    else:
        print("Please provide --run-dir or --batch-dir")
        sys.exit(1)

if __name__ == "__main__":
    main()
