<script lang="ts">
  let {
    label,
    options,
    selected,
    onchange,
  }: {
    label: string;
    options: string[];
    selected: Set<string>;
    onchange: (updated: Set<string>) => void;
  } = $props();

  let open = $state(false);
  let container: HTMLDivElement;

  let summary = $derived(() => {
    const count = selected.size;
    const total = options.length;
    if (count === 0) return `No ${label}`;
    if (count === total) return `All ${label}`;
    return `${count} of ${total} ${label}`;
  });

  function toggle(option: string) {
    // eslint-disable-next-line svelte/prefer-svelte-reactivity -- local copy passed to parent via onchange; parent owns the reactive state
    const next = new Set(selected);
    if (next.has(option)) {
      next.delete(option);
    } else {
      next.add(option);
    }
    onchange(next);
  }

  function selectAll() {
    onchange(new Set(options));
  }

  function clearAll() {
    onchange(new Set());
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Escape" && open) {
      open = false;
      e.stopPropagation();
    }
  }

  function handleClickOutside(e: MouseEvent) {
    if (open && container && !container.contains(e.target as Node)) {
      open = false;
    }
  }

  $effect(() => {
    if (open) {
      document.addEventListener("click", handleClickOutside, true);
      document.addEventListener("keydown", handleKeydown, true);
      return () => {
        document.removeEventListener("click", handleClickOutside, true);
        document.removeEventListener("keydown", handleKeydown, true);
      };
    }
  });
</script>

<div class="multi-select" bind:this={container}>
  <button
    type="button"
    class="trigger"
    onclick={() => (open = !open)}
    aria-haspopup="listbox"
    aria-expanded={open}
  >
    {summary()}
  </button>

  {#if open}
    <div
      class="dropdown"
      role="listbox"
      aria-multiselectable="true"
      aria-label={label}
    >
      <div class="actions">
        <button type="button" class="action-btn" onclick={selectAll}
          >Select All</button
        >
        <button type="button" class="action-btn" onclick={clearAll}
          >Clear All</button
        >
      </div>
      {#each options as option (option)}
        <label class="option">
          <input
            type="checkbox"
            checked={selected.has(option)}
            onchange={() => toggle(option)}
          />
          {option}
        </label>
      {/each}
    </div>
  {/if}
</div>

<style>
  .multi-select {
    position: relative;
    display: inline-block;
  }
  .trigger {
    padding: 0.35rem 0.6rem;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    background: var(--input-bg, #fff);
    color: inherit;
    cursor: pointer;
    font-size: 0.85rem;
    white-space: nowrap;
  }
  .trigger:hover {
    border-color: var(--accent-color, #396cd8);
  }
  .dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    z-index: 10;
    min-width: 180px;
    max-height: 280px;
    overflow-y: auto;
    margin-top: 2px;
    padding: 0.25rem 0;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    background: var(--input-bg, #fff);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }
  .actions {
    display: flex;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    border-bottom: 1px solid var(--border-color, #eee);
    margin-bottom: 0.25rem;
  }
  .action-btn {
    flex: 1;
    padding: 0.2rem 0.4rem;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 3px;
    background: none;
    cursor: pointer;
    font-size: 0.75rem;
    color: inherit;
  }
  .action-btn:hover {
    background: var(--hover-bg, #e8e8e8);
  }
  .option {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.25rem 0.5rem;
    cursor: pointer;
    font-size: 0.85rem;
  }
  .option:hover {
    background: var(--hover-bg, #e8e8e8);
  }
  .option input[type="checkbox"] {
    margin: 0;
  }
  @media (prefers-color-scheme: dark) {
    .dropdown {
      background: #2a2a2a;
      border-color: #555;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    }
    .actions {
      border-bottom-color: #555;
    }
    .action-btn:hover,
    .option:hover {
      background: #3a3a3a;
    }
    .trigger {
      background: #2a2a2a;
      border-color: #555;
    }
  }
</style>
