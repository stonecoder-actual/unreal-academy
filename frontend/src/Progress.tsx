import { useEffect, useRef, useState } from 'react';
import { request } from './api';
import { Avatar, Icon, LevelRing, Meter } from './UI';

export type XP = {total_xp:number;level:number;level_xp:number;xp_per_level:number;xp_to_next_level:number};
export function useXP() {
  const [xp,setXP]=useState<XP|null>(null);
  const [error,setError]=useState('');
  const [celebration,setCelebration]=useState('');
  const previous=useRef<XP|null>(null);
  useEffect(()=>{
    let active=true;
    const refresh=async()=>{
      try {
        const result:XP=await request('/api/xp');
        if(!active)return;
        if(previous.current && result.total_xp>previous.current.total_xp) {
          setCelebration(result.level>previous.current.level ? `Level ${result.level} reached. Keep building!` : `+${result.total_xp-previous.current.total_xp} XP earned. Nice thinking!`);
        }
        previous.current=result;setXP(result);setError('');
      }catch{if(active)setError('Your XP could not load. Please try again.');}
    };
    void refresh();window.addEventListener('academy-xp',refresh);
    return()=>{active=false;window.removeEventListener('academy-xp',refresh);};
  },[]);
  return {xp,error,celebration,dismiss:()=>setCelebration('')};
}

export function XPPanel({compact=false}:{compact?:boolean}) {
  const {xp,error,celebration,dismiss}=useXP();
  return <div className={compact?'xp-panel compact':'xp-panel'} aria-label="Jaxon's level">
    {xp ? <><div className="xp-heading"><Icon name="spark"/><strong>Level {xp.level}</strong><span>{xp.total_xp} XP</span></div>
      <Meter value={xp.level_xp} max={xp.xp_per_level} label="Progress to next level"/>
      <p>{xp.xp_to_next_level} XP to Level {xp.level+1}</p>
    </> : <p role={error?'alert':'status'}>{error||'Loading your level…'}</p>}
    {celebration&&<div className="celebration" role="status"><Icon name="spark"/><span>{celebration}</span><button className="icon-button" aria-label="Dismiss XP notification" onClick={dismiss}>×</button></div>}
  </div>;
}

type EvidenceGuide={id:string;solved:string[];submission:{status:string}|null;document:{title:string;questions:{id:string}[];practice?:object|null}};
export function Evidence({full=false}:{full?:boolean}) {
  const [guides,setGuides]=useState<EvidenceGuide[]|null>(null);
  const [error,setError]=useState('');
  useEffect(()=>{
    let active=true;
    async function refresh(){
      try{
        const index:{lesson_id:string}[]=await request('/api/guided-lessons');
        const result=await Promise.all(index.map(g=>request(`/api/lessons/${g.lesson_id}/guide`)));
        if(active){setGuides(result.filter(Boolean));setError('');}
      }catch{if(active)setError('Learning records could not load. Your saved progress is safe.');}
    }
    void refresh();window.addEventListener('academy-xp',refresh);
    return()=>{active=false;window.removeEventListener('academy-xp',refresh);};
  },[]);
  if(error)return <p role="alert">{error}</p>;
  if(!guides)return <p role="status" className="loading-state">Loading your learning records…</p>;
  const correct=guides.reduce((sum,g)=>sum+g.solved.length,0);
  const completed=guides.filter(g=>g.solved.length===g.document.questions.length).length;
  return <div className={full?'evidence-grid full':'evidence-grid'}>
    <article className="evidence-card"><span className={`evidence-icon ${correct?'earned':''}`}><Icon name="check" size={24}/></span><div><strong>{correct}</strong><h3>Knowledge checks solved</h3><p>{correct?'Ideas you have checked and understood.':'Your first correct check is a great next milestone.'}</p></div></article>
    <article className="evidence-card"><span className={`evidence-icon ${completed?'earned':''}`}><Icon name="cube" size={24}/></span><div><strong>{completed}</strong><h3>Lesson quizzes completed</h3><p>All questions answered correctly. Keep going with your next video.</p></div></article>
    {full&&<section className="record-list"><div className="section-heading"><div><p className="eyebrow">YOUR LEARNING RECORD</p><h2>Ideas into action</h2></div><Icon name="flag"/></div>
      {guides.length?guides.map(g=><article key={g.id}><h3>{g.document.title.replace(/^Mission:\s*/,'')}</h3><p>{g.solved.length} of {g.document.questions.length} checks solved</p><Meter value={g.solved.length} max={g.document.questions.length} label={`Knowledge checks for ${g.document.title}`}/><p className="muted">{g.solved.length===g.document.questions.length?'Knowledge check complete':'Quiz in progress'} · Answers and XP saved</p></article>):<div className="empty-state"><Icon name="book"/><h3>Your learning story starts here</h3><p>Your lesson takeaways and knowledge checks appear here as you learn.</p></div>}
    </section>}
  </div>;
}

export function Profile() {
  const {xp,error}=useXP();
  return <div className="profile-page"><header className="page-heading"><p className="eyebrow">YOUR DEVELOPER JOURNEY</p><h1>Look what you're learning.</h1><p>Every idea understood. Every experiment tried. It all adds up.</p></header>
    <section className="profile-hero"><Avatar large/><div><p className="eyebrow">ACADEMY EXPLORER</p><h2>Jaxon</h2><p>Learning to bring new worlds to life.</p></div>{xp?<div className="profile-level"><LevelRing level={xp.level} percent={xp.level_xp/xp.xp_per_level*100}/><div><strong>{xp.total_xp} XP earned</strong><p>{xp.xp_to_next_level} XP to your next level</p></div></div>:<p role={error?'alert':'status'}>{error||'Loading your level…'}</p>}</section>
    <div className="section-heading"><div><p className="eyebrow">REAL PROGRESS</p><h2>What you can show</h2></div></div><Evidence full/>
    <aside className="learning-note"><Icon name="spark"/><p>Correct knowledge checks earn XP once. Follow the Udemy instructor for activities in Unreal Engine; your level is a progress marker.</p></aside>
  </div>;
}
