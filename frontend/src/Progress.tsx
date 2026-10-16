import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from 'react';
import { request } from './api';
import { Avatar, Icon, LevelRing, Meter } from './UI';
import { RankBadge, type Rank } from './RankBadge';

type MasteryCourse = {course_id:string;title:string;videos:number;authored_videos:number;planned_checks:number;solved_checks:number;required_checks:number;percent:number;complete:boolean};
export type XP = {total_xp:number;level:number;level_xp:number;xp_per_level:number;xp_to_next_level:number;max_level:number;at_max_level:boolean;
  ranks:Rank[];highest_rank:Rank;equipped_title:Rank;equipped_icon:Rank;next_rank:Rank|null;
  equipment:{title_id:string|null;icon_id:string|null};
  mastery:{finalized:boolean;ready_to_finalize:boolean;eligible:boolean;estimate:boolean;courses:MasteryCourse[];planned_checks:number;solved_checks:number;required_checks:number;overall_percent:number;videos:number;authored_videos:number}};
function useProgressionState() {
  const [xp,setXP]=useState<XP|null>(null);
  const [error,setError]=useState('');
  const [celebration,setCelebration]=useState('');
  const [unlocked,setUnlocked]=useState<Rank|null>(null);
  const previous=useRef<XP|null>(null);
  useEffect(()=>{
    let active=true;
    const refresh=async()=>{
      try {
        const result:XP=await request('/api/progression');
        if(!active)return;
        if(previous.current && result.total_xp>previous.current.total_xp) {
          setCelebration(result.level>previous.current.level ? `Level ${result.level} reached. Keep building!` : `+${result.total_xp-previous.current.total_xp} XP earned. Nice thinking!`);
        }
        if(previous.current && result.highest_rank.level>previous.current.highest_rank.level) {setUnlocked(result.highest_rank);setCelebration('');}
        previous.current=result;setXP(result);setError('');
      }catch{if(active)setError('Your XP could not load. Please try again.');}
    };
    void refresh();window.addEventListener('academy-xp',refresh);
    return()=>{active=false;window.removeEventListener('academy-xp',refresh);};
  },[]);
  async function equip(selection:{title_id?:string|null;icon_id?:string|null}) {
    const result:XP=await request('/api/progression/equipment',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(selection)});
    previous.current=result;setXP(result);
  }
  return {xp,error,celebration,unlocked,equip,dismiss:()=>setCelebration(''),dismissUnlock:()=>setUnlocked(null)};
}

const ProgressionContext=createContext<ReturnType<typeof useProgressionState>|null>(null);
export function ProgressionProvider({children}:{children:ReactNode}) {
  const state=useProgressionState();
  return <ProgressionContext.Provider value={state}>{children}{state.unlocked&&<aside className="rank-reveal" role="status" aria-live="polite">
    <RankBadge rank={state.unlocked} large/><div><p className="eyebrow">GUILD MILESTONE</p><h2>{state.unlocked.title} unlocked!</h2><p>A new title and emblem are yours to keep. Find them in My progress.</p></div>
    <button className="icon-button" aria-label="Dismiss rank unlock" onClick={state.dismissUnlock}>×</button>
  </aside>}</ProgressionContext.Provider>;
}
export function useXP(){const value=useContext(ProgressionContext);if(!value)throw new Error('ProgressionProvider is required');return value;}

export function LearnerIdentity(){const {xp}=useXP();return <div className="learner-identity">{xp?<RankBadge rank={xp.equipped_icon}/>:<Avatar/>}<div><strong>Learner</strong><span>{xp?`${xp.equipped_title.title} · Level ${xp.level}`:'Your developer journey'}</span></div></div>;}

