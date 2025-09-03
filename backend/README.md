# Heidi Backend - Local Development Setup

This directory contains the MCP (Model Context Protocol) server implementation for Heidi Clinical Decision Support System.

## 🏥 What is Heidi?

Heidi is an intelligent clinical decision support system that:
- Parses clinical notes to extract patient data
- Identifies medical conditions from symptoms and assessment
- Calculates weight-based medication doses
- Generates comprehensive treatment plans following clinical guidelines

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ (currently using Python 3.13)
- pip3 package manager

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Run Local Development Server
```bash
python3 run_local_server.py
```

This interactive script will:
- ✅ Check your environment setup
- 🧪 Run tests to verify functionality  
- 🚀 Start the MCP server

### 3. Alternative: Run Individual Components

**Run Tests Only:**
```bash
# Full test suite
python3 -m pytest tests/ -v

# Parser tests only
python3 -m pytest tests/test_parser.py -v

# End-to-end workflow test
python3 test_runner.py
```

**Run MCP Server:**
```bash
python3 -m mcp_server.server
```

## 📁 Project Structure

```
backend/
├── mcp_server/           # Main MCP server implementation
│   ├── data/            # Clinical data files
│   │   ├── conditions.json    # Medical conditions with medications
│   │   └── guidelines.json    # Clinical guidelines
│   ├── schemas/         # Pydantic data models
│   ├── tools/           # MCP tools (parser, treatment planner)
│   ├── utils/           # Error handling and utilities
│   └── server.py        # Main MCP server
├── lambda/              # AWS Lambda handlers (for deployment)
├── tests/               # Comprehensive test suite
├── .env                 # Environment configuration
├── requirements.txt     # Python dependencies
└── run_local_server.py  # Development server runner
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
API_KEY=<secure-32-char-hex-key>    # Generated automatically
CORS_ORIGINS=https://noteparser.uk,http://localhost:3000
AWS_REGION=us-east-1                # For production deployment
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Data Files
- `conditions.json`: Medical conditions with embedded medications and dosing
- `guidelines.json`: Clinical decision-making guidelines and protocols

Both files contain real clinical data for the MVP implementation.

## 🧪 Testing

The project includes comprehensive testing:

### Test Coverage
- **Parser Tests** (12/12 passing): Clinical note parsing with various formats
- **Tool Tests**: Condition identification, dose calculation, treatment planning
- **Integration Tests**: End-to-end workflow validation
- **Error Handling Tests**: Comprehensive error scenario coverage

### Sample Clinical Note
```
Patient: Jack T.
DOB: 12/03/2022
Age: 3 years
Weight: 14.2 kg

Presenting complaint:
Jack presented with a 2-day history of barky cough, hoarse voice, and low-grade fever.
Symptoms worsened overnight, with increased work of breathing and stridor noted at rest.

Assessment:
Jack presents with classic features of moderate croup (laryngotracheobronchitis).

Plan:
- Administer corticosteroids
- Plan as per local guidelines for croup
```

### Expected Output
- **Condition**: Croup (Laryngotracheobronchitis)
- **Medication**: Dexamethasone 2.13mg oral (0.15mg/kg × 14.2kg)
- **Treatment Plan**: Comprehensive plan with monitoring, red flags, discharge criteria

## 🔬 MCP Tools Available

1. **parse_clinical_note**: Extract structured data from clinical text
2. **identify_condition**: Match symptoms to medical conditions
3. **calculate_medication_dose**: Weight-based dose calculations with safety limits
4. **generate_treatment_plan**: Comprehensive clinical management plans

## 🛡️ Security & Safety

- ⚠️ **Medical Device Warning**: This is a prototype for demonstration only
- 🔐 Environment variables never committed to version control
- 📝 No PHI (Personal Health Information) stored or logged
- ✅ Input validation and sanitization throughout
- 🚨 Comprehensive error handling with clinical safety considerations

## 🚧 Development Notes

### Current Status: Phase 1 Complete ✅
- [x] MCP server implementation
- [x] Clinical note parser
- [x] Condition identification  
- [x] Dose calculation with safety limits
- [x] Treatment plan generator
- [x] Comprehensive error handling
- [x] Full test suite (107 tests)
- [x] Local development environment

### Next Phase: AWS Infrastructure 🚀
- [ ] SST configuration
- [ ] Lambda deployment
- [ ] API Gateway setup
- [ ] CloudFront CDN
- [ ] Custom domain configuration

## 📚 Usage Examples

### Via Python
```python
import asyncio
from mcp_server.server import parse_clinical_note, identify_condition

# Parse clinical note
result = await parse_clinical_note("3-year-old with barky cough...")

# Identify condition
matches = await identify_condition(
    symptoms=["barky cough", "hoarse voice"], 
    assessment="moderate croup",
    patient_age=3
)
```

### Via MCP Protocol
The server implements the standard MCP protocol and can be used with any MCP-compatible client.

## 🆘 Troubleshooting

**Import Errors:**
```bash
pip3 install -r requirements.txt
```

**Data File Missing:**
```bash
# Check data files exist
ls -la mcp_server/data/
```

**Server Won't Start:**
```bash
# Test imports
python3 -c "from mcp_server.server import app; print('OK')"
```

## 📖 Documentation

- **Project Overview**: `/docs/Overview.md`
- **MCP Implementation**: `/docs/MCP_Implementation_Guide.md`  
- **Task Management**: `/docs/taskManagement.md`
- **Root Configuration**: `/CLAUDE.md`

## 🤝 Contributing

1. Follow the task-based development workflow in `/docs/taskManagement.md`
2. All changes must include tests
3. Run the full test suite before committing
4. Use conventional commit messages with task IDs

---

🏥 **Heidi Clinical Decision Support System**  
*Empowering clinicians with intelligent, evidence-based decision support*