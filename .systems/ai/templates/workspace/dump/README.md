# Dump Template

Dump is the inbox for incoming files when ownership is unknown, mixed, or not yet trusted.

AI may classify files here. AI may not move, copy, delete, rename, or archive them without owner approval.

Use `incoming/` as the default drop zone.

When the owner already knows a file belongs to a specific client, use `clients/<client>/dump/incoming/` instead.

When the owner already knows a file belongs to a specific owned asset, use `owned-assets/<asset>/dump/incoming/` instead.
