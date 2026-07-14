import os
import json
import re
from urllib.parse import quote_plus
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


SHOPPING_INTENT_RE = re.compile(
    r"\b(buy|purchase|shop|shopping|price|prices|cheap|cheapest|best|top|under|budget|deal|deals|amazon|flipkart|product|products|phone|phones|smartphone|smartphones|laptop|laptops|tablet|tablets|watch|watches|headphone|headphones|earphone|earphones|tv|television|camera|shoes|shoe|sneaker|sneakers)\b",
    re.IGNORECASE,
)


def build_direct_search_plan(user_prompt: str):
    normalized_prompt = " ".join(user_prompt.split()).strip()
    if not normalized_prompt or not SHOPPING_INTENT_RE.search(normalized_prompt):
        return None

    prompt_lower = normalized_prompt.lower()
    search_term = quote_plus(normalized_prompt)

    if "flipkart" in prompt_lower:
        search_url = f"https://www.flipkart.com/search?q={search_term}"
        result_selector = "a._1fQZEK, a[href*='/p/']"
    else:
        search_url = f"https://www.amazon.in/s?k={search_term}"
        result_selector = "[data-component-type='s-search-result'] a.a-link-normal"

    plan = {
        "steps": [
            {
                "action": "goto",
                "url": search_url,
            },
            {
                "action": "wait_for_selector",
                "selector": result_selector,
                "timeout": 15000,
            },
        ]
    }

    if any(keyword in prompt_lower for keyword in ("open", "view", "details", "browse", "compare", "select", "choose")):
        plan["steps"].append(
            {
                "action": "click",
                "selector": result_selector,
            }
        )

    return plan


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
    direct_plan = build_direct_search_plan(user_prompt)
    if direct_plan is not None:
        print(f"Direct search plan: {json.dumps(direct_plan, indent=2)}")
        return direct_plan

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are a browser automation agent. Convert user requests into detailed JSON action plans.

Always return a JSON object in this exact shape:
{"steps": [{"action": "...", "...": "..."}]}

Prefer direct destination URLs over navigating through search inputs. For shopping and product queries, go straight to Amazon or Flipkart search URLs when possible instead of opening Google and typing into the search box.

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
