import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, within } from "@testing-library/svelte";
import WorkItemList from "./WorkItemList.svelte";

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
    sprint: null,
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
    wi_status: "archived",
    wi_tshirt: "L",
    sprint: null,
    title: "Old task",
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
  getValidStatuses: vi.fn().mockResolvedValue(["active", "archived", "open"]),
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

describe("WorkItemList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockListWorkItems.mockResolvedValue(ITEMS);
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
  });

  it("status defaults exclude archived", async () => {
    renderList();
    await vi.waitFor(() => {
      expect(screen.getByText("Fix bug")).toBeInTheDocument();
    });
    expect(screen.queryByText("Old task")).not.toBeInTheDocument();
    expect(screen.getByText("Fix bug")).toBeInTheDocument();
    expect(screen.getByText("Add feature")).toBeInTheDocument();
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
