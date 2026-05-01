# FAQ Maker AI - System Workflow

## Overview
The FAQ Maker AI is an intelligent system that automatically analyzes chatbot conversations to suggest new FAQ entries, helping the knowledge base grow organically based on actual user questions.

---

## Workflow Diagram

```
Student asks question
        ↓
Chatbot logs to ai_chat_logs
        ↓
[If unanswered/failed]
        ↓
Admin clicks "Run AI Analysis"
        ↓
AI groups similar queries → Creates suggestions
        ↓
Admin reviews in "AI Suggestions" tab
        ↓
┌─────────────────┴─────────────────┐
│                                   │
Approve                        Reject
│                                   │
↓                                   ↓
Creates FAQ Entry            Logs reason for
                              learning
```

---

## Step-by-Step Process

### 1. Student Interaction
- Student asks a question via the chatbot
- Query is saved to `ai_chat_logs` table with:
  - `user_query`: The question asked
  - `ai_response`: Bot's response (if any)
  - `is_successful`: Whether answer was found
  - `faq_entry_id`: Matched FAQ (null if no match)
  - `mode`: 'online' (AI) or 'offline' (rule-based)

### 2. Detection of Unanswered Queries
System identifies failed interactions:
- Queries where `is_successful = FALSE`
- Queries where `faq_entry_id IS NULL` (no exact match)
- These are candidates for FAQ creation

### 3. AI Analysis (Admin-Triggered)
Admin configures analysis parameters:
| Parameter | Default | Description |
|-----------|---------|-------------|
| Analysis Period | 7 days | How far back to look |
| Min Query Count | 2 | Minimum similar queries needed |
| Similarity Threshold | 0.7 | How similar queries must be (70%) |

**AI Algorithm:**
1. Collects all unanswered queries from period
2. Groups similar queries using **Jaccard Similarity**
3. Extracts common keywords from each group
4. Auto-categorizes based on keywords:
   - `location`: library, gym, office, where
   - `schedule`: time, when, hour, open
   - `academic`: enrollment, grade, course
   - `services`: payment, ID, help
   - `general`: default category
5. Generates template answer with admin placeholder
6. Calculates confidence score based on query count

### 4. Suggestion Creation
For each valid group, creates `FAQSuggestion` entry:
```javascript
{
  suggested_question: "Most common query from group",
  suggested_answer: "Template with [Admin: ...] placeholder",
  category: "auto-detected",
  keywords: "extracted, keywords, from, queries",
  source_queries: ["query1", "query2", ...],
  query_count: 5,
  confidence_score: 0.85,
  status: "pending"
}
```

### 5. Admin Review Process
**AI Suggestions Tab** provides:
- List of pending suggestions with confidence scores
- Expandable cards showing:
  - Sample queries that triggered suggestion
  - Suggested question and answer
  - Keywords and category
  - Edit capability before approval

**Actions:**
- **Approve**: Converts to live FAQ entry
- **Reject**: Logs reason for future improvement
- **Edit**: Modify question/answer before approval

### 6. Knowledge Base Growth
Approved suggestions become:
- Active FAQ entries in `faq_entries` table
- Immediately available to chatbot
- Tracked for usage analytics

---

## Database Tables

### ai_chat_logs
Stores all chatbot interactions:
```sql
CREATE TABLE ai_chat_logs (
    id SERIAL PRIMARY KEY,
    user_query TEXT NOT NULL,
    ai_response TEXT NULL,
    mode VARCHAR(10) NOT NULL,
    is_successful BOOLEAN DEFAULT TRUE,
    faq_entry_id INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### faq_suggestions
Stores AI-generated suggestions:
```sql
CREATE TABLE faq_suggestions (
    id SERIAL PRIMARY KEY,
    suggested_question TEXT NOT NULL,
    suggested_answer TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    keywords TEXT,
    source_queries JSONB,
    query_count INTEGER DEFAULT 1,
    confidence_score FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    reviewed_by_id INTEGER NULL,
    reviewed_at TIMESTAMP NULL,
    review_note TEXT NULL,
    faq_entry_id INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### faq_entries
Live FAQ knowledge base:
```sql
CREATE TABLE faq_entries (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    keywords TEXT,
    usage_count INTEGER DEFAULT 0,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chatbot/faq-maker/analyze/` | POST | Run AI analysis on chat logs |
| `/api/chatbot/faq-suggestions/` | GET | List suggestions (filter by status) |
| `/api/chatbot/faq-suggestions/{id}/approve/` | POST | Approve or reject suggestion |
| `/api/chatbot/analytics/` | GET | Chatbot performance metrics |
| `/api/chatbot/chat-logs/` | GET | View conversation logs |

---

## Frontend Components

### AdminFAQ.vue
Three-tab interface:
1. **Manual FAQs**: Traditional CRUD for FAQ entries
2. **AI Suggestions**: Review and approve AI-generated suggestions
3. **Analytics**: Performance dashboard with:
   - Total queries / success rate
   - Mode breakdown (online/offline)
   - Top unanswered queries
   - Most used FAQs

---

## Benefits

1. **Self-Improving**: System gets smarter as students ask questions
2. **Data-Driven**: FAQs based on actual user needs, not guesses
3. **Efficient**: Admins review pre-drafted suggestions, not blank pages
4. **Quality Control**: Human approval ensures accurate information
5. **Continuous Learning**: Rejected suggestions inform improvements

---

## Best Practices

1. **Run analysis weekly** to capture new question patterns
2. **Set min_query_count=2** to avoid one-off questions
3. **Review pending suggestions** before they accumulate
4. **Edit suggestions** to add specific campus details
5. **Monitor analytics** to track chatbot improvement over time
