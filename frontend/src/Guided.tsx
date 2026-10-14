import { useEffect, useState, type FormEvent } from 'react';
import { request } from './api';

type XP = {total_xp:number;level:number;level_xp:number;xp_per_level:number;xp_to_next_level:number};
type Question = {id:string;section:string;prompt:string;options:string[];correct?:number;explanation?:string;hint:string;xp:number};
type Section = {id:string;title:string;start:number;end:number;objective:string;notes:string[];pause_prompt:string};
type Practice = {title:string;estimated_minutes:number;steps:string[];criteria:string[];troubleshooting:string[];xp:number};
type Document = {title:string;overview:string;prerequisites:string[];objectives:string[];corrections:string[];
  references:{title:string;url:string}[];sections:Section[];questions:Question[];practice:Practice};
type Submission = {id:string;guide_id:string;evidence:string;status:string;feedback:string};
type Guide = {id:string;status:string;document:Document;solved:string[];submission:Submission|null;xp:XP;source_error?:string|null};
const xpChanged = () => window.dispatchEvent(new Event('academy-xp'));
const time = (seconds:number) => `${Math.floor(seconds/60)}:${String(Math.floor(seconds%60)).padStart(2,'0')}`;

export function XPBar() {
  const [xp,setXP] = useState<XP|null>(null);
  const [error,setError] = useState('');
  useEffect(() => {
    const refresh = () => request('/api/xp').then(result => {setXP(result);setError('');}).catch(() => setError('XP is unavailable. Your saved awards have not been reset.'));
    void refresh(); window.addEventListener('academy-xp',refresh);
    return () => window.removeEventListener('academy-xp',refresh);
  },[]);
  return <div className="xp-bar" aria-label="Jaxon's level">{xp ? <>
    <strong>Level {xp.level}</strong><span>{xp.total_xp} XP total</span>
    <progress value={xp.level_xp} max={xp.xp_per_level} aria-label="Progress to next level"/>
    <span>{xp.xp_to_next_level} XP to Level {xp.level+1}</span>
  </> : <span>{error || 'Loading XP…'}</span>}</div>;
}

function Check({question,guideId,solved,onSaved}:{question:Question;guideId:string;solved:boolean;onSaved:()=>void}) {
  const [answer,setAnswer] = useState('');
  const [busy,setBusy] = useState(false);
  const [result,setResult] = useState<{correct:boolean;awarded_xp:number;explanation:string}|null>(null);
  const [error,setError] = useState('');
  async function submit(event:FormEvent) {
    event.preventDefault(); setBusy(true);setError('');
    try {
      const response = await request(`/api/guides/${guideId}/questions/${question.id}/answer`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answer})});
      setResult(response);onSaved();xpChanged();
    } catch(e) {setError((e as Error).message);} finally {setBusy(false);}
  }
  return <form className="knowledge-check" onSubmit={submit}><fieldset disabled={busy}>
    <legend>{question.prompt}</legend>
    <p className="muted">{solved ? 'Correct answer recorded · XP already earned' : `${question.xp} XP for understanding this check · awarded once`}</p>
    {question.options.map(option => <label className="answer-option" key={option}>
      <input type="radio" name={question.id} checked={answer===option} value={option} onChange={() => setAnswer(option)} required/>{option}
    </label>)}
    <button disabled={!answer || busy}>{busy ? 'Checking…' : solved ? 'Practice again · no extra XP' : 'Check my answer'}</button>
    <details><summary>Need a hint?</summary><p>{question.hint}</p></details>
  </fieldset>{result && <div role="status" className={result.correct ? 'answer-feedback correct' : 'answer-feedback'}>
    <strong>{result.correct ? result.awarded_xp ? `Correct! +${result.awarded_xp} XP` : 'Correct · XP was already awarded' : 'Not yet. Review the explanation and try again.'}</strong>
    <p>{result.explanation}</p>
  </div>}{error && <p role="alert">{error}</p>}</form>;
}

