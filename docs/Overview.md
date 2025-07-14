# Heidi Clinical Decision Support - Deployment Overview

## Project Architecture

### Tech Stack
- **Frontend**: React + Vite + shadcn/ui
- **Backend**: Python MCP Server + Express.js API Gateway
- **Infrastructure**: AWS SST (Serverless Stack)
- **Data Storage**: JSON files (in repository)
- **Static Assets**: AWS S3
- **CDN**: AWS CloudFront

### Architecture Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React/Vite)                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Clinical Note  │  │  Treatment Plan │  │  Dose Calculator│ │
│  │     Input       │  │     Display     │  │     Results     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTPS/API Gateway
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AWS API Gateway                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   POST /parse   │  │  POST /calculate│  │  POST /generate │ │
│  │                 │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Lambda Functions
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Server (Python)                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Parse Clinical │  │  Calculate Dose │  │  Generate Plan  │ │
│  │      Note       │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ File System Access
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        JSON Data Files                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  conditions.json│  │ medications.json│  │ guidelines.json │ │
│  │                 │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Development Sequence

### Phase 1: Backend Development (Week 1-2)
1. **MCP Server Setup**
   - Initialize Python MCP server with core tools
   - Implement clinical note parsing
   - Create dose calculation logic
   - Set up data models and validation

2. **AWS Infrastructure**
   - Configure SST for Lambda deployment
   - Create API Gateway endpoints
   - Configure IAM roles and permissions

3. **Data Setup**
   - Create JSON files for clinical guidelines
   - Build medication database (JSON)
   - Define condition data structures

### Phase 2: Frontend Development (Week 2-3)
1. **React App Setup**
   - Initialize Vite project with TypeScript
   - Install shadcn/ui components
   - Set up routing and state management

2. **UI Components**
   - Clinical note input form
   - Treatment plan display
   - Dose calculator interface
   - Results visualization

3. **API Integration**
   - Connect to backend endpoints
   - Implement error handling
   - Add loading states

### Phase 3: Deployment & Testing (Week 3-4)
1. **SST Deployment**
   - Deploy backend to AWS
   - Configure CloudFront CDN
   - Set up custom domain

2. **Testing & Validation**
   - End-to-end testing
   - Clinical scenario validation
   - Performance optimization

## Domain Requirements

### Primary Domain
- **Production**: `heidi.clinical-ai.com`
- **Staging**: `staging.heidi.clinical-ai.com`
- **API**: `api.heidi.clinical-ai.com`

### SSL/TLS
- AWS Certificate Manager for SSL certificates
- CloudFront for HTTPS termination
- Route 53 for DNS management

## API Requirements

### External APIs
- **OpenAI API**: Not required for MVP
  - MCP server handles all clinical logic internally
  - No external LLM calls needed for core functionality
  - Could be added later for natural language processing enhancements

### Internal APIs
- **MCP Server Endpoints**:
  - `POST /api/parse` - Parse clinical notes
  - `POST /api/calculate` - Calculate medication doses
  - `POST /api/generate` - Generate treatment plans
  - `GET /api/conditions` - List available conditions
  - `GET /api/medications` - List available medications

## Environment Variables

### Backend (Lambda)
```bash
# Data Configuration
DATA_PATH=/opt/data/
CONDITIONS_FILE=conditions.json
MEDICATIONS_FILE=medications.json
GUIDELINES_FILE=guidelines.json

# Caching
CACHE_ENABLED=true
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO
```

### Frontend (React)
```bash
# API Configuration
VITE_API_BASE_URL=https://api.heidi.clinical-ai.com
VITE_APP_NAME=Heidi Clinical Decision Support
VITE_APP_VERSION=1.0.0
```

## Security Considerations

### Authentication
- Simple API key authentication (MVP)
- CORS configuration for frontend
- Can upgrade to AWS Cognito later

### Data Protection
- Encryption at rest (Lambda filesystem)
- Encryption in transit (HTTPS)
- No PHI storage in logs
- HIPAA-compliant data handling
- JSON files bundled with Lambda deployment

### API Security
- Rate limiting
- Input validation
- CORS configuration
- API key management

## Monitoring & Logging

### CloudWatch Integration
- Lambda function metrics
- API Gateway logs
- File system access monitoring
- Frontend error tracking

### Alerting
- High error rates
- Performance degradation
- File system access issues
- API endpoint failures

## Cost Estimation

### Monthly AWS Costs (Estimated)
- **Lambda**: $5-10 (based on usage)
- **API Gateway**: $5-15 (per million requests)
- **CloudFront**: $1-5 (CDN costs)
- **Route 53**: $0.50 (hosted zone)
- **Certificate Manager**: Free
- **S3**: $1-2 (static assets)
- **Total**: ~$15-35/month for moderate usage

## Development Commands

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run MCP server locally (with local JSON files)
python -m mcp_server.server

# Bundle JSON files with Lambda
npx sst deploy --stage prod
```

### Frontend
```bash
# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## File Structure

```
heidi/
├── backend/
│   ├── mcp_server/          # MCP server implementation
│   ├── lambda/              # Lambda function handlers  
│   ├── data/                # Clinical data (JSON files)
│   │   ├── conditions.json  # Medical conditions database
│   │   ├── medications.json # Medication dosing database
│   │   └── guidelines.json  # Treatment guidelines
│   └── tests/               # Backend tests
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── lib/             # Utilities and API calls
│   │   └── styles/          # CSS and theme files
│   ├── public/              # Static assets
│   └── dist/                # Build output
├── infrastructure/
│   ├── sst.config.ts        # SST configuration
│   └── stacks/              # AWS CDK stacks
└── docs/
    ├── architecture.png     # Architecture diagram
    └── demo-video.mp4       # Walk-through video
```

## Next Steps

1. **Start with backend development** to establish the MCP server foundation
2. **Set up AWS infrastructure** using SST for consistent deployments
3. **Build frontend incrementally** with shadcn/ui components
4. **Deploy to staging** for testing before production release
5. **Create demo content** for walk-through video

This approach prioritizes the backend MCP server implementation first, ensuring the core clinical logic is solid before building the user interface.

## JSON File Benefits for MVP

### Advantages
- **Simplicity**: No database setup or configuration needed
- **Version Control**: Clinical data tracked in git with code changes
- **Performance**: Fast file reads from Lambda filesystem
- **Cost**: No database costs for MVP
- **Portability**: Easy to migrate to database later
- **Development Speed**: Instant data updates without deployment

### File Structure & Access
- JSON files bundled with Lambda deployment
- Files loaded into memory at Lambda cold start
- Data cached for subsequent requests
- File updates require Lambda redeployment

### Performance Considerations
- **Cold Start**: ~100-200ms to load JSON files
- **Warm Requests**: Sub-millisecond data access
- **Memory Usage**: ~10-50MB for clinical data
- **Scalability**: Suitable for 1000s of requests/minute

### Migration Path
- Start with JSON files for rapid development
- Add database layer when scaling requirements increase
- MCP server interface remains unchanged

### Data Management
- **Updates**: Edit JSON files and redeploy Lambda
- **Versioning**: Git tracks all data changes
- **Validation**: JSON schema validation before deployment
- **Rollback**: Git revert for quick data rollbacks
- **Testing**: Local JSON files for development/testing