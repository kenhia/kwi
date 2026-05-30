import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/svelte";
import MultiSelectFilter from "./MultiSelectFilter.svelte";

const OPTIONS = ["bug", "feature", "task"];

function renderFilter(overrides: Record<string, unknown> = {}) {
  const onchange = vi.fn();
  const result = render(MultiSelectFilter, {
    props: {
      label: "types",
      options: OPTIONS,
      selected: new Set(OPTIONS),
      onchange,
      ...overrides,
    },
  });
  return { onchange, ...result };
}

describe("MultiSelectFilter", () => {
  it("renders button with label showing all selected", () => {
    renderFilter();
    expect(
      screen.getByRole("button", { name: /all types/i }),
    ).toBeInTheDocument();
  });

  it("shows count when partially selected", () => {
    renderFilter({ selected: new Set(["bug"]) });
    expect(
      screen.getByRole("button", { name: /1 of 3 types/i }),
    ).toBeInTheDocument();
  });

  it("shows 'No types' when none selected", () => {
    renderFilter({ selected: new Set() });
    expect(
      screen.getByRole("button", { name: /no types/i }),
    ).toBeInTheDocument();
  });

  it("opens dropdown on click", async () => {
    renderFilter();
    const trigger = screen.getByRole("button", { name: /all types/i });
    await fireEvent.click(trigger);
    expect(screen.getByRole("listbox")).toBeInTheDocument();
  });

  it("toggles individual checkbox", async () => {
    const { onchange } = renderFilter();
    await fireEvent.click(screen.getByRole("button", { name: /all types/i }));

    const bugCheckbox = screen.getByLabelText("bug");
    await fireEvent.click(bugCheckbox);

    expect(onchange).toHaveBeenCalledWith(new Set(["feature", "task"]));
  });

  it("Select All checks all options", async () => {
    const { onchange } = renderFilter({ selected: new Set(["bug"]) });
    await fireEvent.click(screen.getByRole("button", { name: /1 of 3/i }));

    await fireEvent.click(screen.getByRole("button", { name: /select all/i }));
    expect(onchange).toHaveBeenCalledWith(new Set(OPTIONS));
  });

  it("Clear All unchecks all options", async () => {
    const { onchange } = renderFilter();
    await fireEvent.click(screen.getByRole("button", { name: /all types/i }));

    await fireEvent.click(screen.getByRole("button", { name: /clear all/i }));
    expect(onchange).toHaveBeenCalledWith(new Set());
  });

  it("closes on Escape key", async () => {
    renderFilter();
    await fireEvent.click(screen.getByRole("button", { name: /all types/i }));
    expect(screen.getByRole("listbox")).toBeInTheDocument();

    await fireEvent.keyDown(
      screen.getByRole("listbox").closest(".multi-select")!,
      {
        key: "Escape",
      },
    );
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("closes on outside click", async () => {
    renderFilter();
    await fireEvent.click(screen.getByRole("button", { name: /all types/i }));
    expect(screen.getByRole("listbox")).toBeInTheDocument();

    await fireEvent.click(document.body);
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });
});
