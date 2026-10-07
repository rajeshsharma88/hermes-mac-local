# Hermes Kanban + Agent Creation SOP

## Standard Operating Procedure for Creating Any AI Agent and Its Kanban Workflow

**Version:** 1.0\
**Purpose:** Create a repeatable, scalable process for building
specialist AI agents in Hermes and connecting them to Kanban workflows.\
**Audience:** Agency owners, AI operations managers, automation teams,
and anyone building multi-agent workflows in Hermes.

------------------------------------------------------------------------

# 1. Purpose of This SOP

This SOP explains how to:

1.  Create a Hermes agent/profile.
2.  Give the agent a clear role, name, and description.
3.  Configure the agent's behavior and operating instructions.
4.  Create or configure a Kanban board.
5.  Create a Triage task through the Hermes Web UI.
6.  Use Hermes Auto Orchestration to decompose a large objective.
7.  Assign work to specialist agents.
8.  Configure task workspace settings.
9.  Understand task dependencies.
10. Pass research, briefs, and files between agents.
11. Create quality-control and human-approval stages.
12. Build repeatable multi-agent workflows.

The goal is not merely to create an AI chatbot. The goal is to create an
**AI worker that can reliably perform a specific job inside a larger
operating system**.

------------------------------------------------------------------------

# 2. The Core Mental Model

Always remember these four concepts:

  Hermes Concept          Real-World Analogy
  ----------------------- -------------------------------------------
  Profile                 Employee
  Kanban Board            Department / Office
  Kanban Task             Job assigned to an employee
  Workspace               Employee's temporary or permanent desk
  Attachment / Artifact   Work document
  Dependency              "You cannot start until this is finished"
  Orchestrator            Operations Manager
  Reviewer                Quality-Control Manager

The architecture is:

``` text
YOU / HUMAN
    |
    v
BUSINESS OBJECTIVE
    |
    v
KANBAN BOARD
    |
    v
ORCHESTRATOR
    |
    +------------------+------------------+
    |                  |                  |
    v                  v                  v
RESEARCH AGENT    STRATEGY AGENT     PRODUCTION AGENT
    |                  |                  |
    +------------------+------------------+
                       |
                       v
                 REVIEW AGENT
                       |
              +--------+--------+
              |                 |
             PASS          CHANGES REQUIRED
              |                 |
              v                 +------> Production Agent
       HUMAN APPROVAL
              |
              v
           PUBLISH
```

------------------------------------------------------------------------

# 3. Before Creating an Agent

Do not start by asking:

> "What prompt should I give the AI?"

Start with:

> "What job should this AI own?"

Define these seven things first:

``` text
1. Agent Name
2. Business Role
3. Primary Objective
4. Inputs
5. Outputs
6. Boundaries
7. Success Criteria
```

Example:

``` text
Agent:
SMM Researcher

Role:
Social Media Research Specialist

Objective:
Produce reliable audience, competitor, platform and content research.

Inputs:
Client brief, brand information, target audience, previous campaign data.

Outputs:
Structured research document with sources and assumptions.

Boundaries:
Do not invent facts. Clearly separate verified facts from assumptions and gaps.

Success:
The strategy agent can use the research without needing to repeat the research.
```

------------------------------------------------------------------------

# 4. Agent Naming Standard

Use short, predictable, machine-friendly names.

## Recommended format

``` text
<department>-<function>
```

Examples:

``` text
smm-manager
smm-researcher
smm-copywriter
smm-creative
smm-reviewer

seo-researcher
seo-writer
seo-reviewer

ads-strategist
ads-copywriter
ads-analyst

crm-analyst
crm-reporting
crm-reviewer
```

## Naming rules

Use:

-   lowercase
-   hyphens
-   one clear function
-   no spaces
-   no unnecessary numbers

Avoid:

``` text
Super AI Marketing Expert 2026
BestAgent
Agent1
Marketing Genius
```

Prefer:

``` text
smm-copywriter
```

The name should immediately tell the orchestrator and the human operator
what the profile does.

------------------------------------------------------------------------

# 5. Profile Description Standard

The profile description is extremely important.

In an orchestrated Kanban system, the description helps communicate
**which type of work the profile is designed to handle**.

Use this structure:

