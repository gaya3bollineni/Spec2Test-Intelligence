# Spec2Test Intelligence

**Spec2Test Intelligence** is an open-source requirements intelligence platform that helps QA engineers transform software requirements into structured, traceable, and testable artifacts.

Instead of simply generating test cases, Spec2Test analyzes requirement quality, identifies ambiguities, measures completeness, generates positive, negative, and edge test scenarios, and builds a Requirement Traceability Matrix (RTM) to improve test coverage and requirement validation.

---

## Why Spec2Test?

Writing high-quality test cases starts with high-quality requirements.

In many projects, testers spend significant time:
- Reviewing unclear acceptance criteria
- Identifying missing information
- Creating repetitive test scenarios
- Maintaining requirement traceability
- Measuring test coverage

Spec2Test Intelligence automates these activities while keeping the generated artifacts structured, transparent, and explainable.

---

## Current Features

### Requirement Intelligence

Evaluate requirement quality before writing test cases.

- Requirement Quality Score
- Completeness Analysis
- Ambiguity Detection
- Improvement Recommendations

---

### Test Case Generation

Automatically generate structured QA test cases including:

- Positive Scenarios
- Negative Scenarios
- Edge Cases
- Preconditions
- Test Steps
- Expected Results

---

### Requirement Traceability Matrix (RTM)

Automatically map requirements to generated test cases.

Includes:

- Requirement ID
- Acceptance Criteria
- Positive Scenario Count
- Negative Scenario Count
- Edge Scenario Count
- Coverage Percentage

---

### Export Options

Generate downloadable artifacts including:

- Excel
- JSON

---

### Streamlit Dashboard

Interactive web interface with:

- Requirement Intelligence Dashboard
- Test Summary
- Traceability Matrix
- Generated Test Cases

---

# Project Workflow

```
Acceptance Criteria
        │
        ▼
Requirement Intelligence
        │
        ▼
Completeness Analysis
        │
        ▼
Test Case Generation
        │
        ▼
Requirement Traceability Matrix
        │
        ▼
Export Results
```

---

# Project Structure

```
Spec2Test-Intelligence/
│
├── app/
│   ├── streamlit_app.py
│   ├── config.py
│   └── ui/
│
├── src/
│   ├── ingestion/
│   ├── parsing/
│   ├── requirements_analysis/
│   ├── scenario_expander/
│   ├── oracle_builder/
│   └── traceability/
│
└── requirements.txt
```

---

# Installation

Clone the repository.

```bash
git clone https://github.com/<your-username>/Spec2Test-Intelligence.git

cd Spec2Test-Intelligence
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Run the application.

```bash
PYTHONPATH=. streamlit run app/streamlit_app.py
```

---

# Example Input

```
User should be able to log in with valid credentials.
The system shall display an error message for invalid credentials.
The account shall be locked after five unsuccessful login attempts.
```

---

# Example Output

✔ Requirement Quality Analysis

✔ Completeness Analysis

✔ Ambiguity Detection

✔ Positive Test Cases

✔ Negative Test Cases

✔ Edge Test Cases

✔ Requirement Traceability Matrix

✔ Excel Export

✔ JSON Export

---

# Roadmap

### Completed

- Requirement Parsing
- Requirement Intelligence
- Completeness Analysis
- Ambiguity Detection
- Structured Test Case Generation
- Requirement Traceability Matrix
- Excel Export
- JSON Export
- Streamlit UI

### Planned

- Excel Requirement Upload
- AI-assisted Requirement Improvement
- Jira Integration
- qTest Integration
- Xray Integration
- Risk-based Test Prioritization
- Data Validation Test Generation
- API Test Case Generation
- Requirement Version Comparison

---

# Tech Stack

- Python
- Streamlit
- Pandas
- OpenPyXL
- Pydantic

---

# Vision

The long-term vision of Spec2Test Intelligence is to evolve from a test case generator into a comprehensive Requirements Intelligence Platform that helps QA teams improve requirement quality, automate test design, and maintain end-to-end traceability throughout the software development lifecycle.

---

# Contributing

Contributions, suggestions, and feature requests are welcome.

Feel free to open an issue or submit a pull request.