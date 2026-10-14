import { Avatar, Icon, LevelRing, Meter } from './UI';

export function ResponsivePreview({size}:{size:string}) {
  const width=size==='tablet'?768:size==='small-phone'?320:390;
  return <div style={{padding:16}}><p>Development QA · {width}px viewport · isolated test database</p><iframe title="Responsive academy preview" src="http://localhost:3004/" width={width} height={1050} style={{display:'block',border:'1px solid #555263'}}/></div>;
}

// Development only. No learner data, awards, or preferences are written here.
export function DesignPreview() {
  return <main className="design-preview"><header className="page-heading"><p className="eyebrow">DESIGN DEMONSTRATION · SAMPLE STATES</p><h1>Progression design studio</h1><p>These examples are not Jaxon's progress. Badges and avatar unlocks need future persistence and reward rules.</p></header>
    <section><h2>XP & level states</h2><div className="preview-grid">
      <article><LevelRing level={1} percent={0}/><h3>Just beginning</h3><p>0 of 100 XP · Sample</p><Meter value={0} max={100} label="Sample empty level"/></article>
      <article><LevelRing level={1} percent={70}/><h3>A milestone in reach</h3><p>30 XP to Level 2 · Sample</p><Meter value={70} max={100} label="Sample partial level"/></article>
      <article><LevelRing level={2} percent={0}/><h3>Level 2 reached</h3><p>Learning is adding up · Sample</p><div className="answer-feedback correct"><Icon name="spark"/>Level up. Keep building!</div></article>
    </div></section>
    <section><h2>Achievement states · proposed</h2><div className="preview-grid">
      <article className="preview-badge locked"><span className="achievement-art"><Icon name="lock" size={32}/></span><h3>First idea explained</h3><p>Locked · Solve your first knowledge check.</p></article>
      <article className="preview-badge"><span className="achievement-art"><Icon name="check" size={32}/></span><h3>First idea explained</h3><p>Earned example · An idea understood.</p></article>
      <article className="preview-badge"><span className="achievement-art"><Icon name="cube" size={32}/></span><h3>First build approved</h3><p>Earned example · A working project reviewed with a parent.</p></article>
    </div></section>
    <section><h2>Academy emblem & cosmetics · proposed</h2><div className="preview-grid">
      <article><Avatar large/><h3>Explorer emblem</h3><p>Default identity · available today.</p><button disabled>Equipped example</button></article>
      <article className="avatar-teal"><Avatar large/><h3>Builder finish</h3><p>Available example · selection persistence needed.</p><button disabled>Equip example</button></article>
      <article className="preview-badge locked"><Avatar large/><h3>Creator frame</h3><p>Locked example · suggested unlock after an approved build.</p><button disabled><Icon name="lock"/>Locked example</button></article>
    </div></section>
    <section><h2>Practice feedback</h2><div className="practice-feedback"><Icon name="flag"/><div><strong>Ready for your parent's feedback</strong><p>Show the actual build, then discuss what you discovered.</p></div></div><div className="practice-feedback approved"><Icon name="check"/><div><strong>Build approved. You brought the idea to life!</strong><p>Sample approval · a production message requires a real reviewed submission.</p></div></div></section>
    <section><h2>Dialog pattern · layout demonstration</h2><div className="preview-dialog" role="group" aria-label="Static dialog layout example"><h3>Use this academy emblem?</h3><p>This is a design example. It cannot change your profile.</p><div className="actions"><button disabled className="secondary">Cancel</button><button disabled>Use emblem</button></div></div><p className="muted">A future live dialog must trap focus, support Escape, and restore focus to its trigger.</p></section>
  </main>;
}
