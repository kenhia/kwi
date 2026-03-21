-- kwi initial schema
-- Apply with: psql -f migrations/001_initial_schema.sql

-- Reference tables

CREATE TABLE IF NOT EXISTS workitem_type (
    id      serial PRIMARY KEY,
    name    text   UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS workitem_status (
    id      serial PRIMARY KEY,
    name    text   UNIQUE NOT NULL
);

-- Core tables

CREATE TABLE IF NOT EXISTS project (
    id          serial       PRIMARY KEY,
    project     text         UNIQUE NOT NULL,
    gh_repo     text,
    cn_path     text         NOT NULL,
    created     timestamptz  NOT NULL DEFAULT NOW(),
    updated     timestamptz  NOT NULL DEFAULT NOW(),
    description text
);

CREATE TABLE IF NOT EXISTS area (
    id          serial  PRIMARY KEY,
    project_id  integer NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    name        text    NOT NULL,
    description text,
    UNIQUE (project_id, name)
);

CREATE TABLE IF NOT EXISTS workitem (
    id           serial       PRIMARY KEY,
    project_id   integer      NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    area_id      integer      REFERENCES area(id) ON DELETE SET NULL,
    wi_type_id   integer      NOT NULL REFERENCES workitem_type(id),
    wi_status_id integer      NOT NULL REFERENCES workitem_status(id),
    wi_tshirt    text         DEFAULT 'Unknown'
                              CHECK (wi_tshirt IN ('XS','S','M','L','XL','Huge','Unknown')),
    sprint       text,
    title        text         NOT NULL,
    content      text         NOT NULL,
    details      text,
    parent_id    integer      REFERENCES workitem(id) ON DELETE SET NULL,
    created      timestamptz  NOT NULL DEFAULT NOW(),
    updated      timestamptz  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS related (
    id           serial  PRIMARY KEY,
    left_id      integer NOT NULL REFERENCES workitem(id) ON DELETE CASCADE,
    right_id     integer NOT NULL REFERENCES workitem(id) ON DELETE CASCADE,
    relationship text    NOT NULL
);

-- Indexes

CREATE INDEX IF NOT EXISTS idx_workitem_project  ON workitem(project_id);
CREATE INDEX IF NOT EXISTS idx_workitem_area     ON workitem(area_id);
CREATE INDEX IF NOT EXISTS idx_workitem_type     ON workitem(wi_type_id);
CREATE INDEX IF NOT EXISTS idx_workitem_status   ON workitem(wi_status_id);
CREATE INDEX IF NOT EXISTS idx_workitem_parent   ON workitem(parent_id);
CREATE INDEX IF NOT EXISTS idx_related_left      ON related(left_id);
CREATE INDEX IF NOT EXISTS idx_related_right     ON related(right_id);

-- Seed data

INSERT INTO workitem_type (name) VALUES
    ('bug'), ('task'), ('idea'), ('research'), ('tweak'),
    ('issue'), ('feature'), ('epic'), ('story')
ON CONFLICT (name) DO NOTHING;

INSERT INTO workitem_status (name) VALUES
    ('open'), ('active'), ('resolved'), ('closed'), ('draft'), ('archived')
ON CONFLICT (name) DO NOTHING;
