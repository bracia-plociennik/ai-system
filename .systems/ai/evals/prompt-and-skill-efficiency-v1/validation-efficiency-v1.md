# Validation Efficiency V1

## Method

Local macOS checkout, baseline commit `bdcf046`, one wall-clock run per case using `/usr/bin/time -p`. The baseline was measured before editing; the candidate was measured after the profile and smoke-suite changes. These are directional timings, not a latency guarantee or semantic QA result. The synthetic cases read product contracts only; no private workspace or client data was used.

| Case | Baseline validators | Candidate validators | Baseline real | Candidate real |
| --- | ---: | ---: | ---: | ---: |
| Small sanity check: `--profile fast` | 13 + diff | 2 + diff | 3.89 s | 0.77 s |
| One scoped artifact check: `check-validation-profiles` | 14 + diff | 2 + diff | 4.55 s | 1.13 s |
| Full system verification: `--profile full` | complete chain + all smoke cases | same chain + all smoke cases | 167.06 s | 164.25 s |

Additional small scoped cases used a clean archive of the baseline product. They are exploratory because archive extraction and file-system cache state differ from the working checkout:

| Scoped checker | Archive baseline | Candidate checkout |
| --- | ---: | ---: |
| `check-validation-profiles` | 8.55 s | 1.23 s |
| `check-delivery-constraints` | 4.17 s | 1.06 s |
| `check-system-skills` | 4.71 s | 1.64 s |

All seven domain smoke suites (`core`, `skills`, `workspace`, `personal-ops`, `tasks`, `dreaming`, `quality`) passed in isolated invocations. `all` retained the complete negative-case chain. Green script results are supporting evidence only; the implementation still requires findings-first diff review and the appropriate product QA. The path-oriented privacy check is not a content or secret scanner.
