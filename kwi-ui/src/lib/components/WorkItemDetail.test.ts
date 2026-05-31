import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/svelte";
import WorkItemDetail from "./WorkItemDetail.svelte";
import type { WorkItem } from "$lib/types";

const unarchiveWorkItem = vi.fn().mockResolvedValue(undefined);

vi.mock("$lib/commands", () => ({
  listRelated: vi.fn().mockResolvedValue([]),
  searchWorkItems: vi.fn().mockResolvedValue([]),
  relateWorkItems: vi.fn().mockResolvedValue(undefined),
  unrelateWorkItems: vi.fn().mockResolvedValue(undefined),
  unarchiveWorkItem: (id: number) => unarchiveWorkItem(id),
}));

function makeItem(overrides: Partial<WorkItem> = {}): WorkItem {
  return {
    id: 1,
    project_id: 1,
    project_name: "proj",
    area_id: null,
    area_name: null,
    wi_type: "bug",
    wi_status: "open",
    wi_tshirt: "S",
    archived: false,
    sprint: null,
    title: "A thing",
    content: "body",
    details: null,
    parent_id: null,
    created: "2026-01-01T00:00:00Z",
    updated: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}

function renderDetail(item: WorkItem, onUnarchive = vi.fn()) {
  return render(WorkItemDetail, {
    props: {
      item,
      onBack: vi.fn(),
      onEdit: vi.fn(),
      onArchive: vi.fn(),
      onUnarchive,
    },
  });
}

describe("WorkItemDetail", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders an Un-archive action for an archived item", async () => {
    renderDetail(makeItem({ archived: true }));
    expect(
      screen.getByRole("button", { name: /un-archive/i }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /^archive$/i }),
    ).not.toBeInTheDocument();
  });

  it("invokes the un-archive handler when clicked", async () => {
    const onUnarchive = vi.fn();
    const item = makeItem({ archived: true });
    renderDetail(item, onUnarchive);
    await fireEvent.click(screen.getByRole("button", { name: /un-archive/i }));
    expect(onUnarchive).toHaveBeenCalledWith(item);
  });

  it("renders an Archive action (not Un-archive) for an active item", async () => {
    renderDetail(makeItem({ archived: false }));
    expect(
      screen.getByRole("button", { name: /^archive$/i }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /un-archive/i }),
    ).not.toBeInTheDocument();
  });
});
