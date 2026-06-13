use deadpool_postgres::Pool;

use crate::models::{Area, Project, RelatedItem, WorkItem};

pub async fn list_projects(pool: &Pool) -> Result<Vec<Project>, String> {
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;
    let rows = client
        .query(
            "SELECT id, project, cn_path, gh_repo, description, \
             created::text, updated::text FROM project ORDER BY project",
            &[],
        )
        .await
        .map_err(|e| format!("Query error: {e}"))?;

    Ok(rows
        .iter()
        .map(|r| Project {
            id: r.get(0),
            project: r.get(1),
            cn_path: r.get(2),
            gh_repo: r.get(3),
            description: r.get(4),
            created: r.get(5),
            updated: r.get(6),
        })
        .collect())
}

pub async fn list_areas(pool: &Pool, project_id: i32) -> Result<Vec<Area>, String> {
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;
    let rows = client
        .query(
            "SELECT id, project_id, name, description \
             FROM area WHERE project_id = $1 ORDER BY name",
            &[&project_id],
        )
        .await
        .map_err(|e| format!("Query error: {e}"))?;

    Ok(rows
        .iter()
        .map(|r| Area {
            id: r.get(0),
            project_id: r.get(1),
            name: r.get(2),
            description: r.get(3),
        })
        .collect())
}

#[allow(clippy::too_many_arguments)]
pub async fn list_work_items(
    pool: &Pool,
    project_id: Option<i32>,
    area_id: Option<i32>,
    wi_type: Option<String>,
    wi_status: Option<String>,
    show_archived: Option<bool>,
) -> Result<Vec<WorkItem>, String> {
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;

    let mut query = String::from(
        "SELECT w.id, w.project_id, p.project, w.area_id, a.name, \
         t.name, s.name, w.wi_tshirt, w.sprint, w.title, w.content, \
         w.details, w.parent_id, w.created::text, w.updated::text, \
         w.archived \
         FROM workitem w \
         JOIN project p ON w.project_id = p.id \
         JOIN workitem_type t ON w.wi_type_id = t.id \
         JOIN workitem_status s ON w.wi_status_id = s.id \
         LEFT JOIN area a ON w.area_id = a.id \
         WHERE 1=1",
    );
    let mut param_idx = 0u32;
    let mut params: Vec<Box<dyn tokio_postgres::types::ToSql + Sync + Send>> = Vec::new();

    if let Some(pid) = project_id {
        param_idx += 1;
        query.push_str(&format!(" AND w.project_id = ${param_idx}"));
        params.push(Box::new(pid));
    }

    if let Some(aid) = area_id {
        param_idx += 1;
        query.push_str(&format!(" AND w.area_id = ${param_idx}"));
        params.push(Box::new(aid));
    }

    if let Some(ref wt) = wi_type {
        param_idx += 1;
        query.push_str(&format!(" AND t.name = ${param_idx}"));
        params.push(Box::new(wt.clone()));
    }

    if let Some(ref ws) = wi_status {
        param_idx += 1;
        query.push_str(&format!(" AND s.name = ${param_idx}"));
        params.push(Box::new(ws.clone()));
    }

    if !show_archived.unwrap_or(false) {
        query.push_str(" AND w.archived = false");
    }

    query.push_str(" ORDER BY w.id ASC");

    let param_refs: Vec<&(dyn tokio_postgres::types::ToSql + Sync)> = params
        .iter()
        .map(|p| p.as_ref() as &(dyn tokio_postgres::types::ToSql + Sync))
        .collect();

    let rows = client
        .query(&query, &param_refs)
        .await
        .map_err(|e| format!("Query error: {e}"))?;

    Ok(rows
        .iter()
        .map(|r| WorkItem {
            id: r.get(0),
            project_id: r.get(1),
            project_name: r.get(2),
            area_id: r.get(3),
            area_name: r.get(4),
            wi_type: r.get(5),
            wi_status: r.get(6),
            wi_tshirt: r.get(7),
            sprint: r.get(8),
            title: r.get(9),
            content: r.get(10),
            details: r.get(11),
            parent_id: r.get(12),
            created: r.get(13),
            updated: r.get(14),
            archived: r.get(15),
        })
        .collect())
}

