# Dump Template

Dump is the inbox for incoming files when ownership is unknown, mixed, or not yet trusted.

AI may classify files here. AI may not move, copy, delete, rename, or archive them without owner approval.

Use `incoming/` as the default drop zone.

When the owner already knows a file belongs to a specific client, use `clients/<client>/dump/incoming/` instead.

In a primary-entity workspace, files already known to belong to the primary entity may also use this workspace-level `dump/incoming/`.

In a generic workspace, when the owner already knows a file belongs to a specific owned asset, use `owned-assets/<asset>/dump/incoming/` instead.
