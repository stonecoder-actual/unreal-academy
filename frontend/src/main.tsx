import { useEffect, useState, type FormEvent } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';
import { request } from './api';
import { Library, ParentImport } from './Library';

function App() {
  const [view, setView] = useState<'learn' | 'parent'>('learn');
  const [revision, setRevision] = useState(0);
  const [status, setStatus] = useState('Connecting to backend…');
  const [message, setMessage] = useState('');
  const [feedback, setFeedback] = useState('');
  const [ready, setReady] = useState(false);
  const [saving, setSaving] = useState(false);
  useEffect(() => {
    Promise.all([request('/api/health'), request('/api/settings')])
      .then(([health, settings]) => {
        if (health.status !== 'ok') throw new Error();
        setStatus('Backend connected · SQLite ready');
        setMessage(settings.welcome_message);
        setReady(true);
      }).catch(() => setStatus('Backend unavailable. Refresh to retry.'));
  }, []);
  async function save(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setFeedback('');
    try {
      const result = await request('/api/settings', {
        method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ welcome_message: message }),
      });
      setMessage(result.welcome_message);
      setFeedback('Saved to your local database.');
    } catch { setFeedback('Save failed. Please try again.'); }
    finally { setSaving(false); }
  }
  return <main>
    <span className="badge">PHASE 2 · IN DEVELOPMENT</span>
    <h1>Unreal Academy</h1>
    <p className="intro">A place to learn, experiment, and build your own worlds.</p>
    <p className="welcome">{message}</p>
    <nav aria-label="Main navigation"><button aria-pressed={view === 'learn'} onClick={() => setView('learn')}>My learning</button>
      <button className="secondary" aria-pressed={view === 'parent'} onClick={() => setView('parent')}>Parent setup</button></nav>
    {view === 'learn' ? <Library revision={revision}/> : <>
    <ParentImport onImported={() => setRevision(value => value + 1)}/>
    <section aria-labelledby="foundation"><h2 id="foundation">Development status</h2>
      <p role="status">{status}</p>
      <p>Course playback is available. Quizzes, practical assignments, accounts, XP, and AI are future milestones.</p>
    </section>
    <section aria-labelledby="local"><h2 id="local">Make it yours</h2>
      <p>Set a welcome message. It stays here when the app restarts.</p>
      <form onSubmit={save}><label htmlFor="message">Welcome message</label>
        <input id="message" value={message} onChange={e => setMessage(e.target.value)} required maxLength={200} disabled={!ready || saving}/>
        <button disabled={!ready || saving}>{saving ? 'Saving…' : 'Save message'}</button>
      </form><p role="status">{feedback}</p>
    </section></>}<footer>Local development · Your data stays on this computer</footer>
  </main>;
}

createRoot(document.getElementById('root')!).render(<App/>);
