# Claude Code Project Configuration

This file contains configuration and context for Claude Code to help with development tasks.

## Project Information

- **Project Name**: heidi
- **License**: MIT
- **Repository**: Git repository (main branch)
- **Project Type**: Intelligent Clinical Decision Support System

## Project Overview

**Core Concept**: Leverage clinical data and context to assist clinician's needs in real time, by helping guide treatment decisions using up-to-date clinical guidelines & tool use.

**Key Features**:
- Ingests visit notes or transcripts as input
- Queries & references local guidelines using RAG/agentic AI
- Calculates weight-based medication doses
- Returns detailed clinical decision support plans

**Example Use Case**: Pediatric croup management - suggesting appropriate treatment approach and calculating oral steroid dose (prednisone/dexamethasone) based on history, examination, and guideline references.

## Deliverables

1. **Working prototype (MVP)**
   - Accepts unstructured clinical text
   - Queries relevant local guidelines
   - Calculates weight & evidence-based medication doses
   - Returns detailed management plans grounded in clinical guidelines

2. **Architecture diagram** (one-page PNG/PDF)
   - Major components and data flow
   - Service/API/framework explanations with rationales

3. **Walk-through video** (5-10 minutes)
   - Demonstrate prototype on test cases
   - Explain design decisions and limitations

## Sample Clinical Note

```
Patient: Jack T.
DOB: 12/03/2022
Age: 3 years
Weight: 14.2 kg

Presenting complaint:
Jack presented with a 2-day history of barky cough, hoarse voice, and low-grade fever. Symptoms worsened overnight, with increased work of breathing and stridor noted at rest this morning.

Assessment:
Jack presents with classic features of moderate croup (laryngotracheobronchitis), likely viral in origin.

Plan:
- Administer corticosteroids
- Plan as per local guidelines for croup
```

## Project Structure

This appears to be a new project with minimal initial structure:
- `README.md` - Project documentation
- `LICENSE` - MIT license file
- `CLAUDE.md` - This configuration file

## Development Commands

<!-- Add common development commands here as they become available -->
<!-- Examples:
- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint`
- Dev server: `npm run dev`
-->

## Notes

- This is a new project repository for clinical decision support
- Focus on rapid prototyping, not production-ready scalability
- Consider using Python with LLM frameworks for implementation
- Need to implement RAG for guideline retrieval
- Need medication dose calculation logic