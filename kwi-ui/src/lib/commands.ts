import { invoke } from "@tauri-apps/api/core";
import type { Project, Area, WorkItem, RelatedItem } from "./types";

export async function checkConnection(): Promise<void> {
  return invoke("check_connection");
}

export async function listProjects(): Promise<Project[]> {
  return invoke("list_projects");
}

export async function listAreas(projectId: number): Promise<Area[]> {
  return invoke("list_areas", { projectId });
}

export async function listWorkItems(
  projectId?: number,
  areaId?: number,
  wiType?: string,
  wiStatus?: string,
  showArchived?: boolean,
): Promise<WorkItem[]> {
  return invoke("list_work_items", {
    projectId,
    areaId,
    wiType,
    wiStatus,
    showArchived,
  });
}

export async function getWorkItem(id: number): Promise<WorkItem> {
  return invoke("get_work_item", { id });
}

export async function getValidTypes(): Promise<string[]> {
  return invoke("get_valid_types");
}

export async function getValidStatuses(): Promise<string[]> {
  return invoke("get_valid_statuses");
}

export async function getValidTshirtSizes(): Promise<string[]> {
  return invoke("get_valid_tshirt_sizes");
}

export async function createWorkItem(params: {
  projectId: number;
  title: string;
  content: string;
  wiType: string;
  wiStatus?: string;
  wiTshirt?: string;
  areaId?: number;
  sprint?: string;
  details?: string;
  parentId?: number;
}): Promise<WorkItem> {
  return invoke("create_work_item", params);
}

export async function updateWorkItem(params: {
  id: number;
  title?: string;
  content?: string;
  wiType?: string;
  wiStatus?: string;
  wiTshirt?: string;
  areaId?: number;
  sprint?: string;
  details?: string;
  parentId?: number;
}): Promise<WorkItem> {
  return invoke("update_work_item", params);
}

export async function archiveWorkItem(id: number): Promise<WorkItem> {
  return invoke("archive_work_item", { id });
}

export async function searchWorkItems(
  query: string,
  projectId?: number,
): Promise<WorkItem[]> {
  return invoke("search_work_items", { query, projectId });
}

export async function listRelated(workItemId: number): Promise<RelatedItem[]> {
  return invoke("list_related", { workItemId });
}

export async function relateWorkItems(
  leftId: number,
  rightId: number,
  relationship: string,
): Promise<void> {
  return invoke("relate_work_items", { leftId, rightId, relationship });
}

export async function unrelateWorkItems(
  leftId: number,
  rightId: number,
): Promise<void> {
  return invoke("unrelate_work_items", { leftId, rightId });
}

export async function createProject(params: {
  project: string;
  cnPath: string;
  ghRepo?: string;
  description?: string;
}): Promise<Project> {
  return invoke("create_project", params);
}

export async function createArea(params: {
  projectId: number;
  name: string;
  description?: string;
}): Promise<Area> {
  return invoke("create_area", params);
}
