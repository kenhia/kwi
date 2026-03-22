# Feature Specification: kwi Desktop GUI

**Feature Branch**: `003-kwi-ui`
**Created**: 2026-03-21
**Status**: Draft
**Input**: Desktop GUI for work item management using Tauri and Svelte

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Browse Projects and Work Items (Priority: P1)

As a user, I want to launch the desktop application, see my
projects, and browse work items so that I can quickly find and
review the work I'm tracking.

**Why this priority**: Reading and navigating is the most frequent
activity. Without browsing, no other interaction is useful. This
is the foundation of the GUI experience.

**Independent Test**: Launch the app, select a project from the
sidebar, see a filtered list of work items, click one to view its
full details. Delivers immediate read-only value.

**Acceptance Scenarios**:

1. **Given** the app is launched, **When** the main window opens,
   **Then** I see a sidebar listing all projects by short name.
2. **Given** the sidebar shows projects, **When** I select a
   project, **Then** the main panel shows a table of work items
   for that project with columns: ID, area, type, status, t-shirt
   size, sprint, and title.
3. **Given** a work item list is displayed, **When** I click a
   work item row, **Then** a detail view opens showing all fields
   including rendered markdown content and details.
4. **Given** a project with areas, **When** I view the project's
   work items, **Then** I can filter by area, status, type, t-shirt
   size, and sprint using controls above the list.
5. **Given** a work item list, **When** archived items exist,
   **Then** they are hidden by default but can be shown by toggling
   an "include archived" option in the filter controls.
6. **Given** no database connection is configured, **When** the app
   launches, **Then** it displays a clear message explaining how to
   configure the connection.

---

### User Story 2 — Create Work Items (Priority: P1)

As a user, I want to create new work items through a form so that
I can capture bugs, tasks, and ideas without leaving the GUI.

**Why this priority**: Creating work items is the core purpose of
the tool. Combined with browsing, this completes the minimum
viable product.

**Independent Test**: Open the create form, fill in required and
optional fields, submit, and verify the new item appears in the
work item list.

**Acceptance Scenarios**:

1. **Given** a project is selected, **When** I click a "New Work
   Item" button, **Then** a form opens with fields for project
   (pre-filled), title, content (markdown editor), type, status,
   t-shirt size, area, sprint, details, and parent.
2. **Given** the create form is open, **When** I select type or
   status, **Then** I choose from dropdown menus populated with
   valid values from the database. T-shirt size is a hardcoded
   enum (XS, S, M, L, XL, Huge, Unknown) since no reference table exists.
3. **Given** the create form is open, **When** I select an area,
   **Then** I choose from areas belonging to the selected project.
4. **Given** I have filled in at least project, title, and content,
   **When** I submit the form, **Then** the work item is created
   and appears in the work item list.
5. **Given** I submit a form with missing required fields, **When**
   the submission is processed, **Then** I see clear validation
   messages indicating which fields are required.

---

### User Story 3 — Edit Work Items (Priority: P1)

As a user, I want to edit existing work items so that I can update
status, fix descriptions, and refine details as work progresses.

**Why this priority**: Updating work items is essential to the daily
workflow. Items change status, get re-prioritized, and receive
updated content constantly.

**Independent Test**: Open a work item, modify one or more fields,
save changes, and verify the updated values persist.

**Acceptance Scenarios**:

1. **Given** a work item detail view is open, **When** I click an
   "Edit" button, **Then** the view switches to an editable form
   pre-populated with the current values.
2. **Given** the edit form is open, **When** I change one or more
   fields and save, **Then** the work item is updated and the
   detail view refreshes with the new values.
3. **Given** the edit form is open, **When** I click "Cancel",
   **Then** no changes are saved and I return to the detail view.
4. **Given** the edit form is open, **When** I change the type or
   status to an invalid value, **Then** I see a validation error
   before saving.

---

### User Story 4 — Archive Work Items (Priority: P2)

As a user, I want to archive work items that are no longer active
so that they stop cluttering my default work item list.

**Why this priority**: Archiving keeps the active list manageable.
Important but less frequent than creating or editing items.

**Independent Test**: Select a work item, archive it, verify it
disappears from the default list, toggle "include archived" to
see it again.

**Acceptance Scenarios**:

1. **Given** a work item detail or list view, **When** I click
   "Archive" on a work item, **Then** a confirmation prompt
   appears.
2. **Given** I confirm the archive action, **When** the operation
   completes, **Then** the item's status is set to "archived" and
   it is removed from the default work item list.
3. **Given** items have been archived, **When** I enable "include
   archived" in the filters, **Then** archived items appear in
   the list with a visual indicator of their archived status.

---

### User Story 5 — Manage Relationships (Priority: P2)

As a user, I want to create and view relationships between work
items so that I can track dependencies and connections.

**Why this priority**: Relationships add structure to the work item
graph. Valuable but not needed for the initial read-create-edit
workflow.

**Independent Test**: Navigate to a work item, add a relationship
to another item, see the relationship listed, remove it.

**Acceptance Scenarios**:

1. **Given** a work item detail view, **When** I view the
   relationships section, **Then** I see a list of related items
   with their relationship labels and titles.
2. **Given** a work item detail view, **When** I click
   "Add Relationship", **Then** I can search for or select another
   work item and specify a relationship label.
3. **Given** a relationship exists, **When** I click "Remove" on
   a relationship, **Then** the relationship is deleted after
   confirmation.
4. **Given** a related item is shown, **When** I click its title,
   **Then** I navigate to that work item's detail view.

---

### User Story 6 — Search Work Items (Priority: P2)

