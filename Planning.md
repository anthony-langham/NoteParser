# Heidi Clinical Decision Support MVP - Architecture Planning

## Executive Summary

This document outlines the technical architecture and implementation strategy for building a clinical decision support MVP that ingests clinical notes, queries guidelines, calculates medication doses, and returns evidence-based treatment recommendations.

## Problem Analysis

**Core Requirements:**

1. Ingest unstructured clinical text (visit notes/transcripts)
2. Query and reference local clinical guidelines
3. Calculate weight-based medication doses
4. Return detailed clinical decision support plans

**Key Challenges:**

- Balancing structured data access with contextual understanding
- Ensuring medical accuracy and safety
- Rapid prototyping while maintaining extensibility
- Handling complex medical relationships and contraindications

## Data Storage Decision Analysis

### Option 1: Database (SQLite/PostgreSQL)

**Pros:**

- Structured relationships (conditions ↔ medications ↔ doses)
- Fast queries, indexing, data integrity
- Can handle complex metadata (age ranges, contraindications, severity levels)
- ACID compliance for medical data safety
- Scalable for production use

**Cons:**

- More complex setup for prototyping
- Less human-readable for quick edits
- Requires database management skills
- Overkill for MVP scope

### Option 2: Excel/CSV

**Pros:**

- Easy to edit and view
- Non-technical users can modify
- Simple tabular format
- Version controllable
- Familiar to medical professionals

**Cons:**

- Limited query capabilities
- No data validation or relationships
- Becomes unwieldy with complex medical data
- Hard to handle nested information (multiple dosing regimens)
- No support for complex medical logic

### Option 3: Markdown

**Pros:**

- Human-readable and editable
- Version controllable
- Good for guideline documentation
- Can include rich formatting and explanations
- Easy to maintain and update

**Cons:**

- Requires parsing for structured queries
- Not ideal for tabular medical data
- Can become messy with lots of structured data
- Limited structure enforcement

### **Decision: Hybrid JSON + Markdown Approach**

**Rationale:**

- **JSON/YAML** for structured medical data (conditions, medications, doses, contraindications)
- **Markdown** for clinical guidelines and treatment protocols
- Balances structure with readability
- Enables both computational precision and contextual understanding

## MCP vs RAG Analysis

### MCP (Model Context Protocol)

**Best for:**

- Structured medical data queries
- Dose calculations and medical computations
- Real-time data access and validation
- Deterministic medical logic

**Use Cases:**

- Medication dose calculations
- Contraindication checking
- Structured data retrieval
- Medical parameter validation

### RAG (Retrieval-Augmented Generation)

**Best for:**

- Unstructured guideline interpretation
- Contextual clinical reasoning
- Natural language understanding of medical text
- Flexible knowledge retrieval

**Use Cases:**

- Clinical guideline interpretation
- Treatment protocol recommendations
- Differential diagnosis suggestions
- Clinical note analysis

### **Decision: Hybrid MCP + RAG Architecture**

**Rationale:**

- MCP for precise, structured medical computations
- RAG for contextual clinical knowledge and guidelines
- Leverages strengths of both approaches
- Ensures accuracy while maintaining flexibility

## Proposed MVP Architecture

### 1. Data Layer

**Structured Medical Data (JSON)**

```json
{
  "conditions": {
    "croup": {
      "name": "Croup (Laryngotracheobronchitis)",
      "severity_levels": ["mild", "moderate", "severe"],
      "medications": ["dexamethasone", "prednisolone"],
      "diagnostic_criteria": [...],
      "contraindications": [...]
    }
  },
  "medications": {
    "dexamethasone": {
      "name": "Dexamethasone",
      "dosing": {
        "croup": {
          "dose": 0.15,
          "unit": "mg/kg",
          "route": "oral",
          "frequency": "single_dose",
          "max_dose": 10
        }
      }
    }
  }
}
```

**Clinical Guidelines (Markdown)**

- Separate files for each condition
- Treatment protocols and clinical reasoning
- Evidence-based recommendations
- Contraindications and special considerations

