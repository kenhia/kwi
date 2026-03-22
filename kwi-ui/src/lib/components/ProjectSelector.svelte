<script lang="ts">
  import type { Project } from "$lib/types";
  import { listProjects, createProject, createArea, listAreas } from "$lib/commands";
  import type { Area } from "$lib/types";

  let { onSelect }: { onSelect: (project: Project) => void } = $props();

  let projects = $state<Project[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);

  // Add project form
  let showAddProject = $state(false);
  let newProjectName = $state("");
  let newProjectCnPath = $state("");
  let newProjectGhRepo = $state("");
  let newProjectDesc = $state("");
  let addProjectError = $state<string | null>(null);
  let addingProject = $state(false);

  // Add area form
  let showAddArea = $state(false);
  let addAreaForProject = $state<Project | null>(null);
  let newAreaName = $state("");
  let newAreaDesc = $state("");
  let addAreaError = $state<string | null>(null);
  let addingArea = $state(false);

  async function loadProjects() {
    loading = true;
    error = null;
    try {
      projects = await listProjects();
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }

  $effect(() => {
    loadProjects();
  });

  async function handleAddProject(e: Event) {
    e.preventDefault();
    if (!newProjectName.trim() || !newProjectCnPath.trim()) return;
    addingProject = true;
    addProjectError = null;
    try {
      const created = await createProject({
        project: newProjectName.trim(),
        cnPath: newProjectCnPath.trim(),
        ghRepo: newProjectGhRepo.trim() || undefined,
        description: newProjectDesc.trim() || undefined,
      });
      showAddProject = false;
      newProjectName = "";
      newProjectCnPath = "";
      newProjectGhRepo = "";
      newProjectDesc = "";
      await loadProjects();
      onSelect(created);
    } catch (e) {
      addProjectError = String(e);
    } finally {
      addingProject = false;
    }
  }

  function startAddArea(project: Project) {
    addAreaForProject = project;
    showAddArea = true;
    newAreaName = "";
    newAreaDesc = "";
    addAreaError = null;
  }

  async function handleAddArea(e: Event) {
    e.preventDefault();
    if (!addAreaForProject || !newAreaName.trim()) return;
    addingArea = true;
    addAreaError = null;
    try {
      await createArea({
        projectId: addAreaForProject.id,
        name: newAreaName.trim(),
        description: newAreaDesc.trim() || undefined,
      });
      showAddArea = false;
      addAreaForProject = null;
      newAreaName = "";
      newAreaDesc = "";
    } catch (e) {
      addAreaError = String(e);
    } finally {
      addingArea = false;
    }
  }
</script>

<nav class="sidebar" aria-label="Projects">
  <div class="sidebar-header">
    <h2>Projects</h2>
    <button type="button" class="add-btn" onclick={() => { showAddProject = !showAddProject; }} title="Add project">+</button>
  </div>

  {#if showAddProject}
    <form class="add-form" onsubmit={handleAddProject}>
      {#if addProjectError}
        <p class="form-error">{addProjectError}</p>
      {/if}
      <input type="text" bind:value={newProjectName} placeholder="Short name *" required />
      <input type="text" bind:value={newProjectCnPath} placeholder="CN path *" required />
      <input type="text" bind:value={newProjectGhRepo} placeholder="GitHub repo (optional)" />
      <input type="text" bind:value={newProjectDesc} placeholder="Description (optional)" />
      <div class="form-actions">
        <button type="button" class="cancel-btn" onclick={() => { showAddProject = false; }}>Cancel</button>
        <button type="submit" class="submit-btn" disabled={addingProject}>{addingProject ? "…" : "Create"}</button>
      </div>
    </form>
  {/if}

  {#if loading}
    <p class="loading">Loading…</p>
  {:else if error}
    <p class="error">{error}</p>
  {:else if projects.length === 0}
    <p class="empty">No projects found</p>
  {:else}
    <ul>
      {#each projects as project (project.id)}
        <li>
          <button
            type="button"
            class="project-btn"
            onclick={() => onSelect(project)}
            title={project.description || project.project}
          >
            {project.project}
          </button>
          <button
            type="button"
            class="area-btn"
            onclick={() => startAddArea(project)}
            title="Add area to {project.project}"
          >◆</button>
        </li>
      {/each}
    </ul>
  {/if}

  {#if showAddArea && addAreaForProject}
    <form class="add-form area-form" onsubmit={handleAddArea}>
      <p class="form-label">Add area to <strong>{addAreaForProject.project}</strong></p>
      {#if addAreaError}
        <p class="form-error">{addAreaError}</p>
      {/if}
      <input type="text" bind:value={newAreaName} placeholder="Area name *" required />
      <input type="text" bind:value={newAreaDesc} placeholder="Description (optional)" />
      <div class="form-actions">
        <button type="button" class="cancel-btn" onclick={() => { showAddArea = false; }}>Cancel</button>
        <button type="submit" class="submit-btn" disabled={addingArea}>{addingArea ? "…" : "Create"}</button>
      </div>
    </form>
  {/if}
</nav>

<style>
  .sidebar {
    width: 220px;
    min-width: 180px;
    border-right: 1px solid var(--border-color, #ddd);
    padding: 1rem;
    overflow-y: auto;
    height: 100vh;
    box-sizing: border-box;
  }
  .sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }
  h2 {
    margin: 0;
    font-size: 1.1rem;
  }
  .add-btn {
    width: 28px;
    height: 28px;
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
  .add-btn:hover {
    background: var(--hover-bg, #e8e8e8);
  }
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  li {
    margin-bottom: 2px;
    display: flex;
    align-items: center;
  }
  .project-btn {
    flex: 1;
    text-align: left;
    padding: 0.5rem 0.75rem;
    border: none;
    background: none;
    cursor: pointer;
    border-radius: 4px;
    font-size: 0.95rem;
    color: inherit;
  }
  .project-btn:hover {
    background: var(--hover-bg, #e8e8e8);
  }
  .project-btn:focus-visible {
    outline: 2px solid var(--focus-color, #396cd8);
    outline-offset: -2px;
  }
  .area-btn {
    width: 24px;
    height: 24px;
    padding: 0;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 0.6rem;
    color: var(--muted-color, #888);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .area-btn:hover {
    color: var(--accent-color, #396cd8);
    background: var(--hover-bg, #e8e8e8);
  }
  .add-form {
    padding: 0.75rem;
    margin-bottom: 0.75rem;
    background: var(--card-bg, #f0f0f0);
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }
  .add-form input {
    width: 100%;
    padding: 0.35rem 0.5rem;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    font-size: 0.8rem;
    background: var(--input-bg, #fff);
    color: inherit;
    box-sizing: border-box;
  }
  .form-actions {
    display: flex;
    gap: 0.3rem;
    justify-content: flex-end;
  }
  .cancel-btn, .submit-btn {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    cursor: pointer;
  }
  .cancel-btn {
    border: 1px solid var(--border-color, #ccc);
    background: none;
    color: inherit;
  }
  .submit-btn {
    border: none;
    background: var(--accent-color, #396cd8);
    color: #fff;
  }
  .submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  .form-error {
    color: var(--error-color, #c33);
    font-size: 0.8rem;
    margin: 0;
  }
  .form-label {
    font-size: 0.8rem;
    margin: 0;
  }
  .loading, .empty {
    color: var(--muted-color, #888);
    font-size: 0.9rem;
  }
  .error {
    color: var(--error-color, #c33);
    font-size: 0.9rem;
  }
  @media (prefers-color-scheme: dark) {
    .sidebar {
      border-right-color: #444;
    }
    .project-btn:hover, .add-btn:hover, .area-btn:hover {
      background: #3a3a3a;
    }
    .add-form {
      background: #3a3a3a;
    }
    .add-form input {
      background: #2a2a2a;
      border-color: #555;
    }
  }
</style>