pub async fn get_work_item(pool: &Pool, id: i32) -> Result<WorkItem, String> {
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;
    let row = client
        .query_opt(
            "SELECT w.id, w.project_id, p.project, w.area_id, a.name, \
             t.name, s.name, w.wi_tshirt, w.sprint, w.title, w.content, \
             w.details, w.parent_id, w.created::text, w.updated::text, \
             w.archived \
             FROM workitem w \
             JOIN project p ON w.project_id = p.id \
             JOIN workitem_type t ON w.wi_type_id = t.id \
             JOIN workitem_status s ON w.wi_status_id = s.id \
             LEFT JOIN area a ON w.area_id = a.id \
             WHERE w.id = $1",
            &[&id],
        )
        .await
        .map_err(|e| format!("Query error: {e}"))?
        .ok_or_else(|| format!("Work item {id} not found"))?;

    Ok(WorkItem {
        id: row.get(0),
        project_id: row.get(1),
        project_name: row.get(2),
        area_id: row.get(3),
        area_name: row.get(4),
        wi_type: row.get(5),
        wi_status: row.get(6),
        wi_tshirt: row.get(7),
        sprint: row.get(8),
        title: row.get(9),
        content: row.get(10),
        details: row.get(11),
        parent_id: row.get(12),
        created: row.get(13),
        updated: row.get(14),
        archived: row.get(15),
    })
}

pub async fn get_valid_types(pool: &Pool) -> Result<Vec<String>, String> {
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;
    let rows = client
        .query("SELECT name FROM workitem_type ORDER BY name", &[])
        .await
        .map_err(|e| format!("Query error: {e}"))?;
    Ok(rows.iter().map(|r| r.get(0)).collect())
}

pub async fn get_valid_statuses(pool: &Pool) -> Result<Vec<String>, String> {
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;
    let rows = client
        .query("SELECT name FROM workitem_status ORDER BY name", &[])
        .await
        .map_err(|e| format!("Query error: {e}"))?;
    Ok(rows.iter().map(|r| r.get(0)).collect())
}

pub fn get_valid_tshirt_sizes() -> Vec<String> {
    vec![
        "XS".to_string(),
        "S".to_string(),
        "M".to_string(),
        "L".to_string(),
        "XL".to_string(),
        "Huge".to_string(),
        "Unknown".to_string(),
    ]
}

#[allow(clippy::too_many_arguments)]
pub async fn create_work_item(
    pool: &Pool,
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
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;

    let status = wi_status.unwrap_or_else(|| "open".to_string());
    let tshirt = wi_tshirt.unwrap_or_else(|| "M".to_string());

    // Resolve type_id
    let type_row = client
        .query_opt("SELECT id FROM workitem_type WHERE name = $1", &[&wi_type])
        .await
        .map_err(|e| format!("Query error: {e}"))?
        .ok_or_else(|| format!("Invalid type '{wi_type}'"))?;
    let type_id: i32 = type_row.get(0);

    // Resolve status_id
    let status_row = client
        .query_opt("SELECT id FROM workitem_status WHERE name = $1", &[&status])
        .await
        .map_err(|e| format!("Query error: {e}"))?
        .ok_or_else(|| format!("Invalid status '{status}'"))?;
    let status_id: i32 = status_row.get(0);

    let row = client
        .query_one(
            "INSERT INTO workitem \
             (project_id, area_id, wi_type_id, wi_status_id, wi_tshirt, sprint, \
              title, content, details, parent_id) \
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) \
             RETURNING id, created::text, updated::text",
            &[
                &project_id,
                &area_id,
                &type_id,
                &status_id,
                &tshirt,
                &sprint,
                &title,
                &content,
                &details,
                &parent_id,
            ],
        )
        .await
        .map_err(|e| format!("Insert error: {e}"))?;

    // Fetch the full work item to return with resolved names
    get_work_item(pool, row.get(0)).await
}

