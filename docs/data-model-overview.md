# Survey Manager: Key Data at a Glance (Teaching Edition)

A survey holds its questions. Responses belong to one survey and hold answers
keyed by question id. See [data-model.md](data-model.md) for every field and how
each is stored.

```mermaid
erDiagram
    SURVEY ||--|{ QUESTION : "contains"
    SURVEY ||--o{ RESPONSE : "has submitted"
    RESPONSE }o..o{ QUESTION : "answers"

    SURVEY {
        string id PK
        string title "the survey's name"
    }
    QUESTION {
        string id PK
        string text
        string type "text, yesno or checkbox"
    }
    RESPONSE {
        string id PK "internal, e.g. resp_1a2b3c4d"
        string survey_id FK
        string respondent_id "5-digit ID the taker enters"
        dict answers "question id to answer"
    }
```

**How to read it:** `||--|{` means one survey contains one or more questions.
`||--o{` means one survey has zero or more responses. The dotted line means
responses point to questions by putting each question's id in their `answers`
keys; a question the respondent left blank has no entry.
