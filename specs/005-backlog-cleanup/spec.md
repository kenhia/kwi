# Feature Specification: Backlog Cleanup (Archived Flag, Filters, MCP & Tooling)

**Feature Branch**: `005-backlog-cleanup`  
**Created**: 2026-05-30  
**Status**: Draft  
**Input**: User description: "Clear the kwi backlog in one sprint (005): make archived a first-class boolean separate from status; add un-archive; sticky session filters with closed excluded by default and a visual cue; sprint filter dropdown; MCP project/area creation; fix tshirt/area/parent updates via CLI and MCP; replace the GUI icon with the kiwi mascot."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Archived is independent of status (Priority: P1)

A user archives a work item without losing the item's real status. An archived
item retains whatever status it had (e.g. `open`, `active`, `closed`) and is
simply flagged as archived. Archiving no longer forces the status to a special
`archived` value, and the archive action no longer interrupts the user with a
confirmation pop-up.

**Why this priority**: This is the foundational data-model change. Un-archive
(US4) and the filter rework (US5) both depend on archived being a separate flag,
so it must land first. It is also independently valuable: archiving immediately
becomes non-destructive.

**Independent Test**: Archive an item that is `active`; confirm it disappears
from the default view but still reports status `active` and `archived = true`.
Confirm existing items previously in the `archived` status now report
`status = closed, archived = true` after migration, and that `archived` is no
longer offered as a selectable status.

**Acceptance Scenarios**:

1. **Given** an `active` work item, **When** the user archives it, **Then** the
   item's status remains `active` and it is marked archived, with no confirmation
   dialog shown.
2. **Given** items that held the legacy `archived` status before the upgrade,
   **When** the migration runs, **Then** each becomes `status = closed,
   archived = true` and the `archived` entry is removed from the list of
   selectable statuses.
3. **Given** the archive action is invoked from the CLI, MCP, or GUI, **When** it
   completes, **Then** all three paths set the archived flag (not a status) and
   produce identical results.

---

### User Story 2 - Create projects and areas from MCP (Priority: P1)

An agent working in a brand-new project can create the project and its areas
directly through MCP tools, without dropping to the CLI.

**Why this priority**: High-value and fully independent of the schema work. It
removes a sharp edge in the new-project onboarding flow.

**Independent Test**: From an MCP client, create a new project, then create
areas under it, then list them back — all without invoking the CLI.

**Acceptance Scenarios**:

1. **Given** no matching project exists, **When** the agent calls the MCP
   create-project tool, **Then** the project is created and returned with its id.
2. **Given** an existing project, **When** the agent calls the MCP create-area
   tool, **Then** the area is created and associated with that project.
3. **Given** a newly created project, **When** the agent lists areas, **Then**
   the created areas are returned.

---

### User Story 3 - Custom application icon (Priority: P1)

The desktop application displays the kiwi mascot icon instead of the default
framework icon, across all platforms' icon formats.

**Why this priority**: Quick, independent, visible branding win.

**Independent Test**: Build the GUI and confirm the window/taskbar icon is the
kiwi mascot rather than the default.

**Acceptance Scenarios**:

1. **Given** the kiwi mascot source image, **When** the platform icon set is
   generated, **Then** the application uses the mascot for its window, taskbar,
   and installer icons.

---

### User Story 4 - Un-archive a work item (Priority: P2)

A user viewing an archived item can un-archive it, restoring it to the active
views with its preserved status intact.

**Why this priority**: Completes the archive lifecycle. Depends on US1 (the
archived flag and preserved status must exist first).

**Independent Test**: Archive an `active` item, then un-archive it, and confirm
it returns to the default view still showing status `active`.

**Acceptance Scenarios**:

1. **Given** an archived item, **When** the user un-archives it, **Then**
   `archived` becomes false and the item reappears in non-archived views with its
   prior status unchanged.

---

### User Story 5 - Sticky filters with sensible defaults (Priority: P2)

A user's work-item filters persist as they navigate within a session, default to
hiding `closed` items, and clearly indicate when a filter is not at its default.

**Why this priority**: Improves daily usability. Best built after US1 so filter
logic is written once against the final status model.

**Independent Test**: Set a status filter, navigate to a detail view and back,
and confirm the filter is retained. Confirm `closed` items are hidden by default
and that a visual cue appears when a filter differs from its default.

**Acceptance Scenarios**:

1. **Given** the default view, **When** the list first loads, **Then** items with
   status `closed` are hidden.
2. **Given** a user has changed a filter, **When** they navigate elsewhere in the
   app and return, **Then** the filter selection is retained for the session.
3. **Given** a filter is not at its default value, **When** the user views the
   filter controls, **Then** a visual cue indicates the filter is active/modified.

---

### User Story 6 - Sprint filter dropdown (Priority: P2)

A user can filter the work-item list by sprint, including an "Unassigned" bucket
for items with no sprint.

**Why this priority**: Rounds out filtering. Folds naturally into the US5 filter
work and reuses the existing multi-select control.

**Independent Test**: With items across multiple sprints plus some with no
sprint, open the sprint filter and confirm it lists each distinct sprint plus
"Unassigned", and that selecting a subset filters the list accordingly.

**Acceptance Scenarios**:

1. **Given** items spanning several sprints and some with no sprint, **When** the
   sprint filter opens, **Then** it lists each distinct sprint value plus an
   "Unassigned" option, all selected by default.
2. **Given** the sprint filter, **When** the user deselects a sprint, **Then**
   items in that sprint are hidden from the list.

---