#[allow(clippy::too_many_arguments)]
pub async fn update_work_item(
    pool: &Pool,
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
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;

    // Verify exists
    client
        .query_opt("SELECT id FROM workitem WHERE id = $1", &[&id])
        .await
        .map_err(|e| format!("Query error: {e}"))?
        .ok_or_else(|| format!("Work item {id} not found"))?;

    let mut set_clauses: Vec<String> = Vec::new();
    let mut params: Vec<Box<dyn tokio_postgres::types::ToSql + Sync + Send>> = Vec::new();
    let mut idx = 0u32;

    if let Some(ref v) = title {
        idx += 1;
        set_clauses.push(format!("title = ${idx}"));
        params.push(Box::new(v.clone()));
    }
    if let Some(ref v) = content {
        idx += 1;
        set_clauses.push(format!("content = ${idx}"));
        params.push(Box::new(v.clone()));
    }
    if let Some(ref v) = wi_type {
        let type_row = client
            .query_opt("SELECT id FROM workitem_type WHERE name = $1", &[v])
            .await
            .map_err(|e| format!("Query error: {e}"))?
            .ok_or_else(|| format!("Invalid type '{v}'"))?;
        let type_id: i32 = type_row.get(0);
        idx += 1;
        set_clauses.push(format!("wi_type_id = ${idx}"));
        params.push(Box::new(type_id));
    }
    if let Some(ref v) = wi_status {
        let status_row = client
            .query_opt("SELECT id FROM workitem_status WHERE name = $1", &[v])
            .await
            .map_err(|e| format!("Query error: {e}"))?
            .ok_or_else(|| format!("Invalid status '{v}'"))?;
        let status_id: i32 = status_row.get(0);
        idx += 1;
        set_clauses.push(format!("wi_status_id = ${idx}"));
        params.push(Box::new(status_id));
    }
    if let Some(ref v) = wi_tshirt {
        idx += 1;
        set_clauses.push(format!("wi_tshirt = ${idx}"));
        params.push(Box::new(v.clone()));
    }
    if let Some(v) = area_id {
        idx += 1;
        set_clauses.push(format!("area_id = ${idx}"));
        params.push(Box::new(v));
    }
    if let Some(ref v) = sprint {
        idx += 1;
        set_clauses.push(format!("sprint = ${idx}"));
        params.push(Box::new(v.clone()));
    }
    if let Some(ref v) = details {
        idx += 1;
        set_clauses.push(format!("details = ${idx}"));
        params.push(Box::new(v.clone()));
    }
    if let Some(v) = parent_id {
        idx += 1;
        set_clauses.push(format!("parent_id = ${idx}"));
        params.push(Box::new(v));
    }

    if set_clauses.is_empty() {
        return get_work_item(pool, id).await;
    }

    set_clauses.push("updated = NOW()".to_string());
    idx += 1;
    params.push(Box::new(id));

    let sql = format!(
        "UPDATE workitem SET {} WHERE id = ${idx}",
        set_clauses.join(", ")
    );

    let param_refs: Vec<&(dyn tokio_postgres::types::ToSql + Sync)> = params
        .iter()
        .map(|p| p.as_ref() as &(dyn tokio_postgres::types::ToSql + Sync))
        .collect();

    client
        .execute(&sql, &param_refs)
        .await
        .map_err(|e| format!("Update error: {e}"))?;

    get_work_item(pool, id).await
}

pub async fn archive_work_item(pool: &Pool, id: i32) -> Result<WorkItem, String> {
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;

    // Verify exists
    client
        .query_opt("SELECT id FROM workitem WHERE id = $1", &[&id])
        .await
        .map_err(|e| format!("Query error: {e}"))?
        .ok_or_else(|| format!("Work item {id} not found"))?;

    client
        .execute(
            "UPDATE workitem SET archived = true, updated = NOW() WHERE id = $1",
            &[&id],
        )
        .await
        .map_err(|e| format!("Update error: {e}"))?;

    get_work_item(pool, id).await
}

pub async fn unarchive_work_item(pool: &Pool, id: i32) -> Result<WorkItem, String> {
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;

    // Verify exists
    client
        .query_opt("SELECT id FROM workitem WHERE id = $1", &[&id])
        .await
        .map_err(|e| format!("Query error: {e}"))?
        .ok_or_else(|| format!("Work item {id} not found"))?;

    client
        .execute(
            "UPDATE workitem SET archived = false, updated = NOW() WHERE id = $1",
            &[&id],
        )
        .await
        .map_err(|e| format!("Update error: {e}"))?;

    get_work_item(pool, id).await
}

pub async fn search_work_items(
    pool: &Pool,
    query_str: String,
    project_id: Option<i32>,
) -> Result<Vec<WorkItem>, String> {
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;
    let pattern = format!("%{query_str}%");

    let mut sql = String::from(
        "SELECT w.id, w.project_id, p.project, w.area_id, a.name, \
         t.name, s.name, w.wi_tshirt, w.sprint, w.title, w.content, \
         w.details, w.parent_id, w.created::text, w.updated::text, \
         w.archived \
         FROM workitem w \
         JOIN project p ON w.project_id = p.id \
         JOIN workitem_type t ON w.wi_type_id = t.id \
         JOIN workitem_status s ON w.wi_status_id = s.id \
         LEFT JOIN area a ON w.area_id = a.id \
         WHERE w.archived = false \
         AND (w.title ILIKE $1 OR w.content ILIKE $1)",
    );

    let mut params: Vec<Box<dyn tokio_postgres::types::ToSql + Sync + Send>> = Vec::new();
    params.push(Box::new(pattern));

    if let Some(pid) = project_id {
        sql.push_str(" AND w.project_id = $2");
        params.push(Box::new(pid));
    }

    sql.push_str(" ORDER BY w.id ASC");

    let param_refs: Vec<&(dyn tokio_postgres::types::ToSql + Sync)> = params
        .iter()
        .map(|p| p.as_ref() as &(dyn tokio_postgres::types::ToSql + Sync))
        .collect();

    let rows = client
        .query(&sql, &param_refs)
        .await
        .map_err(|e| format!("Query error: {e}"))?;

    Ok(rows
        .iter()
        .map(|r| WorkItem {
            id: r.get(0),
            project_id: r.get(1),
            project_name: r.get(2),
            area_id: r.get(3),
            area_name: r.get(4),
            wi_type: r.get(5),
            wi_status: r.get(6),
            wi_tshirt: r.get(7),
            sprint: r.get(8),
            title: r.get(9),
            content: r.get(10),
            details: r.get(11),
            parent_id: r.get(12),
            created: r.get(13),
            updated: r.get(14),
            archived: r.get(15),
        })
        .collect())
}

