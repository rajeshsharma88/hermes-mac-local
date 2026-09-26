---
name: coordinator-intake
description: Use when interviewing the owner before briefing specialists.
---

# Coordinator Intake — the class-level procedure

A user asks you to bootstrap a coordinator agent over a fleet of specialist sub-agents. Before you can delegate anything useful, you need to know the business, the audience, the brand voice, the current ops reality, the tools, and the constraints. This skill is the interview procedure that gathers all of it without dragging the user through an interrogation.

## When this skill applies
- Owner defines a coordinator persona (Atlas/COS/chief-of-staff style) and asks you to fill gaps before delegating.
- Owner explicitly asks you to interview them so you can brief specialist agents.
- You sense you don't yet have enough context to delegate meaningfully to a named specialist role.

Does NOT apply: single-shot task intake ("do X for me"), already-complete persona where the user only wants execution, or specialist-agent work once briefed.

## Question format — hard rules

1. **One question at a time.** Wait for the answer before asking the next. The user will set this explicitly; if not, prefer it anyway — parallel intake feels like an interrogation.
2. **Prefer 3-4 short options over open-ended.** A `clarify` with choices always yields a clean pick. A `clarify` with a free-text answer is fragile on Telegram.
3. **Never rely on free-text answers in `clarify`.** The `clarify` answer box has failed silently on Telegram for this user multiple times — the `user_response` comes back empty even after the user picks a free-text option. If you need a specific value (a name, an email, a URL), give the user explicit short options ("A) type it in a plain message / B) use option X") OR ask them to send it as a plain message. Do NOT ask for a name and hope it comes through.
4. **Concrete, not abstract.** "₹5L+/mo Meta spend" > "current ad spend level". Give ranges the user can pick from.
5. **Sequence has an order** — see below. Don't jump to voice/tone before you know what's actually being sold.
6. **Aim for ~10-14 questions total.** Enough to brief four specialists. More is padding; less is a gap.

## Intake sequence (order matters)

Each step's answer often changes what later questions make sense to ask:

1. **Business structure** — is the primary account they named their own or a client? Sets scope of everything that follows.
2. **Product / offer** — single hero vs broad catalogue; which SKUs actually drive revenue.
3. **Primary audience** — demo, geography, decision-maker role. Different hero SKU lines skew very differently.
4. **Language + voice** — regional-language mix, and brand tone (founder-warm / expert-formal / punchy-performance / mixed).
5. **Current spend & revenue order of magnitude** — sizes the playbooks, not precise numbers.
6. **Ops reality check** — current response times, current conversion rates, current confirmation rates. Look for the wound the system is meant to fix.
7. **Tools + infra in production vs planned** — don't brief DEV to build what's already running.
8. **Team size** — solo vs hires, dictates how much can be automated vs briefed.
9. **Own brand / positioning** — separate from client brands; SCRIBE needs this to brief agency-facing work.
10. **Constraints / non-negotiables** — only if the earlier answers left a real gap.

## Splitting into specialist briefs

Once intake is done, map what you learned:
- **SCOUT (research)** ← product line, hero SKUs, audience, geography
- **SCRIBE (writing)** ← voice, language mix, brand positioning (own agency + each client)
- **REACH (marketing/growth)** ← spend, revenue, audience, ops metrics, conversion baseline
- **DEV (engineering)** ← tools in prod, infrastructure map, current pain points

Do NOT dump the full intake at every specialist — each gets only what they need to do their first pass well.

## Pitfalls

- Asking "what's your budget?" or "what's your brand voice?" with no options — user has to compose an answer from scratch every time, and often gives a hedge. Always offer concrete ranges.
- Asking multiple questions in one `clarify` call during intake — the sequence point is the whole value of one-at-a-time; batching defeats it.
- Assuming the named brand is the user's own. Client/agency vs own-business is the single biggest framing question and often wrong by default assumption.
- Writing to long-term memory only. The user's intake also produces standing preferences that live as SKILL rules (e.g. voice tone, brand positioning) — but for this class of skill, preferences are captured *in the specialist briefs you construct*, not re-saved into coordinator memory repeatedly.
- Treating intake as complete after one pass. New intake info surfaces during execution ("wait, we also ship to South India", "the agency name is X"). Leave a soft invitation to amend, don't treat intake as frozen.
- Saving client-confidential specifics (customer names, precise revenue, contact details) into persistent memory or a specialist brief beyond what's needed to brief. Briefs should be capability-scoped, not identity-scoped.

## Do NOT save

- The specific intake answers from any single session as skill content. They belong in memory or in the specialist briefs, not in a skill that a future coordinator reads.
- A transcript of what a user said. Distill to the *rule* — but that distilled fact lives in memory too, not in this skill.
- Session-specific client names as if they are the general pattern. If this skill ever gets cited, it should not name a specific client.
