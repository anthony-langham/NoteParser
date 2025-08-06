# 🩺 NoteParser - Clinical Decision Support System

## Overview

An intelligent clinical decision support system that leverages the Model Context Protocol (MCP) to provide structured, auditable clinical recommendations. The system ingests unstructured clinical notes and generates evidence-based treatment plans with precise medication dosing calculations.

### 🎯 Core Features

- **Clinical Note Parsing**: Extracts structured patient data from unstructured text
- **Condition Identification**: Matches symptoms and assessments to medical conditions
- **Medication Dosing**: Calculates weight-based doses with safety constraints
- **Treatment Planning**: Generates comprehensive, evidence-based treatment plans
- **Audit Trail**: Provides transparent, reproducible clinical reasoning

### 🏥 Supported Conditions

- **Pediatric Croup** (Laryngotracheobronchitis)
- **Adult Acute Asthma** (Bronchospasm)
- **COPD Exacerbation** (Chronic Obstructive Pulmonary Disease)
- **Community-Acquired Pneumonia** (CAP)
- **Pediatric Gastroenteritis** (Dehydration management)

### 🌐 Live Demo

🔗 **Production System**:

## Architecture

```
┌──────────────-───┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   AWS Gateway   │    │   MCP Server    │
│   (Vite + UI)    │───▶│   (Lambda)      │───▶│   (Python)      │
└──────────────── ─┘    └─────────────────┘    └─────────────────┘
                                                        │
                                              ┌─────────────────┐
                                              │   JSON Data     │
                                              │   (Conditions   │
                                              │   & Guidelines) │
                                              └─────────────────┘
```

### Key Technical Decisions

#### Why MCP over RAG?
- **Deterministic Results**: Medical decisions require reproducible, auditable outputs
- **Structured Validation**: Medical data needs strict input/output validation
- **Performance**: Direct tool calls are faster than semantic search
- **Safety**: Explicit logic is safer than AI interpretation for medical calculations
- **Transparency**: Clear reasoning chain for clinical decisions

#### Why JSON Files over Database?
- **Simplicity**: No database setup/configuration for MVP
- **Version Control**: Clinical data tracked in git with code
- **Performance**: Fast file reads from Lambda filesystem
- **Cost**: No database costs for MVP
- **Development Speed**: Instant data updates without deployment

## Installation

### Prerequisites

- **Node.js 18+** (managed via .nvmrc)
- **Python 3.9+** for MCP server
- **AWS CLI** configured (for deployment)
- **NVM** (Node Version Manager)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/username/heidi.git
cd heidi

# 2. Install Node Version Manager (if not installed)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 3. Use correct Node version
nvm use

# 4. Install dependencies
npm install
pip3 install -r requirements.txt

# 5. Setup environment variables
cp .env.example .env
# Edit .env with your actual values

# 6. Run the system
python3 -m backend.mcp_server.server  # MCP server
npm run dev -- --port 4000            # Frontend (in separate terminal)
```

## Usage

### 🔬 Quick Demo

```bash
# Run the 20-line agent demo
python3 demo_agent.py
```

### 📝 Clinical Note Example

```
Patient: Jack T.
DOB: 12/03/2022
Age: 3 years
Weight: 14.2 kg

Presenting complaint:
Jack presented with a 2-day history of barky cough, hoarse voice, and low-grade fever. 
Symptoms worsened overnight, with increased work of breathing and stridor noted at rest this morning.

Assessment:
Jack presents with classic features of moderate croup (laryngotracheobronchitis), likely viral in origin.
```

### 💊 Expected Output

```json
{
  "condition": "croup",
  "severity": "moderate",
  "medication_dose": {
    "medication": "dexamethasone",
    "final_dose": 2.13,
    "unit": "mg",
    "dosing_rationale": "Calculated at 0.15 mg/kg for 14.2kg patient"
  },
  "treatment_plan": {
    "immediate_actions": ["Administer corticosteroids", "Monitor respiratory status"],
    "monitoring": "Observe for symptom improvement over 2-4 hours",
    "follow_up": "Return if symptoms worsen or persist >5 days"
  }
}
```

## API Documentation

### MCP Tools

#### 1. `parse_clinical_note`
Extracts structured patient data from unstructured clinical text.

```json
{
  "clinical_note": "Patient: John Doe, Age: 5 years, Weight: 18kg..."
}
```

#### 2. `identify_condition`
Matches symptoms and assessment to medical conditions.

```json
{
  "symptoms": ["barky cough", "hoarse voice", "stridor"],
  "assessment": "moderate croup",
  "patient_age": 3
}
```

#### 3. `calculate_medication_dose`
Calculates weight-based medication doses with safety constraints.

```json
{
  "medication": "dexamethasone",
  "condition": "croup",
  "patient_weight": 14.2,
  "severity": "moderate"
}
```

#### 4. `generate_treatment_plan`
Generates comprehensive, evidence-based treatment plans.

```json
{
  "condition": "croup",
  "severity": "moderate",
  "patient_data": {"age": 3, "weight": 14.2, "name": "Jack T."},
  "calculated_doses": [...]
}
```

### Input Validation

All tools include comprehensive input validation:

- **Patient Weight**: 0.5-300 kg (with 0.1 kg precision)
- **Patient Age**: 0-150 years (integer)
- **Severity**: Enum ["mild", "moderate", "severe", "life-threatening"]
- **Clinical Notes**: 10-10,000 characters
- **Medications**: Pattern validation for known drugs

### Error Handling

The system provides structured error responses:

```json
{
  "success": false,
  "error": "Patient weight must be between 0.5 and 300 kg",
  "error_code": "INVALID_PATIENT_DATA",
  "details": {"provided_weight": -5.0},
  "recoverable": true
}
```

## Development

### Project Structure

```
heidi/
├── backend/
│   ├── mcp_server/          # MCP server implementation
│   │   ├── server.py        # Main MCP server
│   │   ├── tools/           # MCP tools (parser, dosing, etc.)
│   │   ├── schemas/         # Pydantic data models
│   │   └── data/            # JSON data files
│   ├── lambda/              # Lambda function handlers
│   └── tests/               # Backend tests
├── frontend/
│   ├── src/
│   │   ├── components/      # React components (shadcn/ui)
│   │   ├── pages/           # Page components
│   │   └── lib/             # Utilities and API calls
│   └── dist/                # Build output
├── infrastructure/
│   ├── sst.config.ts        # SST configuration
│   └── stacks/              # AWS CDK stacks
└── docs/                    # Documentation
```

### Development Commands

#### Backend (MCP Server)
```bash
# Run MCP server locally
python3 -m backend.mcp_server.server

