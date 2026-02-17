# Commit Changes

You are tasked with creating git commits for the changes made during this session.

## Process:

1.  **Think about what changed:**
    - Review the conversation history and understand what was accomplished.
    - Run `git status` to see the current state of staged and unstaged files.
    - Run `git diff` to review **unstaged** modifications.
    - Run `git diff --staged` to review **staged** modifications.
    - Consider whether changes should be one commit or multiple logical commits.

2.  **Plan your commit(s):**
    - Identify which files belong together in a logical commit.
    - Draft clear, descriptive commit messages. Git commit titles should be formatted as `{type}: {short description}`, for example: "feat: Added identity management API endpoints". Use one of the following types: [feat, fix, refactor, docs, test, build, chore, revert, merge].
    - Use imperative mood in commit messages (e.g., "Add feature" not "Added feature").
    - Focus on *why* the changes were made, not just *what*.

3.  **Present your plan to the user:**
    - List the files you plan to `git add` for each commit.
    - Show the full commit message(s) you'll use.
    - Ask: "I plan to create [N] commit(s) with these changes. Shall I proceed?"

4.  **Execute upon confirmation:**
    - Use `git add` with specific file paths for each planned commit.
    - Create the commit(s) with your planned messages using `git commit -m "..."`.
    - Show the result with `git log --oneline -n [number of commits created]`.

## Important:
- **NEVER add co-author information or AI attribution.**
- Commits should be authored solely by the user.
- Do not include any "Generated with..." or "Co-Authored-By" lines.
- Write commit messages as if the user wrote them.

## Remember:
- You have the full context of what was done in this session.
- Group related changes together into focused, atomic commits.
- The user trusts your judgment to organize and commit the changes logically.