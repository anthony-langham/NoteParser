# Claude Code Project Configuration

This file contains configuration and context for Claude Code to help with development tasks.

## Project Information

- **Project Name**: heidi
- **License**: MIT
- **Repository**: Git repository (main branch)
- **Project Type**: Intelligent Clinical Decision Support System

## Project Overview

**Core Concept**: Leverage clinical data and context to assist clinician's needs in real time, by helping guide treatment decisions using up-to-date clinical guidelines & MCP tool use.

**Key Features**:

- Ingests visit notes or transcripts as input
- Queries & references local guidelines using MCP server tools
- Calculates weight-based medication doses
- Returns detailed clinical decision support plans

**Example Use Case**: Pediatric croup management - suggesting appropriate treatment approach and calculating oral steroid dose (prednisone/dexamethasone) based on history, examination, and guideline references.

**Architecture**: React + Vite frontend → AWS API Gateway → Python MCP Server → JSON data files

## Deliverables

1. **Working prototype (MVP)**

   - Accepts unstructured clinical text
   - Queries relevant local guidelines via MCP tools
   - Calculates weight & evidence-based medication doses
   - Returns detailed management plans grounded in clinical guidelines
   - **LIVE URL**: `https://heidimcp.uk`

2. **Architecture diagram** (one-page PNG/PDF)

   - Major components and data flow
   - Service/API/framework explanations with rationales

3. **Walk-through video** (5-10 minutes)
   - Demonstrate prototype on test cases
   - Explain design decisions and limitations

## Current Status

- **Phase**: Backend Foundation Complete (Phase 2 in progress)
- **Tech Stack**: React + Vite + shadcn/ui → AWS SST + Lambda → Python MCP Server → JSON files
- **Data Storage**: JSON files (conditions.json with embedded medications, guidelines.json)
- **Data Structure**: Conditions contain embedded medication dosing for streamlined clinical workflow
- **Deployment**: AWS SST (Serverless Stack) with CloudFront CDN
- **Domain**: heidimcp.uk (Cloudflare hosted)
- **Authentication**: Simple API key (MVP), upgrade to AWS Cognito later
- **Cost**: ~$15-35/month for moderate usage

### Completed Tasks (Phase 1 & 2)
- ✅ **#001-#012**: Complete backend foundation with MCP server, Lambda handlers, and SST infrastructure
- ✅ **#013**: API Gateway endpoints configured with authentication, health checks, and main processing
- ✅ **#014**: CloudFront CDN configured with HTTPS redirect, compression, and optimized caching

### Current Priority
- **#015**: ✅ Configure custom domain (heidimcp.uk) and SSL with Cloudflare
- **#016**: Setup CloudWatch logging
- **#017**: Deploy and test backend infrastructure

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

## Data Structure

### conditions.json Schema

```json
{
  "condition_id": {
    "name": "Human-readable condition name",
    "description": "Clinical description",
    "icd_codes": ["ICD-10 codes"],
    "age_groups": ["pediatric", "adult"],
    "symptoms": {
      "primary": ["key symptoms"],
      "secondary": ["additional symptoms"]
    },
    "severity_scales": {
      "mild": "criteria",
      "moderate": "criteria",
      "severe": "criteria"
    },
    "medications": {
      "first_line": {
        "medication_name": {
          "dose_mg_per_kg": 0.0,
          "max_dose_mg": 0,
          "min_dose_mg": 0,
          "route": "oral|iv|im",
          "frequency": "daily|bid|tid",
          "duration": "days",
          "age_restrictions": "constraints",
          "contraindications": ["conditions"]
        }
      },
      "second_line": { "...": "..." }
    },
    "clinical_pearls": ["key points"],
    "red_flags": ["concerning symptoms"]
  }
}
```

### guidelines.json Schema

```json
{
  "guideline_id": {
    "name": "Guideline name",
    "version": "1.0",
    "last_updated": "YYYY-MM-DD",
    "source": "Medical organization",
    "conditions": ["condition_ids"],
    "decision_tree": {
      "assessment": {
        "severity_assessment": "steps",
        "age_considerations": "factors"
      },
      "treatment_algorithm": {
        "mild": "treatment_plan",
        "moderate": "treatment_plan",
        "severe": "treatment_plan"
      }
    },
    "monitoring": "post-treatment monitoring",
    "follow_up": "follow-up instructions"
  }
}
```

