import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/svelte";
import ProjectDetails from "./ProjectDetails.svelte";

const baseProject = {
  id: 1,
  project: "kwi",
  cn_path: "/kwi",
  gh_repo: null as string | null,
  description: null as string | null,
  created: "2026-01-01",
  updated: "2026-01-01",
};

describe("ProjectDetails", () => {
  it("renders collapsed by default", () => {
    render(ProjectDetails, { props: { project: baseProject } });
    const details = screen.getByText("Project Details").closest("details");
    expect(details).not.toHaveAttribute("open");
  });

  it("shows short name and CN path", () => {
    render(ProjectDetails, { props: { project: baseProject } });
    expect(screen.getByText("kwi")).toBeInTheDocument();
    expect(screen.getByText("/kwi")).toBeInTheDocument();
  });

  it("shows GitHub repo when present", () => {
    render(ProjectDetails, {
      props: { project: { ...baseProject, gh_repo: "org/repo" } },
    });
    expect(screen.getByText("GitHub Repo")).toBeInTheDocument();
    expect(screen.getByText("org/repo")).toBeInTheDocument();
  });

  it("omits GitHub repo when null", () => {
    render(ProjectDetails, { props: { project: baseProject } });
    expect(screen.queryByText("GitHub Repo")).not.toBeInTheDocument();
  });

  it("shows description when present", () => {
    render(ProjectDetails, {
      props: { project: { ...baseProject, description: "A test project" } },
    });
    expect(screen.getByText("Description")).toBeInTheDocument();
    expect(screen.getByText("A test project")).toBeInTheDocument();
  });

  it("omits description when null", () => {
    render(ProjectDetails, { props: { project: baseProject } });
    expect(screen.queryByText("Description")).not.toBeInTheDocument();
  });
});
