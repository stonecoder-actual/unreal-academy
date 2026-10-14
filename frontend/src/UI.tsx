import type { CSSProperties } from 'react';

export type IconName = 'home' | 'library' | 'spark' | 'arrow' | 'back' | 'play' | 'check' | 'code' | 'cube' | 'flag' | 'lock' | 'parent' | 'user' | 'book';
export function Icon({name, size=20}:{name:IconName;size?:number}) {
  const paths:Record<IconName,string> = {
    home:'M3 11 12 3l9 8M5 10v11h5v-7h4v7h5V10',
    library:'M4 4h5v16H4zM12 4h3v16h-3zM18 4l3 15',
    spark:'m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5Z',
    arrow:'M4 12h16m-6-6 6 6-6 6', back:'M20 12H4m6-6-6 6 6 6',
    play:'m8 4 12 8-12 8Z', check:'m5 12 4 4L19 6',
    code:'m8 6-6 6 6 6m8-12 6 6-6 6m-3-15-2 18',
    cube:'m12 2 9 5v10l-9 5-9-5V7Zm0 10v10M3 7l9 5 9-5',
    flag:'M5 22V3m0 0c5-4 9 4 15 0v10c-6 4-10-4-15 0',
    lock:'M6 10h12v11H6Zm3 0V6a3 3 0 0 1 6 0v4',
    parent:'M12 2 3 6v6c0 5 9 10 9 10s9-5 9-10V6Zm-4 10 3 3 5-6',
    user:'M8 7a4 4 0 1 0 8 0 4 4 0 1 0-8 0M3 22v-3c0-7 18-7 18 0v3',
    book:'M12 5v16M2 3c4-1 7 0 10 2 3-2 6-3 10-2v16c-4-1-7 0-10 2-3-2-6-3-10-2Z',
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false"><path d={paths[name]}/></svg>;
}

export function Avatar({large=false}:{large?:boolean}) {
  return <div className={`avatar ${large?'avatar-large':''}`} aria-label="Jaxon's academy emblem">
    <svg viewBox="0 0 80 80" aria-hidden="true"><path d="m40 7 28 16v34L40 73 12 57V23Z" fill="#202037" stroke="#b9a2ff" strokeWidth="2"/>
      <path d="m40 20 17 10v20L40 60 23 50V30Z" fill="#a68aff"/><path d="M23 30 40 40l17-10M40 40v20" fill="none" stroke="#272139" strokeWidth="2"/>
      <path d="m31 30 9-5 9 5-9 5Z" fill="#e9e1ff"/></svg>
  </div>;
}

export function CourseArt({theme='violet',hero=false}:{theme?:string;hero?:boolean}) {
  return <div className={`course-art art-${theme} ${hero?'hero-art':''}`} aria-hidden="true">
    <svg viewBox="0 0 480 240" fill="none" focusable="false">
      <g className="art-grid" stroke="currentColor" opacity=".16">{[0,1,2,3,4,5,6].map(n=><path key={n} d={`M${n*80-120} 240 240 ${40-n*12} ${600-n*80} 240`}/>)}</g>
      <path d="m240 199-110-62 110-62 110 62Z" fill="currentColor" opacity=".12"/>
      <g stroke="currentColor" strokeWidth="1.5">
        <path d="m240 48 64 37v73l-64 37-64-37V85Z" fill="var(--art-dark)"/>
        <path d="m240 48 64 37-64 37-64-37Z" fill="var(--art-light)"/>
        <path d="m240 122 64-37v73l-64 37Z" fill="var(--art-mid)"/>
        <path d="M240 122v73"/>
        <path d="m125 122 26 15v30l-26 15-26-15v-30Z" fill="var(--art-dark)"/>
        <path d="m125 122 26 15-26 15-26-15Z" fill="var(--art-light)"/>
        <path d="M125 152v30m0-30 26-15"/>
        <path d="m342 41 22 13v26l-22 13-22-13V54Z" fill="var(--art-dark)"/>
        <path d="m342 41 22 13-22 13-22-13Z" fill="var(--art-light)"/>
        <path d="M342 67v26m0-26 22-13"/>
        <path d="M305 120h44v29h34M175 94h-41V69h-30" strokeDasharray="4 5" opacity=".7"/>
        <circle cx="388" cy="149" r="5"/><circle cx="99" cy="69" r="4"/>
      </g>
      <g fill="currentColor" opacity=".8"><circle cx="210" cy="25" r="2"/><circle cx="367" cy="183" r="2"/><path d="M90 201h12m-6-6v12" stroke="currentColor"/></g>
    </svg>
    <span className="art-caption">{theme==='amber'?'SYSTEMS / ABILITIES':theme==='teal'?'CREATE / EXPERIMENT':'LEARN / BUILD'}</span>
  </div>;
}

export function Difficulty({level}:{level?:string}) {
  if(!level)return null;
  return <span className={`difficulty ${level.toLowerCase()}`}><span className="difficulty-bars" aria-hidden="true"><i/><i className={level==='Intermediate'?'lit':''}/><i/></span>{level}</span>;
}

export function Meter({value,max,label}:{value:number;max:number;label:string}) {
  return <progress className="meter" value={value} max={Math.max(max,1)} aria-label={label}/>;
}

export function coursePresentation(folder:string) {
  const key=folder.split('/')[0];
  const metadata:Record<string,{difficulty:string;theme:string;category:string}>={
    Unreal_Engine_MegaCourse:{difficulty:'Beginner',theme:'violet',category:'UNREAL FOUNDATIONS'},
    Unreal_Engine_MegaCourse_2:{difficulty:'Beginner',theme:'teal',category:'GAME & WORLD CREATION'},
    Unreal_Engine_MegaCourse_3:{difficulty:'Intermediate',theme:'amber',category:'GAMEPLAY SYSTEMS'},
  };
  return metadata[key]??{difficulty:undefined,theme:'violet',category:'GAME DEVELOPMENT'};
}

export function LevelRing({level,percent}:{level:number;percent:number}) {
  return <div className="level-ring" style={{'--level-fill':`${Math.min(100,Math.max(0,percent))}%`} as CSSProperties}><div><span>LEVEL</span><strong>{level}</strong></div></div>;
}
