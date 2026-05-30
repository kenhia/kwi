# Feature Specification: KWI-UI Interface Polish

**Feature Branch**: `004-kwi-ui-polish`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: User description: "kwi-ui interface polish: window size persistence, refresh buttons, multi-select filter dropdowns, form field ordering, project details pane, and save button placement improvements"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Select Filter Dropdowns for Work Items (Priority: P1)

A user working with a large list of work items wants to filter by multiple types, statuses, or sizes simultaneously. For example, they want to see all "bug" and "task" items that are "open" or "active". Currently, each filter dropdown only allows selecting a single value, which forces the user to switch back and forth between filter values to review different categories. With multi-select checkboxes, the user can check the exact combination they need and see the filtered results immediately.

By default, all filter values should be selected except "archived" status, so users see all active work without manually excluding archived items each session.

**Why this priority**: Filtering is the primary way users navigate their work item list. Multi-select dramatically improves daily workflow efficiency and is the most impactful usability improvement.

**Independent Test**: Can be tested by selecting a project with work items of varied types/statuses, toggling checkbox combinations in each filter dropdown, and verifying the list updates correctly.

**Acceptance Scenarios**:

1. **Given** a project is selected and the work item list is displayed, **When** the user opens the Type filter dropdown, **Then** they see checkboxes for each available type with "Select All" and "Clear All" options
2. **Given** the Type filter dropdown is open, **When** the user checks "bug" and "task" only, **Then** the work item list shows only items of type "bug" or "task"
3. **Given** the Status filter dropdown is open for the first time in a session, **When** the user views the default checkbox states, **Then** all statuses are checked except "archived"
4. **Given** multiple filters are active (e.g., Type=bug,task and Status=open), **When** the user views the work item list, **Then** only items matching all active filter criteria are shown (intersection of selected values)
5. **Given** a filter has some checkboxes unchecked, **When** the user clicks "Select All", **Then** all checkboxes in that filter become checked and the list updates accordingly
6. **Given** a filter has some checkboxes checked, **When** the user clicks "Clear All", **Then** all checkboxes in that filter become unchecked and the list shows no items for that filter dimension

---

### User Story 2 - Improved Form Field Ordering (Priority: P1)

A user creating or editing a work item fills out the Title first, then typically sets the Type, Status, and Size metadata. They write the Content (main body) last, often as the longest field. Currently, Content appears directly after Title, pushing the metadata dropdowns and Details field further down. Moving Content to just before Details aligns the form with the natural workflow: set up the item metadata first, then author the content body.

**Why this priority**: Form usability directly affects the core create/edit workflow that every user performs regularly.

**Independent Test**: Can be tested by opening the create and edit forms and verifying the field order matches the specified layout.

**Acceptance Scenarios**:

1. **Given** the user clicks "New Work Item", **When** the create form renders, **Then** the field order from top to bottom is: Title, Type/Status/Size row, Area/Sprint/Parent ID row, Content, Details
2. **Given** the user clicks "Edit" on a work item, **When** the edit form renders, **Then** the field order matches the same layout as the create form
3. **Given** the user is on the create form, **When** they view the Content field, **Then** it appears immediately before the Details field near the bottom of the form

---

### User Story 3 - Sensible Create Form Defaults (Priority: P1)

A user creating a new work item expects the form to pre-populate with the most commonly used values. Currently, defaults are determined by alphabetical database ordering, resulting in "bug" for Type, "active" for Status, and "XS" for Size. The most common use case is creating an "issue" that is "open" and sized "S". Setting these as defaults eliminates repeated manual selection.

**Why this priority**: Reducing unnecessary clicks on every create operation has a high cumulative impact. Tied to basic form usability.

**Independent Test**: Can be tested by clicking "New Work Item" and verifying the pre-selected values in each dropdown.

**Acceptance Scenarios**:

1. **Given** the user clicks "New Work Item", **When** the create form renders, **Then** the Type dropdown defaults to "issue"
2. **Given** the user clicks "New Work Item", **When** the create form renders, **Then** the Status dropdown defaults to "open"
3. **Given** the user clicks "New Work Item", **When** the create form renders, **Then** the Size dropdown defaults to "S"
4. **Given** the user is editing an existing work item, **When** the edit form renders, **Then** the dropdowns show the item's current values (not the defaults)

---

