<script lang="ts">
  import type { WorkItem, Area } from "$lib/types";
  import {
    listWorkItems,
    listAreas,
    getValidTypes,
    getValidStatuses,
    getValidTshirtSizes,
  } from "$lib/commands";
  import MultiSelectFilter from "./MultiSelectFilter.svelte";
  import { filterState } from "$lib/stores.svelte";

  let {
    projectId,
    onSelectItem,
    onCreateItem,
  }: {
    projectId: number;
    onSelectItem: (item: WorkItem) => void;
    onCreateItem: () => void;
  } = $props();

  let allItems = $state<WorkItem[]>([]);
  let areas = $state<Area[]>([]);
  let types = $state<string[]>([]);
  let statuses = $state<string[]>([]);
  let tshirtSizes = $state<string[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);

  // Synthetic option representing items with no sprint assigned.
  const UNASSIGNED = "Unassigned";

  // Distinct sprint option list: each non-null sprint plus "Unassigned".
  let sprintOptions = $derived(sprintValuesOf(allItems));

  function sprintValuesOf(items: WorkItem[]): string[] {
    // eslint-disable-next-line svelte/prefer-svelte-reactivity -- transient local set
    const distinct = new Set<string>();
    let hasUnassigned = false;
    for (const it of items) {
      if (it.sprint == null) hasUnassigned = true;
      else distinct.add(it.sprint);
    }
    const out = Array.from(distinct).sort();
    if (hasUnassigned) out.push(UNASSIGNED);
    return out;
  }

  // Default status selection: everything except `closed` (hidden by default).
  function defaultStatuses(s: string[]): Set<string> {
    return new Set(s.filter((v) => v !== "closed"));
  }

  function setsEqual(a: Set<string>, b: Set<string>): boolean {
    if (a.size !== b.size) return false;
    for (const v of a) if (!b.has(v)) return false;
    return true;
  }

  async function loadRefData() {
    const [a, t, s, ts] = await Promise.all([
      listAreas(projectId),
      getValidTypes(),
      getValidStatuses(),
      getValidTshirtSizes(),
    ]);
    areas = a;
    types = t;
    statuses = s;
    tshirtSizes = ts;

    // Initialize filters once per project (sticky across remounts within a
    // session). `closed` items are hidden by default.
    if (filterState.projectId !== projectId) {
      filterState.projectId = projectId;
      filterState.types = new Set(t);
      filterState.statuses = defaultStatuses(s);
      filterState.sizes = new Set(ts);
      filterState.areas = new Set(a.map((area) => area.name));
    }
  }

  async function loadItems() {
    loading = true;
    error = null;
    try {
      allItems = await listWorkItems(
        projectId,
        undefined,
        undefined,
        undefined,
        true,
      );
      // Initialize the sprint filter once per project (sprints derive from the
      // loaded items, so this happens after items arrive).
      if (filterState.sprintsProjectId !== projectId) {
        filterState.sprintsProjectId = projectId;
        filterState.sprints = new Set(sprintValuesOf(allItems));
      }
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }

  // Client-side filtering across every dimension. Archived items are hidden
  // unless the archived toggle is on.
  let filteredItems = $derived(
    allItems.filter(
      (item) =>
        (filterState.showArchived || !item.archived) &&
        filterState.types.has(item.wi_type) &&
        filterState.statuses.has(item.wi_status) &&
        filterState.sizes.has(item.wi_tshirt) &&
        (item.area_name ? filterState.areas.has(item.area_name) : true) &&
        (item.sprint != null
          ? filterState.sprints.has(item.sprint)
          : filterState.sprints.has(UNASSIGNED)),
    ),
  );

  $effect(() => {
    // Reload ref data and items when project changes
    projectId;
    void loadRefData();
    void loadItems();
  });

  function clearFilters() {
    filterState.types = new Set(types);
    filterState.statuses = defaultStatuses(statuses);
    filterState.sizes = new Set(tshirtSizes);
    filterState.areas = new Set(areas.map((area) => area.name));
    filterState.sprints = new Set(sprintOptions);
  }

  // Off-default cues: each filter differs from its default selection.
  let typesModified = $derived(filterState.types.size !== types.length);
  let statusesModified = $derived(
    !setsEqual(filterState.statuses, defaultStatuses(statuses)),
  );
  let sizesModified = $derived(filterState.sizes.size !== tshirtSizes.length);
  let areasModified = $derived(filterState.areas.size !== areas.length);
  let sprintsModified = $derived(
    filterState.sprints.size !== sprintOptions.length,
  );

  let hasActiveFilters = $derived(
    typesModified ||
      statusesModified ||
      sizesModified ||
      areasModified ||
      sprintsModified,
  );
</script>

<section class="work-item-list" aria-label="Work Items">
  <div class="toolbar">
    <div class="filters" role="group" aria-label="Filters">
      <MultiSelectFilter
        label="areas"
        options={areas.map((a) => a.name)}
        selected={filterState.areas}
        modified={areasModified}
        onchange={(v) => {
          filterState.areas = v;
        }}
      />

      <MultiSelectFilter
        label="types"
        options={types}
        selected={filterState.types}
        modified={typesModified}
        onchange={(v) => {
          filterState.types = v;
        }}
      />

      <MultiSelectFilter
        label="statuses"
        options={statuses}
        selected={filterState.statuses}
        modified={statusesModified}
        onchange={(v) => {
          filterState.statuses = v;
        }}
      />

      <MultiSelectFilter
        label="sizes"
        options={tshirtSizes}
        selected={filterState.sizes}
        modified={sizesModified}
        onchange={(v) => {
          filterState.sizes = v;
        }}
      />

      <MultiSelectFilter
        label="sprints"
        options={sprintOptions}
        selected={filterState.sprints}
        modified={sprintsModified}
        onchange={(v) => {
          filterState.sprints = v;
        }}
      />

      {#if hasActiveFilters}
        <button type="button" class="clear-btn" onclick={clearFilters}
          >Clear filters</button
        >
      {/if}
    </div>

    <div class="list-actions">
      <button
        type="button"
        class="icon-btn"
        onclick={() => {
          loadItems();
        }}
        aria-label="Refresh work items"
        title="Refresh work items"
        class:spinning={loading}>↻</button
      >
      <button type="button" class="new-btn" onclick={onCreateItem}
        >+ New Work Item</button
      >
    </div>
  </div>

  {#if loading}
    <p class="status-msg">Loading…</p>
  {:else if error}
    <p class="status-msg error">{error}</p>
  {:else if filteredItems.length === 0}
    <p class="status-msg">No work items found</p>
  {:else}
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Area</th>
            <th>Type</th>
            <th>Status</th>
            <th>Size</th>
            <th>Sprint</th>
            <th>Title</th>
          </tr>
        </thead>
        <tbody>
          {#each filteredItems as item (item.id)}
            <tr
              tabindex="0"
              role="button"
              class:archived={item.archived}
              onclick={() => onSelectItem(item)}
              onkeydown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelectItem(item);
                }
              }}
            >
              <td class="col-id">{item.id}</td>
              <td>{item.area_name ?? "—"}</td>
              <td
                ><span class="badge type-{item.wi_type.toLowerCase()}"
                  >{item.wi_type}</span
                ></td
              >
              <td
                ><span class="badge status-{item.wi_status.toLowerCase()}"
                  >{item.wi_status}</span
                ></td
              >
              <td>{item.wi_tshirt}</td>
              <td>{item.sprint ?? "—"}</td>
              <td class="col-title">{item.title}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</section>

<style>
  .work-item-list {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 1rem;
    box-sizing: border-box;
  }
  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
  }
  .filters {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    align-items: center;
  }
  .clear-btn {
    padding: 0.3rem 0.6rem;
    font-size: 0.8rem;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    background: none;
    cursor: pointer;
    color: inherit;
  }
  .list-actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }
  .icon-btn {
    width: 32px;
    height: 32px;
    padding: 0;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    background: none;
    cursor: pointer;
    font-size: 1.1rem;
    color: inherit;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .icon-btn:hover {
    background: var(--hover-bg, #e8e8e8);
  }
  .spinning {
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
  .new-btn {
    padding: 0.4rem 1rem;
    font-size: 0.9rem;
    border: none;
    border-radius: 4px;
    background: var(--accent-color, #396cd8);
    color: #fff;
    cursor: pointer;
    white-space: nowrap;
  }
  .new-btn:hover {
    opacity: 0.9;
  }
  .table-wrapper {
    flex: 1;
    overflow: auto;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }
  thead th {
    text-align: left;
    padding: 0.5rem 0.75rem;
    border-bottom: 2px solid var(--border-color, #ddd);
    font-weight: 600;
    position: sticky;
    top: 0;
    background: var(--bg-color, #f6f6f6);
  }
  tbody tr {
    cursor: pointer;
    border-bottom: 1px solid var(--border-color, #eee);
  }
  tbody tr:hover {
    background: var(--hover-bg, #e8e8e8);
  }
  tbody tr:focus-visible {
    outline: 2px solid var(--focus-color, #396cd8);
    outline-offset: -2px;
  }
  td {
    padding: 0.45rem 0.75rem;
    vertical-align: middle;
  }
  .col-id {
    width: 50px;
    font-variant-numeric: tabular-nums;
    color: var(--muted-color, #666);
  }
  .col-title {
    font-weight: 500;
  }
  .archived {
    opacity: 0.55;
    font-style: italic;
  }
  .badge {
    display: inline-block;
    padding: 0.15rem 0.45rem;
    border-radius: 3px;
    font-size: 0.8rem;
    font-weight: 500;
  }
  .status-msg {
    padding: 2rem;
    text-align: center;
    color: var(--muted-color, #888);
  }
  .status-msg.error {
    color: var(--error-color, #c33);
  }
  @media (prefers-color-scheme: dark) {
    thead th {
      background: #2f2f2f;
      border-bottom-color: #555;
    }
    tbody tr:hover {
      background: #3a3a3a;
    }
    tbody tr {
      border-bottom-color: #444;
    }
  }
</style>
