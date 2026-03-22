<script lang="ts">
  import type { WorkItem } from "$lib/types";
  import { marked } from "marked";
  import RelationshipPanel from "./RelationshipPanel.svelte";

  let {
    item,
    onBack,
    onEdit,
    onArchive,
    onNavigateToItem,
  }: {
    item: WorkItem;
    onBack: () => void;
    onEdit: (item: WorkItem) => void;
    onArchive: (item: WorkItem) => void;
    onNavigateToItem?: (id: number) => void;
  } = $props();

  // Configure marked for safe rendering
  marked.setOptions({ breaks: true, gfm: true });

  let renderedContent = $derived(marked.parse(item.content) as string);
  let renderedDetails = $derived(
    item.details ? (marked.parse(item.details) as string) : null,
  );
</script>

<article class="detail" aria-label="Work item detail">
  <header>
    <button type="button" class="back-btn" onclick={onBack}>← Back</button>
    <div class="actions">
      <button type="button" class="edit-btn" onclick={() => onEdit(item)}>Edit</button>
      {#if item.wi_status !== "archived"}
        <button type="button" class="archive-btn" onclick={() => onArchive(item)}>Archive</button>
      {/if}
    </div>
  </header>

  <h1>{item.title}</h1>

  <dl class="meta">
    <div class="meta-item">
      <dt>ID</dt>
      <dd>{item.id}</dd>
    </div>
    <div class="meta-item">
      <dt>Project</dt>
      <dd>{item.project_name ?? "—"}</dd>
    </div>
    <div class="meta-item">
      <dt>Area</dt>
      <dd>{item.area_name ?? "—"}</dd>
    </div>
    <div class="meta-item">
      <dt>Type</dt>
      <dd><span class="badge">{item.wi_type}</span></dd>
    </div>
    <div class="meta-item">
      <dt>Status</dt>
      <dd><span class="badge">{item.wi_status}</span></dd>
    </div>
    <div class="meta-item">
      <dt>Size</dt>
      <dd>{item.wi_tshirt}</dd>
    </div>
    <div class="meta-item">
      <dt>Sprint</dt>
      <dd>{item.sprint ?? "—"}</dd>
    </div>
    {#if item.parent_id}
      <div class="meta-item">
        <dt>Parent</dt>
        <dd>#{item.parent_id}</dd>
      </div>
    {/if}
    <div class="meta-item">
      <dt>Created</dt>
      <dd>{new Date(item.created).toLocaleString()}</dd>
    </div>
    <div class="meta-item">
      <dt>Updated</dt>
      <dd>{new Date(item.updated).toLocaleString()}</dd>
    </div>
  </dl>

  <section class="content-section">
    <h2>Content</h2>
    <div class="markdown-body">
      {@html renderedContent}
    </div>
  </section>

  {#if renderedDetails}
    <section class="content-section">
      <h2>Details</h2>
      <div class="markdown-body">
        {@html renderedDetails}
      </div>
    </section>
  {/if}

  <RelationshipPanel
    workItemId={item.id}
    onNavigate={onNavigateToItem ?? (() => {})}
  />
</article>

<style>
  .detail {
    padding: 1.5rem;
    overflow-y: auto;
    max-width: 900px;
  }
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
  .back-btn {
    padding: 0.35rem 0.75rem;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    background: none;
    cursor: pointer;
    font-size: 0.9rem;
    color: inherit;
  }
  .actions {
    display: flex;
    gap: 0.5rem;
  }
  .edit-btn {
    padding: 0.35rem 0.9rem;
    border: none;
    border-radius: 4px;
    background: var(--accent-color, #396cd8);
    color: #fff;
    cursor: pointer;
    font-size: 0.9rem;
  }
  .archive-btn {
    padding: 0.35rem 0.9rem;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    background: none;
    cursor: pointer;
    font-size: 0.9rem;
    color: var(--error-color, #c33);
  }
  h1 {
    font-size: 1.5rem;
    margin: 0 0 1rem;
  }
  .meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem 1.5rem;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: var(--card-bg, #f0f0f0);
    border-radius: 6px;
  }
  .meta-item {
    display: flex;
    gap: 0.3rem;
  }
  dt {
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--muted-color, #666);
  }
  dd {
    margin: 0;
    font-size: 0.9rem;
  }
  .badge {
    display: inline-block;
    padding: 0.1rem 0.4rem;
    border-radius: 3px;
    font-size: 0.8rem;
    font-weight: 500;
    background: var(--badge-bg, #e0e0e0);
  }
  .content-section {
    margin-bottom: 1.5rem;
  }
  .content-section h2 {
    font-size: 1.1rem;
    margin: 0 0 0.5rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid var(--border-color, #ddd);
  }
  .markdown-body {
    line-height: 1.6;
    font-size: 0.95rem;
  }
  .markdown-body :global(pre) {
    background: var(--code-bg, #f5f5f5);
    padding: 0.75rem;
    border-radius: 4px;
    overflow-x: auto;
  }
  .markdown-body :global(code) {
    font-size: 0.85em;
  }
  .markdown-body :global(a) {
    color: var(--accent-color, #396cd8);
  }
  @media (prefers-color-scheme: dark) {
    .meta {
      background: #3a3a3a;
    }
    .badge {
      background: #555;
    }
    .markdown-body :global(pre) {
      background: #3a3a3a;
    }
  }
</style>
