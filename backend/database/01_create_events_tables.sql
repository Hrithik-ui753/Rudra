-- ============================================================
-- RUDRA SMART CAMPUS AI SYSTEM - CAMPUS EVENTS & REGISTRATION
-- Supabase SQL Schema & Row Level Security (RLS) Policies
-- ============================================================

-- Enable UUID Extension if not enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. EVENTS TABLE
CREATE TABLE IF NOT EXISTS public.events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL DEFAULT 'General',
    organizer TEXT NOT NULL DEFAULT 'VCE',
    department TEXT DEFAULT 'College',
    start_at TIMESTAMPTZ NOT NULL,
    end_at TIMESTAMPTZ NOT NULL,
    location TEXT NOT NULL,
    capacity INT DEFAULT NULL,
    registration_required BOOLEAN NOT NULL DEFAULT TRUE,
    registration_deadline TIMESTAMPTZ DEFAULT NULL,
    registration_url TEXT DEFAULT NULL,
    eligibility TEXT DEFAULT 'All Students',
    speaker TEXT DEFAULT NULL,
    status TEXT NOT NULL DEFAULT 'Upcoming', -- Upcoming, Live, Completed, Cancelled
    online BOOLEAN DEFAULT FALSE,
    meeting_url TEXT DEFAULT NULL,
    image TEXT DEFAULT NULL,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for searching events by date and category
CREATE INDEX IF NOT EXISTS idx_events_start_at ON public.events(start_at);
CREATE INDEX IF NOT EXISTS idx_events_category ON public.events(category);
CREATE INDEX IF NOT EXISTS idx_events_department ON public.events(department);

-- 2. EVENT REGISTRATIONS TABLE
CREATE TABLE IF NOT EXISTS public.event_registrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id TEXT NOT NULL REFERENCES public.events(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'registered', -- registered, cancelled
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_user_event_registration UNIQUE (event_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_event_registrations_user ON public.event_registrations(user_id);
CREATE INDEX IF NOT EXISTS idx_event_registrations_event ON public.event_registrations(event_id);

-- 3. EVENT CALENDAR ENTRIES TABLE (MICROSOFT GRAPH CALENDAR MATCHING)
CREATE TABLE IF NOT EXISTS public.event_calendar_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    event_id TEXT NOT NULL REFERENCES public.events(id) ON DELETE CASCADE,
    microsoft_event_id TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_user_event_calendar UNIQUE (user_id, event_id)
);

CREATE INDEX IF NOT EXISTS idx_event_calendar_user ON public.event_calendar_entries(user_id);

-- ============================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================

-- Enable RLS on all tables
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.event_registrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.event_calendar_entries ENABLE ROW LEVEL SECURITY;

-- EVENTS RLS POLICIES:
-- Everyone (authenticated and anon) can view events.
CREATE POLICY "Public events are viewable by everyone" 
    ON public.events FOR SELECT 
    USING (true);

-- EVENT REGISTRATIONS RLS POLICIES:
-- Users can only view their own registrations.
CREATE POLICY "Users can view own event registrations" 
    ON public.event_registrations FOR SELECT 
    USING (auth.uid()::text = user_id OR user_id = current_setting('request.jwt.claim.sub', true));

-- Users can only create registrations for themselves.
CREATE POLICY "Users can insert own event registrations" 
    ON public.event_registrations FOR INSERT 
    WITH CHECK (auth.uid()::text = user_id OR user_id = current_setting('request.jwt.claim.sub', true));

-- Users can only update/delete their own registrations.
CREATE POLICY "Users can delete own event registrations" 
    ON public.event_registrations FOR DELETE 
    USING (auth.uid()::text = user_id OR user_id = current_setting('request.jwt.claim.sub', true));

-- EVENT CALENDAR ENTRIES RLS POLICIES:
-- Users can only manage their own Microsoft calendar records.
CREATE POLICY "Users can view own calendar entries" 
    ON public.event_calendar_entries FOR SELECT 
    USING (auth.uid()::text = user_id OR user_id = current_setting('request.jwt.claim.sub', true));

CREATE POLICY "Users can insert own calendar entries" 
    ON public.event_calendar_entries FOR INSERT 
    WITH CHECK (auth.uid()::text = user_id OR user_id = current_setting('request.jwt.claim.sub', true));

CREATE POLICY "Users can delete own calendar entries" 
    ON public.event_calendar_entries FOR DELETE 
    USING (auth.uid()::text = user_id OR user_id = current_setting('request.jwt.claim.sub', true));
