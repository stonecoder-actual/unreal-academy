import { useEffect, useState, type FormEvent } from 'react';
import { request } from './api';
import { Icon, Meter } from './UI';

type Question = {id:string;prompt:string;options:string[];hint:string;xp:number};
type Notes = {id:string;solved:string[];document:{takeaways?:string[];sections:{notes:string[]}[];questions:Question[]}};

function KnowledgeCheck({question,reviewId,solved,onSaved}:{question:Question;reviewId:string;solved:boolean;onSaved:()=>void}) {
  const [answer,setAnswer] = useState('');
  const [busy,setBusy] = useState(false);
  const [result,setResult] = useState<{correct:boolean;awarded_xp:number;explanation:string}|null>(null);
  const [error,setError] = useState('');
  async function submit(event:FormEvent) {
    event.preventDefault();setBusy(true);setError('');
    try {
      const response = await request(`/api/guides/${reviewId}/questions/${question.id}/answer`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answer})});
      setResult(response);onSaved();window.dispatchEvent(new Event('academy-xp'));
    } catch(e) {setError((e as Error).message);} finally {setBusy(false);}
  }
  return <form className="knowledge-check" onSubmit={submit}><fieldset disabled={busy}>
    <legend>{question.prompt}</legend>
    <p className="muted">{solved?'Correct answer saved · XP already earned':`${question.xp} XP for your first correct answer`}</p>
    {question.options.map(option=><label className="answer-option" key={option}>
      <input type="radio" name={question.id} checked={answer===option} value={option} onChange={()=>setAnswer(option)} required/>{option}
    </label>)}
    <button disabled={!answer||busy}>{busy?'Checking…':solved?'Try again · no extra XP':'Check my answer'}</button>
    <details><summary>Need a hint?</summary><p>{question.hint}</p></details>
  </fieldset>{result&&<div role="status" className={result.correct?'answer-feedback correct':'answer-feedback'}>
    <strong>{result.correct?result.awarded_xp?`Correct! +${result.awarded_xp} XP`:'Correct · XP was already awarded':'Not yet. Read the explanation and try again.'}</strong>
    <p>{result.explanation}</p>
  </div>}{error&&<p role="alert">{error}</p>}</form>;
}

export function LessonNotes({lessonId,showPending=false}:{lessonId:string;showPending?:boolean}) {
  const [notes,setNotes]=useState<Notes|null>(null);
  const [error,setError]=useState('');
  const [loading,setLoading]=useState(true);
  async function refresh(){
    try{setNotes(await request(`/api/lessons/${lessonId}/guide`));setError('');}
    catch(e){setError((e as Error).message);}finally{setLoading(false);}
  }
  useEffect(()=>{void refresh();},[lessonId]);
  if(error)return <p role="alert">Lesson notes unavailable: {error}</p>;
  if(loading)return <p role="status">Loading lesson takeaways and questions…</p>;
  if(!notes)return showPending?<div className="empty-state"><Icon name="book"/><h3>Lesson notes coming soon</h3><p>Key takeaways and knowledge checks are still being prepared for this video. You can watch on Udemy and follow the instructor in Unreal Engine now.</p></div>:null;
  // Existing local-course notes stay readable without rewriting historical content.
  const takeaways=notes.document.takeaways?.length?notes.document.takeaways:[...new Set(notes.document.sections.flatMap(section=>section.notes))];
  const questions=notes.document.questions;
  return <div className="lesson-notes">
    <section aria-labelledby="takeaways-heading"><p className="eyebrow">AFTER WATCHING</p><h2 id="takeaways-heading">Key takeaways</h2>
      <ul className="key-takeaways">{takeaways.map(note=><li key={note}>{note}</li>)}</ul>
    </section>
    <section aria-labelledby="checks-heading"><h2 id="checks-heading">Knowledge check</h2>
      <p>Answer the questions below. Hints and retries are welcome; correct answers earn XP once.</p>
      <div className="mission-progress"><div><strong>{notes.solved.length} of {questions.length} correct</strong><span><Icon name="spark" size={15}/>{questions.reduce((sum,q)=>sum+q.xp,0)} XP total</span></div><Meter value={notes.solved.length} max={questions.length} label="Knowledge checks answered correctly"/></div>
      {notes.solved.length===questions.length&&<div className="answer-feedback correct" role="status"><strong>Knowledge check complete!</strong><p>Your answers and XP are saved. You’re ready for the next lesson.</p></div>}
      {questions.map(question=><KnowledgeCheck key={question.id} question={question} reviewId={notes.id} solved={notes.solved.includes(question.id)} onSaved={refresh}/>)}
    </section>
  </div>;
}
