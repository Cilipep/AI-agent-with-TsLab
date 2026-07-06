# CLAUDE.md

Claude Code entrypoint for the packaged TSLab automation workspace.

Open these local docs first:
- `@CLAUDE-FastPath.md`
- `@AGENTS-FastPath.md`

Task routing:
- In Claude/openclaude, use `CLAUDE-FastPath.md` as the bootstrap brief.
- Do not open `AGENTS-FastPath.md` end-to-end at startup. Only after a concrete live blocker, open one small slice or one exact keyword match there.
- Common authoring, repair, run, metrics, optimization, and delivery rules still live in `AGENTS-FastPath.md`.
- Open specialized `AGENTS-*.md` files only when the active fast path says you need them.

Important:
- the current packaged workspace is the instruction boundary
- `.opencode/skill/*` is not the primary source of truth
- do not jump to repo-root duplicates or parent/source-tree docs
- before final success, verify the same current artifact through the relevant localhost endpoints