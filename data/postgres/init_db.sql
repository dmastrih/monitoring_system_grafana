CREATE TABLE IF NOT EXISTS grafana_alerts (
    id SERIAL PRIMARY KEY,
    alert_name TEXT,
    severity TEXT,
    service TEXT,
    state TEXT,
    summary TEXT,
    description TEXT,
    message TEXT,
    alert_type TEXT DEFAULT 'grafana',
    status TEXT DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
