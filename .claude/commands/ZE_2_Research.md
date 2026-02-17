---
argument-hint: [solution] [ticket]
description: Research a ticket or provide a prompt for ad-hoc research. It is best to run this command in a new session.
---

# Research Codebase

You are tasked with conducting comprehensive research across the codebase to answer user questions by spawning tasks and synthesizing their findings.

The user will provide a ticket for you to read and begin researching.

## IMPORTANT
**THE FIRST THING YOU MUST do is INVOKE TodoWrite with the following INPUT**
    **Input**
    {
      "tool_input": {
        "todos": [
          {
            "content": "Step 1: Read the ticket - Load ticket file completely into main context",
            "status": "pending",
            "activeForm": "Reading ticket file"
          },
          {
            "content": "Step 2: Detail research steps - Break down ticket into composable research areas and plan agent spawning",
            "status": "pending",
            "activeForm": "Planning research approach"
          },
          {
            "content": "Step 3: Phase 1 - Thoughts Discovery - Spawn thoughts-locator agents, then thoughts-analyzer agents to gather historical context",
            "status": "pending",
            "activeForm": "Discovering historical context from thoughts"
          },
          {
            "content": "Step 4: Phase 2 - Codebase Discovery - Spawn codebase-locator agents to find WHERE components live",
            "status": "pending",
            "activeForm": "Locating codebase components"
          },
          {
            "content": "Step 5: Phase 3 - Deep Analysis - Spawn codebase-analyzer and codebase-pattern-finder agents in parallel",
            "status": "pending",
            "activeForm": "Analyzing code and finding patterns"
          },
          {
            "content": "Step 7: Synthesize findings - Compile all sub-agent results with file:line references",
            "status": "pending",
            "activeForm": "Synthesizing research findings"
          },
          {
            "content": "Step 8: Gather metadata - Collect git metadata for research document frontmatter",
            "status": "pending",
            "activeForm": "Gathering document metadata"
          },
          {
            "content": "Step 9: Generate research document - Create structured markdown document at {solution}/thoughts/research/date_topic.md",
            "status": "pending",
            "activeForm": "Creating research document"
          },
          {
            "content": "Step 10: Present findings - Provide concise summary with key file references to user",
            "status": "pending",
            "activeForm": "Presenting findings"
          },
          {
            "content": "Step 11: Handle follow-up - Process any follow-up questions by updating research document",
            "status": "pending",
            "activeForm": "Handling follow-up questions"
          },
          {
            "content": "Step 12: Update ticket status - Set ticket status to 'researched'",
            "status": "pending",
            "activeForm": "Updating ticket status"
          },
          {
            "content": "Step 13: Present completion summary - Show research summary and next step command",
            "status": "pending",
            "activeForm": "Presenting completion summary"
          }
        ]
      }
    }

## Steps to follow after receiving the research query:

1. **Read the ticket first:**
   - **IMPORTANT**: Use the Read tool WITHOUT limit/offset parameters to read entire files
   - **CRITICAL**: Read these files yourself in the main context before spawning any sub-tasks
   - This ensures you have full context before decomposing the research

2. **Detail the steps needed to perform the research:**
    - Break down the user's ticket into composable research areas
    - Take time to think about the underlying patterns, connections, and architectural the ticket has provided
    - Identify specific components, patterns, or concepts to investigate
    - Lay out what the codebase-locator or thoughts-locator should look for
    - Specify what patterns the codebase-pattern-finder should look for
    - Be clear that locators and pattern-finders collect information for analyzers
    - Typically run a single codebase-analyzer and thoughts-analyzer (in parallel if both needed)
    - Consider which directories, files, or architectural patterns are relevant

3. **Spawn tasks for comprehensive research (follow this sequence):**

   **Phase 1 - Thoughts Discovery:**
   - Identify topics/components/areas that might have historical context
   - Spawn **thoughts-locator** agents <IMPORTANT>in parallel</IMPORTANT> to discover relevant documents in {solution}/thoughts/
   - **WAIT** for all thoughts-locator agents to complete before proceeding
   - Spawn **thoughts-analyzer** agents <IMPORTANT>in parallel</IMPORTANT> to extract key insights from discovered documents
   - **WAIT** for all thoughts-analyzer agents to complete before proceeding
   - Use insights to inform what to search for in codebase

   **Phase 2 - Codebase Discovery:**
   - Based on ticket requirements and thoughts insights, identify components/areas to locate in codebase
   - Group related topics into coherent batches
   - Spawn **codebase-locator** agents <IMPORTANT>in parallel</IMPORTANT> for each topic group to find WHERE files and components live
   - **WAIT** for all codebase-locator agents to complete before proceeding

   **Phase 3 - Deep Analysis (Parallel):**
   - Using locator results, determine what needs deep analysis
   - Spawn <IMPORTANT>in parallel</IMPORTANT>:
     - **codebase-analyzer** agents for each topic group to understand HOW specific code works
     - **codebase-pattern-finder** agents to find examples of similar implementations
   - **WAIT** for all analysis and pattern-finding agents to complete before proceeding

   **Important sequencing notes:**
   - Start with historical context (thoughts) to inform codebase search
   - Each phase builds on the previous one
   - Run agents of the same type <IMPORTANT>in parallel</IMPORTANT> within each phase
   - Phase 3 is the exception: codebase-analyzer and codebase-pattern-finder can run <IMPORTANT>in parallel</IMPORTANT>
   - Each agent knows its job - just tell it what you're looking for
   - Don't write detailed prompts about HOW to search - the agents already know