### User Story 7 - Update t-shirt size, area, and parent (Priority: P3)

A user can change a work item's t-shirt size, area, and parent through both the
CLI and the MCP update tool.

**Why this priority**: A correctness fix for a silent data-loss gap discovered
during planning. Small and additive, lower urgency than the feature work.

**Independent Test**: Via the CLI and again via MCP, set an item's t-shirt size,
area, and parent, then read the item back and confirm all three changed.

**Acceptance Scenarios**:

1. **Given** a work item, **When** the user sets its t-shirt size via the CLI,
   **Then** the change persists and is reflected on read.
2. **Given** a work item, **When** the agent sets its area and parent via the MCP
   update tool, **Then** both changes persist and are reflected on read.
3. **Given** an update request omits these fields, **When** it is applied,
   **Then** the existing values are left unchanged (no accidental clearing).

---

### Edge Cases

- Archiving an already-archived item is a no-op (remains archived, status
  unchanged).
- Un-archiving a non-archived item is a no-op.
- The migration must run only after all legacy `archived`-status rows are
  repointed, so removing the `archived` status row does not violate referential
  integrity.
- Setting a work item's parent to itself, or to a value that would create a
  cycle, must be rejected.
- Setting an invalid area or an out-of-range t-shirt size must be rejected with a
  clear error rather than silently ignored.
- The sprint filter must handle the case where every item is unassigned (only the
  "Unassigned" bucket appears).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A work item MUST carry an `archived` indicator that is independent
  of its status, defaulting to not-archived for new items.
- **FR-002**: Archiving a work item MUST set the archived indicator to true while
  preserving the item's existing status.
- **FR-003**: The system MUST provide a one-time data migration that converts
  every work item currently in the legacy `archived` status to status `closed`
  with the archived indicator set to true.
- **FR-004**: After migration, the system MUST remove `archived` from the set of
  selectable statuses, and this removal MUST be ordered after FR-003 so no item
  references it.
- **FR-005**: Archiving MUST behave identically across the CLI, MCP, and GUI, all
  setting the archived indicator rather than a status value.
- **FR-006**: The GUI MUST archive an item without showing a confirmation dialog.
- **FR-007**: Users MUST be able to un-archive a work item from the GUI,
  returning it to non-archived views with its prior status unchanged.
- **FR-008**: The GUI work-item list MUST exclude `closed` items by default.
- **FR-009**: The GUI MUST retain the user's active filters as they navigate
  within a single application session.
- **FR-010**: Cross-session filter persistence is explicitly OUT OF SCOPE for
  this feature.
- **FR-011**: The GUI MUST display a visual cue whenever a filter is not at its
  default value.
- **FR-012**: The GUI MUST provide a sprint filter listing each distinct sprint
  value plus an "Unassigned" bucket for items with no sprint, using the existing
  multi-select filter control with all options selected by default.
- **FR-013**: The MCP server MUST provide a tool to create a project.
- **FR-014**: The MCP server MUST provide a tool to create an area associated with
  a project.
- **FR-015**: Users MUST be able to set a work item's t-shirt size, area, and
  parent via the CLI work-update command.
- **FR-016**: Agents MUST be able to set a work item's t-shirt size, area, and
  parent via the MCP update-work-item tool.
- **FR-017**: Update operations MUST leave t-shirt size, area, and parent
  unchanged when those fields are not supplied (no accidental clearing).
- **FR-018**: The system MUST reject a parent assignment that would make an item
  its own ancestor (self or cycle).
- **FR-019**: The desktop application MUST use the kiwi mascot as its icon across
  the platform icon formats, generated from the provided square source image.

### Key Entities *(include if feature involves data)*

- **Work Item**: A unit of tracked work. Gains an `archived` boolean independent
  of its `status`. Also has a t-shirt size, an area, and an optional parent
  work item, all of which must be updatable.
- **Status**: The lifecycle state of a work item (e.g. open, active, resolved,
  closed, draft). The legacy `archived` value is retired by this feature.
- **Project**: A top-level grouping that can now be created via MCP.
- **Area**: A subdivision belonging to a project, that can now be created via MCP.
- **Sprint**: A label on a work item used by the new sprint filter; items may have
  no sprint ("Unassigned").

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of work items previously in the `archived` status are migrated
  to `status = closed, archived = true` with zero rows left referencing a removed
  status value.
- **SC-002**: Archiving and un-archiving preserve the work item's status in 100%
  of cases, verified across CLI, MCP, and GUI.
- **SC-003**: A user can archive an item with a single action and no confirmation
  step.
- **SC-004**: On first load, the default work-item view shows no `closed` items.
- **SC-005**: Filters set by the user remain in effect across in-session
  navigation in 100% of navigations within the session.
- **SC-006**: A new project and its areas can be created entirely through MCP
  tools with no CLI invocation.
- **SC-007**: T-shirt size, area, and parent can each be changed via both the CLI
  and MCP, confirmed by reading the item back; unsupplied fields are never
  altered.
- **SC-008**: The built desktop application displays the kiwi mascot icon rather
  than the default framework icon.

## Assumptions

- The source icon image is square (760×760, confirmed) and the platform icon
  generator can produce all required formats from it; no separate tooling install
  or external hand-off is required.
- The existing multi-select filter component is suitable for the sprint filter.
- "Closed excluded by default" combined with in-session stickiness is sufficient;
  cross-session persistence is deliberately deferred and may be revisited later.
- The work-item backlog items 18, 19, 21, 38, 39, 40, and 41 are all in scope for
  this single feature/sprint.