## Project Structure

```
heidi/
├── backend/
│   ├── mcp_server/          # MCP server implementation
│   │   ├── __init__.py
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
│   │   ├── lib/             # Utilities and API calls
│   │   └── styles/          # CSS and theme files
│   ├── public/              # Static assets
│   └── dist/                # Build output
├── infrastructure/
│   ├── sst.config.ts        # SST configuration
│   └── stacks/              # AWS CDK stacks
├── docs/
│   ├── Overview.md          # Deployment overview
│   ├── MCP_Implementation_Guide.md  # MCP server guide
│   ├── Planning.md          # Development planning
│   └── taskManagement.md    # Task tracking and management
├── README.md
├── LICENSE
└── CLAUDE.md                # This file
```

## Development Commands

### Backend (MCP Server)

```bash
# Use correct Node version (for SST)
nvm use

# Install Python dependencies (use python3 for this project)
pip3 install -r requirements.txt

# Run MCP server locally
python3 -m mcp_server.server

# Run tests
python3 -m pytest tests/

# Deploy to AWS
npx sst deploy --stage prod
```

### Frontend (React)

```bash
# Use correct Node version
nvm use

# Install dependencies
npm install

# Development server (always use port 4000)
# MANDATORY: Always stop existing server before starting new one

# Step 1: Check what's running on port 4000
lsof -i:4000

# Step 2: Stop any existing dev server (safe - won't error if nothing running)
lsof -ti:4000 && kill -9 $(lsof -ti:4000) || echo "Port 4000 is free"

# Step 3: Start dev server on port 4000
npm run dev -- --port 4000

# One-liner to stop and restart:
# lsof -ti:4000 && kill -9 $(lsof -ti:4000) || true; npm run dev -- --port 4000

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

### Infrastructure

```bash
# Use correct Node version
nvm use

# Deploy infrastructure
npx sst deploy --stage dev
npx sst deploy --stage prod

# Remove infrastructure
npx sst remove --stage dev

# Configure Cloudflare DNS
# Point heidimcp.uk to CloudFront distribution
# Point api.heidimcp.uk to API Gateway
```

### Environment Setup

```bash
# Install Node Version Manager (if not installed)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Use project Node version
nvm use

# Install dependencies
npm install

# Copy environment files
cp .env.example .env
# Edit .env with your actual values
```

## Dependencies & Requirements

### Backend Dependencies

```python
# requirements.txt
mcp>=1.0.0
pydantic>=2.0.0
pytest>=7.0.0
python-dateutil>=2.8.0
fastapi>=0.104.0
uvicorn>=0.24.0
```

### Frontend Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.0.3",
    "typescript": "^5.0.2",
    "tailwindcss": "^3.3.0",
    "@radix-ui/react-*": "latest",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^1.14.0"
  }
}
```

### Infrastructure Requirements

- AWS Account with appropriate permissions
- Node.js 18+ for SST and frontend (managed via .nvmrc)
- Python 3.9+ for MCP server
- AWS CLI configured
- **Domain**: heidimcp.uk (Cloudflare hosted)
- Cloudflare account for DNS management
- NVM (Node Version Manager) for consistent Node.js versions

## Environment Variables & Configuration

### Node Version Management (.nvmrc)

```
18.18.0
```

### Backend (.env)

```bash
# Data Configuration
DATA_PATH=/opt/data/
CONDITIONS_FILE=conditions.json
GUIDELINES_FILE=guidelines.json

# API Configuration
API_KEY=your-secure-api-key-here
CORS_ORIGINS=https://heidimcp.uk,http://localhost:3000

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Logging
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Frontend (.env)

```bash
# API Configuration
VITE_API_BASE_URL=https://api.heidimcp.uk
VITE_API_KEY=your-secure-api-key-here
VITE_APP_NAME=Heidi Clinical Decision Support
VITE_APP_VERSION=1.0.0