### 2. Processing Layer

**MCP Tools:**

- `calculate_dose()` - Weight-based medication calculations
- `check_contraindications()` - Safety validation
- `get_condition_info()` - Structured data retrieval
- `validate_parameters()` - Input validation

**RAG System:**

- Vector database for guideline embeddings
- Semantic search for relevant protocols
- Context-aware recommendation generation
- Clinical reasoning extraction

### 3. Application Layer

**Core Components:**

1. **Clinical Note Parser** - Extract key information (age, weight, symptoms)
2. **Condition Identifier** - Match symptoms to conditions
3. **Guideline Retriever** - RAG-based protocol lookup
4. **Dose Calculator** - MCP-based medication calculations
5. **Decision Engine** - Combine structured data with guidelines
6. **Output Formatter** - Generate clinical decision support plan

### 4. Technology Stack

**Core Framework:**

- **Python** - Primary language for medical applications
- **FastAPI** - Web framework for API endpoints
- **Pydantic** - Data validation and serialization

**RAG Implementation:**

- **LangChain** - RAG framework and LLM orchestration
- **Chroma** - Vector database for embeddings
- **OpenAI/Anthropic** - LLM API for text processing

**MCP Implementation:**

- **Custom MCP server** - Medical calculation tools
- **JSON Schema** - Data validation
- **PyTest** - Testing framework for medical logic

## Implementation Strategy

### Phase 1: Foundation (Week 1)

1. Set up project structure and dependencies
2. Create structured medical data (JSON) for croup
3. Implement basic MCP tools for dose calculation
4. Create initial clinical guidelines (Markdown)

### Phase 2: Core Processing (Week 2)

1. Implement clinical note parser
2. Build RAG system for guideline retrieval
3. Create decision engine to combine MCP + RAG
4. Develop output formatter

### Phase 3: Integration & Testing (Week 3)

1. Build FastAPI web interface
2. Implement end-to-end workflow
3. Test with sample clinical notes
4. Create demonstration cases

### Phase 4: Documentation & Demo (Week 4)

1. Create architecture diagram
2. Record demonstration video
3. Write setup instructions
4. Performance optimization

## Data Schema Design

### Clinical Conditions

- Condition name and aliases
- Severity classifications
- Diagnostic criteria
- Associated medications
- Age/weight restrictions
- Contraindications

### Medications

- Generic and brand names
- Dosing formulas by condition
- Route of administration
- Frequency and duration
- Maximum doses
- Drug interactions

### Guidelines

- Treatment protocols by condition
- Evidence levels and references
- Clinical decision trees
- Special populations considerations

## Safety Considerations

1. **Data Validation** - Strict input validation for all medical parameters
2. **Dose Limits** - Maximum dose checking to prevent overdose
3. **Contraindications** - Automated checking for drug allergies and interactions
4. **Audit Trail** - Logging of all calculations and decisions
5. **Disclaimer** - Clear medical disclaimer for prototype use

## Testing Strategy

1. **Unit Tests** - Individual component testing
2. **Integration Tests** - End-to-end workflow testing
3. **Medical Validation** - Clinical accuracy verification
4. **Edge Cases** - Boundary condition testing
5. **Performance Tests** - Response time validation

## Success Metrics

1. **Accuracy** - Correct dose calculations and recommendations
2. **Completeness** - Comprehensive clinical decision support
3. **Performance** - Sub-second response times
4. **Usability** - Intuitive interface and clear outputs
5. **Extensibility** - Easy addition of new conditions/medications

## Future Enhancements

1. **Multi-condition Support** - Handle complex cases
2. **Drug Interactions** - Comprehensive interaction checking
3. **Clinical Validation** - Medical professional review workflow
4. **Integration APIs** - EHR system integration
5. **Machine Learning** - Predictive analytics for outcomes

## Conclusion

This hybrid MCP + RAG architecture provides the optimal balance of structured medical computation and contextual clinical reasoning. The JSON + Markdown data approach enables rapid prototyping while maintaining medical accuracy and extensibility for future development.
