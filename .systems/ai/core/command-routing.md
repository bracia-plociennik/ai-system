# Command Routing

## Purpose

Map owner prompts to safe AI System actions.

## Common Commands

| Prompt | Route |
| --- | --- |
| `co teraz` | Guide mode |
| `przejrzyj dump` | Dump triage classification |
| `utwórz klienta` | Create client workspace from template |
| `utwórz projekt klienta` | Create client project workspace |
| `zrób destylację` | Distillation workflow |
| `zaproponuj system-insights` | Anonymized insights proposal |

## Unsafe Commands

Commands that ask AI to skip approval, move files blindly, expose secrets, or write to external tools must stop.
