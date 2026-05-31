import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, within, fireEvent } from "@testing-library/svelte";
import WorkItemList from "./WorkItemList.svelte";
import { filterState } from "$lib/stores.svelte";

const ITEMS = [
  {
    id: 1,
    project_id: 1,
    project_name: "proj",
    area_id: 1,
    area_name: "Frontend",
    wi_type: "bug",
    wi_status: "open",
    wi_tshirt: "S",
    archived: false,
    sprint: null,
    title: "Fix bug",
    content: "desc",
    details: null,
    parent_id: null,
    created: "2026-01-01",
    updated: "2026-01-01",
  },
  {
    id: 2,
    project_id: 1,
    project_name: "proj",
    area_id: 2,
    area_name: "Backend",
    wi_type: "feature",
    wi_status: "active",
    wi_tshirt: "M",
    archived: false,
    sprint: "sprint-1",
    title: "Add feature",
    content: "desc",
    details: null,
    parent_id: null,
    created: "2026-01-01",
    updated: "2026-01-01",
  },
  {
    id: 3,
    project_id: 1,
    project_name: "proj",
    area_id: 1,
    area_name: "Frontend",
    wi_type: "task",
    wi_status: "open",
    wi_tshirt: "L",
    archived: true,
    sprint: null,
    title: "Old task",
    content: "desc",
    details: null,
    parent_id: null,
    created: "2026-01-01",
    updated: "2026-01-01",
  },
  {
    id: 4,
    project_id: 1,
    project_name: "proj",
    area_id: 2,
    area_name: "Backend",
    wi_type: "bug",
    wi_status: "closed",
    wi_tshirt: "S",
    archived: false,
    sprint: "sprint-2",
    title: "Done thing",
    content: "desc",
    details: null,
    parent_id: null,
    created: "2026-01-01",
    updated: "2026-01-01",
  },
];

const mockListWorkItems = vi.fn().mockResolvedValue(ITEMS);

vi.mock("$lib/commands", () => ({
  listAreas: vi.fn().mockResolvedValue([
    { id: 1, project_id: 1, name: "Frontend", description: null },
    { id: 2, project_id: 1, name: "Backend", description: null },
  ]),
  getValidTypes: vi.fn().mockResolvedValue(["bug", "feature", "task"]),
  getValidStatuses: vi
    .fn()
    .mockResolvedValue(["open", "active", "resolved", "closed", "draft"]),
  getValidTshirtSizes: vi.fn().mockResolvedValue(["S", "M", "L"]),
  listWorkItems: (...args: unknown[]) => mockListWorkItems(...args),
}));

function renderList() {
  return render(WorkItemList, {
    props: {
      projectId: 1,
      onSelectItem: vi.fn(),
      onCreateItem: vi.fn(),
    },
  });
}

function resetFilterState() {
  // Reset the shared (module-level) filter store between tests so selections
  // do not bleed across cases.
  filterState.projectId = null;
  filterState.sprintsProjectId = null;
  filterState.showArchived = false;
  filterState.types = new Set();
  filterState.statuses = new Set();
  filterState.sizes = new Set();
  filterState.areas = new Set();
  filterState.sprints = new Set();
}