pub async fn list_related(pool: &Pool, work_item_id: i32) -> Result<Vec<RelatedItem>, String> {
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;
    let rows = client
        .query(
            "SELECT r.id, r.left_id, r.right_id, r.relationship, w.title \
             FROM related r \
             JOIN workitem w ON w.id = CASE \
               WHEN r.left_id = $1 THEN r.right_id \
               ELSE r.left_id END \
             WHERE r.left_id = $1 OR r.right_id = $1 \
             ORDER BY r.id",
            &[&work_item_id],
        )
        .await
        .map_err(|e| format!("Query error: {e}"))?;

    Ok(rows
        .iter()
        .map(|r| {
            let left_id: i32 = r.get(1);
            let right_id: i32 = r.get(2);
            let related_id = if left_id == work_item_id {
                right_id
            } else {
                left_id
            };
            let direction = if left_id == work_item_id {
                "right"
            } else {
                "left"
            };
            RelatedItem {
                id: related_id,
                relationship: r.get(3),
                title: r.get(4),
                direction: direction.to_string(),
            }
        })
        .collect())
}

pub async fn relate_work_items(
    pool: &Pool,
    left_id: i32,
    right_id: i32,
    relationship: String,
) -> Result<(), String> {
    if left_id == right_id {
        return Err("Cannot relate a work item to itself".to_string());
    }

    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;

    // Verify both exist
    client
        .query_opt("SELECT id FROM workitem WHERE id = $1", &[&left_id])
        .await
        .map_err(|e| format!("Query error: {e}"))?
        .ok_or_else(|| format!("Work item {left_id} not found"))?;
    client
        .query_opt("SELECT id FROM workitem WHERE id = $1", &[&right_id])
        .await
        .map_err(|e| format!("Query error: {e}"))?
        .ok_or_else(|| format!("Work item {right_id} not found"))?;

    client
        .execute(
            "INSERT INTO related (left_id, right_id, relationship) VALUES ($1, $2, $3)",
            &[&left_id, &right_id, &relationship],
        )
        .await
        .map_err(|e| format!("Insert error: {e}"))?;

    Ok(())
}

pub async fn unrelate_work_items(pool: &Pool, left_id: i32, right_id: i32) -> Result<(), String> {
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;
    let result = client
        .execute(
            "DELETE FROM related \
             WHERE (left_id = $1 AND right_id = $2) \
             OR (left_id = $2 AND right_id = $1)",
            &[&left_id, &right_id],
        )
        .await
        .map_err(|e| format!("Delete error: {e}"))?;

    if result == 0 {
        return Err("Relationship not found".to_string());
    }
    Ok(())
}

pub async fn create_project(
    pool: &Pool,
    project: String,
    cn_path: String,
    gh_repo: Option<String>,
    description: Option<String>,
) -> Result<Project, String> {
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;
    let row = client
        .query_one(
            "INSERT INTO project (project, cn_path, gh_repo, description) \
             VALUES ($1, $2, $3, $4) \
             RETURNING id, project, cn_path, gh_repo, description, \
             created::text, updated::text",
            &[&project, &cn_path, &gh_repo, &description],
        )
        .await
        .map_err(|e| format!("Insert error: {e}"))?;

    Ok(Project {
        id: row.get(0),
        project: row.get(1),
        cn_path: row.get(2),
        gh_repo: row.get(3),
        description: row.get(4),
        created: row.get(5),
        updated: row.get(6),
    })
}

pub async fn create_area(
    pool: &Pool,
    project_id: i32,
    name: String,
    description: Option<String>,
) -> Result<Area, String> {
    let client = pool
        .get()
        .await
        .map_err(|e| format!("DB connection error: {e}"))?;
    let row = client
        .query_one(
            "INSERT INTO area (project_id, name, description) \
             VALUES ($1, $2, $3) \
             RETURNING id, project_id, name, description",
            &[&project_id, &name, &description],
        )
        .await
        .map_err(|e| format!("Insert error: {e}"))?;

    Ok(Area {
        id: row.get(0),
        project_id: row.get(1),
        name: row.get(2),
        description: row.get(3),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_valid_tshirt_sizes() {
        let sizes = get_valid_tshirt_sizes();
        assert_eq!(sizes, vec!["XS", "S", "M", "L", "XL", "Huge", "Unknown"]);
    }
}
