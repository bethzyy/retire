# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Beijing Retirement Pension Calculation System** (北京退休金测算系统) - a Flask web application that uses AI (GLM-4.7 via ZhipuAI) to calculate Beijing pension benefits and help unemployed users decide whether to pay pension insurance during unemployment, comparing three payment tiers (60%, 80%, 100%) to find the most cost-effective option.

## Core Design Philosophy: Three-Step Workflow

The system follows a strict **three-step process** that must be maintained in the AI system prompt:

1. **Step 1️⃣: Policy Interpretation** - AI analyzes Beijing social security policies to determine what data is genuinely needed for calculation (and what is NOT needed)
2. **Step 2️⃣: Data Collection** - AI asks users ONLY for required data, using ABCD multiple-choice questions when possible
3. **Step 3️⃣: Calculation & Analysis** - User confirms (replies "A"), AI immediately performs calculation without repeated confirmation

**Critical Rule**: AI should only ask for data required by official formulas. For example, "life expectancy" does NOT affect pension calculation itself, so it should NOT be asked. The system calculates "break-even time = total payment ÷ monthly pension increase" instead, showing how many years after retirement to break even.

## Architecture

### Core Components

1. **Flask Web Application** (`app.py`)
   - Main web server with session management and DATA_UPDATE extraction
   - Lines 281-318: Brace-counting algorithm to parse JSON from AI responses
   - Lines 452-487: User data update API for field-by-field editing
   - Integrates AI client, user data manager, and logger

2. **AI Client** (`ai_client.py`)
   - ZhipuAI GLM-4.7 wrapper using Anthropic-compatible API
   - 120-second timeout (line 86) to prevent Chrome browser hanging
   - Supports image uploads for insurance document recognition

3. **User Data Manager** (`user_manager.py`)
   - Name-based user persistence: `user_data/{sanitized_name}.json`
   - Automatic data merging with `merge_user_data()` method
   - Detects missing fields to guide AI questioning flow

4. **Logger** (`logger.py`)
   - JSON logs in `logs/` directory with full request/response metadata
   - Tracks model, IP, user agent, user name for audit trails

5. **Frontend** (`templates/index.html`)
   - Single-page chat app with marked.js for Markdown
   - Lines 854-1027: Three JavaScript functions for user editing feature
   - 120-second fetchWithTimeout to match backend timeout
   - Image upload via base64 encoding

### DATA_UPDATE Protocol (Critical)

**Backend automatically extracts and saves user data from AI responses**

Format required in AI responses:
```
【已记录信息】
✓ 字段中文名：值

DATA_UPDATE: {
  "field_name": "value"
}
```

**Extraction Algorithm** (app.py:284-300):
- Find `DATA_UPDATE:` marker
- Locate opening `{` brace
- Count nested braces to find matching closing `}`
- Parse JSON and merge into user data file

**Field Names** (must match DATA_UPDATE schema in system_prompt.txt):
- `gender`, `birth_year`, `birth_month`, `hukou_type`, `employment_status`
- `first_work_year`, `total_work_years`, `deemed_payment_years`, `actual_payment_years`
- `account_balance`, `has_outside_province`, `has_professional_title`, `retirement_age`

### System Prompt Structure (`prompts/system_prompt.txt`)

**Lines 1-32: Three-Step Workflow** (MOST IMPORTANT)
- Defines the core methodology
- Specifies "don't ask unrelated data, don't miss required data"
- Emphasizes immediate calculation after user confirmation

**Lines 86-91: Real-Time Data Requirement**
- AI must use WebSearch to fetch current social security data
- NEVER use hardcoded data in system prompt
- Always cite data sources and publication dates

**Lines 100-194: 12-Question Framework** (Flexible, not rigid)
- Questions can be skipped based on context
- Example: Deemed years = 0 for post-1992 workers
- Focus on information completeness, not question count

**Lines 538-606: Unemployment Payment Analysis Framework**
- Three-tier comparison (60%, 80%, 100%)
- Break-even calculation WITHOUT asking life expectancy
- Shows "X years after retirement to break even"

