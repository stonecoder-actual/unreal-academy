import { useEffect, useState, type FormEvent } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';
import { request } from './api';
import { Library, ParentImport } from './Library';
import { ParentExternalImport } from './ExternalImport';
import { XPPanel, Profile } from './Progress';
import { Avatar, Icon } from './UI';
import { DesignPreview, ResponsivePreview } from './DesignPreview';

function App() {
  const [view, setView] = useState<'learn' | 'courses' | 'profile' | 'parent'>('learn');
  const [revision, setRevision] = useState(0);
  const [navigationKey,setNavigationKey]=useState(0);
  const [status, setStatus] = useState('Connecting to backend…');
  const [message, setMessage] = useState('');
  const [feedback, setFeedback] = useState('');
  const [ready, setReady] = useState(false);
  const [saving, setSaving] = useState(false);
  useEffect(()=>{document.getElementById('main-content')?.focus();},[view]);
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
  function navigate(next:typeof view){setView(next);setNavigationKey(n=>n+1);window.scrollTo({top:0});}
  return <div className="app-shell">
    <a className="skip-link" href="#main-content">Skip to learning</a>
    <aside className="app-sidebar">
      <button className="brand" onClick={()=>navigate('learn')} aria-label="Unreal Academy home"><span className="brand-symbol"><Icon name="cube" size={27}/></span><span>UNREAL<small>ACADEMY</small></span></button>
      <p className="nav-caption">YOUR WORKSPACE</p>
      <nav aria-label="Main navigation">
        <button className={view==='learn'?'active':''} aria-current={view==='learn'?'page':undefined} onClick={()=>navigate('learn')}><Icon name="home"/>My learning</button>
        <button className={view==='courses'?'active':''} aria-current={view==='courses'?'page':undefined} onClick={()=>navigate('courses')}><Icon name="library"/>Course library</button>
        <button className={view==='profile'?'active':''} aria-current={view==='profile'?'page':undefined} onClick={()=>navigate('profile')}><Icon name="flag"/>My progress</button>
      </nav>
      <div className="sidebar-bottom"><XPPanel compact/><button className={`parent-link ${view==='parent'?'active':''}`} aria-current={view==='parent'?'page':undefined} onClick={()=>navigate('parent')}><Icon name="parent"/>Parent setup</button><div className="sidebar-profile"><Avatar/><div><strong>Jaxon</strong><span>Game developer in the making</span></div></div></div>
    </aside>
    <div className="workspace"><header className="topbar"><span><span className="status-dot"/>Your academy · On this computer</span><span className="development-tag">IN DEVELOPMENT</span></header>
    <main id="main-content" tabIndex={-1}>
    {view==='profile'?<Profile/>:view !== 'parent' ? <Library key={`${view}-${navigationKey}`} revision={revision} home={view==='learn'} welcome={message}/> : <div className="parent-page">
    <header className="page-heading"><p className="eyebrow">PARENT WORKSPACE</p><h1>Set up Jaxon’s academy.</h1><p>Connect the video library, manage course imports, and adjust local settings. Missions appear directly in Jaxon’s learning portal.</p></header>
    <ParentImport onImported={() => setRevision(value => value + 1)}/>
    <ParentExternalImport onImported={() => setRevision(value => value + 1)}/>
    <section aria-labelledby="foundation"><h2 id="foundation">Development status</h2>
      <p role="status">{status}</p>
      <p>Guided missions publish directly. Knowledge checks award XP automatically; practical activities are optional. Accounts and AI services remain future work.</p>
    </section>
    <section aria-labelledby="local"><h2 id="local">Make it yours</h2>
      <p>Set a welcome message. It stays here when the app restarts.</p>
      <form onSubmit={save}><label htmlFor="message">Welcome message</label>
        <input id="message" value={message} onChange={e => setMessage(e.target.value)} required maxLength={200} disabled={!ready || saving}/>
        <button disabled={!ready || saving}>{saving ? 'Saving…' : 'Save message'}</button>
      </form><p role="status">{feedback}</p>
    </section></div>}<footer><Icon name="cube" size={16}/>Unreal Academy <span>Learn a little. Build something. Make it yours.</span></footer>
  </main></div></div>;
}

const previewParams=new URLSearchParams(location.search);
createRoot(document.getElementById('root')!).render(import.meta.env.DEV && previewParams.has('design-preview') ? <DesignPreview/> : import.meta.env.DEV && previewParams.has('responsive-preview') ? <ResponsivePreview size={previewParams.get('responsive-preview')??'phone'}/> : <App/>);