4. **Wait for all sub-agents to complete and synthesize findings:**
   - IMPORTANT: Wait for ALL sub-agent tasks to complete before proceeding
   - Compile all sub-agent results (both codebase and thoughts findings)
   - Prioritize live codebase findings as primary source of truth
   - Use {solution}/thoughts/ findings as supplementary historical context
   - Connect findings across different components
   - Include specific file paths and line numbers for reference
   - Highlight patterns, connections, and architectural decisions
   - Answer the user's specific questions with concrete evidence

5. **Gather metadata for the research document:**

Use the following metadata for the research document frontmatter:

**metadata for frontmatter**

!`agentic metadata`

6. **Generate research document:**
   - Filename: `{solution}/thoughts/research/date_topic.md`
   - Use the metadata gathered in step 5, mapping XML tags to frontmatter fields
   - Structure the document with YAML frontmatter followed by content:
     ```markdown
     ---
     date: [Current date and time with timezone in ISO format]
     git_commit: [from metadata]
     branch: [from metadata]
     repository: [from metadata]
     topic: "[User's Question/Topic]"
     tags: [research, codebase, relevant-component-names]
     last_updated: [from metadata]
     ---

     ## Ticket Synopsis
     [Synopsis of the ticket information]

     ## Summary
     [High-level findings answering the user's question]

     ## Detailed Findings

     ### [Component/Area 1]
     - Finding with reference ([file.ext:line])
     - Connection to other components
     - Implementation details

     ### [Component/Area 2]
     - Finding with reference ([file.ext:line])
     - Connection to other components
     - Implementation details
     ...

     ## Code References
     - `path/to/file.py:123` - Description of what's there
     - `another/file.ts:45-67` - Description of the code block

     ## Architecture Insights
     [Patterns, conventions, and design decisions discovered]

     ## Historical Context (from {solution}/thoughts/)
     [Relevant insights from {solution}/thoughts/ directory with references]
     - `{solution}/thoughts/research/something.md` - Historical decision about X
     - `{solution}/thoughts/plans/build-thing.md` - Past exploration of Y

     ## Related Research
     [Links to other research documents in {solution}/thoughts/research/]

     ## Open Questions
     [Any areas that need further investigation]
     ```

7. **Present findings:**
   - Present a concise summary of findings to the user
   - Include key file references for easy navigation
   - Ask if they have follow-up questions or need clarification

8. **Handle follow-up questions:**
   - If the user has follow-up questions, append to the same research document
   - Update the frontmatter fields `last_updated` and `last_updated_by` to reflect the update
   - Add `last_updated_note: "Added follow-up research for [brief description]"` to frontmatter
   - Add a new section: `## Follow-up Research [timestamp]`
   - Spawn new sub-agents as needed for additional investigation
    - Continue updating the document and syncing

9. **Update ticket status** to 'researched' by editing the ticket file's frontmatter.

10. **Present completion summary to user**

After completing all steps, present this output format:

```
✓ Research Complete: [Topic/Ticket Title]

Research Summary:
- Document: {solution}/thoughts/research/[filename].md
- Components Analyzed: [count]
- Key Findings: [1-2 sentence summary]

Key Discoveries:
- [Most important finding with file:line]
- [Second important finding with file:line]
- [Third important finding with file:line]

Historical Context:
- [Number] related documents found in {solution}/thoughts/
- [Key historical insight if any]

NEXT STEP: Create implementation plan
Copy and run: /ZE_3_Plan {solution} thoughts/tickets/[ticket-file].md thoughts/research/[research-file].md
```

## Important notes:
- Follow the four-phase sequence: Thoughts Discovery → Codebase Discovery → Deep Analysis → Theoretical Foundation
- **Phase 1**: Start with thoughts-locator → thoughts-analyzer to gather historical context first
- **Phase 2**: Use thoughts insights to inform codebase-locator searches
- **Phase 3**: Run codebase-analyzer and codebase-pattern-finder IN PARALLEL (exception to same-type rule)
- **File reading**: Always read mentioned files FULLY (no limit/offset) before spawning sub-tasks
- **Critical ordering**: Follow the numbered steps exactly
  - ALWAYS read mentioned files first before spawning sub-tasks (step 1)
  - ALWAYS wait for all sub-agents to complete before synthesizing (step 4)
  - ALWAYS gather metadata before writing the document (step 5 before step 6)
  - NEVER write the research document with placeholder values
- **Frontmatter consistency**:
  - Always include frontmatter at the beginning of research documents
  - Keep frontmatter fields consistent across all research documents
  - Update frontmatter when adding follow-up research
  - Use snake_case for multi-word field names (e.g., `last_updated`, `git_commit`)
  - Tags should be relevant to the research topic and components studied