---
name: Hermes Agent & Kanban Builder
description: Create, configure, and troubleshoot Hermes AI profiles and Kanban workflows using a repeatable agent, workspace, dependency, artifact, and review process.
---

# Hermes Agent & Kanban Builder

## Purpose

Use this skill whenever the user wants to create, configure, improve, troubleshoot, or standardize an AI agent/profile or Kanban workflow in Hermes.

The goal is to build **specialized AI workers inside a durable workflow**, not generic chatbots.

This skill applies to:
- Creating a new Hermes profile/agent
- Writing profile names and descriptions
- Designing profile operating instructions / SOUL
- Creating and configuring Hermes Kanban boards
- Creating Triage tasks
- Using Auto Orchestration and decomposition
- Designing dependencies and parallel work
- Choosing temporary vs persistent workspaces
- Passing artifacts between agents
- Creating reviewer/QA stages
- Designing human-approval gates
- Troubleshooting agent routing, task status, or artifact flow

For the complete source SOP, consult:
`resources/HERMES_KANBAN_SOP_REFERENCE.md`

---

# 1. Core Mental Model

Always reason about Hermes using this model:

| Hermes | Real-world analogy |
|---|---|
| Profile | Employee |
| Kanban Board | Department / office |
| Kanban Task | Job |
| Workspace | Employee's desk |
| Attachment / Artifact | Work document |
| Dependency | Prerequisite |
| Orchestrator | Operations manager |
| Reviewer | Quality-control manager |

The preferred architecture is:

```text
HUMAN / BUSINESS OBJECTIVE
        |
        v
KANBAN BOARD
        |
        v
ORCHESTRATOR
        |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
    RESEARCH            STRATEGY           PRODUCTION
        |                   |                   |
        +-------------------+-------------------+
                            |
                            v
                         REVIEW
                            |
                    +-------+-------+
                    |               |
                   PASS         CHANGES
                    |               |
                    v               +----> Production
             HUMAN APPROVAL
                    |
                    v
                  DONE
```

---

# 2. Agent Design Rule

Before writing a prompt, define:

1. Agent name
2. Business role
3. Primary objective
4. Inputs
5. Outputs
6. Boundaries
7. Success criteria
8. Upstream dependencies
9. Downstream consumers
10. Reviewer

Do not create vague "do everything" agents when the workflow can be split into specialists.

Prefer:

```text
smm-researcher
smm-copywriter
smm-creative
smm-reviewer
```

over:

```text
marketing-agent
```

---

# 3. Agent Naming Standard

Use:

```text
<department>-<function>
```

Examples:

```text
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

Rules:
- lowercase
- hyphens
- one clear primary function
- no spaces
- no unnecessary numbers
- name should make routing intent obvious

---

# 4. Profile Description Standard

A profile description should help both humans and orchestration logic understand the agent's specialization.

Use this structure:

```text
[ROLE TITLE] responsible for [PRIMARY PURPOSE].

Primary responsibility:
[Single most important job.]

Responsibilities:
- ...
- ...
- ...

Inputs:
- ...
- ...

Outputs:
- ...
- ...

The agent should:
- ...
- ...

The agent must not:
- ...
- ...

Quality standard:
[Definition of a good result.]

When information is missing:
[Block / ask / mark as unknown. Never invent it.]
```

The description should be specific enough to distinguish the agent from neighboring profiles.

Avoid:

```text
Expert AI agent who can do marketing tasks.
```

Prefer:

```text
Senior social media copywriter specializing in platform-specific captions,
hooks, CTAs, carousel copy, short-form scripts, and brand-aligned social content.
```

---

# 5. Profile Operating Prompt / SOUL

When a deeper profile instruction is needed, use this structure:

```text
# ROLE

You are [ROLE] working inside [COMPANY / DEPARTMENT].

# MISSION

Your primary mission is to [MISSION].

# RESPONSIBILITIES

You own:
1. ...
2. ...
3. ...

# INPUTS

Use:
- Parent task context
- Relevant child results
- Comments
- Attachments
- Client brief
- Approved brand information
- Reliable external sources when required

Before starting, inspect all relevant task context and available artifacts.

# OUTPUTS