### User Story 4 - Save Button at Top of Edit Form (Priority: P2)

A user editing a work item with lengthy Content or Details fields needs to scroll to the bottom of the form to reach the "Save Changes" button. When making a quick metadata change (e.g., updating Status from "open" to "active"), scrolling past all the text fields to find the save button is tedious. Adding a "Save Changes" button at the top of the form (mirroring the existing Cancel button placement) lets the user save immediately after making changes to fields near the top.

**Why this priority**: Reduces friction for the common "quick edit" workflow, especially for items with long content.

**Independent Test**: Can be tested by editing a work item and verifying a save button is available at the top of the form without scrolling.

**Acceptance Scenarios**:

1. **Given** the user is on the edit form, **When** the form renders, **Then** a "Save Changes" button appears in the top action bar alongside the "Cancel" button
2. **Given** the user has modified fields on the edit form, **When** they click the top "Save Changes" button, **Then** the changes are saved identically to clicking the bottom "Save Changes" button
3. **Given** the save operation is in progress, **When** the user views either save button, **Then** both buttons show the "Saving…" state and are disabled

---

### User Story 5 - Project Details Pane (Priority: P2)

A user who has selected a project has no way to see the project's metadata (description, CN path, GitHub repo) without looking elsewhere. Displaying the project details in a collapsible section between the search bar and work item list gives users quick access to project context while keeping it out of the way when not needed.

**Why this priority**: Provides useful project context that is currently invisible in the UI, but optional since users can work without it.

**Independent Test**: Can be tested by selecting a project and verifying the details section appears and can be expanded/collapsed.

**Acceptance Scenarios**:

1. **Given** a project is selected, **When** the main panel renders, **Then** a collapsible "Project Details" section appears between the search bar and the work item list
2. **Given** the project details section is visible, **When** the user expands it, **Then** they see the project's short name, CN path, GitHub repo (if set), and description (if set)
3. **Given** the project details section is expanded, **When** the user clicks to collapse it, **Then** the section collapses and only the section header is visible
4. **Given** the project details section, **When** the user first selects a project, **Then** the section defaults to collapsed so the work item list remains prominent

---

### User Story 6 - Refresh Buttons for Projects and Work Items (Priority: P2)

A user whose data may have been modified outside the application (e.g., via CLI or MCP tools) needs a way to manually reload the projects list and the work items list without restarting the application. Dedicated refresh buttons provide clear, intentional control over data freshness.

**Why this priority**: Important for multi-tool workflows where data changes outside the UI, but less frequent than filtering and form interactions.

**Independent Test**: Can be tested by modifying data outside the application, then clicking each refresh button and verifying updated data appears.

**Acceptance Scenarios**:

1. **Given** the Projects sidebar is visible, **When** the user clicks the refresh button in the sidebar header, **Then** the project list reloads from the database
2. **Given** a project is selected and the work item list is displayed, **When** the user clicks the refresh button in the work item list header, **Then** the work item list reloads with current filters applied
3. **Given** the refresh button is clicked, **When** data is loading, **Then** the refresh button shows a loading indicator until data is fully loaded

---

### User Story 7 - Window Size Persistence (Priority: P3)

A user who has resized the application window to fit their preferred layout expects the window to open at the same size the next time they launch the application. Currently, the window always opens at its default size, requiring the user to resize it every session.

**Why this priority**: A quality-of-life improvement that enhances the desktop application feel, but lower priority since users can resize manually each time.

**Independent Test**: Can be tested by resizing the window, closing the application, relaunching, and verifying the window opens at the previously saved size.

**Acceptance Scenarios**:

1. **Given** the user has resized the application window, **When** they close the application, **Then** the current window dimensions are saved
2. **Given** window dimensions were previously saved, **When** the user launches the application, **Then** the window opens at the saved size
3. **Given** no saved dimensions exist (first launch), **When** the application opens, **Then** it uses the default window size
4. **Given** saved dimensions would place the window partially off-screen (e.g., monitor change), **When** the application opens, **Then** the window-state plugin automatically adjusts placement to fit the available screen

---

### Edge Cases

