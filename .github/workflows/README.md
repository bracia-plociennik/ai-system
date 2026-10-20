# GitHub Workflows

This directory stores GitHub Actions workflows for validating the AI System branch.

Current workflow:

- `ai-system-validate.yml` - runs local AI System validators and whitespace checks.

The Ubuntu runner installs ripgrep (`rg`), Poppler utilities (`pdfinfo`,
`pdftotext`, `pdftoppm`) and Tesseract with English/Polish language data before
validation rather than relying on the runner image to provide them. The PDF/OCR
source-library tests use synthetic documents and exercise these real local tools. Bash, Git and Python 3 are also required;
the validator preflight reports missing tools before executing contract checks.
The full profile and its smoke coverage remain mandatory. Script results are
supporting evidence, not semantic acceptance.
Synthetic SPOR fixtures use Python date arithmetic rather than BSD-only `date`
flags; no case or quality gate is skipped for Linux compatibility.