``` text
[ROLE]

[PRIMARY RESPONSIBILITY]

[KEY RESPONSIBILITIES]

[EXPECTED OUTPUTS]

[BOUNDARIES]

[QUALITY STANDARD]
```

## Master Description Template

Copy and adapt this:

``` text
[ROLE TITLE] responsible for [PRIMARY PURPOSE].

Primary responsibility:
[Explain the single most important job this agent owns.]

Responsibilities:
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]
- [Responsibility 4]
- [Responsibility 5]

Inputs:
- [Input 1]
- [Input 2]
- [Input 3]

Outputs:
- [Deliverable 1]
- [Deliverable 2]
- [Deliverable 3]

The agent should:
- [Important operating behavior]
- [Important decision rule]
- [Important collaboration rule]

The agent must not:
- [Boundary 1]
- [Boundary 2]
- [Boundary 3]

Quality standard:
[Define what a good result looks like.]

When information is missing:
[Ask / mark as unknown / create a blocker instead of inventing information.]

When the task is complete:
[Create the required deliverable, attach it to the task when appropriate, and provide a concise completion summary.]
```

------------------------------------------------------------------------

# 6. Agent SOUL / Operating Prompt Structure

The profile description tells Hermes **what the agent is**.

The deeper profile instructions/SOUL should tell the agent **how to
behave**.

Use the following structure.

``` text
# ROLE

You are [ROLE] working inside [COMPANY / DEPARTMENT].

# MISSION

Your primary mission is to [MISSION].

# RESPONSIBILITIES

You own:

1. ...
2. ...
3. ...
4. ...

# INPUTS

You may receive:

- ...
- ...
- ...

Before starting, inspect all available task context, parent tasks, child results, comments, and relevant attachments.

# OUTPUTS

Your final deliverable must contain:

1. ...
2. ...
3. ...

Prefer a structured Markdown file for substantial deliverables.

# WORKING METHOD

Follow this sequence:

1. Understand the task.
2. Inspect the task context.
3. Inspect parent task information.
4. Inspect relevant child results.
5. Read available attachments.
6. Identify missing information.
7. Perform the work.
8. Validate your output.
9. Create the final artifact.
10. Attach the artifact when appropriate.
11. Summarize what was completed.

# FACTUAL ACCURACY

Never present assumptions as verified facts.

Use:

[V] Verified
[A] Assumption
[G] Gap / information required

When external research is required, provide sources.

# COLLABORATION

You are one specialist inside a multi-agent workflow.

Do not unnecessarily duplicate work already completed by another agent.

Use upstream outputs as inputs.

Create clean artifacts that downstream agents can consume.

# DEPENDENCIES

If required information is missing and work cannot continue safely:

1. Identify the missing information.
2. Explain why it is required.
3. Mark or request a blocker according to the Kanban workflow.
4. Do not invent the missing information.

# QUALITY CONTROL

Before completing the task, verify:

- The deliverable satisfies the task.
- Required inputs were considered.
- Facts and assumptions are distinguished.
- The output is complete.
- The format is usable by the next agent.
- No important requirement has been silently ignored.

# COMPLETION

When complete:

- Create the final deliverable.
- Attach it to the Kanban task when appropriate.
- Add a concise completion summary.
- Mention important assumptions or unresolved gaps.
```

------------------------------------------------------------------------

# 7. Example: SMM Researcher Profile

## Profile Name

``` text
smm-researcher
```

## Profile Description

``` text
Social media research specialist for a marketing agency.

Researches target audiences, customer pain points, competitors, social media trends, content formats, platform behavior, search trends, topics, content gaps and relevant market information.

Produces structured research that other agents can use to create social media strategies and content.

The agent should clearly distinguish verified facts from assumptions and should provide useful sources when external research is required.
```

## Recommended SOUL

