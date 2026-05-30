import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/svelte";
import WorkItemForm from "./WorkItemForm.svelte";

vi.mock("$lib/commands", () => ({
  listAreas: vi
    .fn()
    .mockResolvedValue([
      { id: 1, project_id: 1, name: "Frontend", description: null },
    ]),
  getValidTypes: vi.fn().mockResolvedValue(["bug", "feature", "issue", "task"]),
  getValidStatuses: vi.fn().mockResolvedValue(["active", "archived", "open"]),
  getValidTshirtSizes: vi.fn().mockResolvedValue(["L", "M", "S", "XL", "XS"]),
  createWorkItem: vi.fn(),
  updateWorkItem: vi.fn(),
}));

const baseProps = {
  projectId: 1,
  projectName: "Test Project",
  onSave: vi.fn(),
  onCancel: vi.fn(),
};

const editItem = {
  id: 42,
  project_id: 1,
  project_name: "Test Project",
  area_id: 1,
  area_name: "Frontend",
  wi_type: "bug",
  wi_status: "active",
  wi_tshirt: "L",
  sprint: "2026-W01",
  title: "Existing Bug",
  content: "Bug description",
  details: "Some details",
  parent_id: null,
  created: "2026-01-01",
  updated: "2026-01-01",
};

describe("WorkItemForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("field ordering (US2)", () => {
    it("Title appears before Type, Type before Content, Content before Details", async () => {
      render(WorkItemForm, { props: baseProps });
      await vi.waitFor(() => {
        expect(screen.getByLabelText(/^title/i)).toBeInTheDocument();
      });

      const form = screen.getByRole("form");
      const html = form.innerHTML;

      const titlePos = html.indexOf('id="wi-title"');
      const typePos = html.indexOf('id="wi-type"');
      const contentPos = html.indexOf('id="wi-content"');
      const detailsPos = html.indexOf('id="wi-details"');

      expect(titlePos).toBeLessThan(typePos);
      expect(typePos).toBeLessThan(contentPos);
      expect(contentPos).toBeLessThan(detailsPos);
    });
  });

  describe("create form defaults (US3)", () => {
    it("defaults Type to 'issue', Status to 'open', Size to 'S'", async () => {
      render(WorkItemForm, { props: baseProps });
      await vi.waitFor(() => {
        const typeSelect = screen.getByLabelText(/^type/i) as HTMLSelectElement;
        expect(typeSelect.value).toBe("issue");
      });

      const statusSelect = screen.getByLabelText(
        /^status/i,
      ) as HTMLSelectElement;
      expect(statusSelect.value).toBe("open");

      const sizeSelect = screen.getByLabelText(/^size/i) as HTMLSelectElement;
      expect(sizeSelect.value).toBe("S");
    });

    it("edit mode uses existing item values, not defaults", async () => {
      render(WorkItemForm, { props: { ...baseProps, editItem } });
      await vi.waitFor(() => {
        const typeSelect = screen.getByLabelText(/^type/i) as HTMLSelectElement;
        expect(typeSelect.value).toBe("bug");
      });

      const statusSelect = screen.getByLabelText(
        /^status/i,
      ) as HTMLSelectElement;
      expect(statusSelect.value).toBe("active");

      const sizeSelect = screen.getByLabelText(/^size/i) as HTMLSelectElement;
      expect(sizeSelect.value).toBe("L");
    });
  });

  describe("top save button (US4)", () => {
    it("top save button appears only in edit mode", async () => {
      render(WorkItemForm, { props: { ...baseProps, editItem } });
      await vi.waitFor(() => {
        expect(screen.getByLabelText(/^type/i)).toBeInTheDocument();
      });

      // Header area should have a save button
      const header = screen.getByRole("banner");
      const saveBtn = header.querySelector(".submit-btn");
      expect(saveBtn).toBeInTheDocument();
      expect(saveBtn?.textContent).toContain("Save Changes");
    });

    it("top save button does not appear in create mode", async () => {
      render(WorkItemForm, { props: baseProps });
      await vi.waitFor(() => {
        expect(screen.getByLabelText(/^type/i)).toBeInTheDocument();
      });

      const header = screen.getByRole("banner");
      const saveBtn = header.querySelector(".submit-btn");
      expect(saveBtn).toBeNull();
    });
  });
});
