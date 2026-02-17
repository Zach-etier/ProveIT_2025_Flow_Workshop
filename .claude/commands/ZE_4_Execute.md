---
argument-hint: [solution] [plan]
description: Execute a specific implementation plan. Provide a plan file as the argument to this command. It's very important this command runs in a new session.
---

# Implement Plan

You are tasked with implementing an approved technical plan from `{solution}/thoughts/plans/`. These plans contain phases with specific changes and success criteria.

## IMPORTANT
**THE FIRST THING YOU MUST do is INVOKE TodoWrite with the following INPUT**
    **Input**
    {
      "tool_input": {
        "todos": [
          {
            "content": "Step 1: Read plan and determine current phase - Check for checkmarks or checkpoint section to find where to start",
            "status": "pending",
            "activeForm": "Determining current phase"
          },
          {
            "content": "Step 2: Load complete context - Read ticket, research, and critical files for current phase",
            "status": "pending",
            "activeForm": "Loading context files"
          },
          {
            "content": "Step 3: Create implementation todo list - Derive detailed tasks from current phase only",
            "status": "pending",
            "activeForm": "Creating phase task list"
          },
          {
            "content": "Step 4: Implement ONLY current phase - Execute phase systematically, handle mismatches if needed",
            "status": "pending",
            "activeForm": "Implementing current phase"
          },
          {
            "content": "Step 5: Verify the phase - Run automated checks, fix failures, note manual items",
            "status": "pending",
            "activeForm": "Verifying phase completion"
          },
          {
            "content": "Step 6: Update plan progress - Add checkmarks for completed phase",
            "status": "pending",
            "activeForm": "Updating plan progress"
          },
          {
            "content": "Step 7: Present phase completion summary - Show changes and next step",
            "status": "pending",
            "activeForm": "Presenting phase summary"
          },
          {
            "content": "Step 8: Update ticket status - Set to 'implemented' (ONLY if all phases complete)",
            "status": "pending",
            "activeForm": "Updating ticket status"
          },
          {
            "content": "Step 9: Present final completion summary - Show all phases done and verification command (ONLY if all complete)",
            "status": "pending",
            "activeForm": "Presenting final summary"
          }
        ]
      }
    }

## Steps

### Step 1: Read the Plan and Determine Current Phase

1. **Read the plan file completely** provided as an argument
2. **Determine where you are in the implementation** by checking (in order of priority):

   **Option A - Resuming from Checkpoint (highest priority):**
   - Look for "Implementation Progress Checkpoint" section at the end of the plan
   - This indicates a previous session stopped mid-implementation
   - Read the "Currently Working On" to see the exact phase and progress
   - Use "Next Steps" to understand what to do next
   - Review "Files to Review" for critical context

   **Option B - Continuing from Previous Phase:**
   - Look for checkmarks (- [x]) in phase sections
   - The FIRST phase without a checkmark is your current phase
   - All phases with checkmarks are considered complete

   **Option C - Starting Fresh:**
   - No checkmarks and no checkpoint section = start at Phase 1

3. **Document your starting point** clearly:
   ```
   Starting implementation from: Phase [N]: [Phase Name]
   Reason: [New implementation / Resuming from checkpoint / Continuing after Phase N-1]
   ```

### Step 2: Load Complete Context

