## Command Execution Rules
### Auto-Execution Criteria
Commands must be:
- Simple and predictable in outcome
- Non-destructive
- Limited to project scope
- Idempotent when possible
- Use relative paths from project root (e.g., `docs/file.md` not `/Users/path/docs/file.md`)
- Handle subdirectories correctly (create parent dirs if needed)

### Allowlist
- `poetry add/remove` (specific package)
- `pytest` (with specific paths, no -v flag unless requested)
- `git status/log/diff` (read-only operations)
- `ls/pwd/cat` (read-only operations, use relative paths)
- `mkdir -p` (safe directory creation, create parent dirs)
- `commit "type(scope): message" "- detail 1" "- detail 2"` (custom git add/commit/push)

### Denylist
- Any `rm/del` commands
- Any `sudo` operations
- Global pip operations without `-t`
- Force flags (`-f`, `--force`)
- Shell operations (`>&`, `|`, `;`)
- Environment modifications
- Network operations (`curl`, `wget`)
- Absolute paths or paths outside project root

## Package Management
- Install packages directly in environment with pip
- Do not maintain requirements.txt - we work in the environment directly
- Only document critical version dependencies if absolutely necessary
- When you need a new package, run its install command in the root dir
- When you need to update a package, run its update command in the root dir

## Code Style
- Keep it simple
- Less code is better
- Challenge complexity
- Use pytest for testing
- Follow PEP 8 guidelines
- Organize code into appropriate subdirectories:
  - `/src` for source code
  - `/tests` for test files
  - `/docs` for documentation
  - `/scripts` for utility scripts
- Always use relative paths from project root
- When referencing files in prompts, use `{{ filepath:subdir/file.ext }}` format 