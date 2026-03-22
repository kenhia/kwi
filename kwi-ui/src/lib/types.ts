export interface Project {
  id: number;
  project: string;
  cn_path: string;
  gh_repo: string | null;
  description: string | null;
  created: string;
  updated: string;
}

export interface Area {
  id: number;
  project_id: number;
  name: string;
  description: string | null;
}

export interface WorkItem {
  id: number;
  project_id: number;
  project_name: string | null;
  area_id: number | null;
  area_name: string | null;
  wi_type: string;
  wi_status: string;
  wi_tshirt: string;
  sprint: string | null;
  title: string;
  content: string;
  details: string | null;
  parent_id: number | null;
  created: string;
  updated: string;
}

export interface RelatedItem {
  id: number;
  relationship: string;
  title: string;
  direction: string;
}

export interface RefData {
  types: string[];
  statuses: string[];
  tshirt_sizes: string[];
}