``` text
# ROLE

You are the Social Media Research Specialist for a professional marketing agency.

# MISSION

Produce reliable, actionable research that helps strategy and content agents make better decisions.

# RESPONSIBILITIES

You own:

1. Audience research.
2. Competitor research.
3. Platform research.
4. Content trend research.
5. Content-gap identification.
6. Source collection.
7. Research documentation.

# INPUTS

Use:

- Client brief.
- Brand information.
- Target audience.
- Existing campaign information.
- Parent task context.
- Relevant attachments.
- Reliable external sources when research is required.

# OUTPUT

For substantial research tasks, create a structured Markdown research document.

Recommended structure:

1. Executive Summary
2. Brand Context
3. Target Audience
4. Competitor Analysis
5. Platform Trends
6. Content Opportunities
7. Content Gaps
8. Compliance / Risk Notes
9. Sources
10. Open Questions

# FACT TAGGING

Every important factual statement should be classified where practical:

[V] Verified
[A] Assumption
[G] Gap / needs confirmation

Never manufacture facts to fill a gap.

# QUALITY STANDARD

Research must be useful to the next agent.

Do not produce generic marketing advice when specific research is requested.

When competitors are analyzed, distinguish observed facts from your interpretation.

When trends are reported, include dates or time context where relevant.

# COMPLETION

Create the research artifact, attach it to the task, and summarize the major findings and unresolved gaps.
```

------------------------------------------------------------------------

# 8. Example: SMM Copywriter Profile

## Profile Name

``` text
smm-copywriter
```

## Profile Description

``` text
Senior social media copywriter specializing in platform-specific content.

Creates Instagram captions, Facebook posts, LinkedIn posts, hooks, CTAs, carousel copy, short-form video scripts, Reels scripts, promotional copy and educational social media content.

Adapts writing to the client's brand voice, target audience, platform and campaign objective.

Prioritizes strong hooks, clarity, human language, useful information and appropriate calls to action.
```

------------------------------------------------------------------------

# 9. Example: SMM Creative Strategist

## Profile Name

``` text
smm-creative
```

## Profile Description

``` text
Social media creative strategist responsible for turning content strategies into visual concepts.

Creates creative briefs for Instagram posts, carousels, Reels, short videos, thumbnails, social advertisements and other visual formats.

Defines the visual concept, opening hook, scene structure, text hierarchy, composition, visual storytelling and creative direction.

The agent should provide clear instructions that a graphic designer, video editor or image-generation system can execute.
```

------------------------------------------------------------------------

# 10. Example: SMM Reviewer

## Profile Name

``` text
smm-reviewer
```

## Profile Description

``` text
Senior social media quality-control specialist.

Reviews social media strategy and content for factual accuracy, clarity, grammar, brand consistency, audience relevance, platform suitability, hooks, CTAs, compliance and overall quality.

Identifies weaknesses and requests specific changes rather than simply approving poor-quality work.

The reviewer should act as the final quality gate before content reaches human approval.
```

------------------------------------------------------------------------

# 11. Example: SMM Manager / Orchestrator

## Profile Name

``` text
smm-manager
```

## Profile Description

``` text
Social Media Marketing Manager and AI agency orchestrator.

Responsible for understanding client objectives, creating social media strategies, breaking projects into smaller tasks, assigning work to specialized agents, coordinating dependencies, reviewing workflow progress, and ensuring final deliverables meet the client's business objectives.

The agent should delegate specialized work to Researcher, Copywriter, Creative Strategist, Analytics and Reviewer profiles instead of attempting every task itself.

Primary responsibilities:
- Understand client brief
- Define campaign objectives
- Create content strategy
- Break large projects into actionable tasks
- Assign tasks to appropriate specialist profiles
- Manage task dependencies
- Coordinate the Kanban workflow
- Review outputs
- Identify missing information
- Escalate important decisions for human approval
- Maintain brand consistency
- Prepare final client-ready deliverables
```

------------------------------------------------------------------------

# 12. Creating the Kanban Board in the Web UI

Open:

**Kanban → Board selector → New Board**

Create a board for the department or operating system.

## Recommended Board Name

``` text
Social Media Marketing Agency
```

## Board Description

``` text
AI-powered Social Media Marketing Agency workflow for planning, researching, creating, reviewing and managing social media campaigns and content for clients.

This board coordinates specialized AI profiles including Social Media Manager, Researcher, Copywriter, Creative Strategist and Reviewer.

All client social media projects should move through structured stages from research and strategy to content creation, quality review and human approval.
```

## Project Directory

For an initial setup:

``` text
Leave blank
```

Use a persistent project directory only when you deliberately want the
board to inherit a filesystem location for its tasks.

------------------------------------------------------------------------

# 13. Recommended Board Architecture

For a general-purpose agency:

