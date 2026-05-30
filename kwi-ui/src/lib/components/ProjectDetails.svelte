<script lang="ts">
  import type { Project } from "$lib/types";

  let { project }: { project: Project } = $props();
</script>

<details class="project-details">
  <summary>Project Details</summary>
  <dl>
    <dt>Short Name</dt>
    <dd>{project.project}</dd>
    <dt>CN Path</dt>
    <dd>{project.cn_path}</dd>
    {#if project.gh_repo}
      <dt>GitHub Repo</dt>
      <dd>{project.gh_repo}</dd>
    {/if}
    {#if project.description}
      <dt>Description</dt>
      <dd>{project.description}</dd>
    {/if}
  </dl>
</details>

<style>
  .project-details {
    padding: 0 1rem;
    border-bottom: 1px solid var(--border-color, #ddd);
    font-size: 0.9rem;
  }
  summary {
    cursor: pointer;
    padding: 0.5rem 0;
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--muted-color, #666);
    user-select: none;
  }
  summary:hover {
    color: var(--accent-color, #396cd8);
  }
  dl {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.25rem 1rem;
    margin: 0 0 0.75rem;
    font-size: 0.85rem;
  }
  dt {
    font-weight: 600;
    color: var(--muted-color, #666);
    white-space: nowrap;
  }
  dd {
    margin: 0;
  }
  @media (prefers-color-scheme: dark) {
    .project-details {
      border-bottom-color: #444;
    }
  }
</style>
