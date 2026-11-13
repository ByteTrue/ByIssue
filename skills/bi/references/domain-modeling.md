# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline: challenging terms, inventing edge-case scenarios, and capturing the glossary and decisions the moment they crystallise. (Merely *reading* the ubiquitous language for vocabulary is not this skill: that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language — the project's durable vocabulary in `byissue/memory/`, or the code's own naming — call it out immediately. "Your project defines 'cancellation' as X, but you seem to mean Y. Which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account': do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

## ByIssue destinations

Create files lazily, following the current work map:

- **A term that resolved** goes to the relevant `byissue/memory/{topic}.md` when it will affect future decisions. The work entry keeps the local wording and evidence.
- **A durable user decision** goes to the relevant Memory topic when it is long-lived, hard to reverse or surprising without context. The current work keeps the decision needed for this change.
- **An external observation or rerunnable proof** goes to Memory when future work should be able to find and rerun it. Code, tests and configuration remain the implementation truth.

Memory stores the conclusion, scope, basis and revisit condition. It does not become a copy of the code or a second behavior specification.

## Grillable and ungrillable

Some questions can be answered by talking. Others need something concrete to react to.

"One long form or three pages?" and "how should this interaction feel?" are ungrillable. Stop grilling, build a throwaway sketch or prototype, look at it together, then answer in one line. UI questions use [ui-spec](ui-spec.md).

## It's working if

- Questions the codebase can answer get answered by reading the codebase, not asked of the user.
- The agent challenges a word because the existing language defines it differently.
- A resolved term is captured during the session when it will affect future work.
- Decisions are few and each one prevents the user from having to argue the same choice again.