``` text
Social Media Marketing Agency
│
├── Client Campaign
│   ├── Research
│   ├── Strategy
│   ├── Copy
│   ├── Creative
│   ├── Review
│   └── Approval
│
├── Client Campaign
│   ├── Research
│   ├── Strategy
│   └── ...
│
└── Reporting
```

Do not create a separate board for every tiny task.

Create boards around meaningful operating systems or departments.

------------------------------------------------------------------------

# 14. Creating a New Triage Task in the Web UI

When you click `+` in Triage, Hermes displays:

-   Title
-   Specifier
-   Priority
-   Skills
-   Workspace
-   Parent Task
-   Goal Mode

## Field-by-field SOP

### TITLE

Write the business objective in one sentence.

Good:

``` text
Create 7-Day Social Media Content Plan for Aarogya India
```

Bad:

``` text
Do marketing
```

Good titles describe the outcome.

------------------------------------------------------------------------

### SPECIFIER

The UI says:

``` text
SPECIFIER
(BLANK = DISPATCHER PICKS)
```

For Auto Orchestration:

``` text
Leave blank
```

unless you deliberately want a particular profile to specify the task.

------------------------------------------------------------------------

### PRIORITY

Start with:

``` text
0
```

Only introduce a priority system when your team has a clear operational
definition for it.

------------------------------------------------------------------------

### SKILLS

This is optional.

Leave blank initially unless the task specifically requires known Hermes
skills.

Do not invent skill names.

Use only skills that actually exist in your Hermes environment.

------------------------------------------------------------------------

### WORKSPACE

For experimentation:

``` text
Temporary - deleted on completion
```

is appropriate.

Use a persistent workspace when the task needs durable working files.

------------------------------------------------------------------------

### PARENT TASK

For a top-level campaign:

``` text
-- no parent --
```

For a child task:

select the appropriate parent.

This creates dependency relationships.

------------------------------------------------------------------------

### GOAL MODE

Use Goal Mode when the task is an outcome that should continue until its
acceptance criteria are met.

Examples:

``` text
Research 20 competitors and produce a verified report.
```

``` text
Create and validate a complete campaign brief.
```

For a tiny one-step action, Goal Mode may not be necessary.

------------------------------------------------------------------------

# 15. The Correct First Task Pattern

For a new campaign, start with a high-level Triage objective.

Example:

``` text
Create 7-Day Social Media Content Plan for Aarogya India
```

Recommended initial settings:

``` text
Title:
Create 7-Day Social Media Content Plan for Aarogya India

Specifier:
Blank

Priority:
0

Skills:
Blank

Workspace:
Temporary - deleted on completion

Parent:
-- no parent --

Goal Mode:
Enabled
```

Then click:

**Create**

------------------------------------------------------------------------

# 16. Auto Orchestration

When:

``` text
Orchestration: Auto
```

is enabled, Hermes can take the high-level objective and decompose it
into smaller tasks.

A typical SMM decomposition might become:

``` text
MASTER
Create 7-Day Social Media Content Plan
│
├── Research brand, audience and trends
├── Create content strategy
├── Write social media copy
├── Create visual creative briefs
└── Review and quality-check content
```

This is preferable to manually creating every task when the workflow is
repeatable.

------------------------------------------------------------------------

# 17. How Hermes Routes Tasks to Agents

The orchestrator can use the profile roster and profile descriptions to
determine which specialist is appropriate.

Example:

``` text
Research task
        ↓
smm-researcher

Strategy task
        ↓
smm-manager

Copy task
        ↓
smm-copywriter

Creative task
        ↓
smm-creative

Review task
        ↓
smm-reviewer
```

Therefore:

**Profile descriptions should be specific enough to distinguish one
agent from another.**

Do not make every profile description say:

``` text
Expert AI agent who can do marketing tasks.
```

That gives the orchestrator very little useful routing information.

------------------------------------------------------------------------

# 18. Dependency Design

Use dependencies when one task requires another task's output.

Example:

``` text
Research
   ↓
Strategy
   ↓
Copy
   ↓
Review
```

For parallel work:

``` text
              Strategy
                 │
          ┌──────┴──────┐
          ↓             ↓
        Copy         Creative
          │             │
          └──────┬──────┘
                 ↓
               Review
```

This is better than forcing every task to happen sequentially.

Use parallel execution whenever the tasks have no dependency on one
another.

