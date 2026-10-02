# GitHub Workflows

This directory stores GitHub Actions workflows for validating the AI System branch.

Current workflow:

- `ai-system-validate.yml` - runs local AI System validators and whitespace checks.

The Ubuntu runner installs ripgrep (`rg`) before validation rather than relying
on the runner image to provide it. Bash, Git and Python 3 are also required;
the validator preflight reports missing tools before executing contract checks.
The full profile and its smoke coverage remain mandatory. Script results are
supporting evidence, not semantic acceptance.
Synthetic SPOR fixtures use Python date arithmetic rather than BSD-only `date`
flags; no case or quality gate is skipped for Linux compatibility.
