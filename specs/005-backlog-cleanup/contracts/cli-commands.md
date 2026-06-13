# Contracts: CLI Commands (005-backlog-cleanup)

Surface: `src/kwi/cli/` (Typer + Rich). Only additions/changes are listed.

## CHANGED: `kwi work set`

Add three options that were previously missing (WI 41):

```text
kwi work set <ID> [existing options]
                   [--tshirt {XS|S|M|L|XL|Huge|Unknown}]
                   [--area <AREA_NAME>]
                   [--parent <WORKITEM_ID>]
```

- **Behavior**: Each supplied flag updates the corresponding field via
  `queries.update_workitem`. Unsupplied flags leave the field unchanged
  (FR-017).
- **Validation / errors** (to stderr, non-zero exit):
  - `--tshirt` not in the allowed set → actionable error listing valid sizes.
  - `--area` not found in the item's project → actionable error.
  - `--parent` equal to the item or creating a cycle → actionable error
    (FR-018).
- **Maps to**: FR-015, FR-017, FR-018.

## CHANGED: `kwi work archive`

```text
kwi work archive <ID>
```

- **Behavior**: Sets `archived = true`, preserves status (previously set status
  to `archived`). Idempotent.
- **Maps to**: FR-002, FR-005.

## NEW: `kwi work unarchive`

```text
kwi work unarchive <ID>
```

- **Behavior**: Sets `archived = false`, status unchanged. Idempotent.
- **Output**: Confirmation to stdout; consistent Rich formatting.
- **Maps to**: FR-005, FR-007.

## Output / listing

Any CLI listing that displays archived state MUST read the new `archived`
boolean rather than inferring it from status. JSON output (`--json` where
supported) MUST include `archived`.
