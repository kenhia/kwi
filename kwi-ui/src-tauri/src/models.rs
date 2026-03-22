use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KwiConfig {
    pub database_url: String,
    pub db_password: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Project {
    pub id: i32,
    pub project: String,
    pub cn_path: String,
    pub gh_repo: Option<String>,
    pub description: Option<String>,
    pub created: String,
    pub updated: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Area {
    pub id: i32,
    pub project_id: i32,
    pub name: String,
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkItem {
    pub id: i32,
    pub project_id: i32,
    pub project_name: Option<String>,
    pub area_id: Option<i32>,
    pub area_name: Option<String>,
    pub wi_type: String,
    pub wi_status: String,
    pub wi_tshirt: String,
    pub sprint: Option<String>,
    pub title: String,
    pub content: String,
    pub details: Option<String>,
    pub parent_id: Option<i32>,
    pub created: String,
    pub updated: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RelatedItem {
    pub id: i32,
    pub relationship: String,
    pub title: String,
    pub direction: String,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_project_serialize_deserialize() {
        let p = Project {
            id: 1,
            project: "test".to_string(),
            cn_path: "/test".to_string(),
            gh_repo: Some("https://github.com/test".to_string()),
            description: None,
            created: "2026-01-01T00:00:00Z".to_string(),
            updated: "2026-01-01T00:00:00Z".to_string(),
        };
        let json = serde_json::to_string(&p).unwrap();
        let deserialized: Project = serde_json::from_str(&json).unwrap();
        assert_eq!(deserialized.project, "test");
        assert_eq!(
            deserialized.gh_repo,
            Some("https://github.com/test".to_string())
        );
    }

    #[test]
    fn test_workitem_serialize_deserialize() {
        let w = WorkItem {
            id: 42,
            project_id: 1,
            project_name: Some("myproj".to_string()),
            area_id: Some(2),
            area_name: Some("backend".to_string()),
            wi_type: "bug".to_string(),
            wi_status: "open".to_string(),
            wi_tshirt: "M".to_string(),
            sprint: Some("2026-W12".to_string()),
            title: "Fix login".to_string(),
            content: "Login is **broken**".to_string(),
            details: None,
            parent_id: None,
            created: "2026-01-01T00:00:00Z".to_string(),
            updated: "2026-01-02T00:00:00Z".to_string(),
        };
        let json = serde_json::to_string(&w).unwrap();
        let deserialized: WorkItem = serde_json::from_str(&json).unwrap();
        assert_eq!(deserialized.id, 42);
        assert_eq!(deserialized.wi_type, "bug");
        assert_eq!(deserialized.area_name, Some("backend".to_string()));
        assert!(deserialized.details.is_none());
    }

    #[test]
    fn test_area_serialize_deserialize() {
        let a = Area {
            id: 5,
            project_id: 1,
            name: "frontend".to_string(),
            description: Some("Frontend work".to_string()),
        };
        let json = serde_json::to_string(&a).unwrap();
        let deserialized: Area = serde_json::from_str(&json).unwrap();
        assert_eq!(deserialized.name, "frontend");
        assert_eq!(deserialized.description, Some("Frontend work".to_string()));
    }

    #[test]
    fn test_related_item_serialize_deserialize() {
        let r = RelatedItem {
            id: 10,
            relationship: "blocks".to_string(),
            title: "Related task".to_string(),
            direction: "right".to_string(),
        };
        let json = serde_json::to_string(&r).unwrap();
        let deserialized: RelatedItem = serde_json::from_str(&json).unwrap();
        assert_eq!(deserialized.relationship, "blocks");
        assert_eq!(deserialized.direction, "right");
    }

    #[test]
    fn test_config_serialize_deserialize() {
        let c = KwiConfig {
            database_url: "postgresql://user:pass@localhost:5432/workitems".to_string(),
            db_password: None,
        };
        let json = serde_json::to_string(&c).unwrap();
        let deserialized: KwiConfig = serde_json::from_str(&json).unwrap();
        assert_eq!(deserialized.database_url, c.database_url);
        assert!(deserialized.db_password.is_none());
    }

    #[test]
    fn test_config_from_toml() {
        let toml_str = r#"database_url = "postgresql://user:pass@gratch:5432/workitems""#;
        let config: KwiConfig = toml::from_str(toml_str).unwrap();
        assert_eq!(
            config.database_url,
            "postgresql://user:pass@gratch:5432/workitems"
        );
        assert!(config.db_password.is_none());
    }
}