Your final deliverable must contain:
1. ...
2. ...
3. ...

For substantial work, create a structured Markdown artifact.

# WORKING METHOD

1. Understand the task.
2. Inspect parent and child context.
3. Read relevant attachments.
4. Identify missing information.
5. Perform the work.
6. Validate the result.
7. Create the final artifact.
8. Attach the artifact when appropriate.
9. Summarize completion and unresolved gaps.

# FACTUAL ACCURACY

Never present assumptions as verified facts.

Use:
[V] Verified
[A] Assumption
[G] Gap / needs confirmation

# COLLABORATION

Do not unnecessarily duplicate upstream work.

Consume available upstream artifacts.

Create clean artifacts that downstream agents can use.

# MISSING INFORMATION

If required information is missing:
- identify it
- explain why it matters
- block or request clarification according to the workflow
- never invent the missing information

# QUALITY CONTROL

Before completion verify:
- task requirements are satisfied
- required inputs were considered
- facts and assumptions are distinguished
- output is complete
- output is usable by the next agent
- no important requirement was silently ignored

# COMPLETION

Create the final artifact, attach it when appropriate, and provide a concise completion summary.
```

---

# 6. Creating a Hermes Agent

When guiding a user through the Web UI:

1. Open **Profiles**.
2. Choose **Create Profile**.
3. Enter the standardized profile name.
4. Add the specialized profile description.
5. Configure the model.
6. Configure required tools/skills.
7. Add deeper operating instructions/SOUL if the UI supports them.
8. Save the profile.
9. Verify the profile exists before using it in Kanban routing.

If the user is using a hosted/custom Hermes UI, do not assume exact button names. Use the UI labels visible in their screenshots.

If a profile must orchestrate Kanban work, ensure the profile has the required Kanban tool access in the user's Hermes setup.

---

# 7. Creating the Kanban Board

For a department-level operating system:

## Example

Display name:

```text
Social Media Marketing Agency
```

Description:

```text
AI-powered Social Media Marketing Agency workflow for planning,
researching, creating, reviewing and managing social media campaigns
and content for clients.

This board coordinates specialized AI profiles including Social Media
Manager, Researcher, Copywriter, Creative Strategist and Reviewer.

All client social media projects should move through structured stages
from research and strategy to content creation, quality review and human approval.
```

Project directory:

- Leave blank initially unless persistent filesystem storage is intentionally required.
- Do not treat a temporary workspace as permanent storage.

---

# 8. Creating a Triage Task

When the user opens **New Task — Triage**, explain each field.

## Title

Use a clear business outcome.

Good:

```text
Create 7-Day Social Media Content Plan for Aarogya India
```

Bad:

```text
Do marketing
```

## Specifier

If the UI says:

```text
BLANK = DISPATCHER PICKS
```

leave it blank for automatic selection unless a specific profile must specify the task.

## Priority

Use:

```text
0
```

unless the user has defined a meaningful priority system.

## Skills

Leave blank unless the user has confirmed the required skill names exist.

Never invent skill names.

## Workspace

For experiments:

```text
Temporary - deleted on completion
```

For long-running projects or durable shared files, deliberately use a persistent workspace supported by the user's Hermes setup.

## Parent Task

For a top-level project:

```text
-- no parent --
```

For a child task, select its actual parent.

## Goal Mode

Use Goal Mode for outcome-oriented tasks where the worker should continue toward defined acceptance criteria.

Do not assume Goal Mode is the same as orchestration:
- Goal Mode = finish the objective reliably.
- Orchestration = break work into specialist tasks.

---

# 9. Auto Orchestration

When appropriate, use:

```text
Orchestration: Auto
```

A high-level task such as:

```text
Create 7-Day Social Media Content Plan
```

may be decomposed into:

```text
Research
Strategy
Copy
Creative
Review
```

The decomposer should use specialist profile descriptions to route work.

If the user wants predictable production routing at scale, inspect and refine profile descriptions and orchestration settings rather than manually moving cards.

---

# 10. Dependency Design

Use dependencies when work genuinely depends on another task.

Sequential:

```text
Research
   ↓
Strategy
   ↓
Copy
   ↓