**Lines 608-650: DATA_UPDATE Format Enforcement**
- Mandatory JSON format for data saving
- All available field names listed
- Examples of correct format

## Essential Commands

### Running the Application

```bash
# Set API key first (Windows CMD)
set ZHIPU_API_KEY=your_api_key_here

# Or Windows PowerShell
$env:ZHIPU_API_KEY='your_api_key_here'

# Start Flask server (development)
python app.py
# Runs on http://localhost:5000

# Clean user data and restart (useful after system_prompt changes)
rm -f user_data/*.json && python app.py

# Kill all Python processes and restart (Windows)
taskkill /F /IM python.exe 2>nul ; python app.py
```

### Testing

```bash
# Run complete test suite
python tests/test_complete.py

# Test user editing feature
python tests/test_user_edit.py

# Test Chrome timeout fix (120-second timeout)
python tests/test_chrome_timeout.py

# Test ABCD multiple-choice questions
python tests/test_abc_questions.py

# Test calculation trigger mechanism
python tests/test_calculation_trigger.py
```

## Important Implementation Details

### Name-Based User Identification

User's name is the **primary key** for all data:
- Set via `/api/set-name` endpoint on login
- Stored in Flask session
- Determines which `user_data/{sanitized_name}.json` file to load/save
- Allows conversation history and user data to persist across browser sessions

### Smart Question Skipping (Not Rigid 12 Questions)

AI intelligently skips irrelevant questions based on context:
- **Deemed contribution years**: Auto-set to 0 for users starting work after 1992-10
- **Outside province contributions**: Only asked if user has actual contribution years
- Focus on **information completeness**, not question count
- System prompt says "共计12个问题" but this is flexible, not a requirement

### Real-Time Data Requirement

**CRITICAL**: AI is instructed (via system_prompt.txt lines 86-91) to:
- Use WebSearch to fetch latest social security data (e.g., "2026年北京社保缴费基数")
- NEVER use hardcoded data from system prompt
- Fall back to previous year if current year data unavailable
- Always cite data sources and publication dates

**Note**: The AI model in this codebase does NOT actually have WebSearch capability. The prompt asks for it, but the AI will simulate searching or say "正在搜索" without actually calling an external search API.

### Social Security Transfer Logic

