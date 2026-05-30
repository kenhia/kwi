<script lang="ts">
  import type { WorkItem, Area } from "$lib/types";
  import {
    listAreas,
    getValidTypes,
    getValidStatuses,
    getValidTshirtSizes,
    createWorkItem,
    updateWorkItem,
  } from "$lib/commands";

  let {
    projectId,
    projectName,
    editItem = null,
    onSave,
    onCancel,
  }: {
    projectId: number;
    projectName: string;
    editItem?: WorkItem | null;
    onSave: (item: WorkItem) => void;
    onCancel: () => void;
  } = $props();

  let isEdit = $derived(editItem !== null);

  // Form fields — synced from editItem via $effect below
  let title = $state("");
  let content = $state("");
  let wiType = $state("");
  let wiStatus = $state("");
  let wiTshirt = $state("");
  let areaId = $state<number | undefined>(undefined);
  let sprint = $state("");
  let details = $state("");
  let parentId = $state<number | undefined>(undefined);

  // Sync form fields when editItem changes (create vs edit mode)
  $effect(() => {
    title = editItem?.title ?? "";
    content = editItem?.content ?? "";
    wiType = editItem?.wi_type ?? "";
    wiStatus = editItem?.wi_status ?? "";
    wiTshirt = editItem?.wi_tshirt ?? "";
    areaId = editItem?.area_id ?? undefined;
    sprint = editItem?.sprint ?? "";
    details = editItem?.details ?? "";
    parentId = editItem?.parent_id ?? undefined;
  });

  // Ref data
  let areas = $state<Area[]>([]);
  let types = $state<string[]>([]);
  let statuses = $state<string[]>([]);
  let tshirtSizes = $state<string[]>([]);

  // UI state
  let saving = $state(false);
  let errorMsg = $state<string | null>(null);
  let validationErrors = $state<Record<string, string>>({});

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
    // Set defaults for create mode
    if (!isEdit) {
      if (!wiType && types.length > 0)
        wiType = types.find((t) => t === "issue") ?? types[0];
      if (!wiStatus && statuses.length > 0)
        wiStatus = statuses.find((s) => s === "open") ?? statuses[0];
      if (!wiTshirt && tshirtSizes.length > 0)
        wiTshirt = tshirtSizes.find((s) => s === "S") ?? tshirtSizes[0];
    }
  }

  $effect(() => {
    void loadRefData();
  });

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!title.trim()) errors.title = "Title is required";
    if (!content.trim()) errors.content = "Content is required";
    if (!wiType) errors.wiType = "Type is required";
    validationErrors = errors;
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();
    if (!validate()) return;
    saving = true;
    errorMsg = null;
    try {
      let saved: WorkItem;
      if (isEdit && editItem) {
        saved = await updateWorkItem({
          id: editItem.id,
          title: title.trim(),
          content: content.trim(),
          wiType,
          wiStatus: wiStatus || undefined,
          wiTshirt: wiTshirt || undefined,
          areaId: areaId,
          sprint: sprint.trim() || undefined,
          details: details.trim() || undefined,
          parentId: parentId,
        });
      } else {
        saved = await createWorkItem({
          projectId,
          title: title.trim(),
          content: content.trim(),
          wiType,
          wiStatus: wiStatus || undefined,
          wiTshirt: wiTshirt || undefined,
          areaId: areaId,
          sprint: sprint.trim() || undefined,
          details: details.trim() || undefined,
          parentId: parentId,
        });
      }
      onSave(saved);
    } catch (e) {
      errorMsg = String(e);
    } finally {
      saving = false;
    }
  }
</script>

<form
  class="work-item-form"
  onsubmit={handleSubmit}
  aria-label="{isEdit ? 'Edit' : 'Create'} work item"
