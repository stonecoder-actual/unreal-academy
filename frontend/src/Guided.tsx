import { useEffect, useState, type FormEvent } from 'react';
import { request } from './api';
import { Icon, Meter } from './UI';

type XP = {total_xp:number;level:number;level_xp:number;xp_per_level:number;xp_to_next_level:number};
type Question = {id:string;section:string;prompt:string;options:string[];correct?:number;explanation?:string;hint:string;xp:number};
type Section = {id:string;title:string;start:number|null;end:number|null;objective:string;notes:string[];pause_prompt:string};
type Practice = {kind?:'build'|'reflection';title:string;estimated_minutes:number;steps:string[];criteria:string[];troubleshooting:string[];xp:number};
type Document = {lesson_id:string;title:string;overview:string;prerequisites:string[];objectives:string[];corrections:string[];
  references:{title:string;url:string}[];sections:Section[];questions:Question[];practice:Practice|null};
type Submission = {id:string;guide_id:string;evidence:string;status:string;feedback:string};
type Guide = {id:string;status:string;document:Document;solved:string[];submission:Submission|null;xp:XP;source_error?:string|null};
const xpChanged = () => window.dispatchEvent(new Event('academy-xp'));
const time = (seconds:number) => `${Math.floor(seconds/60)}:${String(Math.floor(seconds%60)).padStart(2,'0')}`;

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

function PracticeTask({guide}:{guide:Guide}) {
  const task=guide.document.practice!;
  return <section className="practice-task"><p className="eyebrow">OPTIONAL / TRY IT YOURSELF</p><h3>{task.title}</h3>
    <p>About {task.estimated_minutes} minutes. Try this whenever you like, and show your progress to your parent if you want.</p>
    <p>Your quiz completes the mission. This activity needs no written submission or approval and awards no extra XP.</p>
    <ol>{task.steps.map(step=><li key={step}>{step}</li>)}</ol>
    <h4>Things to look for</h4><ul>{task.criteria.map(item=><li key={item}>{item}</li>)}</ul>
    <details><summary>Something did not work?</summary><ul>{task.troubleshooting.map(item=><li key={item}>{item}</li>)}</ul></details>
    {guide.submission?.status==='approved'&&<p className="muted">Previously reviewed activity · your earned XP is saved.</p>}
  </section>;
}

export function GuidedLesson({lessonId,onSeek,externalUrl,showPending=false}:{lessonId:string;onSeek:(seconds:number)=>void;externalUrl?:string;showPending?:boolean}) {
  const [guide,setGuide]=useState<Guide|null>(null);const [error,setError]=useState('');
  const [loading,setLoading]=useState(true);
  async function refresh(){try{setGuide(await request(`/api/lessons/${lessonId}/guide`));setError('');}catch(e){setError((e as Error).message);}finally{setLoading(false);}}
  useEffect(()=>{void refresh();},[lessonId]);
  if(error)return <p role="alert">Guided lesson unavailable: {error}</p>;
  if(loading)return <p role="status" className="loading-state">Checking for a guided mission…</p>;
  if(!guide)return showPending?<div className="empty-state"><Icon name="book"/><h3>Personalized mission coming soon</h3><p>This lesson has no personalized mission yet. You can watch on Udemy now and return for knowledge checks when they are added.</p></div>:null;
  const doc=guide.document;
  
  return <div className="guided-lesson"><p className="eyebrow">YOUR GUIDED MISSION</p><h2>{doc.title.replace(/^Mission:\s*/,'')}</h2><p>{doc.overview}</p>
    <ol className="learning-steps" aria-label="How a guided mission works"><li><Icon name="play"/><span><strong>01 · Watch</strong><small>Explore the idea</small></span></li><li><Icon name="book"/><span><strong>02 · Read</strong><small>Review the key ideas</small></span></li><li><Icon name="check"/><span><strong>03 · Quiz</strong><small>Automatic feedback & XP</small></span></li></ol>
    <div className="mission-progress"><div><strong>{guide.solved.length} of {doc.questions.length} checks solved</strong><span><Icon name="spark" size={15}/>{doc.questions.reduce((sum,q)=>sum+q.xp,0)} quiz XP total</span></div><Meter value={guide.solved.length} max={doc.questions.length} label="Guided mission checks solved"/></div>
    {guide.solved.length===doc.questions.length&&<div className="answer-feedback correct" role="status"><strong>Mission complete! All checks solved.</strong><p>You can keep learning now. Try the optional activity or show your parent your progress whenever you like.</p></div>}
    <details><summary>Before you start · what you need</summary><ul>{doc.prerequisites.map(item=><li key={item}>{item}</li>)}</ul></details>
    <h3>Your goals</h3><ul>{doc.objectives.map(item=><li key={item}>{item}</li>)}</ul>
    <p>Read the key ideas and answer the knowledge checks. Answers are checked automatically. Hints and retries are welcome. Watching or replaying does not earn XP.</p>
    {doc.sections.map((section,index)=><details className="guide-section" key={section.id} open={index===0?true:undefined}>
      <summary><span>{section.title}</span><small>{section.start!==null&&section.end!==null?`${time(section.start)}–${time(section.end)} · `:''}{doc.questions.some(q=>q.section===section.id)?`${doc.questions.filter(q=>q.section===section.id&&guide.solved.includes(q.id)).length}/${doc.questions.filter(q=>q.section===section.id).length} checks`:'Discuss'}</small></summary>
      <p><strong>Goal:</strong> {section.objective}</p>{(externalUrl?<a href={externalUrl} target="_blank" rel="noopener noreferrer">Revisit this lesson on Udemy ↗</a>:section.start!==null&&<button className="secondary" onClick={()=>onSeek(section.start!)}>Watch from {time(section.start)}</button>)}
      <ul>{section.notes.map(note=><li key={note}>{note}</li>)}</ul><p className="pause-prompt">Pause and think: {section.pause_prompt}</p>
      {doc.questions.filter(q=>q.section===section.id).map(q=><Check key={q.id} question={q} guideId={guide.id} solved={guide.solved.includes(q.id)} onSaved={refresh}/>)}</details>)}
    {doc.practice?<PracticeTask guide={guide}/>:<section className="practice-task"><p className="eyebrow">OPTIONAL / SHOW YOUR PROGRESS</p><h3>Share whenever you like</h3><p>You can show your parent your quiz results or a game idea later. There is no written answer, submission or approval to wait for, and this optional step earns no extra XP.</p></section>}
    <details><summary>Lesson notes & adaptations</summary><ul>{doc.corrections.map(item=><li key={item}>{item}</li>)}</ul>
      {doc.references.map(ref=><p key={ref.url}><a href={ref.url} target="_blank" rel="noreferrer">{ref.title}</a> (optional online reference)</p>)}</details>
    <p className="muted">Watching and correct knowledge checks are saved separately. Optional practice helps you try the ideas in Unreal Engine. Your level is a progress marker, not a mastery certificate.</p>
  </div>;
}
