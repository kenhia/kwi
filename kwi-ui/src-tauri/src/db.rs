use std::env;
use std::path::PathBuf;
use std::str::FromStr;

use deadpool_postgres::{Manager, ManagerConfig, Pool, RecyclingMethod};
use tokio_postgres::NoTls;

use crate::models::KwiConfig;

pub struct ResolvedDb {
    pub url: String,
    pub password: Option<String>,
}

/// Resolve the database URL from environment variable or config file.
/// Precedence: KWI_DATABASE_URL env var > ~/.config/kwi/config.toml
pub fn resolve_db_url() -> Result<ResolvedDb, String> {
    // 1. Environment variable
    if let Ok(url) = env::var("KWI_DATABASE_URL") {
        if !url.is_empty() {
            return Ok(ResolvedDb {
                url,
                password: None,
            });
        }
    }

    // 2. Config file
    let config_path = config_file_path();
    if config_path.is_file() {
        let content = std::fs::read_to_string(&config_path)
            .map_err(|e| format!("Failed to read {}: {e}", config_path.display()))?;
        let config: KwiConfig = toml::from_str(&content)
            .map_err(|e| format!("Failed to parse {}: {e}", config_path.display()))?;
        if !config.database_url.is_empty() {
            return Ok(ResolvedDb {
                url: config.database_url,
                password: config.db_password,
            });
        }
    }

    Err(format!(
        "No database connection configured. Use one of:\n\
         1. KWI_DATABASE_URL env var: export KWI_DATABASE_URL=postgresql://...\n\
         2. Config file: {}\n\
         with: database_url = \"postgresql://...\"",
        config_path.display()
    ))
}

/// Config file path: ~/.config/kwi/config.toml on all platforms.
/// Uses home_dir() instead of config_dir() to match the Python CLI
/// (which uses Path.home() / ".config" / "kwi" / "config.toml").
fn config_file_path() -> PathBuf {
    dirs::home_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join(".config")
        .join("kwi")
        .join("config.toml")
}

/// Create a deadpool-postgres connection pool from a database URL.
/// Accepts both URI format (postgresql://...) and libpq key=value format
/// (host=... port=... dbname=... user=...).
pub fn create_pool(db: &ResolvedDb) -> Result<Pool, String> {
    let mut pg_config = tokio_postgres::Config::from_str(&db.url)
        .map_err(|e| format!("Failed to parse connection string: {e}"))?;

    if let Some(password) = &db.password {
        pg_config.password(password);
    }

    let mgr_config = ManagerConfig {
        recycling_method: RecyclingMethod::Fast,
    };
    let mgr = Manager::from_config(pg_config, NoTls, mgr_config);
    Pool::builder(mgr)
        .max_size(16)
        .build()
        .map_err(|e| format!("Failed to create connection pool: {e}"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_resolve_db_url_from_env() {
        env::set_var("KWI_DATABASE_URL", "postgresql://test@localhost/testdb");
        let resolved = resolve_db_url().unwrap();
        assert_eq!(resolved.url, "postgresql://test@localhost/testdb");
        assert!(resolved.password.is_none());
        env::remove_var("KWI_DATABASE_URL");
    }

    #[test]
    fn test_resolve_db_url_from_toml_content() {
        let toml_str = r#"database_url = "postgresql://user:pass@gratch:5432/workitems""#;
        let config: KwiConfig = toml::from_str(toml_str).unwrap();
        assert_eq!(
            config.database_url,
            "postgresql://user:pass@gratch:5432/workitems"
        );
        assert!(config.db_password.is_none());
    }

    #[test]
    fn test_toml_with_db_password() {
        let toml_str = r#"
database_url = "postgresql://ken@gratch:5432/workitems"
db_password = "secret123"
"#;
        let config: KwiConfig = toml::from_str(toml_str).unwrap();
        assert_eq!(
            config.database_url,
            "postgresql://ken@gratch:5432/workitems"
        );
        assert_eq!(config.db_password, Some("secret123".to_string()));
    }

    #[test]
    fn test_create_pool_uri_format() {
        let db = ResolvedDb {
            url: "postgresql://user:pass@localhost:5432/testdb".to_string(),
            password: None,
        };
        assert!(create_pool(&db).is_ok());
    }

    #[test]
    fn test_create_pool_keyvalue_format() {
        let db = ResolvedDb {
            url: "host=localhost port=5432 dbname=testdb user=ken".to_string(),
            password: None,
        };
        assert!(create_pool(&db).is_ok());
    }

    #[test]
    fn test_create_pool_with_separate_password() {
        let db = ResolvedDb {
            url: "host=localhost port=5432 dbname=testdb user=ken".to_string(),
            password: Some("secret".to_string()),
        };
        assert!(create_pool(&db).is_ok());
    }

    #[test]
    fn test_config_file_path_uses_home_dir() {
        let path = config_file_path();
        let path_str = path.to_string_lossy();
        assert!(path_str.contains(".config"));
        assert!(path_str.contains("kwi"));
        assert!(path_str.contains("config.toml"));
        // Must NOT use AppData/Roaming (which is what dirs::config_dir returns on Windows)
        assert!(!path_str.contains("AppData"));
    }
}
