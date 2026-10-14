import { useEffect, useRef, useState } from 'react';
import { request } from './api';

type Lesson = {
  id: string; title: string; relative_path: string; position: number;
  duration: number | null; playable: number; available: number; watched: number;
  caption_path: string | null; updated_at: string | null;
};
type Resource = { id: string; relative_path: string; lesson_id: string | null };
type CourseSummary = { id: string; title: string; lesson_count: number; watched_count: number; started_count: number };
type Course = { id: string; title: string; lessons: Lesson[]; resources: Resource[] };

function minutes(seconds: number) {
  return `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
}

function Player({ lesson, resources, onProgress }: {
  lesson: Lesson; resources: Resource[];
  onProgress: (id: string, position: number, watched: number) => void;
}) {
  const video = useRef<HTMLVideoElement>(null);
  const lastSave = useRef(0);
  const queue = useRef<Promise<unknown>>(Promise.resolve());
  const [feedback, setFeedback] = useState('');
  const [error, setError] = useState('');
  const [speed, setSpeed] = useState('1');
  function save(position: number, watched?: boolean) {
    if (!Number.isFinite(position)) return;
    lastSave.current = Date.now();
    // Serialize writes so an earlier playback checkpoint cannot overwrite a later one.
    queue.current = queue.current.catch(() => undefined).then(async () => {
      try {
        const result = await request(`/api/lessons/${lesson.id}/progress`, {
          method: 'PUT', headers: { 'Content-Type': 'application/json' }, keepalive: true,
          body: JSON.stringify({ position, ...(watched === undefined ? {} : { watched }) }),
        });
        setFeedback('Progress saved on this computer.');
        onProgress(lesson.id, result.position, result.watched);
      } catch { setFeedback('Progress could not be saved. Keep this page open and try again.'); }
    });
  }
  const saveRef = useRef(save);
  saveRef.current = save;
  useEffect(() => {
    const element = video.current;
    const checkpoint = () => {
      if (element && element.readyState >= 1) saveRef.current(element.currentTime);
    };
    const visibility = () => { if (document.visibilityState === 'hidden') checkpoint(); };
    window.addEventListener('pagehide', checkpoint);
    document.addEventListener('visibilitychange', visibility);
    return () => {
      checkpoint();
      window.removeEventListener('pagehide', checkpoint);
      document.removeEventListener('visibilitychange', visibility);
    };
  }, []);
  return <section className="player" aria-labelledby="lesson-title">
    <p className="eyebrow">YOUR LESSON</p><h2 id="lesson-title">{lesson.title}</h2>
    {!lesson.available ? <p role="alert">This video is missing. Ask your parent to restore its file and rescan the course.</p>
      : !lesson.playable ? <p role="alert">This video needs a format check or conversion before it can play. Ask your parent to follow the video conversion instructions in the README.</p>
      : <>
        <video ref={video} controls preload="metadata" src={`/api/lessons/${lesson.id}/video`}
          onLoadedMetadata={event => {
            const element = event.currentTarget;
            element.currentTime = Math.min(lesson.position, Number.isFinite(element.duration) ? element.duration : lesson.position);
          }}
          onTimeUpdate={event => {
            if (Date.now() - lastSave.current > 10000 && !event.currentTarget.paused)
              save(event.currentTarget.currentTime);
          }}
          onPause={event => { if (event.currentTarget.readyState >= 1) save(event.currentTarget.currentTime); }}
          onEnded={event => save(event.currentTarget.currentTime, true)}
          onError={() => setError('The video could not play. Ask your parent to check the original file or convert its format.')}>
          {lesson.caption_path && <track kind="subtitles" src={`/api/lessons/${lesson.id}/captions`} srcLang="en" label="Course subtitles" default/>}
          Your browser does not support video playback.
        </video>
        <div className="player-controls"><label htmlFor="speed">Playback speed </label>
          <select id="speed" value={speed} onChange={event => {
            setSpeed(event.target.value);
            if (video.current) video.current.playbackRate = Number(event.target.value);
          }}>{['0.75', '1', '1.25', '1.5', '2'].map(value => <option key={value} value={value}>{value}×</option>)}</select>
          <button className="secondary" onClick={() => {
            if (lesson.watched) {
              if (video.current) video.current.currentTime = 0;
              save(0, false);
            } else save(video.current?.currentTime ?? lesson.position, true);
          }}>
            {lesson.watched ? 'Mark as not watched' : 'I watched this lesson'}
          </button>
        </div>
        <p>{lesson.caption_path ? 'Use the captions button in the player for subtitles.' : 'This lesson has no matching subtitles.'}</p>
      </>}
    {error && <p role="alert">{error}</p>}<p role="status">{feedback}</p>
    <p className="muted">Watching is the first step. Practice what you learn in Unreal Engine; watched does not mean mastered.</p>
    <h3>Lesson resources</h3>
    {resources.length ? <ul>{resources.map(resource => <li key={resource.id}>
      <a href={`/api/resources/${resource.id}/download`}>{resource.relative_path}</a>
    </li>)}</ul> : <p>No resources matched to this lesson.</p>}
  </section>;
}

export function Library({ revision }: { revision: number }) {
  const [courses, setCourses] = useState<CourseSummary[]>([]);
  const [course, setCourse] = useState<Course | null>(null);
  const [lessonId, setLessonId] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const selection = useRef(0);
  useEffect(() => {
    let active = true;
    request('/api/courses').then(result => { if (active) { setCourses(result); setError(''); } })
      .catch(e => { if (active) setError(e.message); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [revision]);
  async function openCourse(id: string) {
    const generation = ++selection.current;
    setLoading(true); setError('');
    try {
      const result: Course = await request(`/api/courses/${id}`);
      if (generation !== selection.current) return;
      setCourse(result);
      const active = result.lessons.filter(l => l.available && l.playable);
      const continuing = active.filter(l => !l.watched && l.position > 0)
        .sort((a, b) => (b.updated_at ?? '').localeCompare(a.updated_at ?? ''))[0];
      setLessonId((continuing ?? active.find(l => !l.watched) ?? active[0] ?? result.lessons[0])?.id ?? null);
    } catch (e) { if (generation === selection.current) setError((e as Error).message); }
    finally { if (generation === selection.current) setLoading(false); }
  }
  function progress(id: string, position: number, watched: number) {
    setCourse(current => current ? { ...current, lessons: current.lessons.map(l => l.id === id ? { ...l, position, watched } : l) } : null);
  }
  const lesson = course?.lessons.find(l => l.id === lessonId);
  return <>
    {error && <p role="alert">{error}</p>}
    {loading && <p role="status">Loading your library…</p>}
    {!course ? <section><h2>Your learning library</h2>
      {!loading && !courses.length && <p>Your first course is on its way. Ask your parent to add it in Parent setup.</p>}
      <div className="course-grid">{courses.map(item => <article key={item.id}>
        <h3>{item.title}</h3><p>{item.lesson_count} lessons · {item.watched_count} watched</p>
        <button onClick={() => openCourse(item.id)}>{item.started_count ? 'Continue learning' : 'Start learning'}</button>
      </article>)}</div>
    </section> : <>
      <button className="secondary" onClick={() => { ++selection.current; setCourse(null); setLessonId(null); setLoading(false);
        request('/api/courses').then(setCourses).catch(e => setError(e.message)); }}>← All courses</button>
      <h2>{course.title}</h2>
      <div className="lesson-layout"><aside aria-label="Lessons"><h3>Lessons</h3>
        <ol>{course.lessons.map(item => <li key={item.id}><button className={item.id === lessonId ? 'lesson selected' : 'lesson'}
          aria-current={item.id === lessonId ? 'step' : undefined} onClick={() => setLessonId(item.id)}>
          {item.title}<small>{!item.available ? 'Missing file' : item.watched ? 'Watched' : item.position > 0 ? `Resume at ${minutes(item.position)}` : 'Ready to start'}
            {item.duration ? ` · ${minutes(item.duration)}` : ''}</small>
        </button></li>)}</ol>
      </aside>{lesson && <Player key={lesson.id} lesson={lesson}
        resources={course.resources.filter(resource => resource.lesson_id === lesson.id)} onProgress={progress}/>}</div>
      <section><h3>Course resources</h3><p>Shared resources are available to every lesson. Copy editable projects to your Projects folder before opening them in Unreal Engine.</p>
        {course.resources.filter(r => !r.lesson_id).length ? <ul>{course.resources.filter(r => !r.lesson_id).map(r => <li key={r.id}>
          <a href={`/api/resources/${r.id}/download`}>{r.relative_path}</a></li>)}</ul> : <p>No shared resources found.</p>}
      </section>
    </>}
  </>;
}

export function ParentImport({ onImported }: { onImported: () => void }) {
  const [folders, setFolders] = useState<string[]>([]);
  const [folder, setFolder] = useState('');
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [warnings, setWarnings] = useState<string[]>([]);
  async function refresh() {
    try {
      const result = await request('/api/library/folders');
      setFolders(result.folders); setFolder(current => result.folders.includes(current) ? current : result.folders[0] ?? '');
      setFeedback('');
    } catch (e) { setFeedback((e as Error).message); }
  }
  useEffect(() => { void refresh(); }, []);
  async function importCourse() {
    setBusy(true); setFeedback('Scanning files and checking video formats. Large courses can take a few minutes.'); setWarnings([]);
    try {
      const result = await request('/api/courses/import', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ folder }) });
      setFeedback(`Imported ${result.lessons} lessons. Open My learning to get started.`);
      setWarnings(result.warnings); onImported();
    } catch (e) { setFeedback((e as Error).message); }
    finally { setBusy(false); }
  }
  return <section><h2>Add a course</h2>
    <p>Copy your purchased lessons into one folder per course inside your configured Courses folder. Keep matching MP4 and SRT filenames together. Originals stay untouched.</p>
    <p className="muted">Set COURSES_DIR in .env and recreate the backend after changing the library location. See the README for Windows setup.</p>
    <label htmlFor="course-folder">Course folder</label><select id="course-folder" value={folder} onChange={e => setFolder(e.target.value)} disabled={busy}>
      {!folders.length && <option value="">No course folders found</option>}
      {folders.map(name => <option key={name}>{name}</option>)}
    </select><div className="actions"><button disabled={!folder || busy} onClick={importCourse}>{busy ? 'Importing…' : 'Import / rescan course'}</button>
      <button className="secondary" disabled={busy} onClick={refresh}>Refresh folders</button></div>
    <p role="status">{feedback}</p>{warnings.length > 0 && <><h3>Import notes</h3><ul>{warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul></>}
    <p>Rescanning updates the library without duplicating lessons. Removed files are marked missing; their saved progress is retained. If a video changes, review its watched state; rescanning never erases progress.</p>
  </section>;
}
