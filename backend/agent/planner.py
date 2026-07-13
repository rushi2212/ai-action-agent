import os
import json
import re
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def normalize_plan_output(parsed):
    if not isinstance(parsed, dict):
        raise ValueError("AI plan must be a JSON object")

    steps = parsed.get("steps")
    if isinstance(steps, list):
        normalized_steps = [step for step in steps if isinstance(step, dict)]
        if normalized_steps:
            parsed["steps"] = normalized_steps
            return parsed

    nested_plan = parsed.get("plan")
    if isinstance(nested_plan, dict):
        nested_steps = nested_plan.get("steps")
        if isinstance(nested_steps, list) and nested_steps:
            return {"steps": [step for step in nested_steps if isinstance(step, dict)]}

    if isinstance(parsed.get("action"), str):
        single_step = {
            key: value
            for key, value in parsed.items()
            if key not in {"plan", "steps"}
        }
        return {"steps": [single_step]}

    raise ValueError(
        "AI plan must include a steps array or a single action object")


def plan_task(user_prompt: str):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are a browser automation agent. Convert user requests into detailed JSON action plans.

Always return a JSON object in this exact shape:
{"steps": [{"action": "...", "...": "..."}]}

Actions:
- goto: {"action": "goto", "url": "https://..."}
- type: {"action": "type", "selector": "css-selector", "text": "text"}
- click: {"action": "click", "selector": "css-selector"}
- select: {"action": "select", "selector": "select css-selector", "option": "option text or value"}
- select_by_text: {"action": "select_by_text", "field_identifier": "dropdown field name/label", "option": "option text"}
- fill_date: {"action": "fill_date", "selector": "input selector (optional)", "date": "YYYY-MM-DD or DD-MM-YYYY"}
- click_text: {"action": "click_text", "text": "exact text to find and click"}
- find_and_click_product: {"action": "find_and_click_product", "product_name": "product name"}
- find_and_click_button: {"action": "find_and_click_button", "button_text": "button text (partial match ok)"}
- wait: {"action": "wait", "ms": 1000}
- wait_for_selector: {"action": "wait_for_selector", "selector": "css-selector", "timeout": 10000}
- extract: {"action": "extract", "selector": "css-selector", "label": "description"}
- smart_extract: {"action": "smart_extract", "selectors": ["selector1", "selector2"], "label": "description"}
- extract_smart_results: {"action": "extract_smart_results"} - Intelligently extracts featured snippets, answers, and key info from search results
- press_enter: {"action": "press_enter", "selector": "input selector"} - Press Enter key in an input field
- verify_text_present: {"action": "verify_text_present", "text": "text to verify"} - Verify specific text is present on the page
- scroll_to_bottom: {"action": "scroll_to_bottom"} - Scroll to bottom of page
- fill_form_field: {"action": "fill_form_field", "field_identifier": "label or placeholder text", "value": "text to fill"} - Fill form field by label or placeholder

Output ONLY valid JSON with no additional text or markdown."""
                },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'^```\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        content = content.strip()

        print(f"AI Response: {content}")

        parsed = json.loads(content)
        normalized = normalize_plan_output(parsed)
        print(f"Parsed plan: {json.dumps(normalized, indent=2)}")
        return normalized

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON from AI: {str(e)}")
        raise ValueError(f"AI returned invalid JSON: {str(e)}")
    except Exception as e:
        print(f"❌ Error in plan_task: {str(e)}")
        raise
