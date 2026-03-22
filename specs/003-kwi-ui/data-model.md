# Data Model: kwi Desktop GUI

**Date**: 2026-03-21
**Feature**: 003-kwi-ui

The GUI uses the same PostgreSQL schema as the CLI and MCP server.
No schema changes are needed. This document defines the Rust structs
and TypeScript interfaces that map to the existing tables.

## Rust Structs (src-tauri)

### Project

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Project {
    pub id: i32,
    pub project: String,        // short name
    pub cn_path: String,        // canonical path
    pub gh_repo: Option<String>,
    pub description: Option<String>,
    pub created: String,        // ISO 8601 timestamp
    pub updated: String,
}
```

### Area

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Area {
    pub id: i32,
    pub project_id: i32,
    pub name: String,
    pub description: Option<String>,
}
```

### WorkItem

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkItem {
    pub id: i32,
    pub project_id: i32,
    pub project_name: Option<String>,
    pub area_id: Option<i32>,
    pub area_name: Option<String>,
    pub wi_type: String,
    pub wi_status: String,
    pub wi_tshirt: String,
    pub sprint: Option<String>,
    pub title: String,
    pub content: String,
    pub details: Option<String>,
    pub parent_id: Option<i32>,
    pub created: String,
    pub updated: String,
}
```

### Related

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RelatedItem {
    pub id: i32,               // related work item ID
    pub relationship: String,
    pub title: String,
    pub direction: String,     // "left" or "right"
}
```

### Reference Data

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RefData {
    pub types: Vec<String>,
    pub statuses: Vec<String>,
    pub tshirt_sizes: Vec<String>,  // hardcoded: XS, S, M, L, XL, Huge, Unknown
}
```

## TypeScript Interfaces (frontend)

### Project

```typescript
interface Project {
  id: number;
  project: string;
  cn_path: string;
  gh_repo: string | null;
  description: string | null;
  created: string;
  updated: string;
}
```

### Area

```typescript
interface Area {
  id: number;
  project_id: number;
  name: string;
  description: string | null;
}
```

### WorkItem

```typescript
interface WorkItem {
  id: number;
  project_id: number;
  project_name: string | null;
  area_id: number | null;
  area_name: string | null;
  wi_type: string;
  wi_status: string;
  wi_tshirt: string;
  sprint: string | null;
  title: string;
  content: string;
  details: string | null;
  parent_id: number | null;
  created: string;
  updated: string;
}
```

### RelatedItem

```typescript
interface RelatedItem {
  id: number;
  relationship: string;
  title: string;
  direction: string;
}
```

## Entity Relationships

```text
Project 1──* Area
Project 1──* WorkItem
Area    1──* WorkItem (optional)
WorkItem 1──* WorkItem (parent/child, optional)
WorkItem *──* WorkItem (via Related, bidirectional)
```

## State Transitions

Work item status values: `open`, `active`, `resolved`, `closed`,
`draft`, `archived`.

No enforced state machine — any status can transition to any other.
Archiving is a special case: sets status to `archived`, which hides
the item from default list views.

## Validation Rules

- **Project**: `project` (short name) and `cn_path` are required,
  must be unique.
- **Area**: `name` is required, must be unique within a project.
- **WorkItem**: `project_id`, `title`, `content` are required.
  `wi_type` must be a valid type name. `wi_status` must be a valid
  status name. `wi_tshirt` must be one of the defined sizes.
- **Related**: `left_id` and `right_id` must reference existing
  work items. Cannot relate an item to itself.