>
  <header>
    <h2>{isEdit ? "Edit" : "New"} Work Item</h2>
    <div class="header-actions">
      <button type="button" class="cancel-btn" onclick={onCancel}>Cancel</button
      >
      {#if isEdit}
        <button type="submit" class="submit-btn" disabled={saving}>
          {saving ? "Saving…" : "Save Changes"}
        </button>
      {/if}
    </div>
  </header>

  {#if errorMsg}
    <p class="form-error" role="alert">{errorMsg}</p>
  {/if}

  <div class="field">
    <label for="wi-project">Project</label>
    <input id="wi-project" type="text" value={projectName} disabled />
  </div>

  <div class="field">
    <label for="wi-title">Title <span class="required">*</span></label>
    <input
      id="wi-title"
      type="text"
      bind:value={title}
      class:invalid={validationErrors.title}
    />
    {#if validationErrors.title}<span class="field-error"
        >{validationErrors.title}</span
      >{/if}
  </div>

  <div class="field-row">
    <div class="field">
      <label for="wi-type">Type <span class="required">*</span></label>
      <select
        id="wi-type"
        bind:value={wiType}
        class:invalid={validationErrors.wiType}
      >
        <option value="">Select…</option>
        {#each types as t (t)}
          <option value={t}>{t}</option>
        {/each}
      </select>
      {#if validationErrors.wiType}<span class="field-error"
          >{validationErrors.wiType}</span
        >{/if}
    </div>

    <div class="field">
      <label for="wi-status">Status</label>
      <select id="wi-status" bind:value={wiStatus}>
        {#each statuses as s (s)}
          <option value={s}>{s}</option>
        {/each}
      </select>
    </div>

    <div class="field">
      <label for="wi-tshirt">Size</label>
      <select id="wi-tshirt" bind:value={wiTshirt}>
        {#each tshirtSizes as sz (sz)}
          <option value={sz}>{sz}</option>
        {/each}
      </select>
    </div>
  </div>

  <div class="field-row">
    <div class="field">
      <label for="wi-area">Area</label>
      <select id="wi-area" bind:value={areaId}>
        <option value={undefined}>None</option>
        {#each areas as area (area.id)}
          <option value={area.id}>{area.name}</option>
        {/each}
      </select>
    </div>

    <div class="field">
      <label for="wi-sprint">Sprint</label>
      <input
        id="wi-sprint"
        type="text"
        bind:value={sprint}
        placeholder="e.g. 2024-W03"
      />
    </div>

    <div class="field">
      <label for="wi-parent">Parent ID</label>
      <input
        id="wi-parent"
        type="number"
        bind:value={parentId}
        placeholder="Optional"
      />
    </div>
  </div>

  <div class="field">
    <label for="wi-content">Content <span class="required">*</span></label>
    <textarea
      id="wi-content"
      bind:value={content}
      rows="6"
      class:invalid={validationErrors.content}
    ></textarea>
    {#if validationErrors.content}<span class="field-error"
        >{validationErrors.content}</span
      >{/if}
  </div>

  <div class="field">
    <label for="wi-details">Details</label>
    <textarea
      id="wi-details"
      bind:value={details}
      rows="4"
      placeholder="Additional markdown details"
    ></textarea>
  </div>

  <div class="form-actions">
    <button type="button" class="cancel-btn" onclick={onCancel}>Cancel</button>
    <button type="submit" class="submit-btn" disabled={saving}>
      {saving ? "Saving…" : isEdit ? "Save Changes" : "Create"}
    </button>
  </div>
</form>

<style>
  .work-item-form {
    padding: 1.5rem;
    overflow-y: auto;
    max-width: 800px;
  }
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
  .header-actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }
  h2 {
    margin: 0;
    font-size: 1.3rem;
  }
  .field {
    margin-bottom: 1rem;
  }
  label {
    display: block;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
  }
  .required {
    color: var(--error-color, #c33);
  }
  input[type="text"],
  input[type="number"],
  textarea,
  select {
    width: 100%;
    padding: 0.45rem 0.6rem;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    font-size: 0.9rem;
    font-family: inherit;
    background: var(--input-bg, #fff);
    color: inherit;
    box-sizing: border-box;
  }
  textarea {
    resize: vertical;
  }
  .invalid {
    border-color: var(--error-color, #c33);
  }
  .field-error {
    display: block;
    color: var(--error-color, #c33);
    font-size: 0.8rem;
    margin-top: 0.2rem;
  }
  .form-error {
    color: var(--error-color, #c33);
    background: #fff5f5;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    font-size: 0.9rem;
  }
  .field-row {
    display: flex;
    gap: 1rem;
  }
  .field-row .field {
    flex: 1;
  }
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color, #ddd);
  }
  .cancel-btn {
    padding: 0.4rem 1rem;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
    background: none;
    cursor: pointer;
    font-size: 0.9rem;
    color: inherit;
  }
  .submit-btn {
    padding: 0.4rem 1.2rem;
    border: none;
    border-radius: 4px;
    background: var(--accent-color, #396cd8);
    color: #fff;
    cursor: pointer;
    font-size: 0.9rem;
  }
  .submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  @media (prefers-color-scheme: dark) {
    input[type="text"],
    input[type="number"],
    textarea,
    select {
      background: #2a2a2a;
      border-color: #555;
    }
    .form-error {
      background: #3a2020;
    }
  }
</style>
