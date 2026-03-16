# Company Wiki

**Document Information**
- Version: 4.2
- Last Updated: January 8, 2026
- Document Owner: Engineering & Product Operations
- Contact: wiki-admin@apextech.solutions
- Wiki Home: apextech.notion.so/wiki

---

## Table of Contents
1. [Using This Wiki](#using-this-wiki)
2. [Engineering Workflow](#engineering-workflow)
3. [Product Development Process](#product-development-process)
4. [Documentation Standards](#documentation-standards)
5. [Communication Guidelines](#communication-guidelines)
6. [Meeting Culture](#meeting-culture)
7. [Project Management](#project-management)
8. [Release Process](#release-process)
9. [Incident Response](#incident-response)
10. [Company Calendar & Events](#company-calendar--events)

---

## Using This Wiki

### Purpose
This wiki serves as the central knowledge repository for all company processes, workflows, and institutional knowledge. When in doubt, check here first!

### Navigation
- **Browse by Department**: Engineering, Product, Sales, Marketing, etc.
- **Search**: Use Notion search (Cmd+K / Ctrl+K) to find anything
- **Recently Updated**: Check the "What's New" page weekly
- **Ask for Help**: Post in #ask-anything if you can't find what you need

### Contributing to the Wiki
Everyone can (and should!) improve the wiki:

**How to Edit:**
1. Click "Edit" on any page
2. Make your changes
3. Add a brief note in the "Edit Summary" field
4. Save (auto-saves as you type)

**Guidelines:**
- Keep it current: Update outdated info immediately
- Be clear and concise: Assume readers are new to the topic
- Use templates: Standard templates exist for common page types
- Link generously: Cross-reference related pages
- Add examples: Real scenarios help readers understand

**Page Ownership:**
Each wiki section has designated owners listed at the top. Owners are responsible for:
- Keeping content accurate and current
- Reviewing community contributions
- Quarterly content audits

---

## Engineering Workflow

### Development Methodology
ApexTech Engineering follows **Agile/Scrum** with two-week sprints.

### Sprint Cycle Overview

**Week 1:**
- **Monday 10:00 AM - Sprint Planning** (2 hours)
  - Review and prioritize backlog
  - Team commits to sprint goals
  - Break down stories into tasks
  - Estimate effort using story points
  
- **Daily Standups** (Monday-Friday, 9:30 AM, 15 min)
  - What did you complete yesterday?
  - What are you working on today?
  - Any blockers?

- **Wednesday 2:00 PM - Backlog Refinement** (1 hour)
  - Groom upcoming stories
  - Add acceptance criteria
  - Identify dependencies

**Week 2:**
- **Daily Standups** (continue)

- **Thursday 3:00 PM - Sprint Review** (1 hour)
  - Demo completed work
  - Gather stakeholder feedback
  - Celebrate wins

- **Friday 10:00 AM - Sprint Retrospective** (1 hour)
  - What went well?
  - What could improve?
  - Action items for next sprint

### Story Workflow in Jira

**Story States:**
1. **Backlog** → Unscheduled work
2. **Ready for Dev** → Refined, estimated, has acceptance criteria
3. **In Progress** → Actively being worked on
4. **Code Review** → PR submitted, awaiting review
5. **QA Testing** → Testing in staging environment
6. **Done** → Merged to main, deployed to production

**Story Point Scale (Fibonacci):**
- **1 point**: Few hours (simple bug fix, copy change)
- **2 points**: Half day (small feature, straightforward implementation)
- **3 points**: 1 day (medium feature, some complexity)
- **5 points**: 2-3 days (complex feature, multiple components)
- **8 points**: 1 week (large feature, cross-team coordination)
- **13+ points**: Break it down! Stories this large should be split

### Code Review Process

**Before Submitting PR:**
- [ ] Code follows style guide (auto-enforced by linters)
- [ ] Tests written and passing (minimum 80% coverage)
- [ ] Documentation updated (README, API docs, inline comments)
- [ ] Self-review completed (read your own diff)
- [ ] No sensitive data, API keys, or secrets in code

**PR Description Template:**
```markdown
## What
Brief description of changes

## Why
Link to Jira ticket: APEX-1234
Business context or problem being solved

## How
Technical approach and key decisions

## Testing
- How to test this change
- Edge cases covered
- Automated tests added

## Screenshots (if UI change)
[attach screenshots]

## Deployment Notes
Any migrations, config changes, or rollback considerations
```

**Review Standards:**
- **2 approvals required** for production code
- **1 approval required** for documentation or minor changes
- **Response SLA**: Review within 24 hours (4 hours for critical fixes)
- **Reviewer Responsibilities**: Test locally, check for edge cases, ensure clarity

**PR Etiquette:**
- Keep PRs small (<400 lines changed when possible)
- Use draft PRs for early feedback
- Respond to all review comments
- Mark conversations as "Resolved" once addressed
- Be respectful: "Consider..." not "You should..."

### Branching Strategy

**Main Branches:**
- `main` - Production-ready code, protected
- `staging` - QA testing environment
- `develop` - Integration branch for features

**Feature Branches:**
- Naming: `feature/APEX-1234-short-description`
- Branch from: `develop`
- Merge to: `develop` (then to staging, then to main)

**Hotfix Branches:**
- Naming: `hotfix/APEX-5678-brief-description`
- Branch from: `main`
- Merge to: `main` and `develop` immediately

**Release Branches:**
- Created for major releases
- Naming: `release/v2.4.0`
- Feature freeze for stabilization and bug fixes

### Development Environment Setup

**Required Tools:**
- Docker Desktop (for local services)
- Node.js 18+ (backend)
- Python 3.11+ (AI/ML services)
- PostgreSQL 14+
- Redis 7+

**Getting Started:**
```bash
# Clone the monorepo
git clone git@github.com:apextech/platform.git
cd platform

# Install dependencies
npm install

# Set up local environment
cp .env.example .env.local
# Edit .env.local with your credentials

# Start local services
docker-compose up -d

# Run database migrations
npm run db:migrate

# Start development server
npm run dev
```

**Detailed setup guide**: apextech.notion.so/dev-setup

### Testing Standards

**Required Test Types:**
- **Unit Tests**: All business logic (80%+ coverage)
- **Integration Tests**: API endpoints and database interactions
- **E2E Tests**: Critical user flows (login, checkout, etc.)

**Running Tests:**
```bash
# Run all tests
npm test

# Run specific test file
npm test -- user.test.js

# Run with coverage
npm run test:coverage

# Run E2E tests (requires local environment)
npm run test:e2e
```

**Pre-Commit Hooks:**
- Linting (ESLint, Prettier)
- Unit tests for changed files
- No console.logs or debugger statements
- Commit message format check

---

## Product Development Process

### Product Lifecycle

**1. Discovery (Ongoing)**
- Customer interviews and feedback analysis
- Market research and competitive analysis
- Data analysis (usage metrics, feature requests)
- Identify problems worth solving

**2. Ideation (Quarterly)**
- Product team generates concepts
- Evaluate against strategic priorities
- Estimate impact vs. effort
- Prioritize top ideas for roadmap

**3. Requirements & Design (1-3 weeks)**
- Product manager writes PRD (Product Requirements Document)
- Designer creates mockups and prototypes
- Engineering provides technical feasibility review
- Stakeholder review and approval

**4. Development (1-6 weeks)**
- Sprint planning and execution
- Regular syncs between PM, Design, and Eng
- QA testing throughout development
- Iterative refinement based on feedback

**5. Launch (1 week)**
- Beta testing with select customers
- Documentation and training materials
- Marketing and sales enablement
- Public release and monitoring

**6. Post-Launch (Ongoing)**
- Monitor adoption and usage metrics
- Gather user feedback
- Iterate based on learnings
- Plan next phase or improvements

### Product Requirements Document (PRD) Template

All new features require a PRD. Template: apextech.notion.so/prd-template

**Key Sections:**
- **Executive Summary**: Problem, solution, success metrics
- **User Stories**: Who needs this and why
- **Requirements**: Must-have vs. nice-to-have features
- **Design Mocks**: Wireframes or high-fidelity designs
- **Technical Considerations**: Architecture, dependencies, risks
- **Success Metrics**: KPIs to measure impact
- **Go-to-Market Plan**: Launch strategy and rollout

**Approval Process:**
1. PM drafts PRD
2. Design review (UX team)
3. Technical review (Engineering lead)
4. Stakeholder review (CPO, relevant VPs)
5. Final approval and roadmap scheduling

### Feature Flags & Rollouts

We use **LaunchDarkly** for feature flags, allowing gradual rollouts and safe experimentation.

**Rollout Strategy:**
- **5%**: Internal employees
- **10%**: Beta customers (volunteers)
- **25%**: Early adopters (power users)
- **50%**: Half of users
- **100%**: General availability

**When to Use Flags:**
- Large or risky features
- A/B testing experiments
- Gradual rollouts to monitor impact
- Kill switches for quick rollback

---

## Documentation Standards

### Types of Documentation

**Code Documentation:**
- **Inline Comments**: Explain "why", not "what" (code should be self-explanatory)
- **Function/Class Docs**: Parameters, return values, exceptions
- **README Files**: Project overview, setup, usage examples

**API Documentation:**
- Auto-generated from OpenAPI specs
- Hosted at docs.apextech.com/api
- Includes examples, authentication, error codes

**User Documentation:**
- Help center (help.apextech.com)
- In-app tooltips and guides
- Video tutorials for complex features

**Internal Documentation (This Wiki):**
- Processes, workflows, runbooks
- Architecture diagrams
- Troubleshooting guides
- Team-specific knowledge

### Writing Style Guide

**Principles:**
- **Clear**: Simple language, short sentences
- **Concise**: No fluff; get to the point
- **Accurate**: Keep information current
- **Scannable**: Use headings, lists, tables
- **Actionable**: Tell readers what to do

**Formatting Standards:**
- Use Markdown for all text documentation
- Include table of contents for docs >500 words
- Add diagrams for complex processes (use Mermaid or Figma)
- Link to related pages generously
- Include "Last Updated" date on procedural docs

**Diagram Tools:**
- **Architecture Diagrams**: Lucidchart or Mermaid
- **User Flows**: Figma or Whimsical
- **Data Models**: dbdiagram.io

**Example Structure:**
```markdown
# Title

**Metadata**
- Owner: Team/Person
- Last Updated: Date
- Related: [Links to related docs]

## Overview
Brief summary of what this document covers.

## Prerequisites (if applicable)
What the reader needs to know/have before proceeding.

## Step-by-Step Instructions
1. Do this
2. Then this
3. Finally this

## Examples
Show concrete examples.

## Troubleshooting
Common issues and solutions.

## FAQ
Anticipated questions.
```

---

## Communication Guidelines

### Choosing the Right Channel

| Channel | Use For | Response Time | Examples |
|---------|---------|---------------|----------|
| **Slack** | Quick questions, updates, casual chat | Minutes-hours | "Can someone review my PR?" |
| **Email** | Formal communication, external stakeholders | Hours-days | Contract negotiations, legal |
| **Jira Comments** | Task-specific discussion | Hours | "This ticket needs clarification" |
| **Notion** | Long-form documentation, decisions | N/A (async) | Technical specs, meeting notes |
| **Zoom/Meet** | Real-time collaboration, complex topics | Scheduled | Architecture reviews, 1:1s |
| **GitHub Comments** | Code review feedback | Hours | "Consider refactoring this function" |

### Slack Best Practices

**Do:**
- Use threads to keep conversations organized
- Use @channel sparingly (only urgent, everyone-needs-to-know)
- Set status when away, in meetings, or focusing
- Mute channels that aren't immediately relevant
- Use reactions (emoji) to acknowledge messages
- Share wins and celebrate teammates in #wins

**Don't:**
- Expect instant responses (async-first culture)
- Send "hey" or "are you there?" without context
- Use @here/@channel for non-urgent messages
- Have sensitive conversations in public channels
- Forget to update status when away

**Channel Naming Conventions:**
- `#team-[name]`: Team-specific channels (#team-platform)
- `#proj-[name]`: Temporary project channels
- `#off-[topic]`: Off-topic/social (#off-pets, #off-gaming)
- `#ask-[department]`: Department Q&A channels

### Writing Effective Messages

**Subject Lines (Email/Slack):**
- Be specific: "Q4 Roadmap Review" not "Meeting"
- Use [ACTION REQUIRED], [FYI], [URGENT] tags when appropriate

**Message Structure:**
- **Start with the "why"**: Provide context
- **Be specific**: Include relevant details, links, screenshots
- **Clear ask**: What do you need? By when?
- **TL;DR**: For long messages, include summary at top

**Example:**
```
Hey team! 👋

TL;DR: Need design feedback on login flow by EOD Thursday.

We're redesigning the login experience to reduce friction. 
I've created a Figma prototype (link) with 3 options.

Could you review and leave comments by Thursday EOD? 
We're presenting to stakeholders Friday morning.

Questions? Drop them in thread below. Thanks!
```

---

## Meeting Culture

### Meeting Principles
- **Default to No Meeting**: Could this be an email/Slack message?
- **Invite Intentionally**: Only include essential participants
- **Start and End on Time**: Respect everyone's calendar
- **Have an Agenda**: No agenda = no meeting
- **Document Outcomes**: Meeting notes, decisions, action items

### Required Meeting Elements

**Before the Meeting:**
- [ ] Clear objective and desired outcome
- [ ] Agenda sent 24 hours in advance
- [ ] Pre-reads shared (if applicable)
- [ ] Right attendees invited (required vs. optional)
- [ ] Room/Zoom link booked

**During the Meeting:**
- [ ] Start with agenda review
- [ ] Assign note-taker
- [ ] Stay on topic; park tangents for later
- [ ] Capture decisions and action items
- [ ] End with summary of next steps

**After the Meeting:**
- [ ] Share notes within 24 hours (in Notion)
- [ ] Assign action items with owners and due dates
- [ ] Follow up on commitments

### Standard Meeting Types

**Daily Standup (15 min)**
- What you did yesterday
- What you're doing today
- Blockers
- No problem-solving (take offline)

**Weekly 1:1s (30 min)**
- Employee's agenda (not manager's status check)
- Career development, feedback, support
- Remove roadblocks

**Sprint Planning (2 hours)**
- Review backlog priorities
- Commit to sprint goals
- Break down stories and estimate

**Sprint Retro (1 hour)**
- What went well?
- What didn't?
- Action items for improvement

**All-Hands (Monthly, 1 hour)**
- Company updates from leadership
- Team spotlights
- Q&A with executives
- **When**: Last Friday of month, 4:00 PM PT

### Meeting-Free Time Blocks
- **Focus Fridays**: No meetings after 2:00 PM (unless critical)
- **No-Meeting Wednesdays**: Engineering only (for deep work)
- **Lunch Hours**: 12:00-1:00 PM protected

---

## Project Management

### Project Kickoff Checklist
- [ ] Project charter created (goals, scope, stakeholders)
- [ ] Jira epic created with linked stories
- [ ] Project Slack channel created (#proj-name)
- [ ] Kickoff meeting scheduled with all stakeholders
- [ ] Notion project page created
- [ ] Success criteria defined
- [ ] Timeline and milestones established
- [ ] Risk assessment completed

### Tracking Progress
- **Jira Dashboards**: Real-time view of sprint velocity and burndown
- **Weekly Status Updates**: Posted in project Slack channel
- **Biweekly Stakeholder Syncs**: For large projects
- **Monthly Roadmap Reviews**: Leadership reviews progress against roadmap

### Project Roles
- **Project Sponsor**: Executive champion
- **Project Manager**: Day-to-day coordination (usually PM or Eng Lead)
- **Tech Lead**: Technical direction and architecture
- **Contributors**: Engineers, designers, QA, etc.

---

## Release Process

### Release Schedule
- **Minor Releases**: Weekly (Tuesdays, 2:00 PM PT)
- **Major Releases**: Quarterly (Q1, Q2, Q3, Q4)
- **Hotfixes**: As needed (follow expedited process)

### Pre-Release Checklist
- [ ] All features tested in staging
- [ ] Release notes drafted
- [ ] Database migrations tested
- [ ] Rollback plan documented
- [ ] Customer-facing teams notified (Sales, CS, Support)
- [ ] Monitoring alerts configured
- [ ] On-call engineer identified

### Deployment Process
1. Code freeze (48 hours before release)
2. Final QA testing in staging
3. Create release branch
4. Deploy to production during maintenance window
5. Smoke tests (verify critical flows work)
6. Monitor for 1 hour post-deploy
7. Announce in #releases channel
8. Update status page

### Post-Release
- Monitor error rates and performance metrics (DataDog)
- Respond to any customer reports immediately
- Conduct post-mortem if issues occurred
- Archive release branch

---

## Incident Response

### Severity Levels

**SEV1 - Critical**: Complete outage, data loss, security breach
- Response: Immediate
- On-call: Paged
- Comms: Hourly updates to customers

**SEV2 - Major**: Significant feature degradation, affects many users
- Response: Within 1 hour
- On-call: Notified
- Comms: Updates every 4 hours

**SEV3 - Minor**: Limited impact, workaround available
- Response: Next business day
- On-call: Logged for next sprint

### Incident Response Steps
1. **Detect**: Alerts fired, customer reports, monitoring
2. **Triage**: Assess severity and impact
3. **Assemble**: Page on-call engineer, notify incident commander
4. **Communicate**: Update status page, notify stakeholders
5. **Mitigate**: Deploy fix or rollback
6. **Monitor**: Ensure stability
7. **Post-Mortem**: Root cause analysis, prevention measures

### Incident Slack Workflow
1. Create incident channel: #incident-2026-03-15
2. Assign roles: Incident Commander, Comms Lead, Tech Lead
3. Use PagerDuty for on-call escalation
4. Document timeline in channel
5. Update statuspage.apextech.com

### Post-Mortem Template
- **Incident Summary**: What happened?
- **Timeline**: Key events with timestamps
- **Root Cause**: Why did it happen?
- **Impact**: Users affected, revenue loss, duration
- **Resolution**: How was it fixed?
- **Action Items**: Prevent recurrence (assign owners)

**No Blame Culture**: Post-mortems focus on systems, not individuals.

---

## Company Calendar & Events

### 2026 Company Holidays
- January 1 - New Year's Day
- January 20 - MLK Jr. Day
- February 17 - Presidents' Day
- May 26 - Memorial Day
- July 3-4 - Independence Day (office closed both days)
- September 7 - Labor Day
- November 26-27 - Thanksgiving
- December 24 - Christmas Eve (half day)
- December 25 - Christmas Day
- December 31 - New Year's Eve (half day)

**Floating Holidays**: 2 per year (your choice, manager approval)

### Regular Company Events

**Monthly:**
- All-Hands Meeting (Last Friday, 4:00 PM PT)
- New Hire Welcome Lunch (First Wednesday)
- Product Demo Day (Third Thursday)

**Quarterly:**
- Hackathon (3 days, typically mid-quarter)
- Team Offsites (per department)
- Board Meeting (Exec team presents)

**Annually:**
- Company Kickoff (January, 2-day event)
- Summer Retreat (August, team-building)
- Holiday Party (December)
- Performance Review Cycles (June, December)

### Team Traditions
- **Donut Fridays**: Random coffee pairings
- **Demo Days**: Show off side projects
- **Lunch & Learns**: Brown bag sessions, weekly
- **ERG Events**: Various (Women in Tech, LGBTQ+ Allies, etc.)

---

## Frequently Asked Questions

**Q: How do I update my wiki page?**
A: Click "Edit", make changes, add edit summary, save. If you're a page owner, you can also archive outdated content.

**Q: What if I can't find something in the wiki?**
A: Use search (Cmd+K), ask in #ask-anything Slack channel, or contact the department owner listed on relevant pages.

**Q: How are sprint commitments decided?**
A: Team discusses capacity in sprint planning, considers velocity from past sprints, and commits to achievable goals collaboratively.

**Q: What's the process for urgent production fixes?**
A: Follow hotfix process—create hotfix branch from main, fix, test, deploy, then merge back to develop. See "Release Process" section.

**Q: Can I work on projects outside my team?**
A: Yes! Innovation Fridays and hackathons are great opportunities. For larger commitments, discuss with your manager.

**Q: How do I propose a process improvement?**
A: Post in #process-improvements Slack channel or bring up in team retros. Ops teams review suggestions monthly.

---

## Related Documents
- [Onboarding Guide](onboarding_guide.md) - New employee orientation
- [Employee Handbook](employee_handbook.md) - Company culture and values
- [IT Support Guide](it_support_guide.md) - Technical help resources
- [Security Policy](security_policy.md) - Security best practices

---

**Wiki Questions?**
Contact: wiki-admin@apextech.solutions
Slack: #wiki-feedback