# Environment
VITE_ENVIRONMENT=development
```

### Environment File Templates

#### Backend (.env.example)

```bash
# Copy this to .env and fill in your values
API_KEY=generate-a-secure-api-key
CORS_ORIGINS=https://heidimcp.uk,http://localhost:3000
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
LOG_LEVEL=INFO
ENVIRONMENT=development
```

#### Frontend (.env.example)

```bash
# Copy this to .env and fill in your values
VITE_API_BASE_URL=https://api.heidimcp.uk
VITE_API_KEY=your-secure-api-key
VITE_APP_NAME=Heidi Clinical Decision Support
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=development
```

## Development Task Sequence

See [docs/taskManagement.md](docs/taskManagement.md) for detailed task tracking and management guidelines.

## Key Technical Decisions

### Why MCP over RAG?

1. **Deterministic Results**: Medical decisions need reproducible, auditable outputs
2. **Structured Validation**: Medical data requires strict input/output validation
3. **Performance**: Direct tool calls faster than semantic search
4. **Safety**: Explicit logic safer than AI interpretation for medical calculations
5. **Transparency**: Clear reasoning chain for clinical decisions

### Why JSON Files over Database?

1. **Simplicity**: No database setup/configuration for MVP
2. **Version Control**: Clinical data tracked in git with code
3. **Performance**: Fast file reads from Lambda filesystem
4. **Cost**: No database costs for MVP
5. **Development Speed**: Instant data updates without deployment

### Why Embedded Medications in Conditions?

1. **Clinical Workflow**: Aligns with clinical thinking (condition → treatment)
2. **Atomic Updates**: Condition and treatment data maintained together
3. **Reduced Complexity**: No need to manage relationships between separate files
4. **Faster Lookups**: Single file read instead of multiple joins
5. **Easier Validation**: Related data validated as a unit

### Security Considerations

- No PHI (Personal Health Information) stored in logs
- HIPAA-compliant data handling practices
- Encryption at rest (Lambda filesystem)
- Encryption in transit (HTTPS)
- Input validation and sanitization
- Rate limiting on API endpoints
- **Environment Variables**: Never commit .env files to version control
- **API Keys**: Use secure, randomly generated API keys
- **AWS Credentials**: Use IAM roles in production, not hardcoded keys
- **CORS**: Restrict origins to known domains only
- **Secrets Management**: Consider AWS Secrets Manager for production

## Git Configuration

### .gitignore

```
# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pids
*.pid
*.seed
*.pid.lock

# Coverage
coverage/
.nyc_output

# AWS
.aws/

# SST
.sst/

# Build outputs
dist/
build/

# Temporary files
.tmp/
.cache/

# Medical data (if any test files)
*.csv
*.xlsx
*.json.backup

# Secrets and keys
*.pem
*.key
*.crt
*.p12
*.pfx
```

## Testing Strategy

### Backend Testing

- Unit tests for each MCP tool
- Integration tests with sample clinical notes
- Dose calculation validation tests
- Error handling and edge case tests

### Frontend Testing

- Component unit tests
- API integration tests
- User workflow tests
- Cross-browser compatibility

### Clinical Validation

- Test with real clinical scenarios
- Validate dose calculations against clinical guidelines
- Verify treatment recommendations
- Medical professional review

## Deployment Checklist

### Pre-deployment

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] JSON data files validated
- [ ] API endpoints tested
- [ ] Frontend builds successfully
- [ ] Domain and SSL configured

### Post-deployment

- [ ] Health checks passing
- [ ] CloudWatch logs configured
- [ ] Error monitoring active
- [ ] Performance metrics tracked
- [ ] Backup and recovery tested

## Notes

- Focus on rapid prototyping, not production-ready scalability
- MCP server provides deterministic, auditable clinical logic
- JSON files enable fast iteration and version control
- Simple API key authentication for MVP
- Upgrade path to database and advanced auth when needed

# important-instruction-reminders

Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (\*.md) or README files. Only create documentation files if explicitly requested by the User.

# development-workflow

When implementing tasks:

1. Update task status to [INPROG] in docs/taskManagement.md when starting a task
2. Use the task ID (#001, #002, etc.) in git commit messages
3. Think really hard before commencing
4. Test functionality locally before committing
5. Focus on one atomic deliverable per task
6. Update CLAUDE.md with new commands as they become available
7. **MANDATORY**: Mark task as [DONE] in docs/taskManagement.md when completed
8. **MANDATORY**: Add detailed completion information to docs/taskManagement.md with bullet points explaining all work done
9. **MANDATORY**: Update docs/taskManagement.md task status BEFORE making git commits
10. Each task should be completable in a single Claude Code session
11. Git commit messages should follow the format: "#XXX [DONE] Brief description"
12. **MANDATORY**: At the end of each task, commit ALL changes across ALL files in the ENTIRE repository using `git add .` before committing
13. **MANDATORY**: After every commit, ALWAYS ask user for permission to push to GitHub before proceeding

## Git Commit Format

```
#001 [DONE] Setup project structure and environment configuration

