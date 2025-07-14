# Task Management

## Development Task Sequence

### Task Status Indicators

- **[TODO]**: Task not yet started
- **[INPROG]**: Task currently in progress
- **[DONE]**: Task completed and committed
- **[BLOCKED]**: Task blocked by dependencies or issues

### Phase 1: Backend Foundation

- **#001** [DONE]: Setup project structure, dependencies, and environment configuration
- **#002** [DONE]: Create JSON data files (conditions with embedded medications, guidelines)
- **#003** [DONE]: Implement MCP server basic structure
- **#004** [DONE]: Build clinical note parser tool
- **#005** [DONE]: Implement dose calculation tool
- **#006** [DONE]: Create condition identification tool
- **#007** [TODO]: Build treatment plan generator
- **#008** [TODO]: Add comprehensive error handling
- **#009** [TODO]: Write unit tests for all tools
- **#010** [TODO]: Setup local development environment

### Phase 2: AWS Infrastructure

- **#011** [TODO]: Configure SST project structure
- **#012** [TODO]: Setup Lambda function handlers
- **#013** [TODO]: Configure API Gateway endpoints
- **#014** [TODO]: Setup CloudFront CDN
- **#015** [TODO]: Configure custom domain (heidimcp.uk) and SSL with Cloudflare
- **#016** [TODO]: Setup CloudWatch logging
- **#017** [TODO]: Deploy and test backend

### Phase 3: Frontend Development

- **#018** [TODO]: Initialize React + Vite project
- **#019** [TODO]: Setup shadcn/ui components
- **#020** [TODO]: Create clinical note input component
- **#021** [TODO]: Build treatment plan display
- **#022** [TODO]: Implement dose calculator interface
- **#023** [TODO]: Add API integration layer
- **#024** [TODO]: Implement error handling and loading states
- **#025** [TODO]: Add responsive design
- **#026** [TODO]: Deploy frontend to AWS

### Phase 4: Integration & Testing

- **#027** [TODO]: End-to-end integration testing
- **#028** [TODO]: Clinical scenario validation
- **#029** [TODO]: Performance optimization
- **#030** [TODO]: Create architecture diagram
- **#031** [TODO]: Record demo video
- **#032** [TODO]: Final documentation

## Task Guidelines

- Before commencing a new task ensure you think really hard about the optimal solution before starting
- Each task should be completable in a single Claude Code session
- Tasks must be atomic and focused on one specific deliverable
- Use task IDs (#001, #002, etc.) in all git commits
- Test locally before committing
- Each task should include appropriate documentation
- **Environment Setup**: Always use `nvm use` before starting work
- **Security**: Never commit .env files or sensitive data
- **Dependencies**: Use exact Node version specified in .nvmrc
- **Status Updates**: Update task status in CLAUDE.md when starting/completing tasks

### Task Status Management

1. **Starting a task**: Change status from [TODO] to [INPROG]
2. **Completing a task**: Change status from [INPROG] to [DONE]
3. **Blocking issues**: Change status to [BLOCKED] with reason
4. **Git commits**: Always include task ID and status (e.g., "#001 [DONE] Setup project structure")
5. **Commit ALL files**: **MANDATORY** - At the end of each task, commit ALL changes across ALL files in the ENTIRE repository using `git add .` before committing
6. **Git push**: **MANDATORY** - After every commit, ALWAYS ask user for permission to push to GitHub before proceeding

### Example Task Status Flow

```
#001 [TODO] → #001 [INPROG] → #001 [DONE]
```