Review
```

Parallel:

```text
              Strategy
                 |
          +------+------+
          |             |
          v             v
        Copy         Creative
          |             |
          +------+------+
                 |
                 v
               Review
```

Prefer parallel execution when tasks do not depend on each other.

Do not create unnecessary serial bottlenecks.

---

# 11. Artifact-First Information Passing

For substantial work, prefer artifacts over giant chat responses.

Recommended pattern:

```text
Research Agent
      |
      v
research.md
      |
      v
Strategy Agent
      |
      v
strategy.md
      |
      +------------------+
      |                  |
      v                  v
Copywriter           Creative
      |                  |
      +--------+---------+
               |
               v
            Reviewer
```

Recommended filenames:

```text
<client>_<deliverable>.md
```

Examples:

```text
aarogya_india_research.md
aarogya_india_strategy.md
aarogya_india_copy.md
aarogya_india_creative_briefs.md
aarogya_india_review.md
```

For split outputs:

```text
aarogya_india_days1_3_copy.md
aarogya_india_days4_7_copy.md
```

Avoid vague filenames such as:

```text
final.md
new.md
output2.md
test.md
```

---

# 12. Workspace Strategy

## Temporary workspace

Use for:
- experiments
- disposable scratch work
- tasks whose final artifacts are attached to the Kanban record
- short-lived processing

## Persistent workspace

Use when:
- multiple tasks need shared durable files
- a client project must persist across tasks
- code/assets/reports need to remain available
- the workflow is long-running

Do not rely on a temporary workspace as the permanent source of truth.

---

# 13. Reviewer Design

Production workflows should normally include a reviewer.

The reviewer should inspect:

1. Original brief
2. Research
3. Strategy
4. Produced deliverable
5. Brand rules
6. Compliance requirements
7. Required format

Use structured review output:

```text
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

Avoid reviewers that only return:

```text
Looks good.
```

A useful reviewer identifies concrete issues and gives actionable corrections.

---

# 14. Human Approval

For client-facing or high-impact work, use:

```text
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

Keep human approval before:
- client-facing publication
- advertising claims
- healthcare claims
- financial claims
- legal/compliance-sensitive content
- irreversible external actions

---

# 15. Blocker Protocol

If an agent cannot safely continue:

```text
BLOCKED

Missing:
[Specific information]

Why required:
[Reason]

Required action:
[What the human or upstream agent must provide]
```

Never fill critical gaps with invented facts.

---

# 16. Quality and Reliability Rules

Every agent should follow these principles:

### One agent, one primary job
Avoid giant all-purpose agents.

### Make outputs reusable
Produce artifacts downstream agents can consume.

### Never hide uncertainty
Use `[V]`, `[A]`, `[G]` where appropriate.

### Use dependencies deliberately
Only block work when there is a real dependency.

### Verify before completion
A completed task should contain evidence of the requested deliverable.

### Preserve human control
Keep human approval at important decision points.

### Avoid unnecessary duplication
Read upstream outputs before repeating research.

---

# 17. Agent Creation Checklist

Before production, verify:

## Identity
- [ ] Clear profile name
- [ ] Clear role
- [ ] Specific description
- [ ] No overlap with neighboring profiles

## Inputs
- [ ] Required inputs documented
- [ ] Parent context considered
- [ ] Attachments considered

## Outputs
- [ ] Exact deliverable defined
- [ ] Format defined
- [ ] Filename convention defined

## Behavior
- [ ] Fact vs assumption rule
- [ ] Missing-information rule
- [ ] Quality standard
- [ ] Collaboration rule

## Kanban
- [ ] Board exists
- [ ] Orchestration mode understood
- [ ] Dependencies defined
- [ ] Workspace selected
- [ ] Routing is understood

## Quality
- [ ] Reviewer defined
- [ ] Human approval defined where necessary
- [ ] No unsupported claims
- [ ] No invented facts

---

# 18. Reusable Agent Specification

When asked to design any new Hermes agent, use:

```text
AGENT CREATION SPECIFICATION

Agent Name:
<department>-<function>

Business Role:
<one sentence>

Primary Objective:
<what this agent exists to accomplish>

Profile Description:
<structured description>

