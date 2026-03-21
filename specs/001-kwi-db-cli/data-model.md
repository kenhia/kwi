# Data Model: kwi Database Schema & CLI

**Date**: 2026-03-21
**Feature**: 001-kwi-db-cli
**Source**: Spec FR-001 through FR-005, schema from design notes

## Entities

### workitem_type (reference table)

| Field | Type | Constraints |
|-------|------|-------------|
| id | serial | PK |
| name | text | UNIQUE, NOT NULL |

**Seed values**: bug, task, idea, research, tweak, issue, feature,
epic, story

---

### workitem_status (reference table)

| Field | Type | Constraints |
|-------|------|-------------|
| id | serial | PK |
| name | text | UNIQUE, NOT NULL |

**Seed values**: open, active, resolved, closed, draft, archived

---

### project

| Field | Type | Constraints |
|-------|------|-------------|
| id | serial | PK |
| project | text | UNIQUE, NOT NULL (short name) |
| gh_repo | text | nullable (GitHub repo URL) |
| cn_path | text | NOT NULL (canonical filesystem path) |
| created | timestamptz | NOT NULL, DEFAULT NOW() |
| updated | timestamptz | NOT NULL, DEFAULT NOW() |
| description | text | nullable (markdown) |

**Relationships**:
- One project → many areas (cascade delete)
- One project → many work items (cascade delete)

---

### area

| Field | Type | Constraints |
|-------|------|-------------|
| id | serial | PK |
| project_id | integer | FK → project(id), ON DELETE CASCADE, NOT NULL |
| name | text | NOT NULL |
| description | text | nullable |

**Constraints**:
- UNIQUE INDEX on (project_id, name) — no duplicate area names
  within a project

---

### workitem

| Field | Type | Constraints |
|-------|------|-------------|
| id | serial | PK |
| project_id | integer | FK → project(id), ON DELETE CASCADE, NOT NULL |
| area_id | integer | FK → area(id), ON DELETE SET NULL, nullable |
| wi_type_id | integer | FK → workitem_type(id), NOT NULL |
| wi_status_id | integer | FK → workitem_status(id), NOT NULL |
| wi_tshirt | text | CHECK IN ('XS','S','M','L','XL','Huge','Unknown'), DEFAULT 'Unknown' |
| sprint | text | nullable (free-form label) |
| title | text | NOT NULL |
| content | text | NOT NULL (markdown) |
| details | text | nullable (markdown) |
| parent_id | integer | FK → workitem(id), ON DELETE SET NULL, nullable |
| created | timestamptz | NOT NULL, DEFAULT NOW() |
| updated | timestamptz | NOT NULL, DEFAULT NOW() |

**Relationships**:
- Belongs to one project (required)
- Optionally belongs to one area
- Has one type (required, FK to workitem_type)
- Has one status (required, FK to workitem_status)
- Optionally has one parent work item (self-referential)
- Many-to-many with other work items via `related` table

---

### related

| Field | Type | Constraints |
|-------|------|-------------|
| id | serial | PK |
| left_id | integer | FK → workitem(id), ON DELETE CASCADE, NOT NULL |
| right_id | integer | FK → workitem(id), ON DELETE CASCADE, NOT NULL |
| relationship | text | NOT NULL |

**Constraints**:
- Application-level: prevent self-referencing (left_id ≠ right_id)
- Relationships are bidirectional in queries (query both left_id
  and right_id when listing related items)

## State Transitions

Work item statuses follow this general flow, though any transition
is allowed:

```
draft → open → active → resolved → closed
                  ↓
               archived
```

- `archived` is a terminal state for filtering purposes (excluded
  from default list) but can be transitioned back if needed.
- No enforced state machine — the user can set any valid status at
  any time via `kwi work set`.

## Entity Relationship Diagram

```
workitem_type 1──┐
                 │
workitem_status 1─┤
                 │
project 1────────┤──* area
  │              │
  └──* workitem *┘
       │    │
       │    └── parent_id (self-ref, optional)
       │
       └──* related *── workitem
```
