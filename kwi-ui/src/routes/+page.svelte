<script lang="ts">
  import type { Project, WorkItem } from "$lib/types";
  import { appState } from "$lib/stores.svelte";
  import {
    getWorkItem,
    archiveWorkItem,
    unarchiveWorkItem,
    checkConnection,
  } from "$lib/commands";
  import ProjectSelector from "$lib/components/ProjectSelector.svelte";
  import ProjectDetails from "$lib/components/ProjectDetails.svelte";
  import WorkItemList from "$lib/components/WorkItemList.svelte";
  import WorkItemDetail from "$lib/components/WorkItemDetail.svelte";
  import WorkItemForm from "$lib/components/WorkItemForm.svelte";
  import SearchBar from "$lib/components/SearchBar.svelte";

  // Check DB connection on startup
  $effect(() => {
    checkConnection().catch((e: unknown) => {
      appState.connectionError = String(e);
    });
  });

  function selectProject(project: Project) {
    appState.selectedProject = project;
    appState.selectedWorkItem = null;
    appState.view = "list";
  }

  async function selectWorkItem(item: WorkItem) {
    try {
      appState.selectedWorkItem = await getWorkItem(item.id);
      appState.view = "detail";
    } catch {
      appState.selectedWorkItem = item;
      appState.view = "detail";
    }
  }

  function backToList() {
    appState.selectedWorkItem = null;
    appState.view = "list";
  }

  function startCreate() {
    appState.view = "create";
  }

  function startEdit(item: WorkItem) {
    appState.selectedWorkItem = item;
    appState.view = "edit";
  }

  function onFormSave(_item: WorkItem) {
    appState.view = "list";
    appState.selectedWorkItem = null;
    // The list component will re-fetch when view changes
    listKey++;
  }

  async function handleArchive(item: WorkItem) {
    try {
      await archiveWorkItem(item.id);
      backToList();
      listKey++;
    } catch (e) {
      alert(String(e));
    }
  }

  async function handleUnarchive(item: WorkItem) {
    try {
      await unarchiveWorkItem(item.id);
      backToList();
      listKey++;
    } catch (e) {
      alert(String(e));
    }
  }

  // Force re-render of WorkItemList after mutations
  let listKey = $state(0);

  async function navigateToItemById(id: number) {
    try {
      appState.selectedWorkItem = await getWorkItem(id);
      appState.view = "detail";
    } catch (e) {
      alert(`Could not load work item #${id}: ${e}`);
    }
  }
</script>

{#if appState.connectionError}
  <main class="error-screen" role="alert">
    <div class="error-card">
      <h1>Database Connection Error</h1>
      <p class="error-message">{appState.connectionError}</p>
      <section>
        <h2>How to configure the connection</h2>
        <ol>
          <li>
            <strong>Option 1 — Environment variable:</strong><br />
            Set <code>KWI_DATABASE_URL</code> before launching the app:<br />
            <code
              >export
              KWI_DATABASE_URL="postgresql://user:pass@host:5432/workitems"</code
            >
          </li>
          <li>
            <strong>Option 2 — Config file:</strong><br />
            The config file path is shown in the error above. Create it with:<br
            />
            <pre>database_url = "postgresql://user:pass@host:5432/workitems"</pre>
            To keep the password out of the connection string, add:<br />
            <pre>db_password = "your_password"</pre>
          </li>
        </ol>
        <p>
          Both <code>postgresql://</code> URI and <code>key=value</code> formats are
          accepted.
        </p>
      </section>
    </div>
  </main>
{:else}
  <div class="app-layout">
    <ProjectSelector onSelect={selectProject} />

    <main class="main-panel">
      {#if appState.selectedProject}
        <div class="top-bar">
          <SearchBar
            projectId={appState.selectedProject.id}
            onSelectResult={selectWorkItem}
          />
        </div>
        <ProjectDetails project={appState.selectedProject} />
      {/if}
      {#if !appState.selectedProject}
        <div class="placeholder">
          <p>Select a project from the sidebar to begin</p>
        </div>
      {:else if appState.view === "create"}
        <WorkItemForm
          projectId={appState.selectedProject.id}
          projectName={appState.selectedProject.project}
          onSave={onFormSave}
          onCancel={backToList}
        />
      {:else if appState.view === "edit" && appState.selectedWorkItem}
        <WorkItemForm
          projectId={appState.selectedProject.id}
          projectName={appState.selectedProject.project}
          editItem={appState.selectedWorkItem}
          onSave={onFormSave}
          onCancel={() => {
            appState.view = "detail";
          }}
        />
      {:else if appState.view === "detail" && appState.selectedWorkItem}
        <WorkItemDetail
          item={appState.selectedWorkItem}
          onBack={backToList}
          onEdit={startEdit}
          onArchive={handleArchive}
          onUnarchive={handleUnarchive}
          onNavigateToItem={navigateToItemById}
        />
      {:else}
        {#key listKey}
          <WorkItemList
            projectId={appState.selectedProject.id}
            onSelectItem={selectWorkItem}
            onCreateItem={startCreate}
          />
        {/key}
      {/if}
    </main>
  </div>
{/if}

<style>
  :global(body) {
    margin: 0;
    font-family: Inter, Avenir, Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1.5;
    color: #0f0f0f;
    background-color: #f6f6f6;
  }
  .app-layout {
    display: flex;
    height: 100vh;
    overflow: hidden;
  }
  .main-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .top-bar {
    display: flex;
    align-items: center;
    padding: 0.5rem 1rem;
    border-bottom: 1px solid var(--border-color, #ddd);
    flex-shrink: 0;
  }
  .placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #888;
    font-size: 1.1rem;
  }
  .error-screen {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    padding: 2rem;
  }
  .error-card {
    max-width: 600px;
    padding: 2rem;
    border: 1px solid #e0c0c0;
    border-radius: 8px;
    background: #fff5f5;
  }
  .error-card h1 {
    color: #c33;
    font-size: 1.4rem;
    margin: 0 0 0.75rem;
  }
  .error-card h2 {
    font-size: 1.1rem;
    margin: 1.5rem 0 0.5rem;
  }
  .error-message {
    color: #c33;
    margin-bottom: 1rem;
  }
  .error-card ol {
    padding-left: 1.5rem;
  }
  .error-card li {
    margin-bottom: 1rem;
  }
  .error-card code {
    background: #f0f0f0;
    padding: 0.1rem 0.3rem;
    border-radius: 3px;
    font-size: 0.85rem;
  }
  .error-card pre {
    background: #f0f0f0;
    padding: 0.5rem;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 0.85rem;
  }
  @media (prefers-color-scheme: dark) {
    :global(body) {
      color: #f6f6f6;
      background-color: #2f2f2f;
    }
    .error-card {
      background: #3a2020;
      border-color: #6a3030;
    }
    .error-card code,
    .error-card pre {
      background: #2a2a2a;
    }
    .top-bar {
      border-bottom-color: #444;
    }
  }
  @media (max-width: 768px) {
    .app-layout {
      flex-direction: column;
    }
    .app-layout :global(.sidebar) {
      width: 100%;
      height: auto;
      max-height: 30vh;
      border-right: none;
      border-bottom: 1px solid var(--border-color, #ddd);
    }
  }
</style>
