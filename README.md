# AI Action Agent - Enhanced for Web Automation

An intelligent browser automation agent that converts natural language commands into executable browser actions using LLM planning and Playwright execution.

## Recent Improvements

### New Features Added:
1. **Smart Product Finding** - `find_and_click_product` action that intelligently locates products by name
2. **Smart Button Clicking** - `find_and_click_button` action with partial text matching
3. **Press Enter Support** - `press_enter` action for submitting forms/searches
4. **Better Element Detection** - Multiple strategies for finding elements on dynamic websites
5. **Enhanced Examples** - Added examples for e-commerce and AI chat interactions

### Fixed Issues:
- ✅ Product search and cart operations on e-commerce sites
- ✅ Chatbot/AI website interactions
- ✅ Better handling of dynamic content
- ✅ Improved element visibility detection

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

4. Set up your GROQ API key:
```bash
# Windows PowerShell
$env:GROQ_API_KEY="your-api-key-here"

# Or create a .env file
echo GROQ_API_KEY=your-api-key-here > .env
```

5. Run the backend server:
```bash
uvicorn main:app --reload
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:5173`

## Testing the Improvements

### Test 1: Product Search and Add to Cart
**Command:**
```
Open the website https://tutedude-react-5.netlify.app/. Find the shoe product named "Air Max 90". Click on the Add to Cart button for this product.
```

**What it does:**
1. Opens the e-commerce site
2. Intelligently finds the "Air Max 90" product using multiple detection strategies
3. Clicks on the product or its parent card
4. Finds and clicks the "Add to Cart" button

### Test 2: AI Chatbot Interaction
**Command:**
```
Go to https://rushi-genai-chatbot.netlify.app/ and search for the features of langchain
```

**What it does:**
1. Opens the chatbot website
2. Finds the input field (handles various input types)
3. Types the query
4. Presses Enter to submit
5. Waits for response and extracts results

### Test 3: Google Search (Still Works)
**Command:**
```
Search for weather in New York
```

**What it does:**
1. Opens Google
2. Searches for weather
3. Extracts temperature, condition, humidity, wind speed

## How It Works

### 1. Planning (planner.py)
- Uses GROQ's Llama 3.3 70B model
- Converts natural language to structured JSON action plan
- Includes examples for common use cases
- Supports multiple action types

### 2. Execution (executer.py)
- Uses Playwright for browser automation
- Executes each action in sequence
- Handles errors gracefully
- Provides detailed logging

### 3. New Action Types

#### `find_and_click_product`
```json
{"action": "find_and_click_product", "product_name": "Air Max 90"}
```
- Searches for product by name using multiple strategies
- Looks for exact and partial text matches
- Finds clickable parent elements (cards, links)
- Works with various e-commerce layouts

#### `find_and_click_button`
```json
{"action": "find_and_click_button", "button_text": "Add to Cart"}
```
- Finds buttons by partial text match
- Checks actual buttons, links, and button-like elements
- Case-insensitive matching
- Handles various button implementations

#### `press_enter`
```json
{"action": "press_enter", "selector": "input[type='text']"}
```
- Simulates pressing Enter key
- Useful for chat apps and search boxes
- Better than clicking submit buttons in many cases

## API Endpoints

### POST /run
Execute a natural language command

**Request:**
```json
{
  "command": "your natural language command here"
}
```

**Response:**
```json
{
  "logs": ["Step 1: ...", "Step 2: ..."],
  "plan": {
    "steps": [...]
  },
  "results": [
    {"label": "Temperature", "value": "75°F"}
  ]
}
```

## Troubleshooting

### Issue: "Could not find product"
**Solution:** 
- Make sure the product name is exact
- Check if the page has loaded completely (increase wait time)
- Inspect the page to see the actual product names

### Issue: "Could not find button"
**Solution:**
- Try using more generic text (e.g., "Add" instead of "Add to Cart")
- The button text matching is partial and case-insensitive
- Some sites use divs or links instead of buttons

### Issue: Chatbot not responding
**Solution:**
- Increase the wait time after pressing Enter
- Some AI chatbots take 5-10 seconds to respond
- Check if the input field selector matches the actual field

### Issue: Browser not visible
**Solution:**
- The browser runs in non-headless mode for debugging
- You should see the browser window open
- It stays open for 30 seconds after completion

## Architecture

```
backend/
├── main.py           # FastAPI server
├── agent/
│   ├── planner.py    # LLM-based action planning
│   └── executer.py   # Playwright-based execution
└── requirements.txt

frontend/
├── src/
│   ├── App.jsx       # Main React component
│   └── components/   # UI components
└── package.json
```

## Environment Variables

- `GROQ_API_KEY` - Your GROQ API key (required)

## Browser Support

- Currently uses Chromium via Playwright
- Runs in non-headless mode for visibility
- Configured to avoid bot detection

## Future Improvements

- [ ] Support for screenshots and visual confirmation
- [ ] Better error recovery and retries
- [ ] Support for file uploads
- [ ] Multi-tab operations
- [ ] Session persistence
- [ ] Custom wait strategies

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT
