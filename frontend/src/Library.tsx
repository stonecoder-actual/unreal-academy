import { useEffect, useRef, useState } from 'react';
import { request } from './api';
import { LessonNotes } from './LessonNotes';
import { CourseArt, Difficulty, Icon, Meter, coursePresentation } from './UI';
import { Evidence } from './Progress';

type Lesson = {
  id: string; title: string; relative_path: string; position: number;
  duration: number | null; playable: number; available: number; watched: number;
  caption_path: string | null; updated_at: string | null;
  external_url?: string | null; item_kind?: 'video'|'article'|'quiz'; section_title?: string|null;
  transcript_status?: 'captured'|'pending'|'not_applicable';
};
type Resource = { id: string; relative_path: string; lesson_id: string | null };
type CourseSummary = { id: string; title: string; folder: string; source_type?:string; difficulty?:string; lesson_count: number; watched_count: number; started_count: number };
type Course = { id: string; title: string; source_type?:string; lessons: Lesson[]; resources: Resource[] };

function minutes(seconds: number) {
  return `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
}

function Player({ lesson, resources, onProgress, checkpoint, index, total, onNext }: {
  lesson: Lesson; resources: Resource[];
  onProgress: (id: string, position: number, watched: number) => void;
  checkpoint: React.MutableRefObject<(() => Promise<unknown>) | null>;
  index:number;total:number;onNext:(()=>void)|null;
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
  checkpoint.current = () => {
    if (video.current && video.current.readyState >= 1) saveRef.current(video.current.currentTime);
    return queue.current;
  };
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
    <div className="lesson-heading"><p className="eyebrow">LESSON {index} OF {total}</p><span className={`pill ${lesson.watched?'watched-pill':''}`}><Icon name={lesson.watched?'check':'play'} size={14}/>{lesson.watched?lesson.external_url?'COMPLETED HERE':'VIDEO WATCHED':'WATCH & EXPLORE'}</span></div><h2 id="lesson-title" tabIndex={-1}>{lesson.title}</h2>
    {lesson.external_url ? <div className="external-lesson">
      <p className="eyebrow">{lesson.item_kind==='video'?'WATCH ON UDEMY':lesson.item_kind==='quiz'?'UDEMY COURSE QUIZ':'UDEMY READING & RESOURCES'}</p>
      <h3>Your lesson opens in a new tab.</h3><p>Keep Unreal Academy open. When you return, follow the instructor’s activities in Unreal Engine, then review the key takeaways and answer the questions below.</p>
      <a className="button-link" href={lesson.external_url} target="_blank" rel="noopener noreferrer">{lesson.item_kind==='video'?'Watch on Udemy':'Open on Udemy'} <Icon name="arrow"/></a>
      <p className="muted">Udemy needs an internet connection and your signed-in purchased course. Playback and Udemy completion do not sync here.</p>
      <button className="secondary" onClick={()=>save(0,!lesson.watched)}>{lesson.watched?'Undo completed state':lesson.item_kind==='video'?'I watched this lesson':'I completed this item on Udemy'}</button>
      {lesson.item_kind!=='video'&&<p>Complete this reading or quiz on Udemy.</p>}
      <p>Opening the link or marking it complete earns no XP. Correct knowledge checks earn XP once. Follow Udemy for the practical work.</p>
    </div> : !lesson.available ? <p role="alert">This video is missing. Ask your parent to restore its file and rescan the course.</p>
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
    {!lesson.external_url&&<p className="muted">Watching is the first step. Practice what you learn in Unreal Engine; watched does not mean mastered.</p>}
    <details className="resource-drawer"><summary>Lesson resources <span className="count-badge">{resources.length}</span></summary>
    {resources.length ? <ul>{resources.map(resource => <li key={resource.id}>
      <a href={`/api/resources/${resource.id}/download`}>{resource.relative_path}</a>
    </li>)}</ul> : <p>{lesson.external_url?'Find any lesson resources in Udemy’s Resources menu.':'No extra files are needed from this lesson\'s resource list.'}</p>}</details>
    <LessonNotes lessonId={lesson.id} showPending={!!lesson.external_url&&lesson.item_kind==='video'}/>
    {onNext&&<div className="next-lesson"><div><p className="eyebrow">WHEN YOU'RE READY</p><p>Take your time. Your progress is saved here.</p></div><button className="secondary" onClick={onNext}>{lesson.external_url?'Next lesson':'Next video'}<Icon name="arrow"/></button></div>}
  </section>;
}

export function Library({ revision, home=false, welcome='' }: { revision: number; home?:boolean; welcome?:string }) {
  const [courses, setCourses] = useState<CourseSummary[]>([]);
  const [guides,setGuides] = useState<{lesson_id:string;course_id:string}[]>([]);
  const [course, setCourse] = useState<Course | null>(null);
  const [lessonId, setLessonId] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const selection = useRef(0);
  const checkpoint = useRef<(() => Promise<unknown>) | null>(null);
  const remembered = useRef<Record<string,string>>({});
  const [search,setSearch]=useState('');
  const [filter,setFilter]=useState('All courses');
  const [lessonSearch,setLessonSearch]=useState('');
  const [progressRevision,setProgressRevision]=useState(0);
  useEffect(()=>{const refresh=()=>setProgressRevision(n=>n+1);window.addEventListener('academy-xp',refresh);return()=>window.removeEventListener('academy-xp',refresh);},[]);
  useEffect(() => {
    let active = true;
    request('/api/guided-lessons').then(result=>{if(active)setGuides(result);}).catch(e=>{if(active)setError(e.message);});
    request('/api/courses').then(result => { if (active) { setCourses(result); setError(''); } })
      .catch(e => { if (active) setError(e.message); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [revision,progressRevision]);
  useEffect(()=>{if(course){document.getElementById('course-title-heading')?.focus();window.scrollTo({top:0});}},[course?.id]);
  useEffect(()=>{if(lessonId)document.getElementById('lesson-title')?.focus();},[lessonId]);
  async function openCourse(id: string) {
    const generation = ++selection.current;
    if (course && lessonId) remembered.current[course.id] = lessonId;
    setLoading(true); setError('');
    try {
      await checkpoint.current?.();
      if (generation !== selection.current) return;
      checkpoint.current = null; setCourse(null); setLessonId(null);
      const result: Course = await request(`/api/courses/${id}`);
      if (generation !== selection.current) return;
      setCourse(result);
      setLessonSearch('');
      const active = result.lessons.filter(l => l.available && l.playable);
      const continuing = active.filter(l => !l.watched && l.position > 0)
        .sort((a, b) => (b.updated_at ?? '').localeCompare(a.updated_at ?? ''))[0];
      const rememberedId = result.lessons.find(l=>l.id === remembered.current[id])?.id;
      setLessonId(rememberedId ?? (continuing ?? active.find(l => !l.watched) ?? active[0] ?? result.lessons[0])?.id ?? null);
    } catch (e) { if (generation === selection.current) setError((e as Error).message); }
    finally { if (generation === selection.current) setLoading(false); }
  }
  function progress(id: string, position: number, watched: number) {
    setCourse(current => current ? { ...current, lessons: current.lessons.map(l => l.id === id ? { ...l, position, watched } : l) } : null);
  }
  const lesson = course?.lessons.find(l => l.id === lessonId);
  const featured=courses.find(c=>c.source_type==='udemy')??courses[0];
  const visibleCourses=courses.filter(c=>c.title.toLowerCase().includes(search.toLowerCase()) && (filter==='All courses'||(c.difficulty??coursePresentation(c.folder).difficulty)===filter));
  async function closeCourse(){
    ++selection.current;
    if(course&&lessonId)remembered.current[course.id]=lessonId;
    await checkpoint.current?.();checkpoint.current=null;setCourse(null);setLessonId(null);setLoading(false);
    request('/api/courses').then(setCourses).catch(e=>setError(e.message));
  }
  const groupedLessons = new Map<string,Lesson[]>();
  course?.lessons.filter(l=>l.title.toLowerCase().includes(lessonSearch.toLowerCase())).forEach(l=>{
    const group=l.section_title??(l.relative_path.includes('/')?l.relative_path.split('/').slice(0,-1).join(' / '):'Course lessons');
    groupedLessons.set(group,[...(groupedLessons.get(group)??[]),l]);
  });
  return <>
    {error && <p role="alert">{error}</p>}
    {loading && <p role="status">Loading your library…</p>}
    {!course ? <>
      <header className="page-heading"><p className="eyebrow">{home?'YOUR NEXT GREAT IDEA STARTS HERE':'EXPLORE. LEARN. CREATE.'}</p><h1>{home?'Welcome back, Jaxon.':'Your course library.'}</h1><p>{home?(welcome||'A little curiosity. A new skill. A world of possibilities.'):'Choose your next adventure in game development.'}</p></header>
      {home&&<>
        <section className="mission-hero"><div className="mission-copy"><span className="pill"><Icon name="play" size={16}/>{featured?.source_type==='udemy'?'START HERE · UDEMY':'YOUR NEXT LESSON'}</span>
          <h2>{featured?.title??'Your next step in Unreal Engine'}</h2>
          <p>Watch the lesson and follow along with the instructor in Unreal Engine. Come back here for key takeaways and a short knowledge check.</p>
          {featured&&<button disabled={loading} onClick={()=>openCourse(featured.id)}>{featured.source_type==='udemy'?featured.started_count?'Continue Udemy course':'Start Udemy course':featured.started_count?'Continue learning':'Start learning'}<Icon name="arrow"/></button>}
        </div><CourseArt hero/></section>
        <Evidence/>
      </>}
      <section className="library-section"><div className="section-heading"><div><p className="eyebrow">BUILD YOUR SKILLS</p><h2>{home?'Your learning library':'All courses'}</h2></div><span className="muted">{courses.length} courses in your library</span></div>
      {!home&&<div className="library-tools"><div><label className="sr-only" htmlFor="course-search">Search courses</label><input id="course-search" type="search" placeholder="Find a course…" value={search} onChange={e=>setSearch(e.target.value)}/></div><div><label className="sr-only" htmlFor="difficulty-filter">Filter by difficulty</label><select id="difficulty-filter" value={filter} onChange={e=>setFilter(e.target.value)}>{['All courses','Beginner','Intermediate'].map(f=><option key={f}>{f}</option>)}</select></div></div>}
      {!loading && !courses.length && <p>Your first course is on its way. Ask your parent to add it in Parent setup.</p>}
      <div className="course-grid">{visibleCourses.map(item => {
        const guided = guides.find(g => g.course_id === item.id);
        const presentation=coursePresentation(item.folder);
        const difficulty=item.difficulty??presentation.difficulty;
        const theme=item.source_type==='udemy'?'teal':presentation.theme;
        const category=item.source_type==='udemy'?'UDEMY · BLUEPRINT GAME DEVELOPMENT':presentation.category;
        const status = item.lesson_count > 0 && item.watched_count === item.lesson_count
          ? 'All videos watched' : item.started_count ? 'In progress' : 'Ready to start';
        return <article className="course-card" key={item.id} aria-labelledby={`course-${item.id}`}>
          <CourseArt theme={theme}/><div className="course-card-body">
          <div className="course-card-badges">
            <Difficulty level={difficulty}/><span className="course-status">{status}</span>
          </div>
          <p className="course-category">{category}</p>
          <h3 id={`course-${item.id}`}>{item.title}</h3>
          <div className="course-card-details">
            <p className="course-count"><Icon name="play" size={14}/>{item.lesson_count} {item.source_type==='udemy'?'curriculum items · online':'video lessons'}</p>
            <p className="course-guidance">{guided?'Key takeaways & knowledge checks':item.source_type==='udemy'?'Follow the instructor on Udemy':'Learn at your own pace'}</p>
            <div className="course-watch-progress">
              <p>{item.watched_count} of {item.lesson_count} {item.source_type==='udemy'?'items completed':'videos watched'}</p>
              <progress max={Math.max(1, item.lesson_count)} value={item.watched_count}
                aria-label={`${item.source_type==='udemy'?'Items completed':'Videos watched'} in ${item.title}`}/>
            </div>
          </div>
          <button disabled={loading} onClick={() => openCourse(item.id)}>
            {item.started_count ? 'Continue learning' : 'Start learning'}<Icon name="arrow" size={18}/>
          </button></div>
        </article>;
      })}</div>
      {!loading&&courses.length>0&&!visibleCourses.length&&<div className="empty-state"><Icon name="library"/><h3>No courses found</h3><p>Try another name or difficulty.</p><button className="secondary" onClick={()=>{setSearch('');setFilter('All courses');}}>Clear filters</button></div>}
    </section></> : <>
      <button className="text-button" onClick={()=>void closeCourse()}><Icon name="back"/>All courses</button>
      <header className="course-heading"><p className="eyebrow">YOUR LEARNING WORKSPACE</p><h1 id="course-title-heading" tabIndex={-1}>{course.title}</h1><p>{course.lessons.filter(l=>l.available&&l.watched).length} of {course.lessons.filter(l=>l.available).length} {course.source_type==='udemy'?'items completed here · Videos open on Udemy':'videos watched · Choose a lesson below'}</p></header>
      <div className="lesson-layout"><aside className="lesson-sidebar" aria-label="Lessons"><div className="section-heading"><h2>Course content</h2><span className="count-badge">{course.lessons.length}</span></div>
        <label className="sr-only" htmlFor="lesson-search">Find a lesson</label><input id="lesson-search" type="search" value={lessonSearch} onChange={e=>setLessonSearch(e.target.value)} placeholder="Find a lesson…"/>
        <div className="lesson-groups">{Array.from(groupedLessons,([group,items])=><details key={group} className="lesson-group" open={!!lessonSearch||items.some(l=>l.id===lessonId)||groupedLessons.size===1}><summary>{group}<span>{items.length}</span></summary><ol>{items.map(item => <li key={item.id}><button className={item.id === lessonId ? 'lesson selected' : 'lesson'}
          aria-current={item.id === lessonId ? 'step' : undefined} onClick={() => setLessonId(item.id)}>
          <span className="lesson-state"><Icon name={item.watched?'check':'play'} size={15}/></span><span>{item.title}<small>{!item.available ? 'Missing file' : item.watched ? item.external_url?'Completed here':'Watched' : item.external_url?`${item.item_kind==='video'?'Video':item.item_kind==='quiz'?'Quiz':'Reading'} · Udemy`:item.position > 0 ? `Resume at ${minutes(item.position)}` : 'Ready to start'}
            {item.duration ? ` · ${minutes(item.duration)}` : ''}</small>
          </span></button></li>)}</ol></details>)}</div>{!groupedLessons.size&&<p>No lessons match your search.</p>}
      </aside>{lesson && <Player key={lesson.id} lesson={lesson}
        resources={course.resources.filter(resource => resource.lesson_id === lesson.id)} onProgress={progress} checkpoint={checkpoint}
        index={course.lessons.findIndex(l=>l.id===lesson.id)+1} total={course.lessons.length}
        onNext={course.lessons.slice(course.lessons.findIndex(l=>l.id===lesson.id)+1).find(l=>l.available&&l.playable)?async()=>{await checkpoint.current?.();setLessonId(course.lessons.slice(course.lessons.findIndex(l=>l.id===lesson.id)+1).find(l=>l.available&&l.playable)!.id);}:null}/>}</div>
      <section><h3>Course resources</h3><p>{course.source_type==='udemy'?'Open Udemy to access course resources. Copy editable projects to your own Projects folder before opening them in Unreal Engine.':'Shared resources are available to every lesson. Copy editable projects to your Projects folder before opening them in Unreal Engine.'}</p>
        {course.resources.filter(r => !r.lesson_id).length ? <ul>{course.resources.filter(r => !r.lesson_id).map(r => <li key={r.id}>
          <a href={`/api/resources/${r.id}/download`}>{r.relative_path}</a></li>)}</ul> : <p>No shared resources found.</p>}
        </section>
    </>}
  </>;
}

export function ParentImport({ onImported }: { onImported: () => void }) {
  const [folders, setFolders] = useState<string[]>([]);
  const [folder, setFolder] = useState('');
  const [title, setTitle] = useState('');
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
      const result = await request('/api/courses/import', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ folder, ...(title.trim() ? {title:title.trim()} : {}) }) });
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
    </select>
    <label htmlFor="course-title">Course name (optional; leave blank to keep the existing name)</label>
    <input id="course-title" value={title} maxLength={200} disabled={busy} onChange={e=>setTitle(e.target.value)}/>
    <div className="actions"><button disabled={!folder || busy} onClick={importCourse}>{busy ? 'Importing…' : 'Import / rescan course'}</button>
      <button className="secondary" disabled={busy} onClick={refresh}>Refresh folders</button></div>
    <p role="status">{feedback}</p>{warnings.length > 0 && <><h3>Import notes</h3><ul>{warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul></>}
    <p>Rescanning updates the library without duplicating lessons. Removed files are marked missing; their saved progress is retained. If a video changes, review its watched state; rescanning never erases progress.</p>
  </section>;
}
