# Root Templates

Templates in this directory generate local-only root runtime files.

`AGENTS.template.md` is the committed source for the ignored root `AGENTS.md` execution contract.

It is management-only. `ai-system.local.template.json` documents the ignored local
`ai-system.local.json` role record; use explicit `init-ai-system --role
management|development`, not a copied placeholder. Development preserves its
own project contract. Neither a role nor a template grants write permission.
