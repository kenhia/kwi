mod commands;
mod db;
mod models;
mod queries;

use commands::AppState;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let (pool, connection_error) = match db::resolve_db_url() {
        Ok(resolved) => match db::create_pool(&resolved) {
            Ok(p) => (Some(p), None),
            Err(e) => {
                eprintln!("{e}");
                (None, Some(e))
            }
        },
        Err(e) => {
            eprintln!("{e}");
            (None, Some(e))
        }
    };

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(AppState {
            pool,
            connection_error,
        })
        .invoke_handler(tauri::generate_handler![
            commands::check_connection,
            commands::list_projects,
            commands::list_areas,
            commands::list_work_items,
            commands::get_work_item,
            commands::get_valid_types,
            commands::get_valid_statuses,
            commands::get_valid_tshirt_sizes,
            commands::create_work_item,
            commands::update_work_item,
            commands::archive_work_item,
            commands::search_work_items,
            commands::list_related,
            commands::relate_work_items,
            commands::unrelate_work_items,
            commands::create_project,
            commands::create_area,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
