import type { Project, WorkItem } from "./types";

// App-level state using Svelte 5 module-level runes
// These are reactive and shared across all components that import them.

export const appState = $state({
  /** Currently selected project */
  selectedProject: null as Project | null,

  /** Currently viewed work item (detail view) */
  selectedWorkItem: null as WorkItem | null,

  /** Current view mode */
  view: "list" as "list" | "detail" | "create" | "edit",

  /** Whether a database connection error occurred */
  connectionError: null as string | null,

  /** Global loading flag */
  loading: false,
});

// Session-scoped filter selections for the work item list.
// Lifted out of WorkItemList so they survive remounts (e.g. navigating to a
// detail view and back). NOT persisted to localStorage — session-only.
export const filterState = $state({
  /** Project the type/status/size/area selections belong to */
  projectId: null as number | null,
  /** Project the sprint selection belongs to (sprints derive from items) */
  sprintsProjectId: null as number | null,
  /** When true, archived items are shown; defaults to hidden */
  showArchived: false,
  // eslint-disable-next-line svelte/prefer-svelte-reactivity -- reassigned wholesale; reactivity tracked at the property level
  types: new Set<string>(),
  // eslint-disable-next-line svelte/prefer-svelte-reactivity -- reassigned wholesale; reactivity tracked at the property level
  statuses: new Set<string>(),
  // eslint-disable-next-line svelte/prefer-svelte-reactivity -- reassigned wholesale; reactivity tracked at the property level
  sizes: new Set<string>(),
  // eslint-disable-next-line svelte/prefer-svelte-reactivity -- reassigned wholesale; reactivity tracked at the property level
  areas: new Set<string>(),
  // eslint-disable-next-line svelte/prefer-svelte-reactivity -- reassigned wholesale; reactivity tracked at the property level
  sprints: new Set<string>(),
});