------------------------------------------------------------------------

# 19. How Information Passes Between Agents

A professional Hermes workflow should use **artifacts**, not giant chat
messages.

Recommended pattern:

``` text
Research Agent
     ↓
aarogya_india_research.md
     ↓
Strategy Agent
     ↓
aarogya_india_strategy.md
     ↓
Copy + Creative Agents
     ↓
copy.md / creative_briefs.md
     ↓
Reviewer
```

This creates a clean information pipeline.

------------------------------------------------------------------------

# 20. Artifact Naming Standard

Use:

``` text
<client>_<deliverable>.md
```

Examples:

``` text
aarogya_india_research.md
aarogya_india_strategy.md
aarogya_india_copy.md
aarogya_india_creative_briefs.md
aarogya_india_review.md
```

For split deliverables:

``` text
aarogya_india_days1_3_copy.md
aarogya_india_days4_7_copy.md
```

Avoid:

``` text
final.md
new.md
final-final.md
output2.md
test.md
```

Clear filenames make multi-agent workflows much easier to understand.

------------------------------------------------------------------------

# 21. Temporary vs Persistent Workspace

## Temporary Workspace

Use when:

-   Work is disposable.
-   The final result will be attached to the task.
-   The agent only needs scratch space.
-   You are testing an agent.

Example:

``` text
Temporary - deleted on completion
```

## Persistent Workspace

Use when:

-   Several tasks need to share a project folder.
-   Files must remain available between tasks.
-   You are maintaining a long-running client project.
-   Code, assets or reports must persist.

Recommended agency architecture:

``` text
Client/
    Research/
    Strategy/
    Content/
    Creative/
    Reports/
```

Do not assume that a temporary workspace is permanent storage.

------------------------------------------------------------------------

# 22. Task Lifecycle

Understand the normal lifecycle:

``` text
TRIAGE
  ↓
TODO
  ↓
READY
  ↓
IN PROGRESS
  ↓
REVIEW
  ↓
DONE
```

Potential exception:

``` text
IN PROGRESS
     ↓
BLOCKED
     ↓
Human provides information
     ↓
READY
     ↓
IN PROGRESS
```

Meaning:

### Triage

Rough idea.

### Todo

Defined work waiting for dependencies or assignment.

### Ready

Dependencies are satisfied and the task can be dispatched.

### In Progress

A worker has claimed the task.

### Blocked

The worker needs human input or another dependency.

### Review

Implementation is complete but requires review.

### Done

Task completed.

------------------------------------------------------------------------

# 23. What to Do When an Agent Gets Blocked

Never encourage an agent to invent missing information.

Example:

``` text
BLOCKED

Missing:
Current product price

Why required:
The CTA and offer cannot be finalized without a verified price.

Required action:
Provide current price and offer.
```

Once the information is available, unblock the task.

This is much safer than letting an AI guess.

------------------------------------------------------------------------

# 24. Reviewer Agent SOP

Every production workflow should eventually have a reviewer.

The reviewer should inspect:

``` text
1. Original brief
2. Research
3. Strategy
4. Produced deliverable
5. Brand rules
6. Compliance requirements
7. Required format
```

Use a structured result:

``` text
STATUS:
PASS / REQUEST CHANGES

BLOCKERS:
-

IMPORTANT:
-

NICE TO HAVE:
-

REQUIRED CHANGES:
1.
2.
3.

REVIEW SUMMARY:
```

Avoid a reviewer that only says:

``` text
Looks good.
```

------------------------------------------------------------------------

# 25. Human Approval Gate

For real client work, use a human approval stage before publishing.

Recommended:

``` text
Research
   ↓
Strategy
   ↓
Production
   ↓
Review
   ↓
Human Approval
   ↓
Publish
```

Do not automatically publish client-facing content until the workflow
has been thoroughly tested.

------------------------------------------------------------------------

# 26. Agent Creation Checklist

Before activating an agent, verify:

### Identity

-   [ ] Clear profile name
-   [ ] Clear role
-   [ ] Specific description
-   [ ] No overlapping role confusion

### Inputs

-   [ ] Required inputs documented
-   [ ] Parent task context considered
-   [ ] Attachments considered

### Outputs

-   [ ] Exact deliverable defined
-   [ ] File format defined
-   [ ] Naming convention defined

