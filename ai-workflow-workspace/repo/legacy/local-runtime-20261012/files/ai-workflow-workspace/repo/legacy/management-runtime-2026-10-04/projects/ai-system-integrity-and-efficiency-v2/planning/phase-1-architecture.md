# Architecture

## Decisions
Use a shared standard-library validation module for source identity, safe output, manifests and execution evidence. Keep existing shell validators and their semantic contracts. Typed smoke assertions have stable identities and declared expected diagnostics. Skill eval freshness uses a separate shared producer-consumer module in skill-creator. New reports and diagnostics are opt-in; existing Dream Reports remain unchanged.

## Producer Consumer Map
CLI -> execution manifest -> evidence/timing -> comparison; smoke helpers -> declared assertion contracts -> executed assertion inventory; eval plan/source -> run manifest -> metadata -> grades -> aggregator; scope inputs/dependencies -> coverage -> eligibility; Dream recommendation -> decision evidence -> recurrence; selected roots -> metadata reports.

## Safety And Failure Paths
Validate all destinations before execution. Fail closed on stale identity, incomplete coverage, infrastructure exits, unknown paths, ahead/diverged updates and unauthorized source roots. Preserve failed results and immutable history. No script issues semantic PASS or grants approval.

## Dependency Order
001 and 003 before lifecycle; 002 and 004 independently after preflight; 005 before 006/007; 008/009/010 after identity primitives; 011 last. Entire program receives full integrated QA.

## Residual Risk
Static contracts cannot prove an agent's complete read-set. Timing is noisy and source changes require honest non-comparability reporting.
