---
argument-hint: [solution] [plan]
description: Reviews the last commit made and determines if the plan was executed completely, and documents any drift that occurred during implementation. Provide a plan file in the arguments for the review to analyze. It is strongly advised to run this command within the session of a plan execution, after running commit.
---

# Review Plan

You are tasked with validating that an implementation plan was correctly executed, verifying all success criteria and identifying any deviations or issues.

You will be given instructions, followed by a review that will contain user specific instructions and the plan file related to this implementation.

## IMPORTANT
**THE FIRST THING YOU MUST do is INVOKE TodoWrite with the following INPUT**
    **Input**
    {
      "tool_input": {
        "todos": [
          {
            "content": "Step 1: Context Discovery - Read plan, identify expected changes and success criteria",
            "status": "pending",
            "activeForm": "Discovering implementation context"
          },
          {
            "content": "Step 2: Systematic Validation - Check completion status and run automated verification for each phase",
            "status": "pending",
            "activeForm": "Validating implementation"
          },
          {
            "content": "Step 3: Generate Validation Report - Create comprehensive review document at {solution}/thoughts/reviews/",
            "status": "pending",
            "activeForm": "Creating validation report"
          },
          {
            "content": "Step 4: Update ticket status - Set ticket status to 'reviewed'",
            "status": "pending",
            "activeForm": "Updating ticket status"
          },
          {
            "content": "Step 5: Present completion summary - Show verification results and recommendations",
            "status": "pending",
            "activeForm": "Presenting verification summary"
          }
        ]
      }
    }

## Validation Process

### Step 1: Context Discovery

1. **Read the implementation plan** completely
2. **Identify what should have changed**:
   - List all files that should be modified
   - Note all success criteria (automated and manual)
   - Identify key functionality to verify

3. **Invoke parallel general-purpose subagents using the Task tool** to discover implementation:
   ```
   Task 1 - Verify database changes:
   Research if migration [N] was added and schema changes match plan.
   Check: migration files, schema version, table structure
   Return: What was implemented vs what plan specified

   Task 2 - Verify code changes:
   Find all modified files related to [feature].
   Compare actual changes to plan specifications.
   Return: File-by-file comparison of planned vs actual

   Task 3 - Verify test coverage:
   Check if tests were added/modified as specified.
   Run test commands and capture results.
   Return: Test status and any missing coverage
   ```

### Step 2: Systematic Validation

For each phase in the plan:

1. **Check completion status**:
   - Look for checkmarks in the plan (- [x])
   - Verify the actual code matches claimed completion

2. **Run automated verification**:
   - Execute each command from "Automated Verification"
   - Document pass/fail status
   - If failures, investigate root cause

3. **Assess manual criteria**:
   - List what needs manual testing
   - Provide clear steps for user verification

4. **Think deeply about edge cases**:
   - Were error conditions handled?
   - Are there missing validations?
   - Could the implementation break existing functionality?

### Step 3: Generate Validation Report

Create comprehensive validation summary and write it to the `{solution}/thoughts/reviews` directory with a filename that matches the plan being reviewed (e.g., if reviewing `plan-feature-x.md`, save as `{solution}/thoughts/reviews/feature-x-review.md`).

### Step 4: Update ticket status to 'reviewed' by editing the ticket file's frontmatter.

### Step 5: Present completion summary to user

After completing validation, present this output format:

```
✓ Verification Complete: [Plan Name]

Implementation Status:
✓ [X] phases fully implemented
⚠ [Y] phases with minor issues
✗ [Z] phases incomplete

Automated Verification:
✓ Build: PASSED
✓ Tests: PASSED
✓ Linting: PASSED (or ⚠ N warnings)

Code Quality Assessment:
- Matches Plan: [percentage or High/Medium/Low]
- Code Quality: [High/Medium/Low]
- Test Coverage: [Good/Adequate/Needs Work]

Issues Found:
- [Critical issue count] critical issues
- [Warning count] warnings
- [Improvement count] improvement suggestions

Deviations from Plan:
- [Number] deviations documented
- [Assessment: All justified / Some concerning / Need review]

Manual Testing Required:
- [count] manual verification items defined
- See detailed checklist in review document

Review Document: {solution}/thoughts/reviews/[filename].md

NEXT STEP: Address any issues, then ready for merge/deploy
- If issues found: Fix issues and re-run verification
- If no critical issues: Proceed with deployment process
- Review document contains full details and recommendations
```

**Validation Report Template:**

```markdown
## Validation Report: [Plan Name]

### Implementation Status
✓ Phase 1: [Name] - Fully implemented
✓ Phase 2: [Name] - Fully implemented
⚠️ Phase 3: [Name] - Partially implemented (see issues)

### Automated Verification Results
✓ Build passes: `turbo build`
✓ Tests pass: `turbo test`
✗ Linting issues: `turbo check` (3 warnings)

### Code Review Findings

#### Matches Plan:
- Database migration correctly adds [table]
- API endpoints implement specified methods
- Error handling follows plan

#### Deviations from Plan:
- Check the plan's "## Deviations from Plan" section (if present)
- For each deviation noted:
  - **Phase [N]**: [Original plan vs actual implementation]
  - **Assessment**: [Is the deviation justified? Impact on success criteria?]
  - **Recommendation**: [Any follow-up needed?]
- Additional deviations found during review:
  - Used different variable names in [file:line]
  - Added extra validation in [file:line] (improvement)

#### Potential Issues:
- Missing index on foreign key could impact performance
- No rollback handling in migration

### Manual Testing Required:
1. UI functionality:
   - [ ] Verify [feature] appears correctly
   - [ ] Test error states with invalid input

2. Integration:
   - [ ] Confirm works with existing [component]
   - [ ] Check performance with large datasets

### Recommendations:
- Address linting warnings before merge
- Consider adding integration test for [scenario]
- Document new API endpoints
```

## Working with Existing Context

- Review the conversation history
- Check your todo list for what was completed
- Focus validation on work done in this session
- Be honest about any shortcuts or incomplete items

## Important Guidelines

1. **Be thorough but practical** - Focus on what matters
2. **Run all automated checks** - Don't skip verification commands
3. **Document everything** - Both successes and issues
4. **Think critically** - Question if the implementation truly solves the problem
5. **Consider maintenance** - Will this be maintainable long-term?
6. **Do not use task subagents** - All review work should be done exclusively in the main context to maintain consistency and avoid fragmentation

## Validation Checklist

Always verify:
- [ ] All phases marked complete are actually done
- [ ] Automated tests pass
- [ ] Code follows existing patterns
- [ ] No regressions introduced
- [ ] Error handling is robust
- [ ] Documentation updated if needed
- [ ] Manual test steps are clear

The validation works best after commits are made, as it can analyze the git history to understand what was implemented.

Remember: Good validation catches issues before they reach production. Be constructive but thorough in identifying gaps or improvements.