### Behavior

-   [ ] Fact vs assumption rule
-   [ ] Missing-information rule
-   [ ] Quality standard
-   [ ] Collaboration rule

### Safety / Quality

-   [ ] No unsupported claims
-   [ ] No invented facts
-   [ ] Appropriate review stage
-   [ ] Human approval where necessary

### Kanban

-   [ ] Board exists
-   [ ] Orchestration mode understood
-   [ ] Dependencies defined
-   [ ] Workspace selected
-   [ ] Assignee/profile routing understood

------------------------------------------------------------------------

# 27. Agent Creation Template

Use this template whenever you create a new agent.

``` text
==================================================
AGENT CREATION SPECIFICATION
==================================================

Agent Name:
<department>-<function>

Business Role:
<one sentence>

Primary Objective:
<what this agent exists to accomplish>

Profile Description:
<paste structured description>

Primary Inputs:
- 
- 
- 

Primary Outputs:
- 
- 
- 

Responsibilities:
1.
2.
3.
4.
5.

Must Not:
1.
2.
3.

Fact Handling:
[V] Verified
[A] Assumption
[G] Gap

Missing Information:
<what the agent should do>

Artifact:
<expected file type>

Filename:
<standard filename>

Quality Criteria:
1.
2.
3.
4.

Dependencies:
<what must be completed first>

Downstream Users:
<which agents consume this output>

Reviewer:
<review profile>

Human Approval:
Yes / No

Workspace:
Temporary / Persistent

Kanban Board:
<board name>
==================================================
```

------------------------------------------------------------------------

# 28. Example: Creating a New SEO Agent

Suppose you want an SEO Researcher.

## Name

``` text
seo-researcher
```

## Description

``` text
SEO research specialist responsible for keyword research, search-intent analysis, competitor SERP analysis, topic clustering and content opportunity identification.

Produces structured research that SEO strategists and writers can use to create search-focused content.

Distinguishes verified search data from assumptions and clearly documents sources, methodology and unresolved gaps.
```

## Workflow

``` text
Client Brief
     ↓
SEO Researcher
     ↓
keyword_research.md
     ↓
SEO Strategist
     ↓
content_plan.md
     ↓
SEO Writer
     ↓
article.md
     ↓
SEO Reviewer
```

The exact same SOP applies.

------------------------------------------------------------------------

# 29. Example: Creating a Data Analyst Agent

## Name

``` text
crm-analyst
```

## Description

``` text
CRM and marketing data analyst responsible for analyzing lead, sales, campaign and agent-performance data.

Identifies campaign performance, cost per lead, cost per sale, revenue, ROAS, city-level trends, agent performance, lead aging, follow-up compliance, funnel drop-offs and repeat-customer patterns.

Produces structured analytical reports with calculations, assumptions, anomalies and actionable findings.
```

Workflow:

``` text
CSV / Excel
    ↓
CRM Analyst
    ↓
analysis.md
    ↓
Marketing Manager
    ↓
recommendations.md
    ↓
Human Approval
```

------------------------------------------------------------------------

# 30. Golden Rules for Building Hermes Agents

## Rule 1: One agent, one primary job

Bad:

``` text
marketing-agent
```

Better:

``` text
smm-researcher
smm-copywriter
smm-reviewer
```

------------------------------------------------------------------------

## Rule 2: Make outputs reusable

Bad:

``` text
Tell the manager what you found.
```

Better:

``` text
Create a structured research artifact that downstream agents can consume.
```

------------------------------------------------------------------------

## Rule 3: Never hide uncertainty

Use:

``` text
[V] Verified
[A] Assumption
[G] Gap
```

------------------------------------------------------------------------

## Rule 4: Let agents specialize

Don't build one enormous prompt containing every possible marketing
function.

Use a team.

------------------------------------------------------------------------

## Rule 5: Use dependencies deliberately

Sequential:

``` text
Research → Strategy
```

Parallel:

``` text
Strategy → Copy
        → Creative
```

Then:

``` text
Copy + Creative → Review
```

------------------------------------------------------------------------

## Rule 6: Don't confuse Kanban with chat

Chat asks:

> "What do you think?"

Kanban asks:

> "Own this job, produce this artifact, report completion, and make it
> available to the next worker."

------------------------------------------------------------------------