- What happens when a filter dropdown has all checkboxes unchecked? The work item list should show no items for that filter dimension, effectively an empty result.
- What happens when the user resets all filters to defaults? All non-archived items should appear (since "archived" is unchecked by default in the Status filter).
- What happens if the window is saved at a very small size (e.g., partially minimized)? A minimum window size should be enforced to prevent unusable layouts.
- What happens if the saved window position is on a disconnected monitor? The application should detect this and fall back to default position on the primary display.
- What happens when a project has no description or GitHub repo? Those fields should be omitted or shown as empty in the project details pane, not display "null" or "undefined".

## Requirements *(mandatory)*

### Functional Requirements

#### Multi-Select Filter Dropdowns

- **FR-001**: Each work item filter (Area, Type, Status, Size) MUST use a multi-select dropdown with checkboxes instead of a single-select dropdown
- **FR-002**: Each multi-select filter dropdown MUST include "Select All" and "Clear All" actions
- **FR-003**: The Status filter MUST default to all statuses selected except "archived" on initial load
- **FR-004**: The Type and Size filters MUST default to all values selected on initial load
- **FR-005**: The work item list MUST update reactively when any filter checkbox is toggled
- **FR-006**: The existing "Include archived" checkbox MUST be removed, as archived inclusion is now handled through the Status filter's "archived" checkbox

#### Form Field Ordering

- **FR-007**: The work item create and edit forms MUST display fields in this order: Title, Type/Status/Size row, Area/Sprint/Parent ID row, Content, Details
- **FR-008**: The Content field MUST appear immediately before the Details field

#### Create Form Defaults

- **FR-009**: The create form MUST default the Type dropdown to "issue"
- **FR-010**: The create form MUST default the Status dropdown to "open"
- **FR-011**: The create form MUST default the Size dropdown to "S"
- **FR-012**: The edit form MUST populate all dropdowns with the work item's existing values, not the defaults

#### Save Button Placement

- **FR-013**: The edit form MUST display a "Save Changes" button in the top action bar alongside the existing "Cancel" button
- **FR-014**: Both top and bottom "Save Changes" buttons MUST trigger the same save operation
- **FR-015**: Both "Save Changes" buttons MUST show a synchronized disabled/loading state during save

#### Project Details Pane

- **FR-016**: A collapsible "Project Details" section MUST appear between the search bar and the work item list when a project is selected
- **FR-017**: The project details section MUST show: short name, CN path, GitHub repo (if present), and description (if present)
- **FR-018**: The project details section MUST default to collapsed
- **FR-019**: Missing optional fields (GitHub repo, description) MUST be omitted from the display rather than showing empty or null values

#### Refresh Buttons

- **FR-020**: The projects sidebar MUST include a manual refresh button in its header area
- **FR-021**: The work item list MUST include a manual refresh button in its header area
- **FR-022**: Refresh actions MUST reload data from the database while preserving current filter selections
- **FR-023**: Refresh buttons MUST show a loading indicator while data is being fetched

#### Window Size Persistence

- **FR-024**: The application MUST save the window dimensions when the user closes the application
- **FR-025**: The application MUST restore window dimensions on launch if previously saved dimensions exist
- **FR-026**: The application MUST use default window dimensions on first launch or if saved dimensions are invalid
- **FR-027**: The application MUST enforce a minimum window size to prevent unusable layouts

## Assumptions

- This sprint focuses exclusively on the Tauri/Svelte desktop UI (`kwi-ui`); no changes to the CLI or MCP server are in scope.
- The existing Tauri commands provide all necessary data—no new backend commands are expected except possibly for window size persistence.
- The Area filter dropdown will also be converted to multi-select checkboxes for consistency, even though it was not explicitly listed.
- Window size is the only dimension persisted; window position on screen is not persisted (to avoid issues with multi-monitor setups).
- This sprint is iterative—additional polish items may be added during development as the user tests and evaluates each improvement.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can filter work items by any combination of multiple types, statuses, and sizes in a single view without switching between filter values
- **SC-002**: Users can create a new work item with sensible defaults (issue/open/S) without changing any dropdown values for the most common case
- **SC-003**: Users can save an edited work item from the top of the form without scrolling past content fields
- **SC-004**: Users can view project metadata (CN path, description, GitHub repo) without leaving the work item list view
- **SC-005**: Users can manually refresh projects and work items to pick up changes made by CLI or MCP tools without restarting the application
- **SC-006**: The application remembers the user's preferred window size across sessions
- **SC-007**: The create and edit forms present fields in a logical order with metadata fields grouped before content fields
