# Format Field Templates

All templates use the Common Artifact in README. Content is agent-authored from
selected safe claims; renderer validates/escapes, it does not invent prose.
Every title/body/metadata/CTA/language change invalidates prior review.
Keep identifiable original lessons in owner-only source review/private storage.
Drafts use separate reviewed derivatives. Blog explains all promised steps;
newsletter may summarize and add a usable checklist/template, never hide a step.

## Blog Article
format: blog-article; output_kind: brief or draft; slot_id omitted as a cadence slot.
format_fields: proposed_slug, meta_description, tldr, key_takeaways, outline, cta.
Strings except nonempty string lists for key_takeaways/outline. Slug lowercase
kebab-case, not a published URL. Brief body is a synopsis; developed draft body
answers the promised audience problem. Distinguish demonstrated fact from advice.

## Newsletter
format: newsletter; output_kind: brief or draft.
format_fields: subject, preheader, standalone_value, additional_value, cta.
Standalone letter may omit additional_value. Related blog requires a concrete
new example/tool/decision/checklist, not merely a duplicated summary. Explain what
the subscriber can do; promised benefit must be supported, not invented.

## Social Post
format: social-post; output_kind: brief or draft.
format_fields: hook, key_takeaways (nonempty string list), cta.
Deliver one useful short lesson. No mandatory link or misleading promise; external
URL requires reviewed proof, otherwise no-link is valid. Never recreate private scope.

## Short Video Concept
format: short-video-concept; output_kind: concept.
format_fields: hook, teaching_point, scenes (nonempty ordered string list),
assets_needed, cta. Explain why visual sequence teaches better than plain text.
Missing media/permission means an unscheduled needs-review concept, not a video.
May replace one social slot only when readiness/effort are explicit.

## YouTube Concept
format: youtube-concept; output_kind: concept; always unscheduled.
format_fields: working_title, promise, outline (nonempty string list), demo_plan,
assets_needed, cta. Justify depth and demonstration. State missing demonstration
and what must be collected; never claim production-ready media.

## Assets And CTA
AssetNeed: kind (screen-demo/illustration/diagram/recording/other), description,
permission_state (unknown/review-required/approved), evidence_claim_ids. No files
are fetched/loaded/recorded. Permission state is evidence to review, not consent.
CTA: omitted, or text, target_kind (none/existing-url), target_url,
verification_ref, verified_at. None has no URL/proof/date; existing-url requires
public http(s), linked selected source proof and reviewed timestamp. Do not invent
live publication from a route edge. No local/private URL or embedded credentials.