As a user, I want to search across work item titles and content
so that I can quickly find items by keyword.

**Why this priority**: Search becomes important as the number of
work items grows. Builds on the browsing foundation.

**Independent Test**: Enter a search term in the search bar, see
matching work items across the current project, click one to view
details.

**Acceptance Scenarios**:

1. **Given** a project is selected, **When** I type in a search
   bar, **Then** work items matching the query in title or content
   are displayed.
2. **Given** search results are shown, **When** I click a result,
   **Then** I navigate to that work item's detail view.
3. **Given** a search term with no matches, **When** the search
   completes, **Then** I see a "no results found" message.

---

### User Story 7 — Manage Projects and Areas (Priority: P3)

As a user, I want to create projects and areas through the GUI
so that I can organize new work without switching to the CLI.

**Why this priority**: Project and area creation is infrequent.
Most users will have projects set up already via CLI. This is a
convenience feature.

**Independent Test**: Create a new project via a form, create an
area under it, verify both appear in the sidebar and are
selectable.

**Acceptance Scenarios**:

1. **Given** the sidebar, **When** I click "Add Project", **Then**
   a form opens with fields for short name, canonical path,
   GitHub repo (optional), and description.
2. **Given** I fill in the required project fields and submit,
   **When** the project is created, **Then** it appears in the
   sidebar project list.
3. **Given** a project is selected, **When** I access area
   management (e.g., via a context menu or settings), **Then** I
   can create a new area with a name and description.
4. **Given** I attempt to create a project with a duplicate short
   name, **When** the submission is processed, **Then** I see a
   clear error message.

---

### Edge Cases

- What happens when the database is unreachable at launch?
  The app displays a connection error screen with instructions
  for configuring the connection.
- What happens when another user or tool modifies data while the
  GUI is open? The list refreshes when the user navigates back
  to it or manually refreshes; stale detail views show updated
  data on re-open.
- What happens when the markdown content is extremely large?
  The rendered view handles scrolling and does not block the UI.
- What happens when the user resizes the window very small?
  The layout remains usable with responsive design — sidebar
  collapses or becomes scrollable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The application MUST connect to the PostgreSQL
  database using the same configuration precedence as the CLI
  (environment variable > config file). The CLI "flag" option
  does not apply to the GUI.
- **FR-002**: The application MUST display a sidebar listing all
  projects by short name, ordered alphabetically.
- **FR-003**: The application MUST display a work item list table
  with columns for ID, area, type, status, t-shirt size, sprint,
  and title when a project is selected.
- **FR-004**: The application MUST support filtering work items by
  area, status, type, t-shirt size, and sprint.
- **FR-005**: The application MUST exclude archived work items from
  the default list view, with an option to include them.
- **FR-006**: The application MUST display a detail view for a
  work item showing all fields with markdown content rendered as
  HTML.
- **FR-007**: The application MUST provide a form to create new
  work items with type, status, and t-shirt size as dropdown
  menus populated from the database.
- **FR-008**: The application MUST provide a form to edit existing
  work items with all mutable fields editable.
- **FR-009**: The application MUST validate required fields (project,
  title, content) before submission on create and edit forms.
- **FR-010**: The application MUST support archiving work items
  with a confirmation prompt.
- **FR-011**: The application MUST display relationships for a work
  item and allow adding and removing relationships.
- **FR-012**: The application MUST provide keyword search across
  work item titles and content within the selected project.
- **FR-013**: The application MUST provide forms to create projects
  (short name, canonical path, optional GitHub repo, optional
  description) and areas (name, optional description).
- **FR-014**: The application MUST display validation errors inline
  on forms when submission fails.
- **FR-015**: The application MUST display a clear error message
  when the database connection cannot be established.
- **FR-016**: The application MUST run as a native desktop window
  on both Linux and Windows.

### Key Entities

- **Project**: Top-level organizational container. Short name serves
  as the primary identifier. Shown in sidebar for navigation.
- **Area**: Subdivision within a project. Used as a filter and
  dropdown option in work item forms.
- **Work Item**: Core entity with type, status, t-shirt size, sprint,
  title, markdown content, and optional markdown details. Displayed
  in list and detail views.
- **Related**: Labeled bidirectional relationship between two work
  items. Displayed in work item detail view.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can browse projects and work items within
  3 clicks of launching the application.
- **SC-002**: A user can create a new work item and see it in the
  list within 30 seconds.
- **SC-003**: A user can edit any field of a work item and see the
  change reflected immediately after saving.
- **SC-004**: All work item management operations available in the
  CLI (list, show, create, edit, archive, relate, search) are
  accessible through the GUI.
- **SC-005**: The application launches and displays the project list
  within 3 seconds on a standard desktop machine.
- **SC-006**: The application handles 1,000+ work items per project
  without noticeable lag in list rendering or filtering.
- **SC-007**: Form validation prevents submission of incomplete
  work items 100% of the time.

## Assumptions

- The PostgreSQL database and schema are already provisioned
  (via migrations from Spec 001). The GUI does not manage
  database schema or migrations.
- The same `~/.config/kwi/config.toml` configuration file is
  shared across all kwi tools. The GUI reads it but does not
  provide a settings UI for database configuration.
- Markdown rendering in the detail view is read-only — the
  content and details fields are edited as plain text in forms.
- The application connects directly to PostgreSQL; it does not
  go through the CLI or MCP server.
- Sprint values are free-form text input, not dropdown selections,
  since sprints are not managed entities.
- Parent work item selection in forms is by numeric ID input,
  not a searchable picker (can be enhanced later).
