export type Rank = {id:string;title:string;level:number;xp:number;icon:string;material:string;unlocked:boolean;unlocked_at:string|null;requires_mastery:boolean};

const glyphs:Record<string,string> = {
  spark:'m24 10 4 10 10 4-10 4-4 10-4-10-10-4 10-4Z',
  compass:'M24 9a15 15 0 1 0 0 30 15 15 0 0 0 0-30Zm7 8-4 10-10 4 4-10Z',
  cube:'m24 10 13 7v14l-13 7-13-7V17Zm0 14v14M11 17l13 7 13-7',
  wrench:'M29 10a10 10 0 0 0-11 13L9 32a4 4 0 0 0 6 6l10-10a10 10 0 0 0 13-11l-7 7-7-7Z',
  hammer:'m14 12 10-4 13 13-7 7-8-8-11 17-5-5 14-14Z',
  globe:'M24 8a16 16 0 1 0 0 32 16 16 0 0 0 0-32Zm0 0c-10 9-10 23 0 32 10-9 10-23 0-32ZM9 19h30M9 29h30',
  nodes:'M14 12h10v10h12v14H24M12 17v14h12M9 8h9v9H9ZM31 18h10v9H31ZM19 31h10v9H19Z',
  controller:'M15 15h18c6 0 11 22 5 22-3 0-6-7-8-7H18c-2 0-5 7-8 7-6 0-1-22 5-22ZM15 20v8m-4-4h8m13-4h.1m5 5h.1',
  crystal:'m17 8 14 0 10 13-17 20L7 21Zm-10 13h34M17 8l-3 13 10 20 10-20-3-13M14 21h20',
  crown:'m8 12 8 7 8-11 8 11 8-7-4 19H12Zm4 24h24m-12-16 7 4v8l-7 4-7-4v-8Zm0 8v8m-7-12 7 4 7-4',
};

export function RankBadge({rank,large=false,locked=false}:{rank:Rank;large?:boolean;locked?:boolean}) {
  return <span className={`rank-badge rank-${rank.material} ${large?'rank-large':''} ${locked?'rank-locked':''}`} role="img" aria-label={`${rank.title} emblem${locked?' · locked':''}`}>
    <svg viewBox="0 0 64 68" fill="none" aria-hidden="true"><path className="rank-frame" d="m32 2 28 16v31L32 65 4 49V18Z"/>
      <path className="rank-inset" d="m32 7 23 14v25L32 60 9 46V21Z"/>
      <g transform="translate(8 9)" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d={glyphs[rank.icon]??glyphs.spark}/></g>
      <path d="m17 52 15 9 15-9" stroke="currentColor" opacity=".6"/></svg>
  </span>;
}
