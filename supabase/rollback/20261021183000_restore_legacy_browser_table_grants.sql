-- EMERGENCY ROLLBACK ONLY for migration 20261021183000_revoke_browser_table_grants.sql.
-- Applying this file restores the broad grants that the security migration removes.
-- Do not run unless the release owner has reviewed the incident and explicitly approved
-- restoration of this legacy browser-access surface. This does not restore default ACLs.
BEGIN;
GRANT ALL PRIVILEGES ON TABLE
    public.users,
    public.learnora_courses,
    public.learnora_creator_accounts,
    public.learnora_discussions,
    public.learnora_learning_paths,
    public.course_modules,
    public.learnora_lessons,
    public.learnora_lesson_progress,
    public.learner_lesson_notes,
    public.quizzes,
    public.quiz_questions,
    public.quiz_attempts
TO anon, authenticated;
COMMIT;
