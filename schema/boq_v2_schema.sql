-- Plan2Takeoff V2 — PostgreSQL / Supabase Database Schema
-- Supports Direct Costing (Material + Labor + Equipment), Rebar Bin Packing,
-- Native Vector Heatmaps, and Public Agentic Manifests.

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    client VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS drawings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- 'pdf', 'dxf', 'dwg'
    storage_url TEXT,
    sheet_no VARCHAR(100),
    scale VARCHAR(50) DEFAULT '1:100',
    width_px NUMERIC,
    height_px NUMERIC,
    status VARCHAR(50) DEFAULT 'processed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS drawing_elements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drawing_id UUID REFERENCES drawings(id) ON DELETE CASCADE,
    element_id_tag VARCHAR(100) NOT NULL, -- e.g. 'F-1', '2B-1'
    element_type VARCHAR(50) NOT NULL, -- 'footing', 'column', 'beam', 'slab', 'chb_wall'
    location VARCHAR(255),
    length_m NUMERIC,
    width_m NUMERIC,
    height_m NUMERIC,
    count_qty INT DEFAULT 1,
    bounding_box JSONB, -- [x1, y1, x2, y2]
    rebar_specs JSONB,
    concrete_class VARCHAR(50) DEFAULT 'Class A',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS backup_computations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drawing_id UUID REFERENCES drawings(id) ON DELETE CASCADE,
    division VARCHAR(100) NOT NULL, -- 'Division 03 — Concrete Works', etc.
    item_code VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255),
    quantity NUMERIC NOT NULL,
    unit VARCHAR(20) NOT NULL,
    material_unit_cost NUMERIC DEFAULT 0.0,
    labor_unit_cost NUMERIC DEFAULT 0.0,
    equipment_unit_cost NUMERIC DEFAULT 0.0,
    total_unit_cost NUMERIC DEFAULT 0.0,
    total_amount NUMERIC DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'Confirmed'
);

CREATE TABLE IF NOT EXISTS boq_checklist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    division VARCHAR(100) NOT NULL,
    item_code VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    unit VARCHAR(20) NOT NULL,
    quantity NUMERIC NOT NULL,
    material_unit_cost NUMERIC DEFAULT 0.0,
    labor_unit_cost NUMERIC DEFAULT 0.0,
    equipment_unit_cost NUMERIC DEFAULT 0.0,
    total_unit_cost NUMERIC DEFAULT 0.0,
    total_amount NUMERIC DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'Confirmed'
);

CREATE TABLE IF NOT EXISTS rebar_cutting_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drawing_id UUID REFERENCES drawings(id) ON DELETE CASCADE,
    diameter_mm INT NOT NULL,
    stock_length_m NUMERIC NOT NULL, -- 6.0, 9.0, 12.0
    bar_count INT NOT NULL,
    cuts_json JSONB NOT NULL,
    scrap_kg NUMERIC DEFAULT 0.0,
    utilization_pct NUMERIC DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS manifest_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(100),
    action VARCHAR(100),
    agent_name VARCHAR(100),
    file_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- V2 Session Persistence Tables
CREATE TABLE IF NOT EXISTS boq_sessions_v2 (
    session_id VARCHAR(100) PRIMARY KEY,
    drawing_name VARCHAR(255) NOT NULL,
    grand_total NUMERIC DEFAULT 0.0,
    sections_subtotal NUMERIC DEFAULT 0.0,
    item_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS boq_items_v2 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(100) REFERENCES boq_sessions_v2(session_id) ON DELETE CASCADE,
    item_code VARCHAR(50) NOT NULL,
    trade VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    quantity NUMERIC DEFAULT 0.0,
    unit VARCHAR(20) NOT NULL,
    material_unit_cost NUMERIC DEFAULT 0.0,
    labor_unit_cost NUMERIC DEFAULT 0.0,
    equipment_unit_cost NUMERIC DEFAULT 0.0,
    total_unit_cost NUMERIC DEFAULT 0.0,
    total_amount NUMERIC DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'Confirmed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS and grant public access policies
ALTER TABLE boq_sessions_v2 ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public read/write on boq_sessions_v2" ON boq_sessions_v2;
CREATE POLICY "Allow public read/write on boq_sessions_v2" ON boq_sessions_v2 FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE boq_items_v2 ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public read/write on boq_items_v2" ON boq_items_v2;
CREATE POLICY "Allow public read/write on boq_items_v2" ON boq_items_v2 FOR ALL USING (true) WITH CHECK (true);


