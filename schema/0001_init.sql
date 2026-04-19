-- FuelEcon D1 Schema
-- Phase 3/4 Implementation

-- Waitlist for premium features
CREATE TABLE IF NOT EXISTS waitlist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  locale TEXT,
  source TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- User vehicles (Garage)
CREATE TABLE IF NOT EXISTS vehicles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT, -- For Phase 4 Auth
  name TEXT NOT NULL,
  make TEXT,
  model TEXT,
  year INTEGER,
  mpg REAL NOT NULL,
  fuel_type TEXT DEFAULT 'gas',
  is_default INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Trip history
CREATE TABLE IF NOT EXISTS trips (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT,
  origin TEXT,
  destination TEXT,
  distance REAL,
  cost REAL,
  mpg REAL,
  gas_price REAL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Gas prices cache (updated by daily agent)
CREATE TABLE IF NOT EXISTS gas_prices_cache (
  region_code TEXT PRIMARY KEY, -- e.g. 'US-CA', 'AU-NSW', 'UK-ENG'
  price REAL NOT NULL,
  currency TEXT DEFAULT 'USD',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- MPG lookup cache (EPA data)
CREATE TABLE IF NOT EXISTS mpg_lookup_cache (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  make TEXT NOT NULL,
  model TEXT NOT NULL,
  year INTEGER NOT NULL,
  engine TEXT,
  drivetrain TEXT,
  mpg_city REAL,
  mpg_hwy REAL,
  mpg_comb REAL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_waitlist_email ON waitlist(email);
CREATE INDEX IF NOT EXISTS idx_vehicles_user ON vehicles(user_id);
CREATE INDEX IF NOT EXISTS idx_trips_user ON trips(user_id);
CREATE INDEX IF NOT EXISTS idx_mpg_lookup ON mpg_lookup_cache(make, model, year);
