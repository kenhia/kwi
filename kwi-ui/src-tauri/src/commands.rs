use deadpool_postgres::Pool;
use tauri::State;

use crate::models::{Area, Project, RelatedItem, WorkItem};
use crate::queries;

pub struct AppState {
    pub pool: Option<Pool>,
    pub connection_error: Option<String>,
}

fn pool_or_err(state: &AppState) -> Result<&Pool, String> {
    state.pool.as_ref().ok_or_else(|| {
        state
            .connection_error
            .clone()
            .unwrap_or_else(|| "Database not configured".to_string())
    })
}

#[tauri::command]
pub async fn check_connection(state: State<'_, AppState>) -> Result<(), String> {
    pool_or_err(&state)?;
    Ok(())
}

#[tauri::command]
pub async fn list_projects(state: State<'_, AppState>) -> Result<Vec<Project>, String> {
    queries::list_projects(pool_or_err(&state)?).await
}

#[tauri::command]
pub async fn list_areas(state: State<'_, AppState>, project_id: i32) -> Result<Vec<Area>, String> {
    queries::list_areas(pool_or_err(&state)?, project_id).await
}

#[tauri::command]
#[allow(clippy::too_many_arguments)]
pub async fn list_work_items(
    state: State<'_, AppState>,
    project_id: Option<i32>,
    area_id: Option<i32>,
    wi_type: Option<String>,
    wi_status: Option<String>,
    show_archived: Option<bool>,
) -> Result<Vec<WorkItem>, String> {
    queries::list_work_items(
        pool_or_err(&state)?,
        project_id,
        area_id,
        wi_type,
        wi_status,
        show_archived,
    )
    .await
}

#[tauri::command]
pub async fn get_work_item(state: State<'_, AppState>, id: i32) -> Result<WorkItem, String> {
    queries::get_work_item(pool_or_err(&state)?, id).await
}

#[tauri::command]
pub async fn get_valid_types(state: State<'_, AppState>) -> Result<Vec<String>, String> {
    queries::get_valid_types(pool_or_err(&state)?).await
}

#[tauri::command]
pub async fn get_valid_statuses(state: State<'_, AppState>) -> Result<Vec<String>, String> {
    queries::get_valid_statuses(pool_or_err(&state)?).await
}

#[tauri::command]
pub async fn get_valid_tshirt_sizes() -> Result<Vec<String>, String> {
    Ok(queries::get_valid_tshirt_sizes())
}

#[tauri::command]
#[allow(clippy::too_many_arguments)]
pub async fn create_work_item(
    state: State<'_, AppState>,
    project_id: i32,
    title: String,
    content: String,
    wi_type: String,
    wi_status: Option<String>,
    wi_tshirt: Option<String>,
    area_id: Option<i32>,
    sprint: Option<String>,
    details: Option<String>,
    parent_id: Option<i32>,
) -> Result<WorkItem, String> {
    queries::create_work_item(
        pool_or_err(&state)?,
        project_id,
        title,
        content,
        wi_type,
        wi_status,
        wi_tshirt,
        area_id,
        sprint,
        details,
        parent_id,
    )
    .await
}

#[tauri::command]
#[allow(clippy::too_many_arguments)]
pub async fn update_work_item(
    state: State<'_, AppState>,
    id: i32,
    title: Option<String>,
    content: Option<String>,
    wi_type: Option<String>,
    wi_status: Option<String>,
    wi_tshirt: Option<String>,
    area_id: Option<i32>,
    sprint: Option<String>,
    details: Option<String>,
    parent_id: Option<i32>,
) -> Result<WorkItem, String> {
    queries::update_work_item(
        pool_or_err(&state)?,
        id,
        title,
        content,
        wi_type,
        wi_status,
        wi_tshirt,
        area_id,
        sprint,
        details,
        parent_id,
    )
    .await
}

#[tauri::command]
pub async fn archive_work_item(state: State<'_, AppState>, id: i32) -> Result<WorkItem, String> {
    queries::archive_work_item(pool_or_err(&state)?, id).await
}

#[tauri::command]
pub async fn unarchive_work_item(state: State<'_, AppState>, id: i32) -> Result<WorkItem, String> {
    queries::unarchive_work_item(pool_or_err(&state)?, id).await
}

#[tauri::command]
pub async fn search_work_items(
    state: State<'_, AppState>,
    query: String,
    project_id: Option<i32>,
) -> Result<Vec<WorkItem>, String> {
    queries::search_work_items(pool_or_err(&state)?, query, project_id).await
}

#[tauri::command]
pub async fn list_related(
    state: State<'_, AppState>,
    work_item_id: i32,
) -> Result<Vec<RelatedItem>, String> {
    queries::list_related(pool_or_err(&state)?, work_item_id).await
}

#[tauri::command]
pub async fn relate_work_items(
    state: State<'_, AppState>,
    left_id: i32,
    right_id: i32,
    relationship: String,
) -> Result<(), String> {
    queries::relate_work_items(pool_or_err(&state)?, left_id, right_id, relationship).await
}

#[tauri::command]
pub async fn unrelate_work_items(
    state: State<'_, AppState>,
    left_id: i32,
    right_id: i32,
) -> Result<(), String> {
    queries::unrelate_work_items(pool_or_err(&state)?, left_id, right_id).await
}

#[tauri::command]
pub async fn create_project(
    state: State<'_, AppState>,
    project: String,
    cn_path: String,
    gh_repo: Option<String>,
    description: Option<String>,
) -> Result<Project, String> {
    queries::create_project(pool_or_err(&state)?, project, cn_path, gh_repo, description).await
}

#[tauri::command]
pub async fn create_area(
    state: State<'_, AppState>,
    project_id: i32,
    name: String,
    description: Option<String>,
) -> Result<Area, String> {
    queries::create_area(pool_or_err(&state)?, project_id, name, description).await
}