Primary Inputs:
- ...
- ...

Primary Outputs:
- ...
- ...

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
```

---

# 19. Example: Social Media Marketing Agency

A strong initial roster is:

```text
smm-manager
smm-researcher
smm-copywriter
smm-creative
smm-reviewer
```

Workflow:

```text
                    SMM MANAGER
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
      RESEARCH        STRATEGY       ANALYTICS
          |              |
          +--------------+
                 |
        +--------+--------+
        |                 |
        v                 v
    COPYWRITER         CREATIVE
        |                 |
        +--------+--------+
                 |
                 v
              REVIEWER
                 |
           +-----+-----+
           |           |
          PASS       CHANGES
           |           |
           v           +----> Production
      HUMAN APPROVAL
           |
           v
        PUBLISH
```

Start small. Add agents only when the workflow demonstrates a real need.

---

# 20. Troubleshooting Guide

## Task remains in Ready

Check:
1. Does the task have a valid assignee?
2. Are dependencies satisfied?
3. Does the assigned profile exist?
4. Is the dispatcher running?
5. Is orchestration configured as intended?

Do not manually force completion just to move the card.

## Agent is not receiving the expected context

Check:
1. Parent task relationship.
2. Child task relationship.
3. Attachments.
4. Artifact filenames.
5. Workspace.
6. Whether the worker actually inspected `kanban_show` or relevant task context.

## Agent invents missing information

Strengthen:
- Missing-information rules.
- `[V]/[A]/[G]` tagging.
- Blocker behavior.
- Reviewer checks.

## Wrong agent receives a task

Improve:
- Profile name.
- Profile description.
- Orchestration settings.
- Task specificity.

Avoid overlapping descriptions such as multiple profiles all claiming to be "marketing experts."

---

# 21. Standard End-to-End Procedure

When asked to create a new Hermes agent and workflow:

```text
1. Define the business job.
2. Identify the agent's primary responsibility.
3. Choose a machine-friendly name.
4. Write a routing-friendly profile description.
5. Write operating instructions/SOUL.
6. Configure tools/skills.
7. Verify the profile exists.
8. Create/select the appropriate Kanban board.
9. Define board purpose.
10. Create a high-level Triage task.
11. Leave Specifier blank when dispatcher selection is desired.
12. Choose workspace intentionally.
13. Set parent only when appropriate.
14. Enable Goal Mode for outcome-oriented tasks.
15. Use Auto Orchestration when appropriate.
16. Decompose into specialist tasks.
17. Verify assignments and dependencies.
18. Run the workflow.
19. Inspect artifacts and task history.
20. Review the result.
21. Route changes back to production if needed.
22. Require human approval where appropriate.
23. Mark the workflow complete.
24. Document the working pattern for reuse.
```

---

# 22. Important Operating Principle

Do not build AI agents as isolated chatbots.

Build them as **workers inside a process**.

Every agent should be able to answer:

```text
What is my job?
What information do I have?
What information am I missing?
What should I produce?
Who will use my output?
How do I prove the work is complete?
```

If those questions are clear, the agent is ready for a serious Hermes workflow.

---

# 23. Example Prompts for Using This Skill

When this skill is enabled, it should help with requests such as:

```text
Create a Hermes agent for SEO research.
```

```text
Create a Meta Ads specialist for my Hermes SMM agency.
```

```text
Design a Kanban workflow for a YouTube production team.
```

```text
What profile description should I use for a CRM analyst?
```

```text
My Hermes task is stuck in Ready. Diagnose it.
```

```text
Build a reviewer agent that sends copy back for revision.
```

```text
Create a multi-agent workflow for a client campaign.
```

```text
Tell me which Hermes task should be parent and which should be child.
```

When responding to these requests, prefer the concrete Web UI fields visible in the user's Hermes installation. Do not invent UI controls that the user has not shown.

---

# 24. Reference Material

For the full expanded SOP, examples, and detailed explanations, read:

`resources/HERMES_KANBAN_SOP_REFERENCE.md`

Use the reference when:
- the user needs deeper explanation
- an edge case is encountered
- a field needs detailed interpretation
- the user wants a complete SOP rather than a quick setup
