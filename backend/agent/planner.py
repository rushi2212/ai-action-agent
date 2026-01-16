import os
import json
import re
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def plan_task(user_prompt: str):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are a browser automation agent. Convert user requests into detailed JSON action plans.

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

Examples:

Q: Search for weather in New York
A: {"steps": [{"action": "goto", "url": "https://www.google.com"}, {"action": "wait", "ms": 2000}, {"action": "type", "selector": "textarea[name='q']", "text": "weather in New York"}, {"action": "wait", "ms": 500}, {"action": "click", "selector": "input[name='btnK']"}, {"action": "wait", "ms": 4000}, {"action": "smart_extract", "selectors": ["#wob_tm", "span[id*='wob_tm']", ".wob_t"], "label": "Temperature"}, {"action": "smart_extract", "selectors": ["#wob_dc", "span[id*='wob_dc']"], "label": "Condition"}, {"action": "smart_extract", "selectors": ["#wob_hm", "span[id*='wob_hm']"], "label": "Humidity"}, {"action": "smart_extract", "selectors": ["#wob_ws", "span[id*='wob_ws']"], "label": "Wind Speed"}]}

Q: What is the capital of France
A: {"steps": [{"action": "goto", "url": "https://www.google.com"}, {"action": "wait", "ms": 2000}, {"action": "type", "selector": "textarea[name='q']", "text": "capital of France"}, {"action": "wait", "ms": 500}, {"action": "click", "selector": "input[name='btnK']"}, {"action": "wait", "ms": 3000}, {"action": "extract_smart_results"}]}

Q: Search for current bitcoin price
A: {"steps": [{"action": "goto", "url": "https://www.google.com"}, {"action": "wait", "ms": 2000}, {"action": "type", "selector": "textarea[name='q']", "text": "bitcoin price"}, {"action": "wait", "ms": 500}, {"action": "click", "selector": "input[name='btnK']"}, {"action": "wait", "ms": 3000}, {"action": "extract_smart_results"}]}

Q: Get price of iPhone 15 on Amazon
A: {"steps": [{"action": "goto", "url": "https://www.amazon.com"}, {"action": "wait", "ms": 2000}, {"action": "type", "selector": "#twotabsearchtextbox", "text": "iPhone 15"}, {"action": "click", "selector": "#nav-search-submit-button"}, {"action": "wait", "ms": 3000}, {"action": "click", "selector": "[data-component-type='s-search-result'] h2 a"}, {"action": "wait", "ms": 3000}, {"action": "extract", "selector": ".a-price-whole", "label": "Price"}]}

Q: Search for laptops on Amazon and add first result to cart
A: {"steps": [{"action": "goto", "url": "https://www.amazon.com"}, {"action": "wait", "ms": 2000}, {"action": "type", "selector": "#twotabsearchtextbox", "text": "laptops"}, {"action": "click", "selector": "#nav-search-submit-button"}, {"action": "wait", "ms": 3000}, {"action": "click", "selector": "[data-component-type='s-search-result'] h2 a"}, {"action": "wait", "ms": 3000}, {"action": "click", "selector": "#add-to-cart-button"}, {"action": "wait", "ms": 2000}]}

Q: Search smartphones under 15000 and open first result
A: {"steps": [{"action": "goto", "url": "https://www.google.com"}, {"action": "wait", "ms": 1500}, {"action": "type", "selector": "textarea[name='q']", "text": "smartphones under 15000"}, {"action": "wait", "ms": 500}, {"action": "click", "selector": "input[name='btnK']"}, {"action": "wait", "ms": 3000}, {"action": "click", "selector": "#search h3"}, {"action": "wait", "ms": 2000}]}

Q: Go to https://tutedude-react-5.netlify.app/ and find Air Max 90 shoe, then add to cart
A: {"steps": [{"action": "goto", "url": "https://tutedude-react-5.netlify.app/"}, {"action": "wait", "ms": 3000}, {"action": "find_and_click_product", "product_name": "Air Max 90"}, {"action": "wait", "ms": 2000}, {"action": "find_and_click_button", "button_text": "Add to Cart"}, {"action": "wait", "ms": 2000}]}

Q: Go to https://rushi-genai-chatbot.netlify.app/ and search for features of langchain
A: {"steps": [{"action": "goto", "url": "https://rushi-genai-chatbot.netlify.app/"}, {"action": "wait", "ms": 3000}, {"action": "type", "selector": "input[type='text'], textarea, input[placeholder*='search'], input[placeholder*='Search'], input[placeholder*='ask'], input[placeholder*='Ask'], input[placeholder*='type'], input[placeholder*='Type']", "text": "features of langchain"}, {"action": "wait", "ms": 500}, {"action": "press_enter", "selector": "input[type='text'], textarea"}, {"action": "wait", "ms": 5000}, {"action": "extract_smart_results"}]}

Q: Open https://tutedude-react-5.netlify.app/, find Air Max 90, add to cart, go to checkout and complete purchase with card 4111 1111 1111 1111, expiry 12/26, CVV 123
A: {"steps": [{"action": "goto", "url": "https://tutedude-react-5.netlify.app/"}, {"action": "wait", "ms": 3000}, {"action": "find_and_click_product", "product_name": "Air Max 90"}, {"action": "wait", "ms": 2000}, {"action": "find_and_click_button", "button_text": "Add to Cart"}, {"action": "wait", "ms": 2000}, {"action": "find_and_click_button", "button_text": "Cart"}, {"action": "wait", "ms": 2000}, {"action": "verify_text_present", "text": "Air Max 90"}, {"action": "find_and_click_button", "button_text": "Checkout"}, {"action": "wait", "ms": 2000}, {"action": "fill_form_field", "field_identifier": "card", "value": "4111111111111111"}, {"action": "wait", "ms": 500}, {"action": "fill_form_field", "field_identifier": "expiry", "value": "12/26"}, {"action": "wait", "ms": 500}, {"action": "fill_form_field", "field_identifier": "cvv", "value": "123"}, {"action": "wait", "ms": 500}, {"action": "find_and_click_button", "button_text": "Place Order"}, {"action": "wait", "ms": 3000}]}