## Rule 7: Human approval should remain at important decision points

Especially for:

-   Client-facing content
-   Advertising claims
-   Healthcare content
-   Financial claims
-   Legal/compliance-sensitive material
-   Publishing
-   Irreversible external actions

------------------------------------------------------------------------

# 31. Recommended Agency Architecture

For a mature Social Media Marketing Agency:

``` text
                         HUMAN / CEO
                              |
                              v
                       SMM ORCHESTRATOR
                              |
       +----------------------+----------------------+
       |                      |                      |
       v                      v                      v
  RESEARCH                 STRATEGY              ANALYTICS
       |                      |                      |
       +----------------------+----------------------+
                              |
                 +------------+------------+
                 |                         |
                 v                         v
             COPYWRITER                CREATIVE
                 |                         |
                 +------------+------------+
                              |
                              v
                           REVIEWER
                              |
                       +------+------+
                       |             |
                      PASS       CHANGES
                       |             |
                       v             |
                HUMAN APPROVAL      |
                       |             |
                       v             |
                    PUBLISH <--------+
                       |
                       v
                   ANALYTICS
                       |
                       v
                  OPTIMIZATION
```

This is the architecture to work toward.

Do not build everything at once.

Start with:

``` text
Manager
Researcher
Copywriter
Creative
Reviewer
```

Then add specialists only when the workflow demonstrates a real need.

------------------------------------------------------------------------

# 32. Final Pre-Launch Test

Before putting an agent into production, run one controlled test.

Give it:

``` text
One clear task
One known input
One expected output
One quality standard
```

Verify:

``` text
1. Agent understands the task.
2. Agent accesses required context.
3. Agent does not invent missing information.
4. Agent produces the correct artifact.
5. Artifact is attached or stored correctly.
6. Downstream agent can consume it.
7. Reviewer can evaluate it.
8. Human can intervene.
9. Task reaches Done correctly.
```

Only after this works should you increase task complexity.

------------------------------------------------------------------------

# 33. The Complete Operating Pattern

The reusable Hermes pattern is:

``` text
DEFINE ROLE
     ↓
CREATE PROFILE
     ↓
WRITE DESCRIPTION
     ↓
WRITE SOUL / OPERATING RULES
     ↓
ENABLE REQUIRED TOOLS / SKILLS
     ↓
CREATE / SELECT KANBAN BOARD
     ↓
DEFINE BOARD PURPOSE
     ↓
CREATE TRIAGE TASK
     ↓
SPECIFY OR DECOMPOSE
     ↓
ASSIGN SPECIALISTS
     ↓
DEFINE DEPENDENCIES
     ↓
SELECT WORKSPACE
     ↓
RUN AGENTS
     ↓
CREATE ARTIFACTS
     ↓
PASS ARTIFACTS DOWNSTREAM
     ↓
REVIEW
     ↓
REQUEST CHANGES OR PASS
     ↓
HUMAN APPROVAL
     ↓
COMPLETE / PUBLISH
```

------------------------------------------------------------------------

# 34. Quick Reference

## Profile

``` text
Name:
<department>-<function>

Description:
Specific role + responsibilities + outputs + boundaries
```

## Board

``` text
Name:
<Department / Operating System>

Description:
What the board manages

Project Directory:
Blank initially unless persistent filesystem storage is required
```

## Triage

``` text
Title:
Clear business outcome

Specifier:
Blank for dispatcher selection

Priority:
0 initially

Skills:
Blank unless a known skill is required

Workspace:
Temporary for experiments

Parent:
No parent for top-level task

Goal Mode:
Enable for outcome-oriented tasks
```

## Workflow

``` text
Triage
  ↓
Auto Decompose
  ↓
Specialist Tasks
  ↓
Dependencies
  ↓
Artifacts
  ↓
Review
  ↓
Human Approval
  ↓
Done
```

------------------------------------------------------------------------

# 35. The Most Important Principle

**Do not build AI agents as isolated chatbots.**

Build them as **workers inside a process**.

A good agent knows:

``` text
What is my job?
What information do I have?
What information am I missing?
What should I produce?
Who will use my output?
How do I prove the work is complete?
```

When every agent answers those six questions clearly, Hermes Kanban
becomes much more powerful and predictable.

------------------------------------------------------------------------

## End of SOP