export function XPPanel({compact=false}:{compact?:boolean}) {
  const {xp,error,celebration,dismiss}=useXP();
  return <div className={compact?'xp-panel compact':'xp-panel'} aria-label="Your level">
    {xp ? <><div className="xp-heading"><Icon name="spark"/><strong>Level {xp.level}</strong><span>{xp.total_xp} XP</span></div>
      <Meter value={xp.at_max_level?1:xp.level_xp} max={xp.at_max_level?1:xp.xp_per_level} label="Progress to next level"/>
      <p>{xp.at_max_level?'Level 50 reached':`${xp.xp_to_next_level} XP to Level ${xp.level+1}`}</p>
      {xp.next_rank&&<p className="next-rank">Next title: <strong>{xp.next_rank.title}</strong> · {Math.max(0,xp.next_rank.xp-xp.total_xp).toLocaleString()} XP{xp.next_rank.requires_mastery?' + mastery goals':''}</p>}
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
    <section className="profile-hero">{xp?<RankBadge rank={xp.equipped_icon} large/>:<Avatar large/>}<div><p className="eyebrow">DEVELOPER GUILD</p><h2>Learner</h2><p>{xp?.equipped_title.title??'Your developer journey'}</p></div>{xp?<div className="profile-level"><LevelRing level={xp.level} percent={xp.at_max_level?100:xp.level_xp/xp.xp_per_level*100}/><div><strong>{xp.total_xp.toLocaleString()} XP earned</strong><p>{xp.at_max_level?'Level 50 reached':`${xp.xp_to_next_level} XP to your next level`}</p></div></div>:<p role={error?'alert':'status'}>{error||'Loading your level…'}</p>}</section>
    {xp&&<><GuildCollection/><MasteryTrack/></>}
    <div className="section-heading"><div><p className="eyebrow">REAL PROGRESS</p><h2>What you can show</h2></div></div><Evidence full/>
    <aside className="learning-note"><Icon name="spark"/><p>Correct knowledge checks earn XP once. Follow the Udemy instructor for activities in Unreal Engine; your level is a progress marker.</p></aside>
  </div>;
}

function GuildCollection(){
  const {xp,equip}=useXP();const [busy,setBusy]=useState(false);const [feedback,setFeedback]=useState('');
  if(!xp)return null;
  async function select(value:{title_id?:string|null;icon_id?:string|null}){setBusy(true);setFeedback('');try{await equip(value);setFeedback('Saved. Your nameplate is updated.');}catch(e){setFeedback((e as Error).message);}finally{setBusy(false);}}
  return <section className="guild-collection" aria-labelledby="guild-heading"><div className="section-heading"><div><p className="eyebrow">PERMANENT UNLOCKS</p><h2 id="guild-heading">Your guild collection</h2><p className="muted">{xp.ranks.filter(r=>r.unlocked).length} of {xp.ranks.length} ranks unlocked. Equip any earned title and emblem.</p></div><button className="secondary" disabled={busy||(!xp.equipment.title_id&&!xp.equipment.icon_id)} onClick={()=>void select({title_id:null,icon_id:null})}>Follow newest rank</button></div>
    <p role="status">{feedback}</p><div className="rank-grid">{xp.ranks.map(rank=><article className={`rank-card ${rank.unlocked?'earned':'locked'}`} key={rank.id}>
      <div className="rank-card-top"><RankBadge rank={rank} large locked={!rank.unlocked}/><span className="rank-level">LEVEL {rank.level}</span></div>
      <h3>{rank.title}</h3><p>{rank.xp.toLocaleString()} XP{rank.requires_mastery?' + mastery goals':''}</p>
      {rank.unlocked?<><span className="rank-earned"><Icon name="check" size={14}/>Unlocked · yours to keep</span><div className="rank-actions">
        <button className="secondary" aria-label={`Equip ${rank.title} title`} disabled={busy||xp.equipped_title.id===rank.id} onClick={()=>void select({title_id:rank.id})}>{xp.equipped_title.id===rank.id?'Title equipped':'Equip title'}</button>
        <button className="secondary" aria-label={`Equip ${rank.title} emblem`} disabled={busy||xp.equipped_icon.id===rank.id} onClick={()=>void select({icon_id:rank.id})}>{xp.equipped_icon.id===rank.id?'Emblem equipped':'Equip emblem'}</button>
      </div></>:<p className="rank-lock"><Icon name="lock" size={14}/>{rank.level<=xp.level?'Complete mastery goals':`${Math.max(0,rank.xp-xp.total_xp).toLocaleString()} XP to unlock`}</p>}
    </article>)}</div></section>;
}

function MasteryTrack(){const {xp}=useXP();if(!xp)return null;const track=xp.mastery;
  return <section className="mastery-track" aria-labelledby="mastery-heading"><p className="eyebrow">THE ROAD TO UNREAL MASTER</p><h2 id="mastery-heading">Broad learning. A title worth earning.</h2>
    <p>Reach Level 50, solve 85% of the track’s checks overall and at least 75% in every course.</p>
    <div className="mastery-summary"><strong>{track.overall_percent}% solved overall</strong><span>{track.solved_checks} / {track.required_checks} checks toward the 85% goal{track.estimate?' · estimated':''}</span></div>
    <Meter value={track.solved_checks} max={Math.max(1,track.required_checks)} label="Overall mastery goal"/>
    {!track.finalized&&<p className="mastery-draft">Track in preparation · {track.authored_videos} of {track.videos} videos have authored checks. Unprepared videos stay in the goal with an estimate of five checks each. Unreal Master unlocks after the full track is authored and finalized.</p>}
    <div className="mastery-courses">{track.courses.map(course=><article key={course.course_id}><h3>{course.title}</h3><p>{course.percent}% solved · 75% needed{course.authored_videos<course.videos?' · estimate':''}</p><Meter value={course.solved_checks} max={Math.max(1,course.required_checks)} label={`Mastery goal for ${course.title}`}/></article>)}</div>
    <p className="muted">Your earned ranks stay unlocked. This title recognizes academy progress; keep developing practical skills through the instructor’s activities.</p>
  </section>;
}

export function ParentMasterySetup(){const {xp}=useXP();const [busy,setBusy]=useState(false);const [message,setMessage]=useState('');if(!xp)return null;const track=xp.mastery;
  async function finalize(){setBusy(true);try{await request('/api/parent/progression/finalize',{method:'POST'});window.dispatchEvent(new Event('academy-xp'));setMessage('Mastery track finalized. Future courses will not move these goals.');}catch(e){setMessage((e as Error).message);}finally{setBusy(false);}}
  return <section><h2>Mastery track setup</h2><p>{track.courses.length} courses · {track.videos} planned videos · {track.authored_videos} authored. {track.finalized?'Track membership is finalized.':'Import all intended courses and finish authoring their checks before finalizing. Later course additions will not revoke earned ranks.'}</p><button disabled={busy||track.finalized||!track.ready_to_finalize} onClick={()=>void finalize()}>{track.finalized?'Track finalized':busy?'Finalizing…':'Finalize mastery track'}</button><p role="status">{message}</p></section>;
}
