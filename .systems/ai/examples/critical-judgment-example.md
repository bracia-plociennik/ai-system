# Critical judgment example

Synthetic case: a solo owner needs ten form submissions per month, one day to deliver, and proposes Kafka plus Kubernetes. Assessment: disproportionate complexity. Basis: the stated volume and operational capacity do not establish a need for distributed infrastructure. Consequence: setup and maintenance displace the small product goal. Recommendation: one small application with durable storage and a backup. Reconsider when measured concurrency, isolation or integration needs justify the extra cost.

A second owner proposes that simpler application with the same constraints. Agree with the direction; do not invent a defect to populate a critique. If data are unavailable, state uncertainty and a relevant test. If a later requirement demands sub-two-second delivery, revise earlier minute-polling advice. A conscious allowed daily-export tradeoff remains accepted until requirements change.

Architecture What-if: a webhook is delivered twice or the process fails between payment and persistence. Determine idempotency/reconciliation behavior, test duplicate and restart traces, and record the condition requiring a design change. This is planning evidence, not permission to charge a payment or migrate a real database.