- Created backend/ and frontend/ directories
- Added .nvmrc file with Node 18.18.0
- Configured .env.example files
- Added comprehensive .gitignore
- Setup requirements.txt for Python dependencies
- Installed all dependencies (infrastructure, backend, frontend)
```

## Task Status Update Requirements

**CRITICAL**: When completing a task, you MUST:

1. Update the task status from [INPROG] to [DONE] in docs/taskManagement.md
2. **MANDATORY**: Add detailed completion information to docs/taskManagement.md following this format:
   ```
   - **#XXX** [DONE]: Task Title
     - Detailed bullet point 1 explaining what was implemented/configured
     - Detailed bullet point 2 explaining technical decisions made
     - Detailed bullet point 3 explaining files created/modified
     - Additional bullet points covering all significant work done
   ```
3. Ensure the update is made BEFORE creating git commits
4. Use git commit messages that include the task ID and status
5. Example workflow:
   - Start task: Change `#001 [TODO]` to `#001 [INPROG]` in docs/taskManagement.md
   - Complete task: Change `#001 [INPROG]` to `#001 [DONE]` in docs/taskManagement.md
   - **Add detailed completion notes** under the task with bullet points explaining:
     - Files created/modified with brief description of contents
     - Technical decisions made and rationale
     - Configuration settings applied
     - Integration points established
     - Testing performed and results
     - Dependencies added or updated
     - Security considerations addressed
   - Commit: `git commit -m "#001 [DONE] Setup project structure and dependencies"`

**This detailed documentation is MANDATORY for every task completion and must be done BEFORE the git commit.**

# quick-start-guide

For new Claude Code sessions:

1. **Current Phase**: Planning & Architecture Complete
2. **Next Task**: Check docs/taskManagement.md for current task status
3. **Priority**: Backend foundation (MCP server) before frontend
4. **Key Files**: Review Overview.md and MCP_Implementation_Guide.md
5. **Sample Data**: Use provided clinical note for Jack T. (croup case)
6. **Status Management**: Update task status in docs/taskManagement.md when starting/completing tasks

# environment-security-checklist

## Before Starting Development

- [ ] Install NVM and use correct Node version (`nvm use`)
- [ ] Copy .env.example to .env for both backend and frontend
- [ ] Generate secure API keys (minimum 32 characters)
- [ ] Configure AWS credentials (prefer IAM roles in production)
- [ ] Verify .gitignore includes all .env files
- [ ] Never commit actual .env files to version control

## API Key Generation

```bash
# Generate secure API key
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Or using OpenSSL
openssl rand -hex 32
```

## Environment File Security

1. **Development**: Use .env files (gitignored)
2. **Production**: Use AWS Secrets Manager or environment variables
3. **Never**: Hardcode secrets in source code
4. **Always**: Use .env.example templates for team sharing

# context-for-claude

This is a medical decision support system that:

- Parses clinical notes to extract patient data
- Calculates medication doses based on weight and condition
- Generates treatment plans following clinical guidelines
- Uses MCP (Model Context Protocol) for deterministic, auditable results
- Stores clinical data in JSON files for rapid MVP development
- Deploys to AWS using SST (Serverless Stack) framework
- **Node Version**: Managed via .nvmrc file
- **Environment**: Secured via .env files (never committed)
- **Domain**: heidimcp.uk (Cloudflare hosted)

IMPORTANT: This is a defensive medical tool to assist clinicians, not replace clinical judgment. All calculations and recommendations must be validated against established medical guidelines.
