import { publicPageMetadata } from "../../lib/seo";

export const metadata = publicPageMetadata("Cookies and browser storage", "See how Learnora ME uses essential cookies and browser storage and manage optional cookie choices.", "/cookies");

export default function CookiesPage() {
  return (
    <main className="min-h-screen bg-[var(--bg)] px-5 py-12 text-[var(--text-body)]">
      <div className="mx-auto max-w-4xl">
        <a href="/" className="text-sm font-semibold text-[var(--primary)]">Learnora ME</a>
        <h1 className="mt-10 font-display text-4xl text-[var(--text-heading)] sm:text-5xl">Cookies and browser storage</h1>
        <p className="mt-4 text-sm text-[var(--text-muted)]">Last updated: 18 November 2026</p>
        <p className="mt-7 max-w-3xl leading-7">Learnora uses a small number of essential cookies and browser storage items to support sign-in, security, account context and the preferences you choose. Optional analytics and marketing technologies are not enabled by this application at present.</p>
        <a href="#preferences" className="mt-6 inline-flex min-h-11 items-center rounded-lg bg-[var(--primary)] px-4 font-semibold text-[var(--on-primary)]">Manage cookie preferences</a>
        <div className="mt-10 space-y-8">
          <section>
            <h2 className="text-xl font-semibold text-[var(--text-heading)]">Essential cookie</h2>
            <div className="mt-3 overflow-x-auto rounded-xl border border-[var(--border)] bg-[var(--card)]">
              <table className="w-full text-left text-sm">
                <thead><tr className="border-b border-[var(--border)]"><th className="p-3">Name</th><th className="p-3">Purpose</th><th className="p-3">Storage</th></tr></thead>
                <tbody><tr><td className="p-3 font-mono">phx_token</td><td className="p-3">Maintains your authenticated Learnora session and protects access to account features.</td><td className="p-3">First-party HttpOnly cookie</td></tr></tbody>
              </table>
            </div>
            <p className="mt-3 text-sm leading-7 text-[var(--text-muted)]">This cookie is required for sign-in and protected account features. It is not used for advertising. It is configured as HttpOnly, SameSite=Lax and Secure in production; its lifetime follows the session token.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold text-[var(--text-heading)]">Essential browser storage</h2>
            <div className="mt-3 overflow-x-auto rounded-xl border border-[var(--border)] bg-[var(--card)]">
              <table className="w-full text-left text-sm">
                <thead><tr className="border-b border-[var(--border)]"><th className="p-3">Name</th><th className="p-3">Purpose</th><th className="p-3">Storage</th></tr></thead>
                <tbody>
                  <tr className="border-b border-[var(--border)]"><td className="p-3 font-mono">phx_session_hint</td><td className="p-3">Helps Learnora recognise an existing cookie session when you open another tab.</td><td className="p-3">Local storage</td></tr>
                  <tr className="border-b border-[var(--border)]"><td className="p-3 font-mono">phx_logged_out</td><td className="p-3">Prevents a signed-out session from being treated as active.</td><td className="p-3">Local and session storage</td></tr>
                  <tr className="border-b border-[var(--border)]"><td className="p-3 font-mono">phx_session_epoch, phx_token</td><td className="p-3">Session markers used by the browser client to coordinate the current authenticated session.</td><td className="p-3">Session storage</td></tr>
                  <tr className="border-b border-[var(--border)]"><td className="p-3 font-mono">learnora_organisation_id</td><td className="p-3">Remembers the active organisation context selected by an authorised user.</td><td className="p-3">Local storage</td></tr>
                  <tr><td className="p-3 font-mono">learnora_api_cache_v1:*, learnora_current_user_cache:*</td><td className="p-3">Temporarily caches session-scoped API responses and the current user record to avoid unnecessary repeat requests.</td><td className="p-3">Session storage</td></tr>
                </tbody>
              </table>
            </div>
          </section>
          <section>
            <h2 className="text-xl font-semibold text-[var(--text-heading)]">Functional preference storage</h2>
            <p className="mt-3 leading-7">When you choose a theme, Learnora stores your appearance preference as <code className="font-mono">learnora_theme</code> in local storage. Your cookie choices are stored as <code className="font-mono">learnora_cookie_consent_v1</code> so the site can remember and respect them. These items are not advertising cookies.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold text-[var(--text-heading)]">Optional technologies</h2>
            <p className="mt-3 leading-7">Analytics and marketing preferences are available in the cookie controls. No optional analytics or advertising tags are currently configured in this Learnora ME frontend. If optional technologies are introduced, they must remain disabled until you actively opt in. You can reject optional categories without losing access to the core service.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold text-[var(--text-heading)]">Change or withdraw your choices</h2>
            <p className="mt-3 leading-7">You can reopen cookie preferences at any time using the control in the banner or the manage button above. You can also clear browser storage in your browser settings; doing so may sign you out or reset saved preferences.</p>
            <p className="mt-3 text-sm">For privacy questions, contact <a className="text-[var(--primary)] underline" href="mailto:learnorame@gmail.com">learnorame@gmail.com</a>. Read the <a className="text-[var(--primary)] underline" href="/privacy">Privacy Policy</a> for more information.</p>
          </section>
        </div>
      </div>
    </main>
  );
}
