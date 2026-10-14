# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline: challenging terms, inventing edge-case scenarios, and capturing the glossary and decisions the moment they crystallise. (Merely *reading* the ubiquitous language for vocabulary is not this skill: that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language — the ubiquitous language in `byissue/spec/`, or the code's own naming — call it out immediately. "Your spec defines 'cancellation' as X, but you seem to mean Y. Which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account': do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

## ByIssue destinations

Three things come out of a session, and they are not equal. Create files lazily: only when the first entry lands, following the `byissue/` map in `SKILL.md`:

- **A term that resolved** → the ubiquitous language in `byissue/spec/`, **the moment it resolves — don't batch these up; capture them as they happen.** Where it lands and in what format is owned by [spec](spec.md). Under Talk, capture the proposal inline and write after the user confirms ([talk](talk.md)).
- **A decision that passes all three gates** — hard to reverse, surprising without context, a real trade-off (the contract and format are owned by `SKILL.md`「什么内容可以写到哪一层」and `templates/entities/decision.md`) → `byissue/decisions/`. Offer sparingly: if any of the three is missing, skip it.
- **Everything else you decided** → the conversation only. At Talk 收束 it lands in `byissue/talks/`, where a settled discussion keeps the decisions that would otherwise evaporate with the context window.

The ubiquitous language holds vocabulary and nothing else: no implementation details, no spec prose. What qualifies is owned by [spec](spec.md).

## Grillable and ungrillable

Some questions can be answered by talking. Others can't, and no amount of grilling will get you there.

"One long form or three pages?" and "how should this interaction feel?" are ungrillable. You need something to react to before you can answer them. When you hit one, stop grilling. Build the throwaway version — a sketch or a prototype — look at it together, then come back and answer in one line (UI → [ui-spec](ui-spec.md)).

Sessions grow too long when you try to talk through an ungrillable question: rephrasing loops, guessing, and the scope growing with the uncertainty.

## It's working if

- Questions the codebase can answer get answered by reading the codebase, not asked of the user.
- It challenges a word the user used because the existing language defines it differently.
- A resolved term is captured *during* the session, term by term, rather than appearing in one lump at the end.
- Decisions are few, and each one is a decision the user would be annoyed to have to argue again.
