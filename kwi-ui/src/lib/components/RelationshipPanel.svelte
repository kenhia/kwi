<script lang="ts">
  import type { RelatedItem } from "$lib/types";
  import {
    listRelated,
    relateWorkItems,
    unrelateWorkItems,
  } from "$lib/commands";

  let {
    workItemId,
    onNavigate,
  }: {
    workItemId: number;
    onNavigate: (id: number) => void;
  } = $props();

  let related = $state<RelatedItem[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);

  // Add relationship form
  let showAddForm = $state(false);
  let newRelatedId = $state<number | undefined>(undefined);
  let newRelationship = $state("related_to");
  let addError = $state<string | null>(null);
  let adding = $state(false);

  async function loadRelated() {
    loading = true;
    error = null;
    try {
      related = await listRelated(workItemId);
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }

  $effect(() => {
    workItemId;
    void loadRelated();
  });

  async function handleAdd(e: Event) {
    e.preventDefault();
    if (!newRelatedId) return;
    adding = true;
    addError = null;
    try {
      await relateWorkItems(workItemId, newRelatedId, newRelationship);
      showAddForm = false;
      newRelatedId = undefined;
      newRelationship = "related_to";
      await loadRelated();
    } catch (e) {
      addError = String(e);
    } finally {
      adding = false;
    }
  }

  async function handleRemove(item: RelatedItem) {
    if (!confirm(`Remove relationship with "${item.title}"?`)) return;
    try {
      await unrelateWorkItems(workItemId, item.id);
      await loadRelated();
    } catch (e) {
      alert(String(e));
    }
  }
</script>

<section class="relationships" aria-label="Relationships">
  <div class="section-header">
    <h2>Relationships</h2>
    <button
      type="button"
      class="add-btn"
      onclick={() => {
        showAddForm = !showAddForm;
      }}
    >
      {showAddForm ? "Cancel" : "+ Add"}
    </button>
  </div>

  {#if showAddForm}
    <form class="add-form" onsubmit={handleAdd}>
      {#if addError}
        <p class="add-error">{addError}</p>
      {/if}
      <div class="add-fields">
        <input
          type="number"
          bind:value={newRelatedId}
          placeholder="Work item ID"
          required
          aria-label="Related work item ID"
        />
        <select bind:value={newRelationship} aria-label="Relationship type">
          <option value="related_to">Related to</option>
          <option value="blocks">Blocks</option>
          <option value="blocked_by">Blocked by</option>
          <option value="depends_on">Depends on</option>
          <option value="parent_of">Parent of</option>
          <option value="child_of">Child of</option>
        </select>
        <button type="submit" class="submit-btn" disabled={adding}>
          {adding ? "Adding…" : "Add"}
        </button>
      </div>
    </form>
  {/if}

  {#if loading}
    <p class="status-msg">Loading…</p>
  {:else if error}
    <p class="status-msg error">{error}</p>
  {:else if related.length === 0}
    <p class="status-msg">No relationships</p>
  {:else}
    <ul class="related-list">
      {#each related as item (item.id + item.direction)}
        <li>
          <button
            type="button"
            class="related-link"
            onclick={() => onNavigate(item.id)}
          >
            <span class="rel-label">{item.relationship}</span>
            <span class="rel-title">#{item.id} {item.title}</span>
            <span class="rel-dir">({item.direction})</span>
          </button>
          <button
            type="button"
            class="remove-btn"
            onclick={() => handleRemove(item)}
            title="Remove relationship"
            aria-label="Remove relationship with {item.title}">×</button
          >
        </li>
      {/each}
    </ul>
  {/if}
</section>

<style>
  .relationships {
    margin-top: 1.5rem;
  }
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid var(--border-color, #ddd);
  }
  h2 {
    font-size: 1.1rem;
    margin: 0;
  }
  .add-btn {
    padding: 0.25rem 0.6rem;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    background: none;
    cursor: pointer;
    font-size: 0.8rem;
    color: inherit;
  }
  .add-form {
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    background: var(--card-bg, #f0f0f0);
    border-radius: 4px;
  }
  .add-fields {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }
  .add-form input[type="number"] {
    width: 120px;
    padding: 0.35rem 0.5rem;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    font-size: 0.85rem;
    background: var(--input-bg, #fff);
    color: inherit;
  }
  .add-form select {
    padding: 0.35rem 0.5rem;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    font-size: 0.85rem;
    background: var(--input-bg, #fff);
    color: inherit;
  }
  .submit-btn {
    padding: 0.35rem 0.75rem;
    border: none;
    border-radius: 4px;
    background: var(--accent-color, #396cd8);
    color: #fff;
    cursor: pointer;
    font-size: 0.85rem;
  }
  .submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  .add-error {
    color: var(--error-color, #c33);
    font-size: 0.85rem;
    margin: 0 0 0.5rem;
  }
  .related-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  .related-list li {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0;
    border-bottom: 1px solid var(--border-color, #eee);
  }
  .related-link {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    border: none;
    background: none;
    cursor: pointer;
    text-align: left;
    padding: 0.2rem 0;
    font-size: 0.9rem;
    color: inherit;
  }
  .related-link:hover .rel-title {
    text-decoration: underline;
    color: var(--accent-color, #396cd8);
  }
  .rel-label {
    font-size: 0.75rem;
    padding: 0.1rem 0.35rem;
    border-radius: 3px;
    background: var(--badge-bg, #e0e0e0);
    white-space: nowrap;
  }
  .rel-dir {
    font-size: 0.75rem;
    color: var(--muted-color, #888);
  }
  .remove-btn {
    width: 24px;
    height: 24px;
    padding: 0;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 1.1rem;
    color: var(--muted-color, #888);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .remove-btn:hover {
    color: var(--error-color, #c33);
    background: var(--hover-bg, #e8e8e8);
  }
  .status-msg {
    font-size: 0.85rem;
    color: var(--muted-color, #888);
    padding: 0.5rem 0;
  }
  .status-msg.error {
    color: var(--error-color, #c33);
  }
  @media (prefers-color-scheme: dark) {
    .add-form {
      background: #3a3a3a;
    }
    .add-form input,
    .add-form select {
      background: #2a2a2a;
      border-color: #555;
    }
    .rel-label {
      background: #555;
    }
    .related-list li {
      border-bottom-color: #444;
    }
  }
</style>
