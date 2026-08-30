# Design System

## Purpose

The AI Codebase Investigator is a developer-focused technical tool.

The UI should feel:

- professional
- technical
- modern
- minimal
- focused
- trustworthy

Avoid generic SaaS dashboard aesthetics.

The interface should prioritize clarity and information density without
becoming visually cluttered.

---

# 1. VISUAL PHILOSOPHY

The product should feel like a developer tool rather than a marketing website.

Priorities:

1. Content clarity
2. Code readability
3. Evidence visibility
4. Investigation state visibility
5. Consistent spacing
6. Minimal visual noise

Avoid unnecessary:

- gradients
- excessive animations
- decorative illustrations
- oversized cards
- excessive rounded containers
- excessive shadows
- decorative statistics
- fake dashboard metrics

---

# 2. THEME

The application should use a dark-first developer-oriented interface.

Theme configuration must be centralized.

Components should consume semantic theme tokens rather than hardcoded colors.

Do not introduce arbitrary colors inside components.

Bad:

```tsx
<div className="bg-[#123456]">
```

Preferred:

```tsx
<div className="bg-background">
```

or the equivalent semantic token supported by the project.

---

# 3. COLOR TOKENS

Use semantic tokens such as:

```text
background
foreground
surface
surface-muted
border
primary
primary-foreground
secondary
muted
muted-foreground
success
warning
error
info
```

Exact values must be defined centrally in the theme configuration.

Components should consume semantic tokens instead of raw color values.

---

# 4. TYPOGRAPHY

Typography must prioritize readability.

Use a clear hierarchy between:

- page titles
- section titles
- body text
- metadata
- labels
- code
- AI-generated answers

Code must use a monospace font.

Do not introduce additional font families without approval.

---

# 5. SPACING

Use the project's existing spacing scale consistently.

Do not create arbitrary spacing values unless necessary.

Prefer existing spacing utilities and design tokens.

---

# 6. BORDER RADIUS

Use a small and consistent radius scale.

Do not give every component a different radius.

Prefer the project's existing radius tokens.

---

# 7. SHADOWS

Shadows should be subtle and purposeful.

Do not use heavy shadows to separate every section.

Prefer:

- borders
- surface contrast
- spacing

for most layout separation.

---

# 8. COMPONENTS

Prefer reusable components for:

- buttons
- inputs
- badges
- cards
- dialogs
- tabs
- code blocks
- evidence references
- status indicators
- investigation events

Do not duplicate visually equivalent components.

Before creating a component, search for an existing reusable component.

---

# 9. BUTTONS

Buttons should clearly communicate:

- primary actions
- secondary actions
- destructive actions
- disabled states
- loading states

Avoid introducing a new button style for individual features.

---

# 10. FORMS

Inputs should provide:

- clear labels
- useful placeholders
- validation feedback
- disabled states
- loading states where appropriate

Validation messages should be concise and actionable.

---

# 11. CODE VIEWER

The code viewer is one of the most important UI elements.

It should provide:

- filename
- language
- line numbers
- highlighted relevant lines
- readable code
- clear evidence indication

Evidence should be visually distinguishable without overwhelming the code.

Code should remain easy to scan.

---

# 12. INVESTIGATION UI

The investigation interface should clearly distinguish:

- current state
- completed steps
- active step
- errors
- final result

Example:

```text
✓ Analyzing question
✓ Searching repository
✓ Inspecting middleware.ts
● Finding references
○ Generating answer
```

Streaming investigation events should feel immediate but not distracting.

---

# 13. AI RESPONSE

AI responses should prioritize:

1. Answer
2. Explanation
3. Evidence
4. Relevant source locations

Avoid presenting large blocks of unstructured AI-generated text.

The interface should make it easy to distinguish:

```text
AI explanation
```

from:

```text
Repository evidence
```

---

# 14. ANIMATION

Use animation sparingly.

Animation should communicate:

- state transitions
- loading
- streaming
- expanding/collapsing content

Do not animate purely for decoration.

Avoid excessive motion during technical investigation.

---

# 15. RESPONSIVE DESIGN

The application must work on:

- desktop
- laptop
- tablet

Desktop is the primary target because the application is a developer tool.

---

# 16. ACCESSIBILITY

Interactive elements must:

- have meaningful labels
- have visible focus states
- support keyboard navigation
- maintain sufficient contrast
- communicate state changes appropriately

Do not sacrifice accessibility for visual effects.

---

# 17. EMPTY STATES

Empty states should explain:

1. What is currently empty.
2. Why it is empty.
3. What the user can do next.

Avoid decorative empty states that provide no useful information.

---

# 18. ERROR STATES

Errors should be:

- clear
- actionable
- concise
- technically useful without exposing internal secrets

Example:

```text
Repository could not be indexed.

The GitHub repository could not be accessed.
Verify that the repository is public and the URL is correct.
```

Avoid generic messages such as:

```text
Something went wrong.
```

when more useful information can safely be provided.

---

# 19. DESIGN TOKENS

All reusable visual values should be centralized.

Prefer:

```text
theme tokens
↓
component styles
↓
feature UI
```

Avoid:

```text
feature
↓
arbitrary custom values
```

---

# 20. DESIGN RULE

If a visual decision is not explicitly defined here, prefer:

> Simple, consistent, semantic, accessible, and developer-tool oriented.

Do not invent a new visual language for individual features.

---

# 21. DESIGN CHANGE APPROVAL

Significant changes to the visual language require explicit approval.

Examples:

- changing the overall color system
- changing typography
- replacing the component library
- introducing a new design system
- introducing a major animation language

Small component-level improvements that follow this document do not require
separate approval.