function PracticeTask({guide,onSaved}:{guide:Guide;onSaved:()=>void}) {
  const [prediction,setPrediction] = useState(''); const [observation,setObservation] = useState('');
  const [explanation,setExplanation] = useState(''); const [busy,setBusy] = useState(false);const [error,setError] = useState('');
  const task=guide.document.practice;const submission=guide.submission;
  async function submit(event:FormEvent) {
    event.preventDefault();setBusy(true);setError('');
    try {await request(`/api/guides/${guide.id}/practice`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prediction,observation,explanation})});onSaved();}
    catch(e) {setError((e as Error).message);}finally{setBusy(false);}
  }
  return <section><h3>{task.title}</h3><p>Optional hands-on challenge · about {task.estimated_minutes} minutes · {task.xp} XP after parent approval</p>
    <p>You can do this on another day. Quiz answers do not prove practical skill.</p>
    <ol>{task.steps.map(step => <li key={step}>{step}</li>)}</ol>
    <h4>What to show your parent</h4><ul>{task.criteria.map(item => <li key={item}>{item}</li>)}</ul>
    <details><summary>Something did not work?</summary><ul>{task.troubleshooting.map(item => <li key={item}>{item}</li>)}</ul></details>
    {submission && <div role="status"><strong>{submission.status === 'approved' ? 'Practice approved · XP earned once' : submission.status === 'pending' ? 'Waiting for parent review · no XP awarded yet' : 'Your parent asked for another attempt'}</strong><p>{submission.feedback}</p></div>}
    {(!submission || submission.status==='changes_requested') && <form onSubmit={submit}>
      <label htmlFor="prediction">What did you predict would happen?</label><textarea id="prediction" minLength={20} maxLength={2000} required value={prediction} onChange={e=>setPrediction(e.target.value)}/>
      <label htmlFor="observation">What actually happened in Unreal Engine?</label><textarea id="observation" minLength={20} maxLength={2000} required value={observation} onChange={e=>setObservation(e.target.value)}/>
      <label htmlFor="explanation">Why did it happen? Explain a setting or relationship.</label><textarea id="explanation" minLength={20} maxLength={2000} required value={explanation} onChange={e=>setExplanation(e.target.value)}/>
      <p>Show the actual editor or a locally saved screenshot to your parent. Writing an answer alone does not complete the practical challenge.</p>
      <button disabled={busy}>{busy?'Sending…':'Ask my parent to review'}</button>
    </form>}{error&&<p role="alert">{error}</p>}
  </section>;
}

export function GuidedLesson({lessonId,onSeek}:{lessonId:string;onSeek:(seconds:number)=>void}) {
  const [guide,setGuide]=useState<Guide|null>(null);const [error,setError]=useState('');
  async function refresh(){try{setGuide(await request(`/api/lessons/${lessonId}/guide`));setError('');}catch(e){setError((e as Error).message);}}
  useEffect(()=>{void refresh();},[lessonId]);
  if(error)return <p role="alert">Guided lesson unavailable: {error}</p>;
  if(!guide)return null;
  const doc=guide.document;
  return <div className="guided-lesson"><h2>{doc.title}</h2><p>{doc.overview}</p>
    <p className="mission-progress">{guide.solved.length}/{doc.questions.length} checks answered correctly · {doc.questions.reduce((sum,q)=>sum+q.xp,0)} quiz XP available in total</p>
    <details><summary>Before you start · navigation warm-up</summary><ul>{doc.prerequisites.map(item=><li key={item}>{item}</li>)}</ul></details>
    <h3>Your goals</h3><ul>{doc.objectives.map(item=><li key={item}>{item}</li>)}</ul>
    <p>Watch a section, pause, explain the idea, then answer its checks. Hints and retries are welcome. Watching or replaying does not earn XP.</p>
    {doc.sections.map((section,index)=><details className="guide-section" key={section.id} open={index===0?true:undefined}>
      <summary>{section.title} · {time(section.start)}–{time(section.end)}</summary>
      <p><strong>Goal:</strong> {section.objective}</p><button className="secondary" onClick={()=>onSeek(section.start)}>Watch from {time(section.start)}</button>
      <ul>{section.notes.map(note=><li key={note}>{note}</li>)}</ul><p className="pause-prompt">Pause and think: {section.pause_prompt}</p>
      {doc.questions.filter(q=>q.section===section.id).map(q=><Check key={q.id} question={q} guideId={guide.id} solved={guide.solved.includes(q.id)} onSaved={refresh}/>)}</details>)}
    <PracticeTask guide={guide} onSaved={refresh}/>
    <details><summary>Video wording and UE5 notes</summary><ul>{doc.corrections.map(item=><li key={item}>{item}</li>)}</ul>
      {doc.references.map(ref=><p key={ref.url}><a href={ref.url} target="_blank" rel="noreferrer">{ref.title}</a> (optional online reference)</p>)}</details>
    <p className="muted">Watched, correct knowledge checks, and parent-approved practice are separate records. Your level is a progress marker, not a mastery certificate.</p>
  </div>;
}