1. **Read the original ticket** (path usually in plan's References section)
2. **Read research documents** mentioned in the plan
3. **Read all critical files** mentioned in the current phase
   - **IMPORTANT**: Always use Read tool WITHOUT limit/offset parameters
   - You need complete file context to implement correctly
   - If resuming, prioritize "Files to Review" from checkpoint section

### Step 3: Create Implementation Todo List

1. **Derive detailed tasks** from the current phase ONLY (not all phases)
2. **If resuming from checkpoint**, use the "Next Steps" as your starting todos
3. **Structure your todos** to match the phase's requirements:
   ```
   Example for Phase 2:
   - Modify file X to add function Y
   - Update file Z to handle edge case W
   - Add tests for new functionality
   - Run verification commands
   ```

### Step 4: Implement ONLY the Current Phase

**CRITICAL RULE: Implement ONE phase, then STOP.**

1. **Work through the current phase systematically**
2. **Follow the plan's intent** while adapting to code reality
3. **If you encounter mismatches**, use the "Handle Mismatches" protocol below
4. **Do NOT proceed to the next phase** - this is a hard stop

### Step 5: Verify the Phase

1. **Run automated verification** from the phase's success criteria:
   - Execute each command listed under "Automated Verification"
   - Document results (pass/fail)

2. **Fix any failures** before proceeding:
   - Debug and resolve test failures
   - Fix linting/type errors
   - Ensure build succeeds

3. **Note manual verification items** for user testing

### Step 6: Update Plan Progress

**Choose based on completion status:**

**If Phase is Fully Complete:**
1. Use Edit tool to add checkmark to the phase:
   ```markdown
   - [x] Phase N: [Name] - Completed [timestamp]
   ```
2. Mark all success criteria items in that phase with [x]

**If ALL Phases Complete:**
1. Add all final checkmarks
2. Add completion summary at end of plan:
   ```markdown
   ## Implementation Complete
   **Completed**: [ISO timestamp]
   **All phases implemented and verified**
   ```

### Step 7: Present Phase Completion Summary

**After completing the phase, present this output format:**

```
✓ Phase [N] Complete: [Phase Name]

Changes Made:
- [Key change 1 with file reference]
- [Key change 2 with file reference]
- [Key change 3 with file reference]

Verification Status:
✓ Automated checks passed
⚠ Manual verification needed:
  - [Manual test item 1]
  - [Manual test item 2]

Progress: [X] of [Y] phases complete

NEXT STEP: Continue to next phase (run in SAME or NEW session)
Copy and run: /ZE_4_Execute {solution} thoughts/plans/[plan-file].md
```

**DO NOT continue to the next phase automatically - STOP here.**

### Step 8: Update Ticket Status (Only When ALL Phases Done)

**Only execute this step if Step 6 resulted in "Implementation Complete":**

1. Edit the ticket file's frontmatter
2. Change status from 'planned' to 'implemented'

### Step 9: Present Final Completion Summary (Only When ALL Phases Done)

**Only execute this step when ALL phases are complete:**

```
✓ Implementation Complete: [Feature/Task Name]

All Phases Completed:
✓ Phase 1: [Name]
✓ Phase 2: [Name]
✓ Phase N: [Name]

Implementation Summary:
- Files Modified: [count]
- Files Created: [count]
- Key Components Changed: [list major components]

Final Verification Status:
✓ All automated checks passed
⚠ Manual verification checklist:
  - [Manual item 1]
  - [Manual item 2]
  - [Manual item N]

NEXT STEP: Review implementation
Copy and run: /ZE_5_Verify {solution} thoughts/plans/[plan-file].md

Note: It's recommended to run /ZE_5_Verify in the SAME session for best context.
```    

## Implementation Philosophy

Plans are carefully designed, but reality can be messy. Your job is to:
- Follow the plan's intent while adapting to what you find
- Implement ONE phase fully, then stop for reinvocation
- Verify your work makes sense in the broader codebase context
- Update checkmarks and progress in the plan file
- Use the "Handle Mismatches Protocol" when reality doesn't match the plan

**Key Principle**: Implement one phase at a time, verify it works, update progress, then stop and ask user to reinvoke for the next phase. This ensures each phase is solid before moving forward.

## Verification Approach

After implementing a phase:
- Run the success criteria checks (usually `bun run check` covers everything)
- Fix any issues before proceeding
- Update your progress in both the plan and your todos
- Check off completed items in the plan file itself using Edit

Don't let verification interrupt your flow - batch it at natural stopping points.

## Handle Mismatches Protocol

When things don't match the plan exactly:

1. **STOP and analyze** why the plan can't be followed as written

2. **Present the issue clearly**:
   ```
   Issue in Phase [N]: [Phase Name]

   Expected (per plan): [what the plan specifies]
   Found (in codebase): [actual situation]
   Why this matters: [impact explanation]

   Proposed solution: [your recommendation]

   Should I proceed with this approach?
   ```

3. **After user approval, document the deviation**:
   Use Edit tool to add/update at the end of plan:

   ```markdown
   ## Deviations from Plan

   ### Phase [N]: [Phase Name]
   - **Original Plan**: [brief summary of plan specification]
   - **Actual Implementation**: [what was actually done]
   - **Reason for Deviation**: [why the change was necessary]
   - **Impact Assessment**: [effects on other phases or success criteria]
   - **Approved By**: User on [timestamp]
   ```

4. **Continue with approved approach** 

## If You Get Stuck

When something isn't working as expected:
- First, make sure you've read and understood all the relevant code
- Consider if the codebase has evolved since the plan was written
- Use the "Handle Mismatches Protocol" to communicate with the user
- Don't make assumptions - ask for clarification

**Sub-tasks**: Use sparingly, mainly for targeted research when encountering unfamiliar territory. Most implementation should happen in the main context.

## Important Reminders

- **One phase at a time**: This is not optional. Implement one phase, verify, update, stop.
- **Read files completely**: Never use limit/offset when reading files for implementation
- **Update progress**: Always mark completed phases with checkmarks
- **Verify before proceeding**: Run automated checks and fix failures
- **Document deviations**: Use the proper protocol when reality doesn't match the plan
- **Trust previous work**: If phases are checked off, they're done - don't re-implement

Remember: You're implementing a solution methodically, one phase at a time. Quality over speed.