# Run tests
python3 -m pytest backend/tests/

# Run edge case tests
python3 -m pytest backend/tests/test_edge_cases.py

# Deploy to AWS
npx sst deploy --stage prod
```

#### Frontend (React)
```bash
# Development server (MANDATORY: port 4000)
lsof -ti:4000 && kill -9 $(lsof -ti:4000) || true
npm run dev -- --port 4000

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

### Testing

The system includes comprehensive test coverage:

- **Unit Tests**: All MCP tools
- **Integration Tests**: Complete clinical workflows
- **Edge Case Tests**: Boundary conditions and error scenarios
- **Performance Tests**: Load and stress testing

```bash
# Run all tests
python3 -m pytest backend/tests/

# Run specific test categories
python3 -m pytest backend/tests/test_edge_cases.py -v
python3 -m pytest backend/tests/test_integration.py -v
```

## Deployment

### AWS Infrastructure

The system deploys to AWS using SST (Serverless Stack):

- **API Gateway**: RESTful endpoints with authentication
- **Lambda Functions**: Serverless compute for MCP server
- **CloudFront CDN**: Global content delivery
- **Route 53**: DNS management
- **CloudWatch**: Logging and monitoring

### Environment Variables

#### Backend (.env)
```bash
# Data Configuration
DATA_PATH=/opt/data/
CONDITIONS_FILE=conditions.json
GUIDELINES_FILE=guidelines.json

# API Configuration
API_KEY=your-secure-api-key-here
CORS_ORIGINS=https://heidimcp.uk,http://localhost:3000

# Logging
LOG_LEVEL=INFO
ENVIRONMENT=production
```

#### Frontend (.env)
```bash
# API Configuration
VITE_API_BASE_URL=https://api.heidimcp.uk
VITE_API_KEY=your-secure-api-key-here
VITE_APP_NAME=Heidi Clinical Decision Support
```

### Security Considerations

- **No PHI Storage**: No Personal Health Information stored in logs
- **HIPAA Compliance**: Data handling follows HIPAA guidelines
- **Encryption**: At rest (Lambda) and in transit (HTTPS)
- **Input Validation**: Comprehensive sanitization
- **Rate Limiting**: API endpoint protection
- **Authentication**: API key-based access control

## Clinical Safety

### ⚠️ Important Safety Information

1. **Not for Clinical Use**: This system is not validated for clinical decision making
2. **Educational Only**: Intended for demonstration and educational purposes
3. **Professional Oversight**: All clinical decisions require qualified healthcare professionals
4. **Liability**: Users assume all responsibility for any clinical decisions
5. **Validation Required**: Any clinical use requires proper validation and regulatory approval

### Medical Disclaimers

- **Not FDA Approved**: This software is not approved by the FDA or any regulatory body
- **Not Diagnostic**: This system does not diagnose medical conditions
- **Not Prescriptive**: This system does not prescribe medications
- **Professional Judgment**: Healthcare professionals must use their clinical judgment
- **Updated Guidelines**: Always refer to current medical guidelines and protocols

## Contributing

We welcome contributions from healthcare professionals and developers:

### For Healthcare Professionals
- Review clinical algorithms and dosing calculations
- Suggest additional conditions and treatment protocols
- Validate against current medical guidelines
- Provide clinical feedback and edge cases

### For Developers
- Improve system architecture and performance
- Add new MCP tools and integrations
- Enhance error handling and validation
- Write comprehensive tests

### Contribution Guidelines
1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

## License

MIT License - See [LICENSE](LICENSE) file for details.

### Medical Liability Disclaimer

This software is provided "as is" without warranty of any kind. The authors and contributors disclaim all liability for any medical decisions made using this system. Users must obtain proper medical advice from qualified healthcare professionals.

## Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: Report bugs on [GitHub Issues](https://github.com/username/heidi/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/username/heidi/discussions)
- **Clinical Questions**: Contact qualified healthcare professionals

## Acknowledgments

- **Clinical Guidelines**: Based on NICE, BTS, AAP, and WHO guidelines
- **MCP Framework**: Built on Anthropic's Model Context Protocol
- **UI Components**: Uses shadcn/ui design system
- **Infrastructure**: Deployed on AWS with SST framework

---

**⚕️ Remember: This is a prototype system. All clinical decisions must be made by qualified healthcare professionals using established medical protocols.**
