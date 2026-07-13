from playwright.sync_api import sync_playwright
import time
import os


def env_flag(name, default="false"):
    return os.getenv(name, default).strip().lower() == "true"


def execute_plan(plan, log):
    extracted_data = []

    # Use headless mode for production (Render, etc)
    is_production = env_flag("RENDER") or env_flag("VERCEL")
    headless_mode = is_production or env_flag("HEADLESS")

    with sync_playwright() as p:
        # Launch browser with more realistic settings
        browser = p.chromium.launch(
            headless=headless_mode,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        context = browser.new_context(
            viewport=None,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        for i, step in enumerate(plan["steps"], 1):
            try:
                log(f"Step {i}/{len(plan['steps'])}: {step['action']}")

                if step["action"] == "goto":
                    page.goto(step["url"], timeout=30000)
                    log(f"  ✓ Navigated to {step['url']}")

                elif step["action"] == "click":
                    page.click(step["selector"], timeout=10000)
                    log(f"  ✓ Clicked {step['selector']}")

                elif step["action"] == "type":
                    page.fill(step["selector"], step["text"], timeout=10000)
                    log(f"  ✓ Typed '{step['text']}' into {step['selector']}")

                elif step["action"] == "select":
                    # Select an option from a dropdown by visible text or value
                    selector = step["selector"]
                    option = step["option"]
                    log(f"  🔍 Selecting '{option}' from dropdown {selector}")

                    try:
                        # Try to select by visible text first
                        page.select_option(
                            selector, label=option, timeout=10000)
                        log(f"  ✓ Selected '{option}' from {selector}")
                    except:
                        try:
                            # Try to select by value
                            page.select_option(
                                selector, value=option, timeout=10000)
                            log(f"  ✓ Selected '{option}' (by value) from {selector}")
                        except Exception as e:
                            log(f"  ❌ Could not select '{option}': {str(e)}")

                elif step["action"] == "select_by_text":
                    # Smart selector that finds dropdown by label/placeholder and selects option
                    field_identifier = step.get("field_identifier", "").lower()
                    option_text = step["option"]
                    log(
                        f"  🔍 Finding dropdown for '{field_identifier}' and selecting '{option_text}'")

                    found = False

                    # Try to find select element by name, id, or nearby label
                    try:
                        selectors = [
                            f"select[name*='{field_identifier}' i]",
                            f"select[id*='{field_identifier}' i]",
                            "select"
                        ]

                        for selector in selectors:
                            try:
                                select_elements = page.locator(selector).all()
                                for select_elem in select_elements:
                                    if select_elem.is_visible():
                                        # Try to select the option
                                        try:
                                            select_elem.select_option(
                                                label=option_text, timeout=5000)
                                            log(f"  ✓ Selected '{option_text}' from dropdown")
                                            found = True
                                            break
                                        except:
                                            try:
                                                select_elem.select_option(
                                                    value=option_text, timeout=5000)
                                                log(
                                                    f"  ✓ Selected '{option_text}' (by value)")
                                                found = True
                                                break
                                            except:
                                                continue
                                if found:
                                    break
                            except:
                                continue
                    except Exception as e:
                        log(f"  ⚠️ Select search failed: {str(e)}")

                    if not found:
                        log(f"  ❌ Could not select option: {option_text}")

                elif step["action"] == "fill_date":
                    # Fill a date input field
                    selector = step.get("selector", "")
                    date_value = step["date"]
                    log(f"  📅 Filling date '{date_value}' into {selector or 'date field'}")

                    try:
                        if selector:
                            # Direct selector provided
                            page.fill(selector, date_value, timeout=10000)
                            log(f"  ✓ Filled date '{date_value}' into {selector}")
                        else:
                            # Find date input by type
                            date_input = page.locator(
                                "input[type='date']").first
                            date_input.fill(date_value, timeout=10000)
                            log(f"  ✓ Filled date '{date_value}'")
                    except Exception as e:
                        log(f"  ❌ Could not fill date: {str(e)}")

                elif step["action"] == "press_enter":
                    # Press Enter key in the input field
                    page.locator(step["selector"]).first.press("Enter")
                    log(f"  ✓ Pressed Enter in {step['selector']}")

                elif step["action"] == "click_text":
                    # Click element containing specific text
                    text = step["text"]
                    page.get_by_text(text, exact=True).click(timeout=10000)
                    log(f"  ✓ Clicked element with text: {text}")

                elif step["action"] == "find_and_click_product":
                    # Intelligently find and click product by name
                    product_name = step["product_name"]
                    log(f"  🔍 Searching for product: {product_name}")

                    # Try multiple strategies to find the product
                    found = False

                    # Strategy 1: Look for exact text match
                    try:
                        elements = page.get_by_text(product_name).all()
                        for elem in elements:
                            if elem.is_visible():
                                # Find the clickable parent (card/link)
                                parent = elem.locator(
                                    'xpath=ancestor::*[self::a or self::button or contains(@class, "card") or contains(@class, "product")][1]')
                                if parent.count() > 0:
                                    parent.first.click()
                                    log(f"  ✓ Clicked product: {product_name}")
                                    found = True
                                    break
                                else:
                                    elem.click()
                                    log(
                                        f"  ✓ Clicked product element: {product_name}")
                                    found = True
                                    break
                    except Exception as e:
                        log(f"  ⚠️ Strategy 1 failed: {str(e)}")

                    # Strategy 2: Look for partial match in headings or titles
                    if not found:
                        try:
                            selectors = [
                                f"h1:has-text('{product_name}')",
                                f"h2:has-text('{product_name}')",
                                f"h3:has-text('{product_name}')",
                                f"[class*='product']:has-text('{product_name}')",
                                f"[class*='card']:has-text('{product_name}')",
                                f"[class*='item']:has-text('{product_name}')"
                            ]
                            for selector in selectors:
                                if page.locator(selector).count() > 0:
                                    elem = page.locator(selector).first
                                    # Find clickable parent
                                    parent = elem.locator(
                                        'xpath=ancestor::*[self::a or self::button or contains(@class, "card") or contains(@class, "product")][1]')
                                    if parent.count() > 0:
                                        parent.first.click()
                                    else:
                                        elem.click()
                                    log(
                                        f"  ✓ Clicked product using selector: {selector}")
                                    found = True
                                    break
                        except Exception as e:
                            log(f"  ⚠️ Strategy 2 failed: {str(e)}")

                    if not found:
                        log(f"  ❌ Could not find product: {product_name}")

                elif step["action"] == "find_and_click_button":
                    # Find and click button by text (partial match)
                    button_text = step["button_text"]
                    log(f"  🔍 Searching for button: {button_text}")

                    found = False

                    # Try different button selectors with text matching
                    try:
                        # Try exact match first
                        if page.get_by_role("button", name=button_text).count() > 0:
                            page.get_by_role(
                                "button", name=button_text).first.click()
                            log(f"  ✓ Clicked button: {button_text}")
                            found = True
                    except:
                        pass

                    if not found:
                        try:
                            # Try partial match with get_by_text
                            buttons = page.locator("button").all()
                            for btn in buttons:
                                btn_text = btn.text_content() or ""
                                if button_text.lower() in btn_text.lower() and btn.is_visible():
                                    btn.click()
                                    log(
                                        f"  ✓ Clicked button with text: {btn_text}")
                                    found = True
                                    break
                        except Exception as e:
                            log(f"  ⚠️ Button search failed: {str(e)}")

                    # Also check for links and divs that might be buttons
                    if not found:
                        try:
                            all_clickables = page.locator(
                                "button, a, [role='button'], [class*='button'], [class*='btn']").all()
                            for elem in all_clickables:
                                elem_text = elem.text_content() or ""
                                if button_text.lower() in elem_text.lower() and elem.is_visible():
                                    elem.click()
                                    log(
                                        f"  ✓ Clicked clickable element: {elem_text}")
                                    found = True
                                    break
                        except Exception as e:
                            log(
                                f"  ⚠️ Fallback button search failed: {str(e)}")

                    if not found:
                        log(f"  ❌ Could not find button: {button_text}")

                elif step["action"] == "verify_text_present":
                    # Verify specific text is present on the page
                    text = step["text"]
                    log(f"  🔍 Verifying text is present: {text}")

                    try:
                        # Wait a bit for content to load
                        page.wait_for_timeout(1000)

                        # Check if text is present
                        if page.get_by_text(text).count() > 0:
                            log(f"  ✓ Verified text is present: {text}")
                        else:
                            # Try partial match
                            page_content = page.content()
                            if text.lower() in page_content.lower():
                                log(
                                    f"  ✓ Verified text is present (partial match): {text}")
                            else:
                                log(f"  ⚠️ Text not found on page: {text}")
                    except Exception as e:
                        log(f"  ⚠️ Verification failed: {str(e)}")

                elif step["action"] == "scroll_to_bottom":
                    # Scroll to bottom of page
                    try:
                        page.evaluate(
                            "window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(1000)
                        log(f"  ✓ Scrolled to bottom of page")
                    except Exception as e:
                        log(f"  ⚠️ Scroll failed: {str(e)}")

                elif step["action"] == "fill_form_field":
                    # Fill form field by finding it using label or placeholder text
                    field_id = step["field_identifier"].lower()
                    value = step["value"]
                    log(f"  🔍 Filling form field: {field_id} with value: {value}")

                    found = False

                    # Strategy 1: Try common input selectors with attribute matching
                    try:
                        selectors = [
                            f"input[placeholder*='{field_id}' i]",
                            f"input[name*='{field_id}' i]",
                            f"input[id*='{field_id}' i]",
                            f"input[type='text'][placeholder*='{field_id}' i]",
                            f"input[aria-label*='{field_id}' i]",
                        ]

                        for selector in selectors:
                            try:
                                if page.locator(selector).count() > 0:
                                    page.locator(selector).first.fill(value)
                                    log(
                                        f"  ✓ Filled field using selector: {selector}")
                                    found = True
                                    break
                            except:
                                continue
                    except Exception as e:
                        log(f"  ⚠️ Strategy 1 failed: {str(e)}")

                    # Strategy 2: Find by label text
                    if not found:
                        try:
                            # Find label containing the text
                            labels = page.locator("label").all()
                            for label in labels:
                                label_text = label.text_content() or ""
                                if field_id in label_text.lower():
                                    # Try to find associated input
                                    label_for = label.get_attribute("for")
                                    if label_for:
                                        input_field = page.locator(
                                            f"#{label_for}")
                                        if input_field.count() > 0:
                                            input_field.fill(value)
                                            log(
                                                f"  ✓ Filled field via label: {label_text}")
                                            found = True
                                            break
                                    else:
                                        # Try to find input within or after label
                                        input_field = label.locator(
                                            "xpath=following-sibling::input[1] | .//input")
                                        if input_field.count() > 0:
                                            input_field.first.fill(value)
                                            log(
                                                f"  ✓ Filled field via label: {label_text}")
                                            found = True
                                            break
                        except Exception as e:
                            log(f"  ⚠️ Strategy 2 failed: {str(e)}")

                    # Strategy 3: Try all visible input fields and match by position/context
                    if not found:
                        try:
                            # Get all text-like inputs
                            inputs = page.locator(
                                "input[type='text'], input[type='tel'], input[type='number'], input:not([type])").all()

                            for inp in inputs:
                                if inp.is_visible():
                                    placeholder = inp.get_attribute(
                                        "placeholder") or ""
                                    name = inp.get_attribute("name") or ""
                                    input_id = inp.get_attribute("id") or ""
                                    aria_label = inp.get_attribute(
                                        "aria-label") or ""

                                    combined = f"{placeholder} {name} {input_id} {aria_label}".lower(
                                    )

                                    if field_id in combined:
                                        inp.fill(value)
                                        log(
                                            f"  ✓ Filled field with matching attribute: {field_id}")
                                        found = True
                                        break
                        except Exception as e:
                            log(f"  ⚠️ Strategy 3 failed: {str(e)}")

                    if not found:
                        log(f"  ❌ Could not find form field: {field_id}")

                elif step["action"] == "wait":
                    page.wait_for_timeout(step["ms"])
                    log(f"  ✓ Waited {step['ms']}ms")

                elif step["action"] == "wait_for_selector":
                    try:
                        page.wait_for_selector(
                            step["selector"], timeout=step.get("timeout", 10000))
                        log(f"  ✓ Element appeared: {step['selector']}")
                    except:
                        log(f"  ⚠️ Timeout waiting for: {step['selector']}")

                elif step["action"] == "smart_extract":
                    # Try multiple selectors for the same data
                    label = step.get("label", "Data")
                    selectors = step.get("selectors", [step.get("selector")])
                    found = False

                    for sel in selectors:
                        try:
                            if page.locator(sel).count() > 0:
                                text = page.locator(
                                    sel).first.text_content(timeout=3000)
                                if text and text.strip():
                                    extracted_data.append(
                                        {"label": label, "value": text.strip()})
                                    log(f"  ✓ Extracted {label}: {text.strip()} using {sel}")
                                    found = True
                                    break
                        except:
                            continue

                    if not found:
                        log(f"  ⚠️ Could not extract {label} with any selector")

                elif step["action"] == "extract_smart_results":
                    # Intelligently extract key information from search results
                    try:
                        log("  🧠 Extracting smart results from page...")
                        page.wait_for_timeout(1000)

                        # Try to extract featured snippets or direct answers
                        featured_selectors = [
                            # Google featured snippet
                            (".hgKElc", "Featured Answer"),
                            (".IZ6rdc", "Quick Answer"),
                            (".kno-rdesc span", "Knowledge Panel"),
                            ("[data-attrid='description'] span", "Description"),
                        ]

                        for selector, label in featured_selectors:
                            try:
                                if page.locator(selector).count() > 0:
                                    text = page.locator(
                                        selector).first.text_content(timeout=3000)
                                    if text and text.strip() and len(text.strip()) > 10:
                                        extracted_data.append(
                                            {"label": label, "value": text.strip()})
                                        log(
                                            f"  ✓ Extracted {label}: {text.strip()[:100]}...")
                            except:
                                continue

                        # Extract key-value pairs from knowledge panel
                        try:
                            kp_items = page.locator(".wDYxhc").all()
                            for item in kp_items[:5]:  # Limit to first 5 items
                                try:
                                    item_text = item.text_content(timeout=2000)
                                    if item_text and ':' in item_text:
                                        parts = item_text.split(':', 1)
                                        if len(parts) == 2:
                                            extracted_data.append(
                                                {"label": parts[0].strip(), "value": parts[1].strip()})
                                            log(
                                                f"  ✓ Extracted {parts[0].strip()}: {parts[1].strip()}")
                                except:
                                    continue
                        except:
                            pass

                        log(f"  ✓ Smart extraction completed")
                    except Exception as e:
                        log(f"  ⚠️ Smart extraction failed: {str(e)}")

                elif step["action"] == "extract":
                    try:
                        # Try to find and extract the element
                        selector = step["selector"]
                        label = step.get("label", "Data")

                        # Wait a bit for element to be ready
                        page.wait_for_timeout(500)

                        # Check if element exists
                        element_count = page.locator(selector).count()
                        log(f"  🔍 Checking {selector} for {label}: found {element_count} element(s)")

                        if element_count > 0:
                            text = page.locator(
                                selector).first.text_content(timeout=5000)
                            if text and text.strip():
                                extracted_data.append(
                                    {"label": label, "value": text.strip()})
                                log(f"  ✓ Extracted {label}: {text.strip()}")
                            else:
                                log(
                                    f"  ⚠️ Element found but empty for {label} ({selector})")
                        else:
                            log(f"  ⚠️ Element not found: {selector} for {label}")
                    except Exception as extract_error:
                        log(f"  ⚠️ Failed to extract {label}: {str(extract_error)}")

            except Exception as e:
                log(f"  ⚠️ Error in step {i}: {str(e)}")
                log(f"  → Continuing with next step...")

        # Try to extract relevant information from final page
        try:
            page_title = page.title()
            if page_title:
                log(f"📄 Page Title: {page_title}")
        except:
            pass

        # If no data was extracted but we're on a results page, try alternative methods
        if not extracted_data:
            log("⚠️ No data extracted, trying intelligent fallback...")

            # Try common weather widget selectors first
            weather_selectors = [
                ("#wob_tm", "Temperature"),
                ("#wob_dc", "Condition"),
                ("#wob_hm", "Humidity"),
                ("#wob_ws", "Wind"),
                ("#wob_pp", "Precipitation"),
            ]

            for selector, label in weather_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        text = page.locator(
                            selector).first.text_content(timeout=2000)
                        if text and text.strip():
                            extracted_data.append(
                                {"label": label, "value": text.strip()})
                            log(f"✓ Fallback extracted {label}: {text.strip()}")
                except:
                    continue

            # Try to extract featured snippets and answers
            if not extracted_data:
                answer_selectors = [
                    (".hgKElc", "Answer"),
                    (".IZ6rdc", "Quick Answer"),
                    (".kno-rdesc span", "Description"),
                    ("[data-attrid='title'] span", "Title"),
                    (".wDYxhc", "Info"),
                ]

                for selector, label in answer_selectors:
                    try:
                        elements = page.locator(selector).all()
                        # Max 3 items per selector
                        for idx, elem in enumerate(elements[:3]):
                            text = elem.text_content(timeout=2000)
                            if text and text.strip() and len(text.strip()) > 10 and len(text.strip()) < 500:
                                final_label = f"{label} {idx + 1}" if len(
                                    elements) > 1 else label
                                extracted_data.append(
                                    {"label": final_label, "value": text.strip()})
                                log(
                                    f"✓ Extracted {final_label}: {text.strip()[:80]}...")
                    except:
                        continue

            # Extract key-value pairs from tables or lists
            if not extracted_data:
                try:
                    # Try to find data tables
                    tables = page.locator("table").all()
                    for table in tables[:2]:  # Max 2 tables
                        rows = table.locator("tr").all()
                        for row in rows[:5]:  # Max 5 rows per table
                            cells = row.locator("td, th").all()
                            if len(cells) >= 2:
                                key = cells[0].text_content(
                                    timeout=1000).strip()
                                value = cells[1].text_content(
                                    timeout=1000).strip()
                                if key and value and len(key) < 100 and len(value) < 300:
                                    extracted_data.append(
                                        {"label": key, "value": value})
                                    log(
                                        f"✓ Extracted from table - {key}: {value[:50]}...")
                except:
                    pass

            # Last resort: extract first few search results
            if not extracted_data:
                try:
                    page_url = page.url
                    log(f"📍 Current URL: {page_url}")

                    # Try to get search result snippets
                    result_selectors = [
                        ".VwiC3b",  # Google search snippets
                        ".s",  # Alternative snippet class
                        "[data-content-feature='1']",
                    ]

                    for selector in result_selectors:
                        try:
                            results = page.locator(selector).all()
                            # Max 3 results
                            for idx, result in enumerate(results[:3]):
                                text = result.text_content(timeout=2000)
                                if text and len(text.strip()) > 20:
                                    clean_text = ' '.join(
                                        text.strip().split())[:300]
                                    extracted_data.append(
                                        {"label": f"Result {idx + 1}", "value": clean_text})
                                    log(
                                        f"✓ Extracted Result {idx + 1}: {clean_text[:80]}...")
                            if extracted_data:
                                break
                        except:
                            continue

                    # Final fallback: main content
                    if not extracted_data:
                        content_selectors = [
                            "#center_col", "#rso", "main", "#main"]
                        for sel in content_selectors:
                            try:
                                content = page.locator(
                                    sel).first.text_content(timeout=2000)
                                if content and len(content.strip()) > 50:
                                    clean_content = ' '.join(
                                        content.strip().split())[:400]
                                    extracted_data.append(
                                        {"label": "Main Content", "value": clean_content})
                                    log(
                                        f"ℹ️ Extracted main content from {sel}")
                                    break
                            except:
                                continue
                except:
                    pass

        log("✅ Task completed - Browser will stay open for 30 seconds")
        time.sleep(30)

        browser.close()
        log("Browser closed")

    return extracted_data
