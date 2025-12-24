import json

SYSTEM_PROMPT = """You are a Senior Principal Engineer at a top-tier technology company. 
Your goal is to analyze simulation results and provide actionable, data-driven insights.

RULES:
1. TRUTHFULNESS: Only use the data provided in the context. DO NOT invent metrics or values.
2. CITATION: When making a claim, cite the specific metric key and value.
3. CONCISENESS: Be brief and professional. Avoid fluff.
4. FORMAT: You must Output Valid JSON ONLY which validates against the provided schema.
5. FOCUS: Focus on trade-offs (e.g., Stability vs. Performance) and engineering constraints.

Your output key 'confidence_score' should reflect your certainty based on the data provided. 
If the data is sparse or nonsensical, lower the score and explain why in 'confidence_justification'.
"""

def build_user_prompt(metrics_payload):
    """
    Constructs the user prompt with the metrics payload.
    """
    # Compact JSON to save tokens
    metrics_str = json.dumps(metrics_payload, separators=(',', ':'))
    
    return f"""
Analyze the following simulation metrics and produce an engineering insight report in JSON format.

METRICS PAYLOAD:
```json
{metrics_str}
```

REQUIRED OUTPUT FORMAT (JSON):
- executive_summary: string
- best_variant: {{ "run_id": string, "reason": string, "key_metrics": dict }}
- tradeoffs: list[string]
- anomalies_or_risks: list[string]
- recommended_next_experiments: list[string]
- confidence_score: float (0.0-1.0)
- confidence_justification: string
"""
