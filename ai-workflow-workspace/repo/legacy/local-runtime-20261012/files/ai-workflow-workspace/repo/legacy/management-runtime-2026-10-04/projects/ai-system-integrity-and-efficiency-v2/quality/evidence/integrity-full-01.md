# Validation Execution Record

- Script evidence role: `supporting-only`
- Semantic QA result: not-provided-by-script
- Final verdict: not-issued-by-script
- Residual risk: command success cannot establish semantic PASS or final acceptance

```json
{
  "checks": [
    {
      "command": [
        "git",
        "-C",
        "/private/tmp/ai-system-integrity-efficiency-v2",
        "diff",
        "--check"
      ],
      "duration_ns": 14566334,
      "exit_code": 0,
      "id": "diff",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 135072666,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-required-artifacts"
      ],
      "duration_ns": 40305125,
      "exit_code": 0,
      "id": "check-required-artifacts",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 149686750,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-readmes"
      ],
      "duration_ns": 4578292,
      "exit_code": 0,
      "id": "check-readmes",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 190040791,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-naming"
      ],
      "duration_ns": 1693220375,
      "exit_code": 0,
      "id": "check-naming",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 194658541,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-privacy-boundary"
      ],
      "duration_ns": 558948750,
      "exit_code": 0,
      "id": "check-privacy-boundary",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 1887943916,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-system-skills"
      ],
      "duration_ns": 756938458,
      "exit_code": 0,
      "id": "check-system-skills",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 2446944458,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-contract-compliance"
      ],
      "duration_ns": 179075291,
      "exit_code": 0,
      "id": "check-contract-compliance",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 3203961250,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-delivery-constraints"
      ],
      "duration_ns": 281821959,
      "exit_code": 0,
      "id": "check-delivery-constraints",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 3383094541,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-owner-approval"
      ],
      "duration_ns": 172043125,
      "exit_code": 0,
      "id": "check-owner-approval",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 3664984250,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-distillation-state"
      ],
      "duration_ns": 255807958,
      "exit_code": 0,
      "id": "check-distillation-state",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 3837093333,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-validation-routing"
      ],
      "duration_ns": 174548625,
      "exit_code": 0,
      "id": "check-validation-routing",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 4092961791,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-model-selection-guidance"
      ],
      "duration_ns": 149888042,
      "exit_code": 0,
      "id": "check-model-selection-guidance",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 4267575041,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-cross-system-upgrade-handoff"
      ],
      "duration_ns": 84745583,
      "exit_code": 0,
      "id": "check-cross-system-upgrade-handoff",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 4417529375,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-weekly-planning"
      ],
      "duration_ns": 257542166,
      "exit_code": 0,
      "id": "check-weekly-planning",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 4502340000,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-personal-ops-v4"
      ],
      "duration_ns": 30085000,
      "exit_code": 0,
      "id": "check-personal-ops-v4",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 4759949875,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-personal-ops-aggregates-v4"
      ],
      "duration_ns": 518260875,
      "exit_code": 0,
      "id": "check-personal-ops-aggregates-v4",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 4790078208,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-spor-proposals"
      ],
      "duration_ns": 406288750,
      "exit_code": 0,
      "id": "check-spor-proposals",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 5308390708,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-weekly-planning-v4"
      ],
      "duration_ns": 32123291,
      "exit_code": 0,
      "id": "check-weekly-planning-v4",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 5714732625,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-block-checkpoint"
      ],
      "duration_ns": 142179750,
      "exit_code": 0,
      "id": "check-block-checkpoint",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 5746898125,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-end-of-task-capture"
      ],
      "duration_ns": 512172375,
      "exit_code": 0,
      "id": "check-end-of-task-capture",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 5889136791,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-update-workspace"
      ],
      "duration_ns": 225487375,
      "exit_code": 0,
      "id": "check-update-workspace",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 6401367083,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-project-state"
      ],
      "duration_ns": 65596708,
      "exit_code": 0,
      "id": "check-project-state",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 6626921000,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-project-orchestration"
      ],
      "duration_ns": 147138708,
      "exit_code": 0,
      "id": "check-project-orchestration",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 6692578958,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-external-source-registry"
      ],
      "duration_ns": 201111541,
      "exit_code": 0,
      "id": "check-external-source-registry",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 6839774750,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-external-export-import-workflow"
      ],
      "duration_ns": 182900042,
      "exit_code": 0,
      "id": "check-external-export-import-workflow",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 7040961708,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-personal-ops"
      ],
      "duration_ns": 462225750,
      "exit_code": 0,
      "id": "check-personal-ops",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 7223927000,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-task-management"
      ],
      "duration_ns": 568575459,
      "exit_code": 0,
      "id": "check-task-management",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 7686218541,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-dreaming-mode"
      ],
      "duration_ns": 600539458,
      "exit_code": 0,
      "id": "check-dreaming-mode",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 8254856375,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-system-insights"
      ],
      "duration_ns": 118250833,
      "exit_code": 0,
      "id": "check-system-insights",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 8855459333,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-prompt-composition"
      ],
      "duration_ns": 95551791,
      "exit_code": 0,
      "id": "check-prompt-composition",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 8973769125,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-validation-profiles"
      ],
      "duration_ns": 337290583,
      "exit_code": 0,
      "id": "check-validation-profiles",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 9069386208,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-validation-integrity"
      ],
      "duration_ns": 7482889584,
      "exit_code": 0,
      "id": "check-validation-integrity",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 9406731791,
      "state": "completed"
    },
    {
      "command": [
        "/private/tmp/ai-system-integrity-efficiency-v2/.systems/scripts/check-validator-smoke-tests"
      ],
      "duration_ns": 226559429542,
      "exit_code": 0,
      "id": "check-validator-smoke-tests",
      "parent_id": "bfe496ca5f2f4bfab9a55518f30a4439",
      "start_offset_ns": 16889675541,
      "state": "completed"
    }
  ],
  "coverage": {
    "eligibility": "full-required"
  },
  "coverage_digest": "351ba0b98eb531daf3cca10c1f8a07cf76531f3857279ea295e53de9b4d2c79f",
  "duration_ns": 244302329250,
  "environment_digest": "c004aa74eb6b0f3c0c0b09c6b9b701eed9d60849fde6836d902303c42f758d35",
  "exit_code": 0,
  "profile": "full",
  "record_kind": "validation-run",
  "run_id": "bfe496ca5f2f4bfab9a55518f30a4439",
  "smoke_status": "completed",
  "source": {
    "files": {
      ".github/workflows/README.md": "7ba45e5b4194075e41020c8a4c2593086235061b39d88c2f2932a71cc88b865e",
      ".github/workflows/ai-system-validate.yml": "aacce41115fb7ef6c1c9656e7527ee52340aed7da45c71d14dac2125fdb48849",
      ".gitignore": "bc958cad651e3095a532533fa6f0bd9c5fbe38dc3dc0eebf26874f78ba9cfc0e",
      ".systems/README.md": "5cffc030d1de76ff17ff9e11d349ba055c2e1b3f59457c6a433f3cbc7073c408",
      ".systems/ai/README.md": "3c1d961426c808e61320737e041cd2aad6cc8fce981d85ae086d76902834e8cd",
      ".systems/ai/core/README.md": "f4aa86838349698e9709d8bee10c43d21cf776338fe9c567f4573e4046266959",
      ".systems/ai/core/block-checkpoint.md": "b77845af6b3c0669427c2695a45821d26ef7124dcd7afc1ff1439dd7cfd2afd4",
      ".systems/ai/core/branch-promotion.md": "b11a51ab8352f05716c2dfa1c964e4e1b26d58c8ab108f3d986efa50ce0505f1",
      ".systems/ai/core/client-brief.md": "f98488d43a1b3c497eb94ffa2fad5512eafd89316f37356d65cd9c6aa608565b",
      ".systems/ai/core/command-routing.md": "0ed2b29d3e31c0838e02782837eb30ea7d72acad7bc027455696567ff3541a6f",
      ".systems/ai/core/context-as-data.md": "d32c994887014f730e5d0dbae7b7cf0f39bb10c396588296fd8fac3475c85867",
      ".systems/ai/core/contract-compliance.md": "93960158568d611d140bdb49e21d51b5a33471ce54df350b417d9a35cbe9cb1f",
      ".systems/ai/core/cross-system-upgrade-handoff.md": "cb899dbfffd687ab15f3b68bb38d57805697e125f94bfe884e59553affc2622f",
      ".systems/ai/core/delivery-constraints.md": "9613785c514b52d7691d4439554d99ce8682c00e715136c42a62a0aee643f286",
      ".systems/ai/core/distillation-state.md": "b8ab79d0bfc4400cacd7279be349a798b0d8dc01e46c9fe9cdf226bcaf6007c0",
      ".systems/ai/core/dreaming-mode.md": "4fc26caac25a68b15b14e4455f70c26fc8535aaf9dd7011064efa30602ec36d7",
      ".systems/ai/core/dump-triage.md": "8fbc53cc1d18d6d04526d0461a28ca36e83c68024ece63d32c682ebd73cd7647",
      ".systems/ai/core/end-of-task-capture.md": "71c56304deed972e4224f57ce1e6506f3dbc7b8f9ac47dea38169d49bfedd964",
      ".systems/ai/core/external-export-import-workflow.md": "b5cfae399a46dfcb4dcf93c41095be46517bb76103289a0584a3df177106bc6d",
      ".systems/ai/core/external-memory.md": "7fb7c5e06b3d302aea28df3665a0ebe3d95bf8f6d93c0045791575d278feebc1",
      ".systems/ai/core/external-source-registry.md": "bc4702d40d8919b6d51fe27718e781aea8927d8586dea6b5046b692c27c4c928",
      ".systems/ai/core/guide.md": "f58687d8a2cd4855cc6c08a48f833b205e6bf45009364eff4a7d1b748a63be31",
      ".systems/ai/core/integrations.md": "716d5d1638ebe1d7d370715ba239e62c11293ebc71daf838adf0554a029a2634",
      ".systems/ai/core/memory.md": "cf933be4e13517e1813ddaaf3fe73e2e185d643e156f9aad2a6271403d064d07",
      ".systems/ai/core/model-selection-guidance.md": "6bd40a746f18473d0d15772f6a2437da68b559268c451fa4509d36048fc8b704",
      ".systems/ai/core/operating-model.md": "b8e3866b5d8174a1c1562c954f37859a128a1f91fceee789f0684a80b70bdb29",
      ".systems/ai/core/owner-approval.md": "c583974449aacbf2cd3c459910e02cd292e0072236245347587cf6f41b44ddff",
      ".systems/ai/core/personal-ops-aggregates-v4.md": "4c7b2761868bcec45b497b2185f5627aa2bcb75767de6cc7c780fa71e28dbe2c",
      ".systems/ai/core/personal-ops-budgets.md": "d22fcb280a3061e247a4a3a081045c4948a0ee2d891fed78a2d6324f9bec535e",
      ".systems/ai/core/personal-ops.md": "a2e9db74129b5ac7e7dad789d43bb4d2e7be02a7b04930762b9638eeabde96ea",
      ".systems/ai/core/privacy.md": "b2fa5ffe8dd88efbbc2cde46298697b4b109353786570a765ea911d0b6dd9a03",
      ".systems/ai/core/project-orchestration.md": "42de325305e33d4e009e5c0ad567f8a9abc47e9268f640dcd60db0b25b1b81b2",
      ".systems/ai/core/project-state.md": "ecbd7291e69541018adacb8656a35f0e52a892e2f59379053646d36b548cd808",
      ".systems/ai/core/prompt-composition.md": "8d8e1341c99cddac638688d3637efe26f77138211a810ad37618f26fd0c1c071",
      ".systems/ai/core/response-contract.md": "dfaa86a95abe7ae77676a1880dd2521db94e5a0496c550a942da364d9459c9dd",
      ".systems/ai/core/spor-proposals.md": "ea1341446b18fe9c53cc30f1ff63c669c06716ce87a3b2a38a5303c565ed4419",
      ".systems/ai/core/system-insights.md": "fd06f91e404847aab82ac32731afb18ee5b2a635f130401e0261d70b2133acce",
      ".systems/ai/core/task-intake.md": "6b5248e06809a7e2ef97966775b40526d4bb626d9ad35edcae92443db4df1bb6",
      ".systems/ai/core/task-management.md": "6b088cb0c4b1f59d977ee338b0c6a6d7cebf2a61fe2028173b0bcffc2797380a",
      ".systems/ai/core/update-from-upstream.md": "cdb4352dd450080e19acb75d7dc9b87b45495dd4250677a4b41f3d404bbd5f30",
      ".systems/ai/core/validation-profiles.md": "c2a12566b920c706dfc912c1269bc4f0e6eb75e66602a58f5ae98c5595d7e1f7",
      ".systems/ai/core/validation-routing.md": "6a9147cf9430496402903b85c7a66828b9c48bc8b99d3c9d4839ce39b2e8a1f6",
      ".systems/ai/core/weekly-planning.md": "1460b3e05ccf9d20e47f8d24e0d37345c64599bd459e9546461346a68fa8c183",
      ".systems/ai/core/workspaces.md": "28ba961b11af251fbbada3ac837ba0ca3bb1807e6a0e0fd3350398bf7887cbde",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/README.md": "926c25f733f082b2a70f36b88a2977e741b6adf0b22982442e0445b65414dd81",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/audit.py": "02d7de3732bb6dd4e600c495a789a82433908ae637ccb8915edaa2a7d53947d5",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/baseline-results.md": "ad8d1698e74fe07fb32ef0533bf3f8ca68d255cfdc6c4230e6cf2147da5d68b4",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/baseline-structural.json": "0227ea5e75cc85fcbf01c45f62f443307d1adf824b3510c3d3575e4d62913420",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/candidate-results.md": "a1a7c8304bd77acfb3e5adcae4eedcc853094f2ab76d50a6669d9036cad2ff65",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/evals.json": "0146b1c3f80e57d71841390d3105bdd6f761b1120448358d619d7333926e55e6",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/expanded-results.md": "0bf54773c2dc682c7cb7ec173b3b701fc67bf9c06ed292e59b4bc7d15a906f57",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/fixtures/TaskNotes/Tasks/.gitkeep": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/fixtures/quickstart.md": "c36b74c35efbb18401fb74a76ace4b52fae61794e827c6679661a96baf7633bc",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/fixtures/sample-config.json": "165c0df848ffaaf479ec5013ca5bd2e7aaabdaaf35f642f247135d44f4268873",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/fixtures/slug.py": "562301cd15ae1bc27d28601daa4ceb4067333ce6272231777ede3a8182aa793f",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/fixtures/test_slug.py": "8718f2f36345ee8eccdef6fef4e341da5ef100ea9105635909be522e0854e8aa",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/summarize_runs.py": "d58aa1a92801583833c89ddfd7866e19acfc8b9b583ecfc1d7fcae8e66240240",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/test_summarize_runs.py": "5dd0c3afa528ad08f85188db79a07d0e0e6324177e57d29a2f30f3601f569c20",
      ".systems/ai/evals/prompt-and-skill-efficiency-v1/validation-efficiency-v1.md": "878c8fcf404943e17b655836b33206c426c9d612c1cf00f64dd0942ed6e231b5",
      ".systems/ai/examples/README.md": "b292b922de686994a16b4d41bcb4cde7b42cf1732a81d6646f93aab5ed6f36a2",
      ".systems/ai/examples/prompting/README.md": "eb76696e3e9f8235df7cb126aa9f9e25044e931b7d2dbcbd30bb788c9bba7c75",
      ".systems/ai/examples/prompting/ai-system-operation-role-example.md": "0be72043c6c54ebbfaa468252e10b7dd372ce1351372390c9cefe73ca588e8b2",
      ".systems/ai/examples/prompting/client-collaboration-profile-example.md": "519d4c6e9d43066ca2fd1ca087c1114dfa616924efc63a33ca058ab267b49450",
      ".systems/ai/examples/prompting/project-domain-role-example.md": "fc2e02e3933bb2ef552f68755e046567834f859b5fa1a45af931d5201daac3a8",
      ".systems/ai/examples/prompting/variable-pack-example.md": "4c533c9e43cc40b5fba433eca6f4b2177a1cdb6250166e656ca6539a60e5327c",
      ".systems/ai/examples/prompting/workspace-prompting-readme-example.md": "8c202671401804e303d109610dd4a0a938cb7647d7612eff72368cb2174e23b4",
      ".systems/ai/examples/workspace/README.md": "d36572c47c9d6ad7bc19a3222dc24c4a4a00f3ae5a9ccd7082174eb137ebef65",
      ".systems/ai/examples/workspace/clients/README.md": "43449a7a72071ddcd4dc5815329ad98acd21c8b92fc259e1da86ecbba1cc0707",
      ".systems/ai/examples/workspace/clients/example-client/README.md": "8b306452e93c08cac755a3c64b07262b43bbc0177644e05f656e918efa76e508",
      ".systems/ai/examples/workspace/clients/example-client/projects/README.md": "242970bd5eb417866f8c9b5d6331435299e7c0efaa1901999eea6d9a63552c9d",
      ".systems/ai/examples/workspace/clients/example-client/projects/example-project/README.md": "68ae2c1989856b1fbbd3ab13429d0e821e632c27d5fdb98a5997394f0d4eef6a",
      ".systems/ai/examples/workspace/dump/README.md": "46e8c862ace8b9934debe03d31149caf2af9926066c6cacede6af083c3980de2",
      ".systems/ai/examples/workspace/dump/incoming/README.md": "5578b5ab7c808cd7f5f95d8376e781a020ff908b5deac9a017e43eb50d62215f",
      ".systems/ai/skills/README.md": "bd30da618424f5a7388672528c48db24358d35cb4f810f788d863bc6caf26f25",
      ".systems/ai/skills/legacy/README.md": "eb6cbb6a4c05d77b7cac683ced7a1ac0e30cad6460fee5725d2ae02207ccf4e6",
      ".systems/ai/skills/legacy/skill-creator-old/README.md": "f895fa0bda3618f32c8f88a95515f45cb18e22e83d398693a43e003e33334da0",
      ".systems/ai/skills/legacy/skill-creator-old/SKILL.md": "dcd4803e61e913e6fc27294184cd3a71f09f5e924ff20c8a9a20173e7b3c2bcf",
      ".systems/ai/skills/legacy/skill-creator-old/agents/analyzer.md": "bf68f4cac5a56c673a928c2e6d619586c5b93ea364026ab37547772cb45a663a",
      ".systems/ai/skills/legacy/skill-creator-old/agents/comparator.md": "fe1fc9787c495d864c5d6eada47396478572325fde1b33a96d78bf4b849b7a3e",
      ".systems/ai/skills/legacy/skill-creator-old/agents/grader.md": "57134da0c1a4eea33fbd74a1c9c44aa814f07d6bc64de303edb586f941e5d21a",
      ".systems/ai/skills/legacy/skill-creator-old/assets/eval_review.html": "ce477dcc74dc1c0d1d3352646a79167b5a63634e936b1019160025065974e452",
      ".systems/ai/skills/legacy/skill-creator-old/eval-viewer/generate_review.py": "fc9d1b9243fe5ab6012ebd579bd76d0035de1b79fd3b969de114defab26478fb",
      ".systems/ai/skills/legacy/skill-creator-old/eval-viewer/viewer.html": "a53213426ee1100441d701a3a0d49cda7a842f992d2c36463f4d3cc0258575fa",
      ".systems/ai/skills/legacy/skill-creator-old/references/schemas.md": "8e8876180a8989b406a4d3edddf875b04cdfd5805cc8616686d552b11ce4455f",
      ".systems/ai/skills/legacy/skill-creator-old/scripts/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      ".systems/ai/skills/legacy/skill-creator-old/scripts/aggregate_benchmark.py": "123ef128ea5ccc01a4b1ac212ef5567f21e9c13d3d240609780beeb3200c49aa",
      ".systems/ai/skills/legacy/skill-creator-old/scripts/generate_report.py": "13df7118a3c50c83c4c3250a606d5f2b20b25a3d44cbc392b3d669ec75281453",
      ".systems/ai/skills/legacy/skill-creator-old/scripts/improve_description.py": "686f346cd682687f16350aa509982f8c7dbc6d9b3bb8a3ad044d565ea21aef24",
      ".systems/ai/skills/legacy/skill-creator-old/scripts/package_skill.py": "1a33059b0db1ef73375d46d513e5ea81369d2e8838c970597b0d52ddef8d1c0f",
      ".systems/ai/skills/legacy/skill-creator-old/scripts/quick_validate.py": "f65315971b2a723349234947062de2ffae76cad98884b7f441e453e6dbe01892",
      ".systems/ai/skills/legacy/skill-creator-old/scripts/run_eval.py": "43e3b8f80dbf69c343967ba77e268fae991d9fa3ed68b32a0ff02532cd48657f",
      ".systems/ai/skills/legacy/skill-creator-old/scripts/run_loop.py": "7bd6f674203168520517eec94c55f493c0d154339b061b4d7c0f0dad187d0f21",
      ".systems/ai/skills/legacy/skill-creator-old/scripts/utils.py": "3af8ae62c40c73ab712207436a0d9a981e845f25c5a7040229eb189cc8e45bb1",
      ".systems/ai/skills/skill-creator/README.md": "3476df6f58ab1765be9d55d5c25ce45493b8f14fb91e66657d38fe2cc8c3d019",
      ".systems/ai/skills/skill-creator/SKILL.md": "717e0eedb382cbe8ab726ee3598834a3f9f33706a0356cbab6d393f4edac5867",
      ".systems/ai/skills/skill-creator/agents/analyzer.md": "df65ecd7350d705959c984b2619246eb4bb26e59d2bca3ca748e0aabfcf99ee3",
      ".systems/ai/skills/skill-creator/agents/comparator.md": "4cfb1b23491661127703a52724527cebdbf2822f6737372d7464a544eb579135",
      ".systems/ai/skills/skill-creator/agents/grader.md": "1e90d8b1b739621916e48ae7ee2a9fed32830e9b855af4a6bcbc3193237bda5a",
      ".systems/ai/skills/skill-creator/assets/eval_review.html": "5a2fb4cfc7e172491f5b8ab780ec1a75e3aad019f8059bc1473fa83c34b56bd8",
      ".systems/ai/skills/skill-creator/eval-viewer/generate_review.py": "f675c452284b83fe5b23364bb8392bd4d9ee700ef6d5b79e1d85626a28fe6d28",
      ".systems/ai/skills/skill-creator/eval-viewer/viewer.html": "55679880246dddda0fd2c3af9079f8f0ddfb8e848fa30a53222fd980af37559f",
      ".systems/ai/skills/skill-creator/references/evaluation.md": "774ca04fc1d579bbf8b17ffc3e13e4ba47949d0840138d5d38c8638a50645a03",
      ".systems/ai/skills/skill-creator/references/schemas.md": "ea47e8a598e3c6ddbc8bac1eebe61207540de9f986eaeca29450c53b2c754a6d",
      ".systems/ai/skills/skill-creator/scripts/__init__.py": "1c2cc39f0f52c7aff1a6390af122bc16562a3bc477725b424b22d75d06b18081",
      ".systems/ai/skills/skill-creator/scripts/aggregate_benchmark.py": "9bb2585462adfa9098bdd8bf04c6f6011caad97a35945e12408989e9d7b9cbef",
      ".systems/ai/skills/skill-creator/scripts/eval_freshness.py": "e8911c7cdb06f78c20ec483d4e6ac3c20324e4b7d4e716abbdef7df99b18f6f5",
      ".systems/ai/skills/skill-creator/scripts/generate_report.py": "1614ecbd70e76f7af964faa432a226787e027d76910acd373338a7beb687b82b",
      ".systems/ai/skills/skill-creator/scripts/improve_description.py": "faf8e920d1676ff18b04c301d453afb50415296b60fb017930bb0ca417a9daaf",
      ".systems/ai/skills/skill-creator/scripts/init_skill.py": "e1caade565750b4a4054c5e12a535687e61db950936ff4108a033648e018d2d0",
      ".systems/ai/skills/skill-creator/scripts/package_skill.py": "06921581ae9ae18f326d04eb03be3388b7ca6e8fe5af2570280511b7177d5b8f",
      ".systems/ai/skills/skill-creator/scripts/quick_validate.py": "c3f5105c43ed4a1ad29beff417fcbfdc1c49d098c55c106d5c6108d3770ee384",
      ".systems/ai/skills/skill-creator/scripts/run_eval.py": "7cc130e04063b305fb5ed5d9fd712d59a2836e71c4b91e6b4a30cef1dcf2b9dd",
      ".systems/ai/skills/skill-creator/scripts/run_loop.py": "5a75184da03f7f5dc73b2a9cd0121407a607b08174b02c57a89b079bd4cc84cf",
      ".systems/ai/skills/skill-creator/scripts/utils.py": "3fbf8407ecc9a11a7b65795d110dd943ba65e79206d7dcf201e8201781afaf04",
      ".systems/ai/templates/README.md": "b7d4be48fbb7011d3d70f60a512257b90701de0776ff6a1c63c7738589cc0286",
      ".systems/ai/templates/capture/cross-system-upgrade-handoff.template.md": "ff75dde16e1ca8fdd5299a2cec68ee4f86b6e4c119e9428f58fb5e9b7f78bf03",
      ".systems/ai/templates/capture/distillation-state.template.md": "941053a4eeb0c4e11fa474194b6d5f81eab9c3f9a18f5f2cf904d254dcef8a3d",
      ".systems/ai/templates/capture/end-of-task-capture.template.md": "6442a35cf91966b157184245183ff9b3ce63b171ccd9958bdc6691f3b817a618",
      ".systems/ai/templates/checkpoint/block-checkpoint.template.md": "1a97ecc8411b2bd8d18aa987243e6d686c8a6a408abea70d3eb7de9d3ad97fd9",
      ".systems/ai/templates/delivery/delivery-constraints.template.md": "12af8086f97e1054176a76cd4a43bac25ab01cd0d998d44dab29932c0474524a",
      ".systems/ai/templates/dreaming/README.md": "28bcb4b018d7aa63dd279f6001f53733a1da6778409cc1e7cfcee8aabea4d619",
      ".systems/ai/templates/dreaming/dream-report.template.md": "9caa508871759cc5528f11e95a168ed0e8c25c9845d5d428a5af5fce71583225",
      ".systems/ai/templates/prompting/README.md": "1580c5e9607684a9102abb2c5c0b3f60ce9d9818062025a7928753929774c0e9",
      ".systems/ai/templates/prompting/ai-system-maintenance-baseline.template.md": "1b044ff08a7150605a5410506521394f4a8f05a9e5cc8b59432fbdf6335fb119",
      ".systems/ai/templates/prompting/ai-system-operation-role.template.md": "21afecb398d9e82a0c90a6afd3e7b6c1072d68dea89f1ef8713d2e68aab4ddbb",
      ".systems/ai/templates/prompting/client-collaboration-profile.template.md": "468c84eb8d160ab5b22730d37f8c8f241c40271d6af91c6315f6ddba12943385",
      ".systems/ai/templates/prompting/client-prompting-readme.template.md": "38a948ec50a8f62afba10a61191fd7d72578d786c452d01b66881ba528c88ee0",
      ".systems/ai/templates/prompting/project-prompting-readme.template.md": "6cf593d47a09fb7d176f6710f5c4acd74ff0201b83ff3dba2f9d7f4345071a77",
      ".systems/ai/templates/prompting/prompt-module.template.md": "3cd339b00ac245ed6e04fc64ef9c72cb5d8f3ff7b34dcbe7c15dc54e87f46915",
      ".systems/ai/templates/prompting/role-profile.template.md": "cfa10e533cbbab0436274c68fe123416519bc0531ab914024b491bed8265c8cb",
      ".systems/ai/templates/prompting/variable-pack.template.md": "d6da46eaf3ff033380f4b0717ab25a587ceebf6265c3423a7994923935cf2750",
      ".systems/ai/templates/prompting/workspace-prompting-readme.template.md": "5a62361aa6f3b6806e07553d3b69deaf083fcf1750705cab9250a4390a8a09ce",
      ".systems/ai/templates/quality/validation-execution-record.template.md": "cc55affd8c2ba19340b4c04f7b69b008d8d79c5eeb6a65ce9bb834601e5733dd",
      ".systems/ai/templates/root/AGENTS.template.md": "1e9fe90a98e5bee325332919057cc1106af8b48abe5bdf3c9c9da8bd4eb6ee34",
      ".systems/ai/templates/root/README.md": "14131a731b2c3ba6f137ee0fd15c22add1603c23218c7834e960721fc4d97fac",
      ".systems/ai/templates/workspace-registry.template.md": "d6e5ac10eb63c7e95fc98e3968dacd7da94772dbd42bb9f4349d038c6ef61ed0",
      ".systems/ai/templates/workspace/README.md": "34643c1f0233e3025eb0f2c1ec581b54375f0f7743367e325e51ff3a0c9c6d2d",
      ".systems/ai/templates/workspace/archive/README.md": "30218e9f8b0b274932597cc2f7ff70d6184f157bc076fce3b3a63ac0ab8f6573",
      ".systems/ai/templates/workspace/capture-state/capture-state-readme.template.md": "b367329b73cc12cca58c3b9e91be0e5c3fc9ac9b4c1cb4d55c705e49851eb73f",
      ".systems/ai/templates/workspace/capture-state/capture-state.template.md": "25e25f6ccbd04e8a3199b3aed3420052d8c90f9008af94946a462c207af601db",
      ".systems/ai/templates/workspace/checkpoints/README.md": "e9d20aa0aa9a3d85846706032f96cf79adc598a6dcaf892c1cd9affe0adfa2ce",
      ".systems/ai/templates/workspace/checkpoints/blocks/README.md": "a082755bd6a4e1b7e8e1d9e1cd46e88064a119db2d726ed527da9d145006c830",
      ".systems/ai/templates/workspace/clients/README.md": "1281048c33376634106a7d4bb32a48cb31913474e37db8908f05d3202415a8f2",
      ".systems/ai/templates/workspace/clients/client-brief.template.md": "70a2d06bd5cd3c398d51036043e28d2413dcbff760dd3a4502ba271696e8d197",
      ".systems/ai/templates/workspace/clients/client-memory-entry.template.md": "1d7537c19112f5b28bf2cb41fc1826128b6d02df0d11ebd3bf546a0bd547b60b",
      ".systems/ai/templates/workspace/clients/client-memory.template.md": "dc2e3355b7b81554cc48a93b580aac2e65626486c9e0e76238bc24427403b9ba",
      ".systems/ai/templates/workspace/clients/client-readme.template.md": "421ab5aa348c2f5191830defaa569d18027c850808732c853221c2a0313db2cc",
      ".systems/ai/templates/workspace/core/README.md": "6a9cb3ad4e81a0fd07e1d67b7af9e0cffb08ccf27791c0c547927210d0ad7fe6",
      ".systems/ai/templates/workspace/core/status.template.md": "035bef949bcfb6e5519b0dc30ac380df09b8e8830a788b9a4ff3df836a5f3183",
      ".systems/ai/templates/workspace/core/workstreams.template.md": "e040bea15a178096796caed06fdd71d36ad562f91a4aa0db07d9a0128dd88264",
      ".systems/ai/templates/workspace/dreams/README.md": "a1be0cbab46e0f08107b9a7db9a5bae7117079f222c35d5836e4e0a121ce52a8",
      ".systems/ai/templates/workspace/dreams/dreaming-scope.local.template.md": "9823cd69b196197c6f95e90eb6dd7501b57198aa191c33be1ae80e72655019ca",
      ".systems/ai/templates/workspace/dreams/dreams-readme.template.md": "1ac8742a17a916aeb7f80d9f2103bf2ce474e92ed1e7fa591000bf1894b28c70",
      ".systems/ai/templates/workspace/dreams/legacy-dream-reports-v1.template.md": "d81e2d0f8fba709a3b12f5b83fe6cfa45ca00789a5ae3a7cb8ed8114933a532b",
      ".systems/ai/templates/workspace/dump/README.md": "7736ff4ed46b1bc1190c630dcc07dc1b6155c3a8b865e8b213be0285004f9cee",
      ".systems/ai/templates/workspace/dump/classification.template.md": "40552aad907b959fbcfdb0e5850c50ebc7983ef90817a75ab7f947c613b75be5",
      ".systems/ai/templates/workspace/dump/external-export-classification.template.md": "ca1455858f013ba43545b89aec2b706834698f443eda7b34ccfd02389f78d764",
      ".systems/ai/templates/workspace/dump/external-import-checklist.template.md": "73ca3f15b3cb29b79447b9f43b184ae9318838d8644a9bb489629f6b766c15cc",
      ".systems/ai/templates/workspace/dump/final-import-checkpoint.template.md": "18312d7b65500bf73beee00f79eaab8c4076659de7f39766f14f41b40d365f57",
      ".systems/ai/templates/workspace/dump/metadata-import.template.md": "2d4e3004b0370381699b0161c975c77927650370aaab5ceb30036df4366b89eb",
      ".systems/ai/templates/workspace/dump/raw-export-readme.template.md": "0bea5d28ecfdf8916349699c7236a3267f4a72b4d2cb6394be9b8d83da740c69",
      ".systems/ai/templates/workspace/external-memory/README.md": "450edef5e3265e804e2fc645eba1f7d1adea0c5e1fe6e97b7242535dc178cfc2",
      ".systems/ai/templates/workspace/external-memory/memory/README.md": "930a4efe4f7e99cb7c5835c03ce0e3f27b59c96420f9e5e321f15bb0c4d7b66f",
      ".systems/ai/templates/workspace/humans/README.md": "6121f06990f9e3b656f3b9546aac7d1ba0abde8cca61a6c37b67d1c8afa712aa",
      ".systems/ai/templates/workspace/links/README.md": "023033bb95f66d869d1d9bab28cc6e6a845af98793123afaaa1c2f61e8a3fa52",
      ".systems/ai/templates/workspace/links/links-readme.template.md": "a2116d154a300be68abbd07338a3bb1c1d2e47e96fe413cd70280d3b1068bb68",
      ".systems/ai/templates/workspace/links/source.template.md": "05b9c3e2ed5a064d95881c68d1b7909f3239b36d2972447d08515825b005df73",
      ".systems/ai/templates/workspace/memory/README.md": "2c0e340945494b0b5cfdcfcd96dcea69a7a941144729ccb0c7b0c634975ca190",
      ".systems/ai/templates/workspace/memory/memory-entry.template.md": "fd065a13fb171e9f486578a0303d017385bc8981f97e13a52cb0e73cb2efbca7",
      ".systems/ai/templates/workspace/memory/workspace-memory-entry.template.md": "e160a3a4adb3874a81ac28346edfea5c4b30883689c187e62802dcbc5a54050a",
      ".systems/ai/templates/workspace/memory/workspace-memory.template.md": "1395ebd90883a160bbd16ece6973d033cc93663dd9b6a267c93330f3f49624c2",
      ".systems/ai/templates/workspace/micro-projects/README.md": "ad4c7129d384f71f0c47577c5784fd5b2195fab3569517d533698043ffc486e9",
      ".systems/ai/templates/workspace/owned-assets/README.md": "6566d73c9971666b2545fd4fd6e70fcb013ccd507a99b843c720ea292a605d4e",
      ".systems/ai/templates/workspace/owned-assets/owned-asset-memory-entry.template.md": "f153adbe7995598e6432685420c9e0c3d57378a19e2d53faf70813b9b89cdf4a",
      ".systems/ai/templates/workspace/owned-assets/owned-asset-memory.template.md": "ddbb987568855c355abd2d4b2eb1cd58254c29effafec3b5ad341273bcb3a419",
      ".systems/ai/templates/workspace/owned-assets/owned-asset-readme.template.md": "8bb5f88d9618df82d03a8c0a868012899a084eef15d3294729fa72fcc2163b83",
      ".systems/ai/templates/workspace/personal-ops/README.md": "ef153ea96a17a6927723dbef01e6d6fb2bac3d5a633bebe7d00de479a4ae39e0",
      ".systems/ai/templates/workspace/personal-ops/check-in-properties-v3.schema.json": "6783ce329bd7946bb01edad06d9edc0efe964bfde006aba8c2c4cca023cb5a35",
      ".systems/ai/templates/workspace/personal-ops/check-in-properties-v4.schema.json": "2d51203a494ea47ca3c4412efb0d92c431da33d05c1ded029f91e38a3fb4f8d6",
      ".systems/ai/templates/workspace/personal-ops/check-in-settings.local.template.md": "598fbec22ce33a2765b0df4e644038e04cb5eca4cfd658ae75b288a531d549ce",
      ".systems/ai/templates/workspace/personal-ops/check-in.template.md": "0eb1d82b5abfe5f11e9f9529eb793b9b669e5ea4bdd2ad754bba690a0859f806",
      ".systems/ai/templates/workspace/personal-ops/check-ins-readme.template.md": "3927ab8ef41254d0384e0f435f9530374777de51b4c3bc49fd5993b091ecae19",
      ".systems/ai/templates/workspace/personal-ops/check-ins-v3-index.template.md": "2b69a1512c9c9a751ff0da5b22db63c0987deceb45d843693f2d8034bd785e83",
      ".systems/ai/templates/workspace/personal-ops/daily-spor-proposal.template.md": "ae8c024943af4eecafe4babb93d6918adedcd09eb898d1b72e6dc3717be5c914",
      ".systems/ai/templates/workspace/personal-ops/manual-daily-check-in-v4.template.md": "b9ee7c1184954f88d8991212def8153900566a8176e9632c47b0ad1f2e94ba0c",
      ".systems/ai/templates/workspace/personal-ops/manual-daily-check-in.template.md": "b1a3cc2c3ec778bef76de850e6a6891497bd5bca5c666ae27e727e073254e071",
      ".systems/ai/templates/workspace/personal-ops/personal-ops-readme.template.md": "28b45e07cbb7b33a0ea52acec2a91835b399d402c365e7bc93b0e310e2fdece2",
      ".systems/ai/templates/workspace/personal-ops/weekly-check-in-v4.template.md": "e0baa52c3e8102c992f75607b3227eaaf9941c5685383b5a3768e630e4be17c8",
      ".systems/ai/templates/workspace/personal-ops/weekly-spor-proposal.template.md": "38e1b90574c28a4ac045426891fd1003dce4b554fe987e44f4187469f9f3c4f3",
      ".systems/ai/templates/workspace/primary-entity-directory-readme.template.md": "81ccb0330ab57e65dd56b8025f32f1e7970f95ee30d3cb06ecee59ec3b07b3fc",
      ".systems/ai/templates/workspace/primary-entity-memory.template.md": "e52f0eb359902bf3c5b780cad9623adae7c158ec44cd955922220ea868bef48b",
      ".systems/ai/templates/workspace/primary-entity-status.template.md": "eb25f49d3336acc07600d121d1ba1ab6db90af36e88691dc15d66672e725d7a8",
      ".systems/ai/templates/workspace/primary-entity-workspace-readme.template.md": "736983695575d758bc204ffe07bee54c5d4e154a35b7755eb1cfb2055887aa11",
      ".systems/ai/templates/workspace/project-state/README.md": "7ced5caf68841a8310e56655a1e5aac6c454d616daa631373c4ac9638c219621",
      ".systems/ai/templates/workspace/project-state/orchestration-record.template.md": "3788052a4af413e42121ae6330c321be66d644523f0db8e94a3e198f7c43ac80",
      ".systems/ai/templates/workspace/project-state/project-state-entry.template.md": "1acf71d662717b95a707f9c5b94cb97233403f81829921698b562225805627aa",
      ".systems/ai/templates/workspace/project-state/project-state-readme.template.md": "c4209fc2df5ea3023cfdd17980f0b1bf520c8a035de63900c955bf809882f995",
      ".systems/ai/templates/workspace/project-state/project-state.template.md": "8f752f0ea261b357439ae5def2f088e18d918a7289c5fa34691a48427d75dbe2",
      ".systems/ai/templates/workspace/projects/README.md": "11db4bf174d6d9c4ba71401d19d488a421c489433fbfc48e7f85153e0f1b50f2",
      ".systems/ai/templates/workspace/projects/checkpoint.template.md": "4c16fff0e57a5bbbf5c6c84312f42b389508292d5c2fec7e65ac205ee1f04994",
      ".systems/ai/templates/workspace/projects/distillation.template.md": "d3d5693a27ef95b8ccf559daeafd2df83f4599c44d507e3af3e744a697d426b5",
      ".systems/ai/templates/workspace/projects/project-memory-entry.template.md": "652f8a55a31cb4846f9e5301e31ffd8c20e7368b86a3e3763824a0924f02eda0",
      ".systems/ai/templates/workspace/projects/project-memory.template.md": "b3b7415291c41bf9c9c310f7873b1e17276def6faa4d8b52aaa8b92e2b2846db",
      ".systems/ai/templates/workspace/projects/project-readme.template.md": "28e2396e254a52e8e58ba06b2fe324e14e0ea9dac11b58f9a1e02adacf630c47",
      ".systems/ai/templates/workspace/skills/README.md": "ed45ebc83548892f9911ad67fc669689cb8e321f0f299ad195f5cd2837909d1c",
      ".systems/ai/templates/workspace/skills/skill-intake-plan.template.md": "6bcf07aa6c0441be3f18914fa82ae98701797e8f9d7656bf1b78ef7437cc17a7",
      ".systems/ai/templates/workspace/system-insights/README.md": "02d1af171e45b40c0f590fd81e4fc0dc29983108866d75526a6be2ed77284a54",
      ".systems/ai/templates/workspace/system-insights/insights-readme.template.md": "b11aeb3e6cbf59c5d11242c9507368d4f587566c851943c1addebecf37cce775",
      ".systems/ai/templates/workspace/system-insights/system-insight.template.md": "e356a7b706d0d9835dd33bf935c641d97f0ea3d983a646baeae79bbe23bb0c56",
      ".systems/ai/templates/workspace/system-insights/system-insights-readme.template.md": "89de471497065630fd764f4292216eeddabe62ba189b64c1417099cbc0b84e6b",
      ".systems/ai/templates/workspace/system-insights/system-insights.template.md": "93a2cf87670ae3e2bba624bed87b0c7e0aff8169a534b2b05a7fe97da6bd1f35",
      ".systems/ai/templates/workspace/tasks/README.md": "d257f6cefc8d8413e8f446ee27e8f2f353b498547e07e5d6e4f06145662f88e9",
      ".systems/ai/templates/workspace/tasks/task-candidate.template.md": "9b4b3e4a090476468d729efcde24b71867ed4accd6c34705c909055b44440c44",
      ".systems/ai/templates/workspace/tasks/task-management-readme.template.md": "84a3ca07daa9f453c984327274b520357d50766f0bca14b39fe19a3967c5b151",
      ".systems/ai/templates/workspace/tasks/taskforge-vault-setup.template.md": "467e7b3a4db00f0685a1bc0040dac96e58f78d137355f609bbcd4fe9ef487679",
      ".systems/ai/templates/workspace/tasks/taskforge-vault.local.template.md": "fcb43be5624d435231f622b2ac48cd95204e384aff86ba431f8d92fec960357c",
      ".systems/ai/templates/workspace/tasks/tasknote.template.md": "cc69d6a30941acea82bc1f2eddb582d0c60f50b3ceb8bc03f5906180c8c091fb",
      ".systems/ai/templates/workspace/tasks/weekly-plan.template.md": "fb36dfc694c111386d620448ef5bc15a5249a0b1de4ecd8550d6bc64ae42ae7a",
      ".systems/ai/templates/workspace/tasks/weekly-plans-readme.template.md": "9622a8440d49f21884ca3009cd6c8aa598a57f6b6e6ebb6036fa91d92ac54f43",
      ".systems/ai/templates/workspace/workspace-readme.template.md": "a119e784f1fadca8d1913177c060cf55ff22b1a9ce7db3a67256d8ab20dacf0e",
      ".systems/scripts/README.md": "19e252adb3c904001c41e06f34dac712369c7ab740fbd1896cd24c3932d768a8",
      ".systems/scripts/calculate-personal-ops-budgets": "519c5509332d9e467d45f292672cf501693a68bc305cfee99df18b4e0508be2b",
      ".systems/scripts/calculate-personal-ops-life-alignment": "1b2d11ec35e97bf818097b0c587be15dc486af63bea15c30443d025fdfc7bc0c",
      ".systems/scripts/check-block-checkpoint": "8f75bc17e3c4b2ebc9ca7972d87e33ec385b3ba505713737486531da62c5daa6",
      ".systems/scripts/check-contract-compliance": "43b8d684b078954708cdb640e51b9b8b41e67928177092511623a0377c892ef9",
      ".systems/scripts/check-cross-system-upgrade-handoff": "e3b41d0c31f576490c0e27d0682bfab33dab7e383ca7c1662cad5b76ea134b4c",
      ".systems/scripts/check-delivery-constraints": "4d47f508401a563d618451a5a5bab9575bfa5a2df0c52d9c3fb716d89f483eb1",
      ".systems/scripts/check-distillation-state": "a65af266b591cda891b763047e21bed9c0244fcc08637c9390f386731ae814b6",
      ".systems/scripts/check-dreaming-mode": "e40dc802a6b6d03b6a4ca242af1ebb32e6d83fa8b997021724572dcca84ce3f0",
      ".systems/scripts/check-dreaming-scope": "8da817c1ea1e75c530dac98dcee13f14a8f58c484f322fa692bbdeb77b3be13c",
      ".systems/scripts/check-end-of-task-capture": "5a0c4e8c7bf5fdd07e3f817d7f5af96d15a23fc7171977af508e4426717ca559",
      ".systems/scripts/check-external-export-import-workflow": "61420346ebcef6a8486b1c8700a74cece1e6f8aa738185dcbeb3a067d7b98d7a",
      ".systems/scripts/check-external-source-registry": "c486171332a5ca6f7111458da50a7e22aa22061dd4bb060e6f140704ddb4b9d4",
      ".systems/scripts/check-life-alignment-v4": "56d1c1a5d994cb7440a937daa1c38bcd65998fe76a45821d16930b750c938cd1",
      ".systems/scripts/check-model-selection-guidance": "6af06885054d4fac34bee55ce31839589edbd5e099729eae1cfe5194d6810874",
      ".systems/scripts/check-naming": "8c960134a7c32bf285039e757882d30f6b7dd884e482c1fec47114c5510bbb07",
      ".systems/scripts/check-owner-approval": "3a41f40ae6ba16918e4ca13d11245108d55ac2fb4466d32fe1ccc9d999a3f363",
      ".systems/scripts/check-personal-ops": "db257d6c3c695be883be7714fa0de1f2781397ebeb89f28763d7d3bd71e1c8e2",
      ".systems/scripts/check-personal-ops-aggregates-v4": "5d05c14a9f458bce9e413aa103b2ea14e26f49f8a502bac8c37a74e7d90fc499",
      ".systems/scripts/check-personal-ops-v4": "b3c1df0e8f24d3b0f12f2fae2750d2ccd46327f97f74815fb60c4f7e77ea3f97",
      ".systems/scripts/check-privacy-boundary": "a0b090d0fa50f4766d0856715a4dc3d00196897a4836c149708198073a1c65ed",
      ".systems/scripts/check-project-orchestration": "8e401f5b69baabb6aa024b26f7649b65b7f0d5250e7e9f9f1a96b81970c935c9",
      ".systems/scripts/check-project-state": "85894ec7aae65c5b7d17ace9464dbb4de9c3a8d66f025364fa6f19d9a884c38a",
      ".systems/scripts/check-prompt-composition": "cc3b5311f6659e853d22bb1ca3f367eb6863862e4eaf411a0edbc33205816569",
      ".systems/scripts/check-readmes": "5d454c9845d7620cba94771b408d06d7d1d391533bcb1e46c6c51011d64be857",
      ".systems/scripts/check-required-artifacts": "2fd0f08d35e0b6eb582b2f8b726c15f989990085010928138f98a9c44be2f5c3",
      ".systems/scripts/check-spor-proposals": "a44dac47195fd9069243b28044aff5e332f002693eeb492d04cfd84524a61f64",
      ".systems/scripts/check-spor-v4": "066d057a556988a04acaaffc7a671eed7e5293c69c812541ea5769afd66e00f0",
      ".systems/scripts/check-system-insights": "fdbf23502ce848000c4616720a4a348e9a710783d03841bd605b95ed22a88a37",
      ".systems/scripts/check-system-skills": "824c6b9dae0e2db3d3ed77490b9e906244c3bceea623a8a6bd6ecbc37e1a25a2",
      ".systems/scripts/check-task-management": "7975d5adbaf0c8d9437d2d935a04e6ba9c6ffcd3affa6557de6f9cea8804b6c1",
      ".systems/scripts/check-update-workspace": "4c70a2bb04d8f9d30b37ea6ff05d83c52f28dea72929b56743e420396cc5188f",
      ".systems/scripts/check-validation-integrity": "a4ffa11cecfc8f2f223f648f3e1b208fad9c32d05a48108377e62dffbd9b0db1",
      ".systems/scripts/check-validation-profiles": "ca3f2fc51f8f8abedefc15b4cc52e626ed16b1af32f92381f416a5aaf8684365",
      ".systems/scripts/check-validation-routing": "7cfa61f20648857f2488c8f46982587020567a5d034aa98fb0ac053f862df146",
      ".systems/scripts/check-validator-smoke-tests": "9d885e72ae4ab516792936c233b5ab62962cb84f074993f7ad25e0ad5ceb71e5",
      ".systems/scripts/check-weekly-planning": "0945dcf343fd28a7f9cd4a23596ba062e9c86f79124f9671f400da6af3f0561e",
      ".systems/scripts/check-weekly-planning-v4": "73108bf4608008c1ffad5d2d23f6aefa5d9f536634f7ddc8f0b5cdbe2233c6c5",
      ".systems/scripts/discover-skills": "5b23040e09a79f717fa1bee2f92243831fff51583804f9f4661923df7dfbca3c",
      ".systems/scripts/dream_recommendations.py": "0fd6fd04a503999fc16e9041d4da837afc08234eab92f5b469499204153cb5aa",
      ".systems/scripts/init-ai-system": "87e5adbc4dfdf36fcb210a8b96065d1e7be2239dfc9311babf4a40ce122458f9",
      ".systems/scripts/init-workspace": "977e984fce90a4b54d351de2f6be63b38044a0975b11c7ce2e3da112d33acbeb",
      ".systems/scripts/lib-workspaces": "4ce9c86e402b6c63eda1e15bc3952c23ce70818fbc9a0eb56aff6e18317a3322",
      ".systems/scripts/map-notion-check-ins": "f3d01e4ca0f5343c695c9d8b45ae64360ac3df8f919ba611427bacc80bc76496",
      ".systems/scripts/migrate-personal-ops-aggregates-v4": "a65f5847fda612364e4d12e4c3f34a1c3d189e8a8ff34247ef9fae5c6cda4dee",
      ".systems/scripts/migrate-personal-ops-legacy-check-ins-v3": "61f390d49e2b98f3b8d2d5f8cd13f61b349c8ceea4a9c921068063ba5b06ab8f",
      ".systems/scripts/personal_ops_aggregates_v4.py": "d817f5d99eea1f4a29af53dafaa5d244ec733220369320c8794880cf88d950ba",
      ".systems/scripts/personal_ops_properties_v3.py": "e701a7ad88a7f8a90cf141e8bedc65a4d16c98ff20cd42c2b7d0d7f2d6be870e",
      ".systems/scripts/personal_ops_spor_proposals.py": "b24b1fa285a16873b2baf7da8f92c8371e93491dcac54937f732a9a7145e09eb",
      ".systems/scripts/personal_ops_v4.py": "84652503ce15515275f1a9191cfc0c736497abf4956115e7d0059a0f10aad94d",
      ".systems/scripts/prepare-personal-ops-spor-proposal": "199a8facc10dcccb5b68c7ea9d799fc5e6febe97be062c8b7322d4b27db9dd85",
      ".systems/scripts/project-orchestration-preflight": "a358e85655152d7bf2ef6ecbaa14cc90626fecdebb08d97cd37e60ec7ca90db4",
      ".systems/scripts/propose-task-candidates": "30f94669f220e1612d3d31543ce1988bcfc39318038f207c327fc992b748def8",
      ".systems/scripts/render-personal-ops-daily-summary": "4ce36d0f5db31ba033cc03d1de38f9e87058fd0ff827702e96092ca36903991e",
      ".systems/scripts/render-personal-ops-daily-summary-v4": "090f1cb44528dc40bc44863bc1caf9b069d117eacb59dce2a99898e5c7abad56",
      ".systems/scripts/render-personal-ops-weekly-summary": "7a404157e7db598d3ec7db2a09a5bc0f9dc2c9fef6f826eb564dc15d784e2a69",
      ".systems/scripts/report-contract-topology": "7d296d1cee64b85284231ac5d5f32335ed97435a6688f55d73f860003cb087e4",
      ".systems/scripts/report-validation-comparison": "da46d0196fda417a14b8b8143789564052e889936a583131823bcb115e2d4f50",
      ".systems/scripts/report-workspace-freshness": "12ca8314f7246e80fdc87651bbfb94149d505b097ff0f740641e924449e724f5",
      ".systems/scripts/smoke/README.md": "c496077a382acd29a6ed3c0dd0ccafe1e4c1dabe06b647b5cbac129696a515c5",
      ".systems/scripts/smoke/negative-expectations.json": "be2f9f720068fa7a1b5518901a3d145593c336c40240b8d0ab77ee2aa79455f9",
      ".systems/scripts/smoke_assertion.py": "d4981381a3ac05233f1fc86873d0cb46c1d2a21d665a40f76b8b6f4f07d260fa",
      ".systems/scripts/smoke_coverage.py": "bdde95c8557078dea06f0343b07a3e3ed9e99e7fa3d40b2a334338bca5a2ba53",
      ".systems/scripts/sync-personal-ops-check-ins": "89ecb1df54ebb720026438b21328512e546658b7b894ae2ea13429cd0d7f880b",
      ".systems/scripts/sync-personal-ops-check-ins-v3": "9e40e3f0ad4c53a47fe477a8679cbd6edfdc5e66db5ac11890c8ada265ec536d",
      ".systems/scripts/sync-personal-ops-check-ins-v4": "3c250f1288a8d2255c035b9872bf46ca6cc0fe5ae0793c0850e17f01623fef4b",
      ".systems/scripts/tests/README.md": "d1621b88850af8e25d79f9e76d4f265de60a19d827018381e23010da28070e17",
      ".systems/scripts/tests/test_validation_integrity.py": "23d1c29c020ec83836a26962bac0300fb61aeba583681b69ebca92999d4fbcc5",
      ".systems/scripts/update-from-upstream": "3c4959f68f07bcef3add6d4dbc4172d973e953f93f140a899220f69373f36bec",
      ".systems/scripts/update-workspace": "917950f3c45b1d1ef6b83c2582f19c9c436e8dc0ee61f5fc92477536abbc6f27",
      ".systems/scripts/validate-ai-system": "cee4ca7a1a78c96df91bf1595572c9cd15498f0496b14a9e487fec4448342c86",
      ".systems/scripts/validation-dependencies.json": "915273e4a758f4e983535bb9a75a5504c2ef9f2aa29c04c0256358ffe7aae0dc",
      ".systems/scripts/validation_runner.py": "a41469e162c89ede55ab3c4b7f5161971854771d8fffedee4bee71aa73c8d1a8",
      ".systems/scripts/validation_support.py": "834e37875531aa2ef028f39a98a8bb50b6d2c5b2b282f6485d96678395140127",
      "HUMANS.md": "b0e1438d8ecda5bece215c54174fc6f7316a749c1719dd1b72d87abbee58acbf",
      "README.md": "9f2df502fc92ac216aa947473993e72e8b76f1c57135df386ba0b3e652b47fd5"
    },
    "head": "dabbf3457b98cd28f44b7785f14ece51b5932017",
    "source_digest": "87b9137c85f3f6daca2448f7a5de3c981f5f0c2e9cd3317e490a6ffb61b41eb4"
  },
  "status": "completed",
  "supporting_only": true
}
```