Q: Fill contact form with name John and email john@example.com
A: {"steps": [{"action": "type", "selector": "input[name='name']", "text": "John"}, {"action": "wait", "ms": 500}, {"action": "type", "selector": "input[name='email']", "text": "john@example.com"}, {"action": "wait", "ms": 500}, {"action": "type", "selector": "textarea[name='message']", "text": "Hello, I would like to get in touch"}, {"action": "wait", "ms": 500}, {"action": "click", "selector": "button[type='submit']"}, {"action": "wait", "ms": 2000}]}

Q: Go to https://tutredude-react-7.netlify.app/ and add a transaction with type Income, amount 5000, category Salary, date 15-01-2026, description work salary
A: {"steps": [{"action": "goto", "url": "https://tutredude-react-7.netlify.app/"}, {"action": "wait", "ms": 2000}, {"action": "click", "selector": "a[href='/transaction']"}, {"action": "wait", "ms": 2000}, {"action": "find_and_click_button", "button_text": "Add"}, {"action": "wait", "ms": 1000}, {"action": "select", "selector": "select[name='type']", "option": "Income"}, {"action": "wait", "ms": 500}, {"action": "type", "selector": "input[name='amount']", "text": "5000"}, {"action": "wait", "ms": 500}, {"action": "type", "selector": "input[name='category']", "text": "Salary"}, {"action": "wait", "ms": 500}, {"action": "type", "selector": "input[name='date']", "text": "2026-01-15"}, {"action": "wait", "ms": 500}, {"action": "type", "selector": "input[name='description']", "text": "work salary"}, {"action": "wait", "ms": 500}, {"action": "click", "selector": "button[type='submit']"}, {"action": "wait", "ms": 2000}, {"action": "verify_text_present", "text": "5000"}]}

Common selectors:
- Navigation links: a[href='/path'], .nav-link, a.navbar-item, Use click action with href selector like a[href='/transaction']
- Google: textarea[name='q'], input[name='btnK'], #search h3, #search a
- Google Weather: #wob_tm (temperature), #wob_dc (condition), #wob_hm (humidity), #wob_pp (precipitation), #wob_ws (wind speed), #wob_dts (day/time)
- Google Featured Snippets: .hgKElc, .IZ6rdc, .kno-rdesc span
- Amazon: #twotabsearchtextbox, #nav-search-submit-button, [data-component-type='s-search-result'] h2 a, #add-to-cart-button, .a-price-whole
- E-commerce sites: Use find_and_click_product for finding products by name, find_and_click_button for "Add to Cart" buttons
- Cart/Checkout: Use find_and_click_button for "Cart", "Checkout", "Place Order", "Pay Now" etc.
- Payment forms: Use fill_form_field for card number, expiry, CVV - it finds fields by label/placeholder text
- Search inputs: input[type='text'], input[type='search'], textarea, input[placeholder*='search'], input[placeholder*='Search']
- Chat/AI apps: input[type='text'], textarea, input[placeholder*='ask'], input[placeholder*='type'], input[placeholder*='message']
- Forms: input[name='name'], input[name='email'], input[type='email'], textarea, button[type='submit']
- Generic buttons: button, input[type='submit'], .btn, [role='button']
- First result: .result:first-child a, h3:first-of-type, [data-index='0']

Rules:
1. Always wait 1500-3000ms after navigation/page loads
2. Wait 500-1000ms after typing in forms
3. Use specific CSS selectors (id, name, data attributes) when known
4. For navigating to different pages within a site: use click action with a[href='/page-path'] selector
5. For product finding: use find_and_click_product with the exact product name
6. For clicking buttons by text: use find_and_click_button (it does partial matching)
7. For forms: type in each field with waits, then click submit
8. For search + action: go to site, search, click result, perform action
9. For information queries (what is, who is, when, where): use extract_smart_results to get featured snippets and direct answers
10. For weather queries: use smart_extract with specific weather selectors
11. For product/price queries on e-commerce sites: use find_and_click_product and find_and_click_button
12. Increase wait time to 3000-5000ms after search/submit to ensure results load
13. For unknown search inputs on custom sites: use broad selectors like input[type='text'], textarea
14. Use press_enter instead of clicking submit buttons when appropriate (chat apps, search boxes)
15. Wait at least 3000-5000ms after submitting queries to AI/chat apps for response to load
16. For checkout flows: add to cart → click Cart → verify product → click Checkout → fill payment fields → click Place Order/Pay
17. Use fill_form_field for payment forms - it's smarter than type and finds fields by label/placeholder
18. Use verify_text_present to confirm items are in cart before checkout
19. Wait 2-3 seconds between checkout steps to allow page transitions
20. For dropdowns/select elements: use select_by_text with field_identifier (e.g., "type", "category") and option text
21. For date fields: use fill_date with date in format YYYY-MM-DD or DD-MM-YYYY
22. After form submission, verify success by checking for confirmation text or submitted values
23. Output ONLY JSON"""
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

    try:
        parsed = json.loads(content)
        print(f"Parsed plan: {json.dumps(parsed, indent=2)}")
        return parsed
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {content}")
        print(f"❌ Error: {e}")
        # Return a default plan if parsing fails
        return {
            "steps": [
                {"action": "goto", "url": "https://www.google.com"},
                {"action": "wait", "ms": 1000}
            ]
        }
