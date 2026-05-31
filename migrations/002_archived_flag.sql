-- kwi migration 002: decouple "archived" from status
-- Apply with: psql -f migrations/002_archived_flag.sql
--
-- Forward-only and idempotent:
--   1. Add workitem.archived boolean column (default false).
--   2. Repoint any legacy rows with the 'archived' status to 'closed' + archived=true.
--   3. Remove the now-unused 'archived' status row.
--   4. Index the new archived column.

-- 1. New column, independent of wi_status_id.
ALTER TABLE workitem
    ADD COLUMN IF NOT EXISTS archived boolean NOT NULL DEFAULT false;

-- 2. Repoint legacy archived-status rows to closed + archived flag.
UPDATE workitem
SET archived = true,
    wi_status_id = (SELECT id FROM workitem_status WHERE name = 'closed'),
    updated = NOW()
WHERE wi_status_id = (SELECT id FROM workitem_status WHERE name = 'archived');

-- 3. Retire the 'archived' status (no rows reference it after step 2).
DELETE FROM workitem_status WHERE name = 'archived';

-- 4. Index for archived filtering.
CREATE INDEX IF NOT EXISTS idx_workitem_archived ON workitem(archived);
