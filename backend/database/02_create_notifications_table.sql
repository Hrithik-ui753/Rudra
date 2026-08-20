-- ============================================================
-- RUDRA SMART CAMPUS AI SYSTEM - EVENT NOTIFICATIONS & REMINDERS
-- Supabase SQL Schema & Row Level Security (RLS) Policies
-- ============================================================

-- 1. NOTIFICATIONS TABLE
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    event_id TEXT REFERENCES public.events(id) ON DELETE CASCADE,
    type TEXT NOT NULL, -- 'event_reminder', 'registration_deadline', 'event_starting'
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    scheduled_for TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    read_at TIMESTAMPTZ DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance & quick user filtering
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_event_id ON public.notifications(event_id);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON public.notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_scheduled ON public.notifications(scheduled_for);

-- ============================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================

ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- Users can only view their own notifications
CREATE POLICY "Users can view own notifications"
    ON public.notifications FOR SELECT
    USING (auth.uid()::text = user_id OR user_id = current_setting('request.jwt.claim.sub', true));

-- Users can only update read status on their own notifications
CREATE POLICY "Users can update own notifications"
    ON public.notifications FOR UPDATE
    USING (auth.uid()::text = user_id OR user_id = current_setting('request.jwt.claim.sub', true));

-- System / Service Role insert policy
CREATE POLICY "System can insert notifications"
    ON public.notifications FOR INSERT
    WITH CHECK (true);
