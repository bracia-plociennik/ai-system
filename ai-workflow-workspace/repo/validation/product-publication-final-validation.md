# Validation Execution Record

- Script evidence role: `supporting-only`
- Semantic QA result: not-provided-by-script
- Final verdict: not-issued-by-script
- Residual risk: command success cannot establish semantic PASS or final acceptance

```json
{
  "checks": [
    {
      "binding": {
        "category": "environment",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "git",
        "-C",
        "/private/tmp/ai-system-product-publication-v1",
        "diff",
        "--check"
      ],
      "duration_ns": 17661000,
      "execution": "executed",
      "exit_code": 0,
      "id": "diff",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 288219125,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "identity": {
          "coverage_digest": "1b6d3040fbec1a37b39f3b59486ba1025c0eecbd9708cab92535690cbc1c2f38",
          "environment_digest": "f1a2a18f81ecf1c8a501a53116ee4d629826d668536abcd641daf4a0c2f66b23",
          "implementation_digest": "c19a5961d049665443e9b46f3689076fd2c559450295cd1d9791bf97188789ed",
          "inputs_digest": "e2a0156844a7c8893bafb8e76c7bc91103b53b330070db31989c62594b1d22a6",
          "parameters_digest": "7ccefb6adbe611bf88bc0bee220e8a614ac44629478461f1b91f1c8e4bb8d002",
          "root": "/private/tmp/ai-system-product-publication-v1"
        },
        "identity_digest": "e1ae4d4c94da7eb71577d4485ec99aae793d168d72fd762ed12a14b96bd4309a",
        "reason": "Complete declared inputs",
        "reuse_eligible": true
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-product-publication"
      ],
      "duration_ns": 8684069833,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-product-publication",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 305940709,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "identity": {
          "coverage_digest": "1b6d3040fbec1a37b39f3b59486ba1025c0eecbd9708cab92535690cbc1c2f38",
          "environment_digest": "f1a2a18f81ecf1c8a501a53116ee4d629826d668536abcd641daf4a0c2f66b23",
          "implementation_digest": "9981cf3f578433136a0e324460cc0ae602a8126792d1a3b2e6f0b2555c9e2f48",
          "inputs_digest": "e2a0156844a7c8893bafb8e76c7bc91103b53b330070db31989c62594b1d22a6",
          "parameters_digest": "db96bad61f1421755b0d180495b62c27dbaa95a70264c6ffecffc82fbed829b1",
          "root": "/private/tmp/ai-system-product-publication-v1"
        },
        "identity_digest": "d3ecf01964191b774e1b1d23051faf6898e219f47554b992d1d46930ebcc1e61",
        "reason": "Complete declared inputs",
        "reuse_eligible": true
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-execution-modes"
      ],
      "duration_ns": 5494947042,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-execution-modes",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 8990054667,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-required-artifacts"
      ],
      "duration_ns": 53929125,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-required-artifacts",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 14485078459,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "identity": {
          "coverage_digest": "1b6d3040fbec1a37b39f3b59486ba1025c0eecbd9708cab92535690cbc1c2f38",
          "environment_digest": "f1a2a18f81ecf1c8a501a53116ee4d629826d668536abcd641daf4a0c2f66b23",
          "implementation_digest": "1bbdbd3f08293d73f46a8670c9c800d7ba4407a7cdb35ebe4c5ac7d26d9739d7",
          "inputs_digest": "e2a0156844a7c8893bafb8e76c7bc91103b53b330070db31989c62594b1d22a6",
          "parameters_digest": "a28e253656dca5556af5ce0ce98ba90c7a683f2dabefc4244ab92094fe08ea7c",
          "root": "/private/tmp/ai-system-product-publication-v1"
        },
        "identity_digest": "8ee29fea5e9ba0aa4374d72a31802e026877d058e09604e7458d5693c16b7a8b",
        "reason": "Complete declared inputs",
        "reuse_eligible": true
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-checkout-role"
      ],
      "duration_ns": 863453458,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-checkout-role",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 14539047209,
      "state": "completed"
    },
    {
      "binding": {
        "category": "product",
        "identity": {
          "coverage_digest": "1b6d3040fbec1a37b39f3b59486ba1025c0eecbd9708cab92535690cbc1c2f38",
          "environment_digest": "f1a2a18f81ecf1c8a501a53116ee4d629826d668536abcd641daf4a0c2f66b23",
          "implementation_digest": "d03508b1e0716f26020df7d8de37b324abfad0c1c1722314a250daf83dd7732f",
          "inputs_digest": "c73d6dc66109c742e81cd3a6d29fd224eb78f36532183d4ca0c41fe33f102292",
          "parameters_digest": "ed0043464af097f25d25e1027b2459b8f15d6c82a42706cc2f8f79ef07c84540",
          "root": "/private/tmp/ai-system-product-publication-v1"
        },
        "identity_digest": "03cfc4a0a839b717986ed701c2cc5c65de4ce0ada38ce7994ffcd5dae3595ca9",
        "reason": "Complete declared inputs",
        "reuse_eligible": true
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-readmes"
      ],
      "duration_ns": 4707708,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-readmes",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 15402537209,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-naming"
      ],
      "duration_ns": 2785710291,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-naming",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 15407274459,
      "state": "completed"
    },
    {
      "binding": {
        "category": "product",
        "identity": {
          "coverage_digest": "1b6d3040fbec1a37b39f3b59486ba1025c0eecbd9708cab92535690cbc1c2f38",
          "environment_digest": "f1a2a18f81ecf1c8a501a53116ee4d629826d668536abcd641daf4a0c2f66b23",
          "implementation_digest": "bb3d295d822ea578993e57fd4e780a3a098216fdd1bfafdd9034a2e50fda3bba",
          "inputs_digest": "e2a0156844a7c8893bafb8e76c7bc91103b53b330070db31989c62594b1d22a6",
          "parameters_digest": "18a692606474f5682a3fc521702f7440ce81fc0335c4466b9d11ba24de12dacd",
          "root": "/private/tmp/ai-system-product-publication-v1"
        },
        "identity_digest": "5a58a3aa99ab700bae45a6ac2d0e505a4dcaa9cd7b9f7de7feb7c1858c9a6955",
        "reason": "Complete declared inputs",
        "reuse_eligible": true
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-privacy-boundary"
      ],
      "duration_ns": 821204333,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-privacy-boundary",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 18193023917,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-system-skills"
      ],
      "duration_ns": 760656291,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-system-skills",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 19014273959,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-contract-compliance"
      ],
      "duration_ns": 178750500,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-contract-compliance",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 19774963584,
      "state": "completed"
    },
    {
      "binding": {
        "category": "product",
        "identity": {
          "coverage_digest": "1b6d3040fbec1a37b39f3b59486ba1025c0eecbd9708cab92535690cbc1c2f38",
          "environment_digest": "f1a2a18f81ecf1c8a501a53116ee4d629826d668536abcd641daf4a0c2f66b23",
          "implementation_digest": "c455769370f6af796e4268ca4a65a31d3d68666f4cc867486793ee72d3d5cbd1",
          "inputs_digest": "e2a0156844a7c8893bafb8e76c7bc91103b53b330070db31989c62594b1d22a6",
          "parameters_digest": "095d3be3f3eff0b714c05ea9942b5616054a08cf4a492e42f8141b818f73127e",
          "root": "/private/tmp/ai-system-product-publication-v1"
        },
        "identity_digest": "2b8dd8e4e57705386448012cb0cb382e048ea5f1d20a1675be950cb49762c853",
        "reason": "Complete declared inputs",
        "reuse_eligible": true
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-delivery-constraints"
      ],
      "duration_ns": 252021208,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-delivery-constraints",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 19953757167,
      "state": "completed"
    },
    {
      "binding": {
        "category": "product",
        "identity": {
          "coverage_digest": "1b6d3040fbec1a37b39f3b59486ba1025c0eecbd9708cab92535690cbc1c2f38",
          "environment_digest": "f1a2a18f81ecf1c8a501a53116ee4d629826d668536abcd641daf4a0c2f66b23",
          "implementation_digest": "b7742b78ad790c6fd879f8a09a1443eae0393e0f15fb5ef82dc41beca10ae357",
          "inputs_digest": "e2a0156844a7c8893bafb8e76c7bc91103b53b330070db31989c62594b1d22a6",
          "parameters_digest": "18f9987763e913e693a08311e5b77afcdcb71f3a7bcd9f32ad4ac20c109ec0d1",
          "root": "/private/tmp/ai-system-product-publication-v1"
        },
        "identity_digest": "18d323d41cf19e9e0f6db7efac11540fce7948d533f0609e6512cc66c64a2f49",
        "reason": "Complete declared inputs",
        "reuse_eligible": true
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-owner-approval"
      ],
      "duration_ns": 167939042,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-owner-approval",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 20205814667,
      "state": "completed"
    },
    {
      "binding": {
        "category": "runtime-artifact",
        "identity": {
          "coverage_digest": "1b6d3040fbec1a37b39f3b59486ba1025c0eecbd9708cab92535690cbc1c2f38",
          "environment_digest": "f1a2a18f81ecf1c8a501a53116ee4d629826d668536abcd641daf4a0c2f66b23",
          "implementation_digest": "5e30226dbdab14771b18772b807d547cecd10e9608c3acf7295064c38dc7faaa",
          "inputs_digest": "e2a0156844a7c8893bafb8e76c7bc91103b53b330070db31989c62594b1d22a6",
          "parameters_digest": "d64cf137cd0960ec9acdac562ed9477e090a1bb7cb8d185dfc5c6062241ba808",
          "root": "/private/tmp/ai-system-product-publication-v1"
        },
        "identity_digest": "14967f919c3b7c7fc8faa93244db0c60aa064a2f0283d7a8dcd73040c4ba822d",
        "reason": "Complete declared inputs",
        "reuse_eligible": true
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-distillation-state"
      ],
      "duration_ns": 270413000,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-distillation-state",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 20373801375,
      "state": "completed"
    },
    {
      "binding": {
        "category": "product",
        "identity": {
          "coverage_digest": "1b6d3040fbec1a37b39f3b59486ba1025c0eecbd9708cab92535690cbc1c2f38",
          "environment_digest": "f1a2a18f81ecf1c8a501a53116ee4d629826d668536abcd641daf4a0c2f66b23",
          "implementation_digest": "032b4db65a4c5e8ac393af695f806b8e4b8d2fa68e8dc7fd1fa97cfca16eb822",
          "inputs_digest": "e2a0156844a7c8893bafb8e76c7bc91103b53b330070db31989c62594b1d22a6",
          "parameters_digest": "866517d8f5c8dbe3ecf6585f4ef7c7071dd47f414d3d55d926d972081c8e1960",
          "root": "/private/tmp/ai-system-product-publication-v1"
        },
        "identity_digest": "b31390280b4273a5c3cb6b4b130762cd37ac642de89796b44cee22854bbe2aaa",
        "reason": "Complete declared inputs",
        "reuse_eligible": true
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-validation-routing"
      ],
      "duration_ns": 193809875,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-validation-routing",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 20644253459,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-model-selection-guidance"
      ],
      "duration_ns": 169118959,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-model-selection-guidance",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 20838113500,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-cross-system-upgrade-handoff"
      ],
      "duration_ns": 92659042,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-cross-system-upgrade-handoff",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 21007287667,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-weekly-planning"
      ],
      "duration_ns": 291351458,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-weekly-planning",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 21099984167,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-personal-ops-v4"
      ],
      "duration_ns": 33943000,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-personal-ops-v4",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 21391372584,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-personal-ops-aggregates-v4"
      ],
      "duration_ns": 593587583,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-personal-ops-aggregates-v4",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 21425345209,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-spor-proposals"
      ],
      "duration_ns": 445456333,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-spor-proposals",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 22018979459,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "identity": {
          "coverage_digest": "1b6d3040fbec1a37b39f3b59486ba1025c0eecbd9708cab92535690cbc1c2f38",
          "environment_digest": "f1a2a18f81ecf1c8a501a53116ee4d629826d668536abcd641daf4a0c2f66b23",
          "implementation_digest": "fc88faf13c728a8e25d462e7614c1a142a39335734a9e39ac9203a70dfe439ff",
          "inputs_digest": "e2a0156844a7c8893bafb8e76c7bc91103b53b330070db31989c62594b1d22a6",
          "parameters_digest": "e2cb0b8ec09423dc78d5a985bc509fc99a31c220db2db01eb2cdfb12cdb98f28",
          "root": "/private/tmp/ai-system-product-publication-v1"
        },
        "identity_digest": "145322c3175b5213183a13f966a68aba93fde4eb28ace83c41d186c850682c10",
        "reason": "Complete declared inputs",
        "reuse_eligible": true
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-work-evidence"
      ],
      "duration_ns": 7789271959,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-work-evidence",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 22464481750,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-weekly-planning-v4"
      ],
      "duration_ns": 36600333,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-weekly-planning-v4",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 30253798084,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-block-checkpoint"
      ],
      "duration_ns": 149018083,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-block-checkpoint",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 30290428209,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-end-of-task-capture"
      ],
      "duration_ns": 517687459,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-end-of-task-capture",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 30439487875,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-update-workspace"
      ],
      "duration_ns": 230314625,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-update-workspace",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 30957220834,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-project-state"
      ],
      "duration_ns": 69478125,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-project-state",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 31187572834,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "identity": {
          "coverage_digest": "1b6d3040fbec1a37b39f3b59486ba1025c0eecbd9708cab92535690cbc1c2f38",
          "environment_digest": "f1a2a18f81ecf1c8a501a53116ee4d629826d668536abcd641daf4a0c2f66b23",
          "implementation_digest": "62c0937f011a4c66f729a310eb418086c3235010f9b17f7bada4a9945db3de4f",
          "inputs_digest": "e2a0156844a7c8893bafb8e76c7bc91103b53b330070db31989c62594b1d22a6",
          "parameters_digest": "420f87028935a18d23dd1576202afca3258f889d8e65540fe4c551284cc7815f",
          "root": "/private/tmp/ai-system-product-publication-v1"
        },
        "identity_digest": "6162f2ce4188f770ddb24aad93706f2c4876d6b9966bc6909dd28c24e4eae11d",
        "reason": "Complete declared inputs",
        "reuse_eligible": true
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-project-orchestration"
      ],
      "duration_ns": 5764187792,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-project-orchestration",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 31257097417,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "identity": {
          "coverage_digest": "1b6d3040fbec1a37b39f3b59486ba1025c0eecbd9708cab92535690cbc1c2f38",
          "environment_digest": "f1a2a18f81ecf1c8a501a53116ee4d629826d668536abcd641daf4a0c2f66b23",
          "implementation_digest": "f131e5f5fb9d64f2324bc1a4cf76535a89c57911784c322f08a068589fff6571",
          "inputs_digest": "e2a0156844a7c8893bafb8e76c7bc91103b53b330070db31989c62594b1d22a6",
          "parameters_digest": "3288d6f775543addbeeeaed69c68122dac9b016ff65383b29190fa5e9457bc44",
          "root": "/private/tmp/ai-system-product-publication-v1"
        },
        "identity_digest": "dfe8617ecd14e60be0f0e6474f421344cc2a18750a764282a19430b2a49bf4d7",
        "reason": "Complete declared inputs",
        "reuse_eligible": true
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-orchestration-compatibility"
      ],
      "duration_ns": 3726807250,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-orchestration-compatibility",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 37021330584,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-external-source-registry"
      ],
      "duration_ns": 205018208,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-external-source-registry",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 40748180417,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-external-export-import-workflow"
      ],
      "duration_ns": 181667750,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-external-export-import-workflow",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 40953235167,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-personal-ops"
      ],
      "duration_ns": 454784792,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-personal-ops",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 41134945125,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-task-management"
      ],
      "duration_ns": 621712375,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-task-management",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 41589765500,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-dreaming-mode"
      ],
      "duration_ns": 635134333,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-dreaming-mode",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 42211523292,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-system-insights"
      ],
      "duration_ns": 115941458,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-system-insights",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 42846698084,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-prompt-composition"
      ],
      "duration_ns": 81361542,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-prompt-composition",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 42962678542,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-validation-profiles"
      ],
      "duration_ns": 334421208,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-validation-profiles",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 43044081334,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-validation-integrity"
      ],
      "duration_ns": 19948510333,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-validation-integrity",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 43378545167,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "identity": {
          "coverage_digest": "1b6d3040fbec1a37b39f3b59486ba1025c0eecbd9708cab92535690cbc1c2f38",
          "environment_digest": "f1a2a18f81ecf1c8a501a53116ee4d629826d668536abcd641daf4a0c2f66b23",
          "implementation_digest": "eb7c7bd46a58da115793676e5a57c2af8d6e9523c2cedeba41093602cc59fd4e",
          "inputs_digest": "e2a0156844a7c8893bafb8e76c7bc91103b53b330070db31989c62594b1d22a6",
          "parameters_digest": "48458f4dbb1575762deb1b5e81924867aaa413b0c260b9d1bdb44bfe3570835d",
          "root": "/private/tmp/ai-system-product-publication-v1"
        },
        "identity_digest": "2a65dab1ee72052b067a6c3909c0263e8fffbcaae7d8e7b0951138d86f7ca999",
        "reason": "Complete declared inputs",
        "reuse_eligible": true
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-execution-efficiency"
      ],
      "duration_ns": 1873820416,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-execution-efficiency",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 63327100834,
      "state": "completed"
    },
    {
      "binding": {
        "category": "integration",
        "reason": "Unknown or incomplete input declaration; execute",
        "reuse_eligible": false
      },
      "command": [
        "/private/tmp/ai-system-product-publication-v1/.systems/scripts/check-validator-smoke-tests"
      ],
      "duration_ns": 213955653458,
      "execution": "executed",
      "exit_code": 0,
      "id": "check-validator-smoke-tests",
      "parent_id": "766f760bcf0f41288a6244837a42d73f",
      "rerun_reason": "Fresh execution requested",
      "start_offset_ns": 65200963959,
      "state": "completed"
    }
  ],
  "coverage": {
    "eligibility": "full-required"
  },
  "coverage_digest": "1c71ee1cc2e61a87c348ea75bd88834e1ef06365ec1499519df2a1b913626fe2",
  "duration_ns": 279415585250,
  "environment_digest": "f1a2a18f81ecf1c8a501a53116ee4d629826d668536abcd641daf4a0c2f66b23",
  "execution_plan": [
    {
      "category": "environment",
      "id": "diff",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-product-publication",
      "reason": "Complete declared inputs"
    },
    {
      "category": "integration",
      "id": "check-execution-modes",
      "reason": "Complete declared inputs"
    },
    {
      "category": "integration",
      "id": "check-required-artifacts",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-checkout-role",
      "reason": "Complete declared inputs"
    },
    {
      "category": "product",
      "id": "check-readmes",
      "reason": "Complete declared inputs"
    },
    {
      "category": "integration",
      "id": "check-naming",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "product",
      "id": "check-privacy-boundary",
      "reason": "Complete declared inputs"
    },
    {
      "category": "integration",
      "id": "check-system-skills",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-contract-compliance",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "product",
      "id": "check-delivery-constraints",
      "reason": "Complete declared inputs"
    },
    {
      "category": "product",
      "id": "check-owner-approval",
      "reason": "Complete declared inputs"
    },
    {
      "category": "runtime-artifact",
      "id": "check-distillation-state",
      "reason": "Complete declared inputs"
    },
    {
      "category": "product",
      "id": "check-validation-routing",
      "reason": "Complete declared inputs"
    },
    {
      "category": "integration",
      "id": "check-model-selection-guidance",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-cross-system-upgrade-handoff",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-weekly-planning",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-personal-ops-v4",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-personal-ops-aggregates-v4",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-spor-proposals",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-work-evidence",
      "reason": "Complete declared inputs"
    },
    {
      "category": "integration",
      "id": "check-weekly-planning-v4",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-block-checkpoint",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-end-of-task-capture",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-update-workspace",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-project-state",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-project-orchestration",
      "reason": "Complete declared inputs"
    },
    {
      "category": "integration",
      "id": "check-orchestration-compatibility",
      "reason": "Complete declared inputs"
    },
    {
      "category": "integration",
      "id": "check-external-source-registry",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-external-export-import-workflow",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-personal-ops",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-task-management",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-dreaming-mode",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-system-insights",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-prompt-composition",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-validation-profiles",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-validation-integrity",
      "reason": "Unknown or incomplete input declaration; execute"
    },
    {
      "category": "integration",
      "id": "check-execution-efficiency",
      "reason": "Complete declared inputs"
    },
    {
      "category": "integration",
      "id": "check-validator-smoke-tests",
      "reason": "Unknown or incomplete input declaration; execute"
    }
  ],
  "exit_code": 0,
  "profile": "full",
  "record_fingerprint": "92b8c1088168cd4de0a1dee873974c896fce1619db81da8e635914649229997b",
  "record_kind": "validation-run",
  "run_id": "766f760bcf0f41288a6244837a42d73f",
  "smoke_status": "completed",
  "source": {
    "files": {
      ".github/workflows/README.md": "03d4d5b5b46c0a55eb22af93cd74ed3a1641ff1cb1f9ee9a3d42fb6314677374",
      ".github/workflows/ai-system-validate.yml": "b42dcac79e67f97812ef75ecddb65d4c71794324af253e71763c8044968b430c",
      ".gitignore": "caaf719b4c0915117333a45777cad58e72e43f41f9b1a0f52f2965225a2cd540",
      ".systems/README.md": "5cffc030d1de76ff17ff9e11d349ba055c2e1b3f59457c6a433f3cbc7073c408",
      ".systems/ai/README.md": "3c1d961426c808e61320737e041cd2aad6cc8fce981d85ae086d76902834e8cd",
      ".systems/ai/capabilities/workflow-execution-modes-v1.json": "f2060e7ee28c7d6cd35936a5711b604c46309a4b38a09b25e7bc0042aaa0866d",
      ".systems/ai/core/README.md": "f4aa86838349698e9709d8bee10c43d21cf776338fe9c567f4573e4046266959",
      ".systems/ai/core/block-checkpoint.md": "b77845af6b3c0669427c2695a45821d26ef7124dcd7afc1ff1439dd7cfd2afd4",
      ".systems/ai/core/branch-promotion.md": "075d63bbe891aea4cfc2311307537b1baa7265bc0608f2d1acf3e2829e08be71",
      ".systems/ai/core/checkout-role.md": "24dcc19e9405753137fae33e37c176a2e20cdd09b724e9d206538051833395ee",
      ".systems/ai/core/client-brief.md": "f98488d43a1b3c497eb94ffa2fad5512eafd89316f37356d65cd9c6aa608565b",
      ".systems/ai/core/command-routing.md": "12f8575a01b89c5a0198302668f2ca0f92d57a521e0b7f93a969cd8eab368812",
      ".systems/ai/core/context-as-data.md": "d32c994887014f730e5d0dbae7b7cf0f39bb10c396588296fd8fac3475c85867",
      ".systems/ai/core/contract-compliance.md": "77ea6960f044949211d6b63293888f659f0ea2b76fdb391585376743b04f115e",
      ".systems/ai/core/cross-system-upgrade-handoff.md": "cb899dbfffd687ab15f3b68bb38d57805697e125f94bfe884e59553affc2622f",
      ".systems/ai/core/delivery-constraints.md": "c49fc986d453b8cb4560a6a8d1093770fc708427a241ecf44113cb549e179053",
      ".systems/ai/core/distillation-state.md": "40a2c26086edcc9c71ceee3a1ccf1109828955083a5aa5ebfb9ba82c4ec4ff27",
      ".systems/ai/core/dreaming-mode.md": "4fc26caac25a68b15b14e4455f70c26fc8535aaf9dd7011064efa30602ec36d7",
      ".systems/ai/core/dump-triage.md": "8fbc53cc1d18d6d04526d0461a28ca36e83c68024ece63d32c682ebd73cd7647",
      ".systems/ai/core/end-of-task-capture.md": "71c56304deed972e4224f57ce1e6506f3dbc7b8f9ac47dea38169d49bfedd964",
      ".systems/ai/core/execution-efficiency.md": "142835d4896a232b98b6c8e54e95f5c5147c7b9eb697e79df369507303016195",
      ".systems/ai/core/execution-modes.md": "419203135ad975fcfb14bb41c450df964a7cb76ef0f194c71b583a6d6bdf4c38",
      ".systems/ai/core/external-export-import-workflow.md": "b5cfae399a46dfcb4dcf93c41095be46517bb76103289a0584a3df177106bc6d",
      ".systems/ai/core/external-memory.md": "7fb7c5e06b3d302aea28df3665a0ebe3d95bf8f6d93c0045791575d278feebc1",
      ".systems/ai/core/external-source-registry.md": "bc4702d40d8919b6d51fe27718e781aea8927d8586dea6b5046b692c27c4c928",
      ".systems/ai/core/guide.md": "34b67d715c20538e5a244c135e593d9f087e6c922bf8836eafb717b507f60f58",
      ".systems/ai/core/integrations.md": "716d5d1638ebe1d7d370715ba239e62c11293ebc71daf838adf0554a029a2634",
      ".systems/ai/core/memory.md": "3d6737269784c06fd00d5c9695c02b035b7b0dfb83e431c15efc44679edf8d8e",
      ".systems/ai/core/model-selection-guidance.md": "6bd40a746f18473d0d15772f6a2437da68b559268c451fa4509d36048fc8b704",
      ".systems/ai/core/operating-model.md": "95c66791781fe46cba1395cff1af1006b3c0b3926c61753c64f56a79f3f0dd58",
      ".systems/ai/core/orchestration-compatibility.md": "0ae99a30af80f81576aca61647e561d6e19fb4b5e21192d036cbbd7dcb959056",
      ".systems/ai/core/owner-approval.md": "ec19c1c510d7fc42571ee465a5ea6126f32c2288d11f9401d1eb2cf636cfed4f",
      ".systems/ai/core/personal-ops-aggregates-v4.md": "4c7b2761868bcec45b497b2185f5627aa2bcb75767de6cc7c780fa71e28dbe2c",
      ".systems/ai/core/personal-ops-budgets.md": "d22fcb280a3061e247a4a3a081045c4948a0ee2d891fed78a2d6324f9bec535e",
      ".systems/ai/core/personal-ops.md": "79adac3a777e85ba204766f29d4d13b09fddee937c29b05545fd0d41ee6e5cd6",
      ".systems/ai/core/phase-commit-policy.md": "35431943fa5474ebbb2843bcd6096a582150033eb24785050e480ef92044d20c",
      ".systems/ai/core/privacy.md": "b2fa5ffe8dd88efbbc2cde46298697b4b109353786570a765ea911d0b6dd9a03",
      ".systems/ai/core/product-publication.md": "1150d70c1850848d79313d1c36aaa81ef863d739b5d60c22d5a2cc7292659fcc",
      ".systems/ai/core/project-orchestration.md": "e28a6c3daddb1c664a4f7544eb7049dbf68ad75b9c6146a347d45e2ef02741b2",
      ".systems/ai/core/project-state.md": "ecbd7291e69541018adacb8656a35f0e52a892e2f59379053646d36b548cd808",
      ".systems/ai/core/prompt-composition.md": "8d8e1341c99cddac638688d3637efe26f77138211a810ad37618f26fd0c1c071",
      ".systems/ai/core/response-contract.md": "25c356278dd9103e9d6c1b59968c7214333ed0cccfabd7341f97f27d8c3b747f",
      ".systems/ai/core/spor-proposals.md": "ea1341446b18fe9c53cc30f1ff63c669c06716ce87a3b2a38a5303c565ed4419",
      ".systems/ai/core/system-insights.md": "fd06f91e404847aab82ac32731afb18ee5b2a635f130401e0261d70b2133acce",
      ".systems/ai/core/task-intake.md": "d6b6ea568dc408a496ed5cf7051e446226dbd74ab7c7f9df085f44f748320463",
      ".systems/ai/core/task-management.md": "6b088cb0c4b1f59d977ee338b0c6a6d7cebf2a61fe2028173b0bcffc2797380a",
      ".systems/ai/core/update-from-upstream.md": "cdb4352dd450080e19acb75d7dc9b87b45495dd4250677a4b41f3d404bbd5f30",
      ".systems/ai/core/validation-profiles.md": "088e5a21a51350e7f218f224be5c7b91487da6d15335af1b0a5bd158c782f2d6",
      ".systems/ai/core/validation-routing.md": "5c3a5adeb5ec36291c337f367394ffeb489a277df628e2ff837f81ea87473ff9",
      ".systems/ai/core/weekly-planning.md": "1460b3e05ccf9d20e47f8d24e0d37345c64599bd459e9546461346a68fa8c183",
      ".systems/ai/core/work-evidence-editorial.md": "679bacb6e8cd60a8e6e532cf75eb1963d99090121136246eb40a57521d653cf8",
      ".systems/ai/core/work-evidence.md": "19ecbea07a490a2f5093fe2a5a9691739f7e7b62d66a17560d5efe316b32e3e8",
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
      ".systems/ai/skills/skill-creator/scripts/aggregate_benchmark.py": "afd69da4c4be189f1b71acd99c81079a4fd181653e679523e12807254384fec3",
      ".systems/ai/skills/skill-creator/scripts/eval_freshness.py": "e8911c7cdb06f78c20ec483d4e6ac3c20324e4b7d4e716abbdef7df99b18f6f5",
      ".systems/ai/skills/skill-creator/scripts/generate_report.py": "1614ecbd70e76f7af964faa432a226787e027d76910acd373338a7beb687b82b",
      ".systems/ai/skills/skill-creator/scripts/improve_description.py": "faf8e920d1676ff18b04c301d453afb50415296b60fb017930bb0ca417a9daaf",
      ".systems/ai/skills/skill-creator/scripts/init_skill.py": "e1caade565750b4a4054c5e12a535687e61db950936ff4108a033648e018d2d0",
      ".systems/ai/skills/skill-creator/scripts/package_skill.py": "06921581ae9ae18f326d04eb03be3388b7ca6e8fe5af2570280511b7177d5b8f",
      ".systems/ai/skills/skill-creator/scripts/quick_validate.py": "c3f5105c43ed4a1ad29beff417fcbfdc1c49d098c55c106d5c6108d3770ee384",
      ".systems/ai/skills/skill-creator/scripts/run_eval.py": "e55a06093e345ef1d7d6e273b2182a702f18dd18082afde6b3ef47f96bcc8b66",
      ".systems/ai/skills/skill-creator/scripts/run_loop.py": "5a75184da03f7f5dc73b2a9cd0121407a607b08174b02c57a89b079bd4cc84cf",
      ".systems/ai/skills/skill-creator/scripts/utils.py": "3fbf8407ecc9a11a7b65795d110dd943ba65e79206d7dcf201e8201781afaf04",
      ".systems/ai/templates/README.md": "b7d4be48fbb7011d3d70f60a512257b90701de0776ff6a1c63c7738589cc0286",
      ".systems/ai/templates/capture/cross-system-upgrade-handoff.template.md": "ff75dde16e1ca8fdd5299a2cec68ee4f86b6e4c119e9428f58fb5e9b7f78bf03",
      ".systems/ai/templates/capture/distillation-state.template.md": "737ba4f3da52ac0a114ec3c0d4dc473d96f410c18fc8493fad4d4c8d2b0e55bc",
      ".systems/ai/templates/capture/end-of-task-capture.template.md": "6442a35cf91966b157184245183ff9b3ce63b171ccd9958bdc6691f3b817a618",
      ".systems/ai/templates/checkpoint/block-checkpoint.template.md": "1a97ecc8411b2bd8d18aa987243e6d686c8a6a408abea70d3eb7de9d3ad97fd9",
      ".systems/ai/templates/delivery/delivery-constraints.template.md": "b6b305a61bc62945050bc7afb69531dc1cfeae36c82188eb7b1bc642664a4fd8",
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
      ".systems/ai/templates/quality/execution-quality-record.template.json": "fd023c83baa02b8099033cadc05cd8da976579d8ded9fc5024635ec400c4cea6",
      ".systems/ai/templates/quality/validation-execution-record.template.md": "cc55affd8c2ba19340b4c04f7b69b008d8d79c5eeb6a65ce9bb834601e5733dd",
      ".systems/ai/templates/root/AGENTS.template.md": "7a7297e592b7609035ebbc7d6c17dc1a36405d44b472f01159fe6338c875468c",
      ".systems/ai/templates/root/README.md": "8d360592437e0c5d92d877a2674422a3beaac6cacecfddbe5091eac2bd946f1e",
      ".systems/ai/templates/root/ai-system.local.template.json": "f554b15727bb009f0e425211637f2026c5880868360d3bdeb2a6a1f87b0c5c67",
      ".systems/ai/templates/work-evidence/README.md": "1846a735632d1168a13354796365626b967857e69f876501d33ca1322bf57bc0",
      ".systems/ai/templates/work-evidence/config.example.json": "44742ff40de44e984cc354bbf6552c70cc611bbd4da302a0f6bba3da7a3c0046",
      ".systems/ai/templates/work-evidence/editorial/README.md": "99a02b8b3498722556e560e7187dcc177c53aa0426205ca44d45fc0732a6c9ee",
      ".systems/ai/templates/work-evidence/editorial/v2/README.md": "825ba1d09643f4c84d0f9ce9927fa9f7ce58f6f96557f35f0b1eee62d2490e06",
      ".systems/ai/templates/work-evidence/editorial/v2/formats.md": "ca03e8f9bf692e9ee347435f181b3b36bc2116abc614158064ebfc55a2b083b3",
      ".systems/ai/templates/work-evidence/editorial/v2/recommendation.md": "dafe2216cb4d36bdbc1839b168fbcc98b774b91b8421e53786510d4af7de1a3a",
      ".systems/ai/templates/work-evidence/editorial/v2/schema.json": "f65411012285ec5d4e4ff19d029cbc587a2a10c0f6a70c15d77d13cf03725f61",
      ".systems/ai/templates/work-evidence/procedure/README.md": "1527ebf5651fbb37556326120e4b9a89a26e0ca171ebbeb9bbf7630d69ed5f88",
      ".systems/ai/templates/work-evidence/recovery/README.md": "4594fc5a945f880997e7d3684ccbb2a9517e93cc2df9a8de64ba76c64e33fba0",
      ".systems/ai/templates/work-evidence/report/README.md": "25f3287184218286a383175c64cb827a64f5b0e39747860047c9d9f1621b9942",
      ".systems/ai/templates/work-evidence/requirements-xlsx.txt": "770e1a29d5ead5489aaa872cf1e6cf1482101d75a6aa97bddd3e684849b21a88",
      ".systems/ai/templates/work-evidence/tax/README.md": "7675714ca9d46ea79d475bee726d8ab91164aea9810e88239ecaf2f4152c61b3",
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
      ".systems/ai/templates/workspace/personal-ops/manual-daily-check-in-v4.template.md": "cc927b2888e98fd9330b45f812db9ef7a8f64852a3a795d0c62fcd67378a47bc",
      ".systems/ai/templates/workspace/personal-ops/manual-daily-check-in.template.md": "b1a3cc2c3ec778bef76de850e6a6891497bd5bca5c666ae27e727e073254e071",
      ".systems/ai/templates/workspace/personal-ops/personal-ops-readme.template.md": "28b45e07cbb7b33a0ea52acec2a91835b399d402c365e7bc93b0e310e2fdece2",
      ".systems/ai/templates/workspace/personal-ops/weekly-check-in-v4.template.md": "e0baa52c3e8102c992f75607b3227eaaf9941c5685383b5a3768e630e4be17c8",
      ".systems/ai/templates/workspace/personal-ops/weekly-spor-proposal.template.md": "38e1b90574c28a4ac045426891fd1003dce4b554fe987e44f4187469f9f3c4f3",
      ".systems/ai/templates/workspace/primary-entity-directory-readme.template.md": "81ccb0330ab57e65dd56b8025f32f1e7970f95ee30d3cb06ecee59ec3b07b3fc",
      ".systems/ai/templates/workspace/primary-entity-memory.template.md": "e52f0eb359902bf3c5b780cad9623adae7c158ec44cd955922220ea868bef48b",
      ".systems/ai/templates/workspace/primary-entity-status.template.md": "eb25f49d3336acc07600d121d1ba1ab6db90af36e88691dc15d66672e725d7a8",
      ".systems/ai/templates/workspace/primary-entity-workspace-readme.template.md": "736983695575d758bc204ffe07bee54c5d4e154a35b7755eb1cfb2055887aa11",
      ".systems/ai/templates/workspace/project-state/README.md": "7ced5caf68841a8310e56655a1e5aac6c454d616daa631373c4ac9638c219621",
      ".systems/ai/templates/workspace/project-state/compatibility-plan.template.json": "c0e39d127efd255819c928086466e7db0e6e5d3dd215388c63834cbc86f75ab2",
      ".systems/ai/templates/workspace/project-state/orchestration-record.template.md": "2e2feaf85080243d2096e0d071bbc4e02e50f270db805a749b4044f9defb3d1f",
      ".systems/ai/templates/workspace/project-state/parallel-run.template.json": "021c0364b3484503e3c4e180c41285ed49856108f2dbab52b19408d89fc1ce6a",
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
      ".systems/scripts/README.md": "2539d40d0a3da952028b84db48c684da5bedf49cd0483ce8b56adffb557ea8fe",
      ".systems/scripts/calculate-personal-ops-budgets": "53ad2e7625e4ed953ab34fe618f11e862d29687c454ecf064f44e326c5b7fd8b",
      ".systems/scripts/calculate-personal-ops-life-alignment": "1b2d11ec35e97bf818097b0c587be15dc486af63bea15c30443d025fdfc7bc0c",
      ".systems/scripts/capture_parity.py": "239c7f409b7eb58b008f7f8895b2ea935c25145b6aba808c041edba7b81be6f5",
      ".systems/scripts/check-block-checkpoint": "8f75bc17e3c4b2ebc9ca7972d87e33ec385b3ba505713737486531da62c5daa6",
      ".systems/scripts/check-checkout-role": "ddbfbd0216a95ce549cf744ad865402256479553b74cfd1c54d0e7edfc5eef11",
      ".systems/scripts/check-contract-compliance": "43b8d684b078954708cdb640e51b9b8b41e67928177092511623a0377c892ef9",
      ".systems/scripts/check-cross-system-upgrade-handoff": "e3b41d0c31f576490c0e27d0682bfab33dab7e383ca7c1662cad5b76ea134b4c",
      ".systems/scripts/check-delivery-constraints": "4d47f508401a563d618451a5a5bab9575bfa5a2df0c52d9c3fb716d89f483eb1",
      ".systems/scripts/check-distillation-state": "61d18a7fbb18c9df91b51b3399a6575e47683355af16949c73309658587d345d",
      ".systems/scripts/check-dreaming-mode": "e40dc802a6b6d03b6a4ca242af1ebb32e6d83fa8b997021724572dcca84ce3f0",
      ".systems/scripts/check-dreaming-scope": "8da817c1ea1e75c530dac98dcee13f14a8f58c484f322fa692bbdeb77b3be13c",
      ".systems/scripts/check-end-of-task-capture": "5a0c4e8c7bf5fdd07e3f817d7f5af96d15a23fc7171977af508e4426717ca559",
      ".systems/scripts/check-execution-efficiency": "b4715a6fa361ad0cc4aaf60b27199f916b2841bfdf332823264ca218b1ed72b7",
      ".systems/scripts/check-execution-modes": "55756f38fea4d1ef8f51be5590144b2dabc1c49cc6249b47cac8c18aa43a027f",
      ".systems/scripts/check-external-export-import-workflow": "61420346ebcef6a8486b1c8700a74cece1e6f8aa738185dcbeb3a067d7b98d7a",
      ".systems/scripts/check-external-source-registry": "c486171332a5ca6f7111458da50a7e22aa22061dd4bb060e6f140704ddb4b9d4",
      ".systems/scripts/check-life-alignment-v4": "56d1c1a5d994cb7440a937daa1c38bcd65998fe76a45821d16930b750c938cd1",
      ".systems/scripts/check-model-selection-guidance": "6af06885054d4fac34bee55ce31839589edbd5e099729eae1cfe5194d6810874",
      ".systems/scripts/check-naming": "8c960134a7c32bf285039e757882d30f6b7dd884e482c1fec47114c5510bbb07",
      ".systems/scripts/check-orchestration-compatibility": "262ca9abd559210f5bd34520c034e7a79a7a83a00442eaf5168164b95393c4e8",
      ".systems/scripts/check-owner-approval": "3a41f40ae6ba16918e4ca13d11245108d55ac2fb4466d32fe1ccc9d999a3f363",
      ".systems/scripts/check-parallel-orchestration": "ae4198779470995219fd098fa0843e5344cf561e3e14454c239a984366108be5",
      ".systems/scripts/check-personal-ops": "db257d6c3c695be883be7714fa0de1f2781397ebeb89f28763d7d3bd71e1c8e2",
      ".systems/scripts/check-personal-ops-aggregates-v4": "5d05c14a9f458bce9e413aa103b2ea14e26f49f8a502bac8c37a74e7d90fc499",
      ".systems/scripts/check-personal-ops-v4": "b3c1df0e8f24d3b0f12f2fae2750d2ccd46327f97f74815fb60c4f7e77ea3f97",
      ".systems/scripts/check-privacy-boundary": "a0b090d0fa50f4766d0856715a4dc3d00196897a4836c149708198073a1c65ed",
      ".systems/scripts/check-product-publication": "2ca1aaeb9465b37fc44b86f7bdc657d6adec966f6f23260737f8ee4fb1f44173",
      ".systems/scripts/check-project-orchestration": "8f14c72597d79785000544c7dd388a03486020d584127a8433a106df9461312d",
      ".systems/scripts/check-project-state": "85894ec7aae65c5b7d17ace9464dbb4de9c3a8d66f025364fa6f19d9a884c38a",
      ".systems/scripts/check-prompt-composition": "cc3b5311f6659e853d22bb1ca3f367eb6863862e4eaf411a0edbc33205816569",
      ".systems/scripts/check-readmes": "5d454c9845d7620cba94771b408d06d7d1d391533bcb1e46c6c51011d64be857",
      ".systems/scripts/check-required-artifacts": "05a48be89aa3b0126aca8e33ef27c26f5b265eaee532027909d1b41d6d73fa28",
      ".systems/scripts/check-spor-proposals": "f0d14a2f04da72c8575a61ffc29abced2dbf325fb3719a7b77896727b8733e5f",
      ".systems/scripts/check-spor-v4": "7e75294a75c95cd61c515472c6762d7078f2dad00a5c54703fab6c402965070a",
      ".systems/scripts/check-system-insights": "fdbf23502ce848000c4616720a4a348e9a710783d03841bd605b95ed22a88a37",
      ".systems/scripts/check-system-skills": "f5146340a19d0ec8f216d59d40e3e90ba2dc2cb80e676dd1828c6563411f26cd",
      ".systems/scripts/check-task-management": "7975d5adbaf0c8d9437d2d935a04e6ba9c6ffcd3affa6557de6f9cea8804b6c1",
      ".systems/scripts/check-update-workspace": "4c70a2bb04d8f9d30b37ea6ff05d83c52f28dea72929b56743e420396cc5188f",
      ".systems/scripts/check-validation-integrity": "a4ffa11cecfc8f2f223f648f3e1b208fad9c32d05a48108377e62dffbd9b0db1",
      ".systems/scripts/check-validation-profiles": "3deea2250e20a1bb03aeddceb428e5c91077f09f9f6124c6d074e6b3b016d2e7",
      ".systems/scripts/check-validation-routing": "7cfa61f20648857f2488c8f46982587020567a5d034aa98fb0ac053f862df146",
      ".systems/scripts/check-validator-smoke-tests": "147b383f94e96ed449241ad1a279e03f8ecbf21df27db784d2bf08a3806f5b45",
      ".systems/scripts/check-weekly-planning": "0945dcf343fd28a7f9cd4a23596ba062e9c86f79124f9671f400da6af3f0561e",
      ".systems/scripts/check-weekly-planning-v4": "73108bf4608008c1ffad5d2d23f6aefa5d9f536634f7ddc8f0b5cdbe2233c6c5",
      ".systems/scripts/check-work-evidence": "61cd2183ad1c9a6cc14da69160a4ce1a7a4ead0931963fce94751943b86a8526",
      ".systems/scripts/checkout_role.py": "c303029182ca3e784a1fe6dbdc606aa70842f7327349e382e83ece6e265dce25",
      ".systems/scripts/discover-skills": "5b23040e09a79f717fa1bee2f92243831fff51583804f9f4661923df7dfbca3c",
      ".systems/scripts/dream_recommendations.py": "0fd6fd04a503999fc16e9041d4da837afc08234eab92f5b469499204153cb5aa",
      ".systems/scripts/execution_efficiency.py": "cf377dc73a371418caa845de92f6822142b426f96ddd5137f6b9b46a47d10663",
      ".systems/scripts/execution_modes.py": "67865e4a1d265392bb1062e3ba8d1f65cef4434e723c9616a69d88c73c37bf60",
      ".systems/scripts/init-ai-system": "2df7611581e8dea8de1002b1c2a477aabbfee73f3aa8882135ec19e7fe5d98c5",
      ".systems/scripts/init-workspace": "977e984fce90a4b54d351de2f6be63b38044a0975b11c7ce2e3da112d33acbeb",
      ".systems/scripts/lib-workspaces": "4ce9c86e402b6c63eda1e15bc3952c23ce70818fbc9a0eb56aff6e18317a3322",
      ".systems/scripts/map-notion-check-ins": "f3d01e4ca0f5343c695c9d8b45ae64360ac3df8f919ba611427bacc80bc76496",
      ".systems/scripts/migrate-personal-ops-aggregates-v4": "a65f5847fda612364e4d12e4c3f34a1c3d189e8a8ff34247ef9fae5c6cda4dee",
      ".systems/scripts/migrate-personal-ops-legacy-check-ins-v3": "61f390d49e2b98f3b8d2d5f8cd13f61b349c8ceea4a9c921068063ba5b06ab8f",
      ".systems/scripts/orchestration_compatibility.py": "64adc4912d1ae1873c869812b3e9289d7ca34ab9f046756d047255231820fbc4",
      ".systems/scripts/parallel_orchestration.py": "1d3db3e49afd91a4a53b3d4bd2172caad7a518d6ae4c3f4c69d8c4962b274519",
      ".systems/scripts/personal_ops_aggregates_v4.py": "d817f5d99eea1f4a29af53dafaa5d244ec733220369320c8794880cf88d950ba",
      ".systems/scripts/personal_ops_properties_v3.py": "e701a7ad88a7f8a90cf141e8bedc65a4d16c98ff20cd42c2b7d0d7f2d6be870e",
      ".systems/scripts/personal_ops_spor_proposals.py": "963a11956cd5641ed9fb747d60327fc0a74d3719f80d11c63979caa2a34a1eab",
      ".systems/scripts/personal_ops_v4.py": "ecdc60ac1813d18b54ebc8b9cd35b4a951450686c676cc76196b5eebd94d1cd7",
      ".systems/scripts/prepare-personal-ops-spor-proposal": "199a8facc10dcccb5b68c7ea9d799fc5e6febe97be062c8b7322d4b27db9dd85",
      ".systems/scripts/prepare-product-release": "7180991f6f65b8341e15b636b8afd17bdcd9370f131ccc66a9982369bea967ea",
      ".systems/scripts/prepare-quality-record": "7c920c7d28d36787163a98e5a9955087ecac469ce74aa739861074bc8da1afe3",
      ".systems/scripts/product_publication.py": "89b11bfa808e4e7a3d74543e7b7532c65443c86609b3c73be31ce9def65a4089",
      ".systems/scripts/project-orchestration-preflight": "6a3243f748d7df0223bb601b6179e80a240a399191ce2ec3ba5aab27fdf12f78",
      ".systems/scripts/propose-task-candidates": "30f94669f220e1612d3d31543ce1988bcfc39318038f207c327fc992b748def8",
      ".systems/scripts/qa_source_binding.py": "9b8c833b375ce1c47ee055ba118efb284b39b3198fb45a207bdbc6d452b07a91",
      ".systems/scripts/render-personal-ops-daily-summary": "4ce36d0f5db31ba033cc03d1de38f9e87058fd0ff827702e96092ca36903991e",
      ".systems/scripts/render-personal-ops-daily-summary-v4": "683854c28bb1d28dc0e5896c611d676b0ca97a7f8214b63cbed1d0445d7d9794",
      ".systems/scripts/render-personal-ops-weekly-summary": "7a404157e7db598d3ec7db2a09a5bc0f9dc2c9fef6f826eb564dc15d784e2a69",
      ".systems/scripts/report-contract-topology": "7d296d1cee64b85284231ac5d5f32335ed97435a6688f55d73f860003cb087e4",
      ".systems/scripts/report-validation-comparison": "da46d0196fda417a14b8b8143789564052e889936a583131823bcb115e2d4f50",
      ".systems/scripts/report-workspace-freshness": "12ca8314f7246e80fdc87651bbfb94149d505b097ff0f740641e924449e724f5",
      ".systems/scripts/smoke/README.md": "20030f16a63a04e99b75e51e8313db5785ddeb881fb5f07d7b5118a2a7e2f98c",
      ".systems/scripts/smoke/negative-expectations.json": "0937e3d08aaeec0d5fb9d93010945fa5a5a43463890b0dfc1400e4c2e11c38ca",
      ".systems/scripts/smoke_assertion.py": "d4981381a3ac05233f1fc86873d0cb46c1d2a21d665a40f76b8b6f4f07d260fa",
      ".systems/scripts/smoke_coverage.py": "0c552c7920a5dfb91b5028996bb540a655dfa4fa6afdb5dffdd8b3864fbe22ae",
      ".systems/scripts/smoke_fixture.py": "2c01809ae9c684957aa80d26c303e12e585b20594eb7c4d3a012517c577857a5",
      ".systems/scripts/sync-personal-ops-check-ins": "89ecb1df54ebb720026438b21328512e546658b7b894ae2ea13429cd0d7f880b",
      ".systems/scripts/sync-personal-ops-check-ins-v3": "9e40e3f0ad4c53a47fe477a8679cbd6edfdc5e66db5ac11890c8ada265ec536d",
      ".systems/scripts/sync-personal-ops-check-ins-v4": "3c250f1288a8d2255c035b9872bf46ca6cc0fe5ae0793c0850e17f01623fef4b",
      ".systems/scripts/tests/README.md": "e02ad08e97c90014ad967e4c991b3ffafe9c7b49b2dab2f92829f1cd40640316",
      ".systems/scripts/tests/benchmark_execution_efficiency.py": "5129a95d4927c90f27bcc4863fd084596e8a82c7c10963cce7eb45526bc5d2aa",
      ".systems/scripts/tests/editorial_v2_semantic_cases.py": "c0e5553c510bdb16110093008bfb8edf8fa878fc51e7e0dd7f76dee8035dac43",
      ".systems/scripts/tests/test_checkout_role.py": "141cd23d1caeb429687dd99a94172603930e92b6e842e6ae082025b53144804a",
      ".systems/scripts/tests/test_execution_efficiency.py": "b6f3c6d0fb2db581a471d093437bc6080b78e29d6ba10548d2973a1e1461cde4",
      ".systems/scripts/tests/test_execution_modes.py": "79874cd0b44bebec3985d7d64dba92c05e7671ddf5741e7e46f9c171fbe8449e",
      ".systems/scripts/tests/test_orchestration_compatibility.py": "e6bfe0a56def9d788ed27db2ce7c9b08d100b81f0b4e0afef9f08a5bfcbc01ec",
      ".systems/scripts/tests/test_parallel_orchestration.py": "6e523fd29dbf7ed9edb8479699809e1a841f57ef711dbd8765f98fe1921ad8fa",
      ".systems/scripts/tests/test_product_publication.py": "208380c6749d8fa5dc5fcc2232bffecc511ee7d70a61dbba5575ca7f9b9fff5b",
      ".systems/scripts/tests/test_validation_integrity.py": "42f7a22f2afe36b0883f0312e14d36dc1a00b579b122edc881ad25eb2e050369",
      ".systems/scripts/tests/test_work_evidence.py": "49f5c6999edd58c2f3ce119794617a99857e0d7eb3f874fd12a6da86316ac97b",
      ".systems/scripts/tests/test_work_evidence_docs.py": "74fe15ac8ff71b0b4a3ea50787309e4d3a8ceb2f9e751bd293263ab3734425d0",
      ".systems/scripts/tests/test_work_evidence_editorial.py": "06573d28bca8e1663d78a69ded7ea68b5703fc176d482b7ed121832043d5dd28",
      ".systems/scripts/tests/test_work_evidence_editorial_v2.py": "507799568b6b3a591558d732a83eafd099114dceee44c529e084b6e92bb387da",
      ".systems/scripts/tests/test_work_evidence_editorial_v2_semantic.py": "5de2043a0daf397405106f014ee890e37297eb78371d4ea22a4a5092ee3bd574",
      ".systems/scripts/tests/test_work_evidence_integration.py": "504d4120292fa7f6ea45ff7c8eea90e7b1382d51733cdcb37bb95fd588d46535",
      ".systems/scripts/tests/test_work_evidence_ledger.py": "2e516d743d40afec62121719dc9c90b6ecf0f47d1436c05c283a2ef4c73d81b4",
      ".systems/scripts/tests/test_work_evidence_recovery.py": "6b49964c56f43d10717168a9e627983f9bc609d603ebd99df1ec4f7ae013f339",
      ".systems/scripts/tests/test_work_evidence_report.py": "da1f4d838d6e528ba2574f8965e472304a8faba073c28f168f690b044801810b",
      ".systems/scripts/tests/test_work_evidence_tax.py": "82b145c20daeac4a692f457255546561cf6538443d0c7dd4fa9725bc17087447",
      ".systems/scripts/tests/test_work_evidence_tax_evidence.py": "7c459374c49c8edf94bb20f4e1101b3b94907b6934da93558bda1b8eb13246c9",
      ".systems/scripts/tests/test_work_evidence_xlsx.py": "5de36bfd46b044b7b4f522d865f7c70d582e94894ffc69783d3b3bc9c0c4b61c",
      ".systems/scripts/tests/verify_execution_modes_counterpart.py": "2972e4c43bcf5db72dc211fb4be57c2619f5346e8456df83ce3c26a2bc3c46f5",
      ".systems/scripts/update-from-upstream": "3c4959f68f07bcef3add6d4dbc4172d973e953f93f140a899220f69373f36bec",
      ".systems/scripts/update-workspace": "917950f3c45b1d1ef6b83c2582f19c9c436e8dc0ee61f5fc92477536abbc6f27",
      ".systems/scripts/validate-ai-system": "a4c4a626c08ef594e97a3a9dc537c0d1312c7decef799ba162cf50a97eec4dbd",
      ".systems/scripts/validation-dependencies.json": "06c68f29b9ff5ac90044a59c68bcafea066607463067863f5e7ecb7a08483b2e",
      ".systems/scripts/validation_runner.py": "631caa6e45b6e0648f69d99acf75761018863353fb7927443b11fc24ff5b65fc",
      ".systems/scripts/validation_support.py": "834e37875531aa2ef028f39a98a8bb50b6d2c5b2b282f6485d96678395140127",
      ".systems/scripts/work-evidence-apply": "4799fe78c18f97c50c79a94dc8c0eb88b0d7df11b2674b0fc2a809effe0d84fb",
      ".systems/scripts/work-evidence-documentation": "8c8c688776d00ed2d4f0b11b05080d7e517c118595ea59f6802425006175dc70",
      ".systems/scripts/work-evidence-editorial": "b1d2385482f349b85eae7c89edc37123b883f29b89eb1e46abfb35a39b369a01",
      ".systems/scripts/work-evidence-prepare": "4a93d0db563d4c69e94b57fe19217f3cca646deebc56d08715b71f46b7b5b748",
      ".systems/scripts/work-evidence-preview": "de6eaef2063efd74437a571ebfac1efc8d21f4e73e097be207ddec560fa8c489",
      ".systems/scripts/work-evidence-rebuild": "5b3d18225a2bc068f79711df7eaff67ade38e4c45ab9d9fe3ce26d0a83392518",
      ".systems/scripts/work-evidence-recover": "3db5c2686782749ecef816d06c805cd42ed13dc4a0c839820ae7f1bab92e1376",
      ".systems/scripts/work-evidence-recover-lock": "dcbc59422c1bab83a8b1038d967716c3bdd561704d5c8aef2dbe85dc91c4221e",
      ".systems/scripts/work-evidence-recovery": "a3e51bdd78ac78db0f6cde48b832dd8a78659ee736e988ab6fa70d5f8563b26e",
      ".systems/scripts/work-evidence-report": "ca9f8d40aa364299975da0cb81ee24863149c04897f252f7c94414fe925d92c4",
      ".systems/scripts/work-evidence-tax-calculate": "ee7bca021fa9d1f795795e57961647698c90393d45b1af3dc50753462ca018b9",
      ".systems/scripts/work-evidence-tax-evidence": "db308449111f56d5ac1589e63687508de2e59bfa2c66ce726ba9e3def2bd215d",
      ".systems/scripts/work-evidence-xlsx": "de780d946081799ffa3cf60215d42e6b71bc578c048ff17f05e0e7fb41e5ba19",
      ".systems/scripts/work_evidence.py": "03aafe714fee1616606e50632cee55c1cee3264a9d6b78ed0bf0d53727c85048",
      ".systems/scripts/work_evidence_cli.py": "c9b4d7a010fe9b4799d1fbc96406e04fec73c17b639c45521b45e1643dbd195a",
      ".systems/scripts/work_evidence_docs.py": "c4ff7b26eb5c4af63bfedfdcbcf04a759ab4ce96157862d670c48dfdc538d7e8",
      ".systems/scripts/work_evidence_editorial.py": "53d3bad51fb477e698a9448e7f9d9d1d1050f332813c0dc0c35d422d68b01ea6",
      ".systems/scripts/work_evidence_editorial_v2.py": "a44d380d881bc6067fa24c15f4d4b5a3deda1f2c31c59076efdf143bfa315be3",
      ".systems/scripts/work_evidence_ledger.py": "ab9cf66901bd3897a31bd7ee56c08fb5fc9500b2eca2819550b43920b1b62352",
      ".systems/scripts/work_evidence_recovery.py": "089c09e11db006b05e8ef2fa4c2a219c886453333c7701fc4f8210f837fb70c7",
      ".systems/scripts/work_evidence_report.py": "b3dd054ba6ab9b458e73d4fe8486fc6671eb6283789fdad358aed9f1a8020f91",
      ".systems/scripts/work_evidence_tax.py": "15d6c49c8cb77f647c563cc1941b10f326a6e3f002a92813ec02e149eb469a9b",
      ".systems/scripts/work_evidence_tax_evidence.py": "a18502d03dbadeecf8b1a42c0e507d2d9d23037b5a57c89bf7ad243a3aca238a",
      ".systems/scripts/work_evidence_xlsx.py": "43876bf8d25a05cdf51877b6cb2ee27fc62dabd5c25c2f56e8f1d58474a831fc",
      "HUMANS.md": "364f50ac08fb2e6a160e2577aadc096fb5d590113647c8e2b4880c8838fca21f",
      "README.md": "a65ce3a63688ff8155bc8b4fc0bf5ad43aeb7c6303613faeb5ef5f5365a243b6"
    },
    "head": "c2834494ec520092a27c035cdd208623d501beb5",
    "source_digest": "6d8be8b685d8ed0430c829bac23c1f52d05a367e9c090263f8eaa9e98eef0e4d"
  },
  "status": "completed",
  "supporting_only": true
}
```
