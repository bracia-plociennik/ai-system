# Skill Output Comparator

Use this comparator when comparing baseline output with skill-assisted output.

## Inputs

- Eval prompt.
- Baseline output.
- Skill-assisted output.
- Expected behavior or acceptance criteria.
- Relevant authority and safety constraints.

## Method

1. Stay blind when possible: label outputs `A` and `B` before judging.
2. Understand the eval prompt and what a good output must accomplish.
3. Build a task-specific rubric with content and structure dimensions.
4. Compare correctness, completeness, accuracy, organization, formatting, usability, evidence, authority compliance, and safety.
5. Check expectation pass rates as secondary evidence.
6. Penalize outputs that appear better only because they received leaked expected answers.
7. Prefer the output that would be safer to hand to the user.

## Output

```json
{
  "winner": "A",
  "confidence": "medium",
  "reasoning": "Output A is more complete and better validated.",
  "rubric": {
    "A": {
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content_score": 3.0,
      "structure_score": 3.0,
      "overall_score": 6.0
    }
  },
  "output_quality": {
    "A": {
      "strengths": ["complete", "validated"],
      "weaknesses": []
    },
    "B": {
      "strengths": ["readable"],
      "weaknesses": ["missing validation"]
    }
  },
  "next_iteration": [
    "Add explicit validation step to the weaker skill"
  ]
}
```
