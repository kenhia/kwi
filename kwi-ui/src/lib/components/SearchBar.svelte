<script lang="ts">
  import type { WorkItem } from "$lib/types";
  import { searchWorkItems } from "$lib/commands";

  let {
    projectId,
    onSelectResult,
  }: {
    projectId?: number;
    onSelectResult: (item: WorkItem) => void;
  } = $props();

  let query = $state("");
  let results = $state<WorkItem[]>([]);
  let hasSearched = $state(false);
  let loading = $state(false);
  let error = $state<string | null>(null);
  let showResults = $state(false);

  let debounceTimer: ReturnType<typeof setTimeout> | undefined;

  function handleInput() {
    clearTimeout(debounceTimer);
    if (query.trim().length < 2) {
      results = [];
      hasSearched = false;
      showResults = false;
      return;
    }
    debounceTimer = setTimeout(() => {
      void doSearch();
    }, 300);
  }

  async function doSearch() {
    const q = query.trim();
    if (q.length < 2) return;
    loading = true;
    error = null;
    hasSearched = true;
    showResults = true;
    try {
      results = await searchWorkItems(q, projectId);
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }

  function selectResult(item: WorkItem) {
    showResults = false;
    query = "";
    hasSearched = false;
    onSelectResult(item);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Escape") {
      showResults = false;
    }
  }

  function handleBlur() {
    // Delay to allow click on results
    setTimeout(() => { showResults = false; }, 200);
  }
</script>

<div class="search-bar" role="search">
  <input
    type="search"
    bind:value={query}
    oninput={handleInput}
    onkeydown={handleKeydown}
    onfocus={() => { if (hasSearched) showResults = true; }}
    onblur={handleBlur}
    placeholder="Search work items…"
    aria-label="Search work items"
  />
  {#if showResults}
    <div class="results-dropdown" role="listbox">
      {#if loading}
        <p class="results-msg">Searching…</p>
      {:else if error}
        <p class="results-msg error">{error}</p>
      {:else if results.length === 0}
        <p class="results-msg">No results found</p>
      {:else}
        <ul>
          {#each results as item (item.id)}
            <li>
              <button
                type="button"
                role="option"
                aria-selected="false"
                onclick={() => selectResult(item)}
              >
                <span class="result-id">#{item.id}</span>
                <span class="result-title">{item.title}</span>
                <span class="result-meta">{item.wi_type} · {item.wi_status}</span>
              </button>
            </li>
          {/each}
        </ul>
      {/if}
    </div>
  {/if}
</div>

<style>
  .search-bar {
    position: relative;
    flex: 1;
    max-width: 400px;
  }
  input[type="search"] {
    width: 100%;
    padding: 0.4rem 0.75rem;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    font-size: 0.9rem;
    background: var(--input-bg, #fff);
    color: inherit;
    box-sizing: border-box;
  }
  .results-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--dropdown-bg, #fff);
    border: 1px solid var(--border-color, #ccc);
    border-top: none;
    border-radius: 0 0 4px 4px;
    max-height: 320px;
    overflow-y: auto;
    z-index: 100;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  li button {
    display: flex;
    flex-direction: column;
    width: 100%;
    text-align: left;
    padding: 0.5rem 0.75rem;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 0.85rem;
    color: inherit;
    gap: 0.15rem;
  }
  li button:hover {
    background: var(--hover-bg, #e8e8e8);
  }
  .result-id {
    font-size: 0.75rem;
    color: var(--muted-color, #888);
  }
  .result-title {
    font-weight: 500;
  }
  .result-meta {
    font-size: 0.75rem;
    color: var(--muted-color, #888);
  }
  .results-msg {
    padding: 0.75rem;
    font-size: 0.85rem;
    color: var(--muted-color, #888);
    margin: 0;
  }
  .results-msg.error {
    color: var(--error-color, #c33);
  }
  @media (prefers-color-scheme: dark) {
    input[type="search"] {
      background: #2a2a2a;
      border-color: #555;
    }
    .results-dropdown {
      background: #2f2f2f;
      border-color: #555;
    }
    li button:hover {
      background: #3a3a3a;
    }
  }
</style>
