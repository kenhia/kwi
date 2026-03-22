<script lang="ts">
  import type { WorkItem, Area } from "$lib/types";
  import { listWorkItems, listAreas, getValidTypes, getValidStatuses, getValidTshirtSizes } from "$lib/commands";

  let {
    projectId,
    onSelectItem,
    onCreateItem,
  }: {
    projectId: number;
    onSelectItem: (item: WorkItem) => void;
    onCreateItem: () => void;
  } = $props();

  let items = $state<WorkItem[]>([]);
  let areas = $state<Area[]>([]);
  let types = $state<string[]>([]);
  let statuses = $state<string[]>([]);
  let tshirtSizes = $state<string[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);

  // Filters
  let filterArea = $state<number | undefined>(undefined);
  let filterType = $state<string | undefined>(undefined);
  let filterStatus = $state<string | undefined>(undefined);
  let filterTshirt = $state<string | undefined>(undefined);
  let showArchived = $state(false);

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
  }

  async function loadItems() {
    loading = true;
    error = null;
    try {
      items = await listWorkItems(projectId, filterArea, filterType, filterStatus, showArchived);
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }

  // Filter by t-shirt on the client side since the backend doesn't support it directly
  let filteredItems = $derived(
    filterTshirt ? items.filter((i) => i.wi_tshirt === filterTshirt) : items
  );

  $effect(() => {
    // Reload ref data when project changes
    void loadRefData();
  });

  $effect(() => {
    // Reload items when project or any filter changes
    // Access reactive vars to track them
    projectId; filterArea; filterType; filterStatus; showArchived;
    void loadItems();
  });

  function clearFilters() {
    filterArea = undefined;
    filterType = undefined;
    filterStatus = undefined;
    filterTshirt = undefined;
    showArchived = false;
  }

  let hasActiveFilters = $derived(
    filterArea !== undefined ||
    filterType !== undefined ||
    filterStatus !== undefined ||
    filterTshirt !== undefined ||
    showArchived
  );
</script>

<section class="work-item-list" aria-label="Work Items">
  <div class="toolbar">
    <div class="filters" role="group" aria-label="Filters">
      <select
        bind:value={filterArea}
        aria-label="Filter by area"
        onchange={() => { filterArea = filterArea === undefined ? undefined : Number(filterArea) || undefined; }}
      >
        <option value={undefined}>All areas</option>
        {#each areas as area (area.id)}
          <option value={area.id}>{area.name}</option>
        {/each}
      </select>

      <select bind:value={filterType} aria-label="Filter by type">
        <option value={undefined}>All types</option>
        {#each types as t (t)}
          <option value={t}>{t}</option>
        {/each}
      </select>

      <select bind:value={filterStatus} aria-label="Filter by status">
        <option value={undefined}>All statuses</option>
        {#each statuses as s (s)}
          <option value={s}>{s}</option>
        {/each}
      </select>

      <select bind:value={filterTshirt} aria-label="Filter by t-shirt size">
        <option value={undefined}>All sizes</option>
        {#each tshirtSizes as sz (sz)}
          <option value={sz}>{sz}</option>
        {/each}
      </select>

      <label class="archived-toggle">
        <input type="checkbox" bind:checked={showArchived} />
        Include archived
      </label>

      {#if hasActiveFilters}
        <button type="button" class="clear-btn" onclick={clearFilters}>Clear filters</button>
      {/if}
    </div>

    <button type="button" class="new-btn" onclick={onCreateItem}>+ New Work Item</button>
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
              class:archived={item.wi_status === "archived"}
              onclick={() => onSelectItem(item)}
              onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelectItem(item); } }}
            >
              <td class="col-id">{item.id}</td>
              <td>{item.area_name ?? "—"}</td>
              <td><span class="badge type-{item.wi_type.toLowerCase()}">{item.wi_type}</span></td>
              <td><span class="badge status-{item.wi_status.toLowerCase()}">{item.wi_status}</span></td>
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
  select {
    padding: 0.35rem 0.5rem;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    font-size: 0.85rem;
    background: var(--input-bg, #fff);
    color: inherit;
  }
  .archived-toggle {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.85rem;
    white-space: nowrap;
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
    select {
      background: #2a2a2a;
      border-color: #555;
    }
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
