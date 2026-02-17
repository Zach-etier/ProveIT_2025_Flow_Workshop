---
argument-hint: [topic]
description: Persist everything you've learned in this conversation to a structured research report on disk. Downstream agents read this file instead of repeating the research.
---

# Create Research Report: $ARGUMENTS

You have been exploring, querying, and gathering information during this conversation. Your context window is full of findings — script outputs, reference material, observations, data from the historian. **All of that is ephemeral.** When this session ends, it's gone.

Your job now: distill what you've learned into a concise, structured file on disk that any future agent or session can read to get up to speed without repeating the research.

## What to Write

Create a file at `analyses/research/research-{topic}-{date}.md` where `{topic}` is derived from `$ARGUMENTS` (lowercased, spaces replaced with hyphens) and `{date}` is today's date (YYYY-MM-DD).

Create the `analyses/research/` directory if it doesn't exist.

The report should include these sections:

### 1. Summary
2-3 sentences: What was investigated and what's the headline finding?

### 2. Key Metrics
A table of the most important numbers discovered. For production data, include:

| Metric | Value | Context |
|--------|-------|---------|

Keep it to the metrics that matter for decision-making. No raw JSON — just the derived values.

### 3. Findings
3-7 bullet points capturing the essential observations. Each bullet should be actionable or informative — not just restating a number, but interpreting what it means.

### 4. Concerns
Anything that needs attention, follow-up, or escalation. If nothing is concerning, say so explicitly (that's useful information too).

### 5. Recommendations
What should the next person (or agent) do with this information? What actions does this research suggest?

### 6. Data Sources
List what scripts were run, what references were consulted, and what time ranges were queried. This gives downstream consumers confidence in the findings and a path to reproduce them if needed.

## Guidelines

- **Be concise.** Target 40-60 lines. The whole point is that this file replaces a long, messy context window with something tight and readable.
- **Interpret, don't dump.** No raw script JSON in the report. Translate outputs into plain language and tables.
- **Write for a reader who wasn't in this conversation.** They should understand the findings without any prior context.
- **Include enough detail to be actionable** but not so much that the reader has to hunt for what matters.

## After Writing

Report to the user:
1. The file path you wrote
2. The number of lines in the report
3. A reminder: "This file is now on the filesystem. Any downstream agent or future session can read it instead of repeating this research."