When user has contributions from other provinces:
- AI asks about outside province experience (question #10)
- DATA_UPDATE includes: `has_outside_province`, `outside_years`, `outside_location`, `outside_transferred`
- Pension calculation merges: `outside_years + Beijing_actual_years = total_actual_years`
- Personal account balances also merged: `outside_account + Beijing_account = total_account`

### Frontend Timeout Configuration (Chrome Bug Fix)

**Problem**: Chrome browser has 60-second timeout for fetch requests by default. AI calculations often take >60 seconds, causing Chrome to hang.

**Solution**: Implemented 120-second timeout on both frontend and backend:
- **Frontend** (index.html): `fetchWithTimeout()` function with 120-second AbortController
- **Backend** (ai_client.py line 86): `timeout=120` parameter in requests.post()

**All fetch calls must use fetchWithTimeout**, not the native fetch().

### User Editing Feature

Frontend provides field-by-field user data editing (lines 854-1027 in index.html):
- `editUserInfo()`: Switches sidebar to editable form mode
- `saveUserInfo()`: Sends partial updates to `/api/update-user-data`
- Backend (app.py lines 452-487): Merges partial updates into existing user data
- Only updates non-empty fields, preserves existing data

### Frontend Null Safety (Lesson from Bug Fix)

All DOM element accesses must check for null:
```javascript
// WRONG (causes null reference errors)
document.getElementById('loading').classList.add('active');

// CORRECT
const loadingElement = document.getElementById('loading');
if (loadingElement) {
    loadingElement.classList.add('active');
}
```

## Data Flow Diagram

```
User enters name
  ↓
POST /api/set-name → Flask session
  ↓
User sends message/images
  ↓
POST /api/chat
  ↓
Load user_data/{name}.json (if exists)
  ↓
Inject historical data into system prompt
  ↓
Call AI with conversation history
  ↓
AI responds with DATA_UPDATE blocks
  ↓
Extract DATA_UPDATE (brace-counting algorithm)
  ↓
Merge with existing user data
  ↓
Save to user_data/{name}.json
  ↓
Return AI reply + updated user data
  ↓
Frontend displays message and updates sidebar
```

## File Structure

```
retire/
├── app.py                  # Main Flask application (539 lines)
├── ai_client.py            # ZhipuAI GLM client wrapper
├── user_manager.py         # User data persistence (JSON files)
├── logger.py               # AI call logging (JSON logs)
├── prompts/
│   ├── system_prompt.txt   # AI system prompt (~700 lines)
│   │   ├── Lines 1-32: Three-step workflow
│   │   ├── Lines 86-91: Real-time data requirement
│   │   ├── Lines 100-194: 12-question framework
│   │   ├── Lines 538-606: Unemployment payment analysis
│   │   └── Lines 608-650: DATA_UPDATE format
│   └── policy_context.txt  # Beijing pension policy reference
├── templates/
│   └── index.html          # Single-page chat interface
│       ├── Lines 1-853: Chat UI and message handling
│       ├── Lines 854-1027: User editing functions
│       └── Lines 1028+: Utility functions
├── tests/
│   ├── test_complete.py    # Full test suite
│   ├── test_user_edit.py   # User editing feature
│   ├── test_chrome_timeout.py # 120-second timeout test
│   ├── test_abc_questions.py # Multiple-choice format
│   └── test_calculation_trigger.py # Immediate calc after "A"
├── user_data/              # User JSON files (auto-created, gitignored)
└── logs/                   # AI call logs (auto-created, gitignored)
```

## Environment Setup

Required environment variable:
- `ZHIPU_API_KEY`: ZhipuAI API key in format `id.secret`

Python dependencies:
- Flask (web framework)
- requests (HTTP client)
- No requirements.txt file (minimal dependencies)

## Known Issues and Limitations

1. **WebSearch Not Available**: System prompt instructs AI to use WebSearch, but the AI model doesn't actually have this capability. AI will say "正在搜索" but cannot execute real searches.

2. **Model Selection**: Currently uses GLM-4.7 (ai_client.py line 35). Can switch to GLM-4.6 if 4.7 has stability issues.

3. **Prompt Length**: System prompt is ~700 lines. GLM-4.7 may behave unpredictably if prompt is too long. Current length optimized for stability.

4. **Session Storage**: User data persists in Flask session, which is lost if server restarts. Critical data is saved to JSON files, but conversation history is session-only.

## Testing Strategy

- **Automated Integration Tests**: All tests in `tests/` use `requests` library to simulate HTTP interactions without browser
- **User Data Persistence**: `test_user_edit.py` verifies field-by-field editing and data merging
- **Timeout Handling**: `test_chrome_timeout.py` validates 120-second timeout prevents browser hanging
- **Calculation Trigger**: `test_calculation_trigger.py` ensures AI calculates immediately after user confirms (replies "A")
- **No Unit Tests**: Project uses integration tests only, no unit test framework

## Common Troubleshooting

1. **AI repeatedly asks same question**: Check if user's historical data in `user_data/{name}.json` contains conflicting information. Delete JSON file and restart: `rm -f user_data/*.json && python app.py`

2. **AI doesn't calculate after "A"**: Check system_prompt.txt lines 410-438 for calculation trigger mechanism. Ensure error example (lines 414-418) doesn't confuse AI.

3. **Chrome browser hangs**: Verify 120-second timeout is configured in both ai_client.py (line 86) and index.html (fetchWithTimeout function).

4. **AI asks about "life expectancy"**: This question was removed from the prompt. If AI still asks, check for legacy references in system_prompt.txt and delete user data files.
