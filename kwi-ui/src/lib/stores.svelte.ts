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