function ReviewWork({submission,guide,onSaved}:{submission:Submission;guide:Guide|undefined;onSaved:()=>void}) {
  const [feedback,setFeedback]=useState('');const [confirmed,setConfirmed]=useState<string[]>([]);const [error,setError]=useState('');const [busy,setBusy]=useState(false);
  const evidence=JSON.parse(submission.evidence) as Record<string,string>;
  async function review(decision:string) {
    setBusy(true);setError('');try{await request(`/api/parent/submissions/${submission.id}/review`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({decision,feedback})});onSaved();xpChanged();}
    catch(e){setError((e as Error).message);}finally{setBusy(false);}
  }
  const criteria=guide?.document.practice.criteria ?? [];
  return <article><h4>{guide?.document.practice.title ?? 'Practice submission'} · {submission.status}</h4>
    {Object.entries(evidence).map(([key,value])=><p key={key}><strong>{key}:</strong> {value}</p>)}
    {submission.feedback&&<p>Parent feedback: {submission.feedback}</p>}
    {submission.status==='pending'&&<>
      <p>Inspect the actual project or local screenshots together. Confirm each criterion you observed before approving.</p>
      {criteria.map(item=><label key={item} className="answer-option"><input type="checkbox" checked={confirmed.includes(item)} onChange={e=>setConfirmed(current=>e.target.checked?[...current,item]:current.filter(c=>c!==item))}/>{item}</label>)}
      <label htmlFor={`feedback-${submission.id}`}>Constructive feedback</label><textarea id={`feedback-${submission.id}`} value={feedback} onChange={e=>setFeedback(e.target.value)} minLength={5} maxLength={2000}/>
      <div className="actions"><button disabled={busy||feedback.trim().length<5||!criteria.length||confirmed.length!==criteria.length} onClick={()=>review('approved')}>Approve practical work · {guide?.document.practice.xp} XP</button>
        <button className="secondary" disabled={busy||feedback.trim().length<5} onClick={()=>review('changes_requested')}>Request another attempt</button></div></>}
    {error&&<p role="alert">{error}</p>}
  </article>;
}

export function ParentGuidedLessons() {
  const [guides,setGuides]=useState<Guide[]>([]);const [submissions,setSubmissions]=useState<Submission[]>([]);const [error,setError]=useState('');const [busy,setBusy]=useState(false);
  async function refresh(){try{const [g,s]=await Promise.all([request('/api/parent/guides'),request('/api/parent/submissions')]);setGuides(g);setSubmissions(s);}catch(e){setError((e as Error).message);}}
  useEffect(()=>{void refresh();},[]);
  async function publish(id:string){setBusy(true);try{await request(`/api/parent/guides/${id}/publish`,{method:'POST'});await refresh();}catch(e){setError((e as Error).message);}finally{setBusy(false);}}
  return <section><h2>Guided lessons · parent review</h2><p>Review the objectives, explanations, answer key and practical criteria before publishing a draft for Jaxon. Nothing earns XP until it is published and answered or approved.</p>
    {error&&<p role="alert">{error}</p>}{guides.map(guide=><article key={guide.id}><h3>{guide.document.title} · {guide.status}</h3><p>{guide.document.overview}</p>
      {guide.source_error&&<p role="alert">{guide.source_error}</p>}
      <details><summary>Review the full lesson and answer key</summary>
        <h4>Prerequisites</h4><ul>{guide.document.prerequisites.map(item=><li key={item}>{item}</li>)}</ul>
        <h4>Objectives</h4><ul>{guide.document.objectives.map(item=><li key={item}>{item}</li>)}</ul>
        {guide.document.sections.map(section=><div key={section.id}><h4>{section.title} · {time(section.start)}–{time(section.end)}</h4><p>{section.objective}</p><ul>{section.notes.map(note=><li key={note}>{note}</li>)}</ul><p>{section.pause_prompt}</p>
          {guide.document.questions.filter(q=>q.section===section.id).map(q=><div className="knowledge-check" key={q.id}><strong>{q.prompt}</strong><ul>{q.options.map((option,index)=><li key={option}>{option}{index===q.correct?' ✓ correct':''}</li>)}</ul><p>{q.explanation}</p><p>Hint: {q.hint}</p><p>{q.xp} XP · once</p></div>)}</div>)}
        <h4>Practical exercise · {guide.document.practice.xp} XP after approval</h4><ol>{guide.document.practice.steps.map(step=><li key={step}>{step}</li>)}</ol>
        <ul>{guide.document.practice.criteria.map(item=><li key={item}>{item}</li>)}</ul><h4>Corrections and caveats</h4><ul>{guide.document.corrections.map(item=><li key={item}>{item}</li>)}</ul>
        {guide.document.references.map(ref=><p key={ref.url}><a href={ref.url} target="_blank" rel="noreferrer">{ref.title}</a></p>)}
      </details>
      {guide.status==='draft'&&<button disabled={busy||!!guide.source_error} onClick={()=>publish(guide.id)}>Approve lesson for Jaxon</button>}
    </article>)}
    <h3>Practical work awaiting feedback</h3>{submissions.length?submissions.map(s=><ReviewWork key={s.id} submission={s} guide={guides.find(g=>g.id===s.guide_id)} onSaved={refresh}/>):<p>No submissions yet.</p>}
    <p className="muted">Parent setup is not password protected; anyone using this local app can access it.</p>
  </section>;
}