describe("WorkItemList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockListWorkItems.mockResolvedValue(ITEMS);
    resetFilterState();
  });

  it("renders MultiSelectFilter components for filters", async () => {
    renderList();
    await vi.waitFor(() => {
      expect(screen.getByText(/types/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/areas/i)).toBeInTheDocument();
    expect(screen.getByText(/types/i)).toBeInTheDocument();
    expect(screen.getByText(/statuses/i)).toBeInTheDocument();
    expect(screen.getByText(/sizes/i)).toBeInTheDocument();
    expect(screen.getByText(/sprints/i)).toBeInTheDocument();
  });

  it("hides archived items by default (via the archived flag)", async () => {
    renderList();
    await vi.waitFor(() => {
      expect(screen.getByText("Fix bug")).toBeInTheDocument();
    });
    // Item 3 is archived -> hidden even though its status ("open") is selected.
    expect(screen.queryByText("Old task")).not.toBeInTheDocument();
    expect(screen.getByText("Fix bug")).toBeInTheDocument();
    expect(screen.getByText("Add feature")).toBeInTheDocument();
  });

  it("default status filter excludes closed on first load", async () => {
    renderList();
    await vi.waitFor(() => {
      expect(screen.getByText("Fix bug")).toBeInTheDocument();
    });
    // Item 4 has status "closed" -> hidden by default.
    expect(screen.queryByText("Done thing")).not.toBeInTheDocument();
    expect(filterState.statuses.has("closed")).toBe(false);
    expect(filterState.statuses.has("open")).toBe(true);
  });

  it("does not render select elements or archived checkbox", async () => {
    renderList();
    await vi.waitFor(() => {
      expect(screen.getByText("Fix bug")).toBeInTheDocument();
    });
    const section = screen.getByRole("region", { name: /work items/i });
    expect(within(section).queryAllByRole("combobox")).toHaveLength(0);
    expect(
      screen.queryByLabelText(/include archived/i),
    ).not.toBeInTheDocument();
  });

  it("renders no off-default cue when filters are at their defaults", async () => {
    renderList();
    await vi.waitFor(() => {
      expect(screen.getByText("Fix bug")).toBeInTheDocument();
    });
    expect(screen.queryByLabelText("filter modified")).not.toBeInTheDocument();
  });

  it("renders a visual cue when a filter is not at its default", async () => {
    renderList();
    await vi.waitFor(() => {
      expect(screen.getByText("Fix bug")).toBeInTheDocument();
    });
    // Open the statuses dropdown and clear it -> off-default.
    await fireEvent.click(screen.getByText(/statuses/i));
    await fireEvent.click(screen.getByText("Clear All"));
    await vi.waitFor(() => {
      expect(
        screen.getAllByLabelText("filter modified").length,
      ).toBeGreaterThan(0);
    });
  });

  it("persists filter selections across a remount (session stickiness)", async () => {
    const first = renderList();
    await vi.waitFor(() => {
      expect(screen.getByText("Add feature")).toBeInTheDocument();
    });
    // Deselect the "active" status -> hides item 2.
    filterState.statuses = new Set(
      [...filterState.statuses].filter((s) => s !== "active"),
    );
    first.unmount();

    renderList();
    await vi.waitFor(() => {
      expect(screen.getByText("Fix bug")).toBeInTheDocument();
    });
    // Selection persisted: item 2 remains hidden after remount.
    expect(screen.queryByText("Add feature")).not.toBeInTheDocument();
  });

  it("sprint filter lists distinct sprints plus Unassigned, all selected by default", async () => {
    renderList();
    await vi.waitFor(() => {
      expect(screen.getByText("Fix bug")).toBeInTheDocument();
    });
    await fireEvent.click(screen.getByText(/sprints/i));
    const dropdown = screen.getByRole("listbox", { name: "sprints" });
    expect(within(dropdown).getByText("sprint-1")).toBeInTheDocument();
    expect(within(dropdown).getByText("sprint-2")).toBeInTheDocument();
    expect(within(dropdown).getByText("Unassigned")).toBeInTheDocument();
    // All sprint checkboxes selected by default.
    const boxes = within(dropdown).getAllByRole("checkbox");
    expect(boxes.every((b) => (b as HTMLInputElement).checked)).toBe(true);
  });

  it("deselecting a sprint hides its items", async () => {
    renderList();
    await vi.waitFor(() => {
      expect(screen.getByText("Fix bug")).toBeInTheDocument();
    });
    await fireEvent.click(screen.getByText(/sprints/i));
    const dropdown = screen.getByRole("listbox", { name: "sprints" });
    // Deselect "Unassigned" -> hides item 1 (sprint == null).
    const unassigned = within(dropdown)
      .getByText("Unassigned")
      .closest("label")!
      .querySelector("input")!;
    await fireEvent.click(unassigned);
    await vi.waitFor(() => {
      expect(screen.queryByText("Fix bug")).not.toBeInTheDocument();
    });
  });

  it("refresh button is rendered", async () => {
    renderList();
    await vi.waitFor(() => {
      expect(screen.getByText("Fix bug")).toBeInTheDocument();
    });
    expect(screen.getByLabelText("Refresh work items")).toBeInTheDocument();
  });

  it("clicking refresh triggers data reload", async () => {
    renderList();
    await vi.waitFor(() => {
      expect(screen.getByText("Fix bug")).toBeInTheDocument();
    });

    const initialCalls = mockListWorkItems.mock.calls.length;
    const refreshBtn = screen.getByLabelText("Refresh work items");
    refreshBtn.click();

    await vi.waitFor(() => {
      expect(mockListWorkItems.mock.calls.length).toBeGreaterThan(initialCalls);
    });
  });
});
