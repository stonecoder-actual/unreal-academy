import { useEffect, useState } from 'react';
import { request } from './api';

type ExternalSummary={id:string;title:string;source_type:string};
type Item={id:string;title:string;item_kind:string;transcript_status:string};

export function ParentExternalImport({onImported}:{onImported:()=>void}) {
  const [manifest,setManifest]=useState('');const [feedback,setFeedback]=useState('');const [busy,setBusy]=useState(false);
  const [courses,setCourses]=useState<ExternalSummary[]>([]);const [courseId,setCourseId]=useState('');
  const [items,setItems]=useState<Item[]>([]);const [lessonId,setLessonId]=useState('');
  const [transcript,setTranscript]=useState<{cues:string[];captured_at:string;source_url:string}|null>(null);
  const [error,setError]=useState('');
  async function refresh(){try{const result:ExternalSummary[]=await request('/api/courses');setCourses(result.filter(c=>c.source_type==='udemy'));setError('');}catch(e){setError((e as Error).message);}}
  useEffect(()=>{void refresh();},[]);
  useEffect(()=>{let active=true;setItems([]);setLessonId('');setTranscript(null);if(courseId)request(`/api/courses/${courseId}`).then(result=>{if(active)setItems(result.lessons);}).catch(e=>{if(active)setError(e.message);});return()=>{active=false;};},[courseId]);
  useEffect(()=>{let active=true;setTranscript(null);if(lessonId)request(`/api/parent/lessons/${lessonId}/transcript`).then(result=>{if(active){setTranscript(result);setError('');}}).catch(e=>{if(active)setError(e.message);});return()=>{active=false;};},[lessonId]);
  async function importManifest(){setBusy(true);setFeedback('');try{const parsed=JSON.parse(manifest);const result=await request('/api/parent/external-courses/import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(parsed)});setFeedback(`Saved ${result.imported_items} curriculum items; ${result.captured_transcripts} transcripts available. Existing progress retained.`);await refresh();setCourseId('');onImported();}catch(e){setFeedback((e as Error).message);}finally{setBusy(false);}}
  return <section><h2>Udemy courses & transcripts</h2><p>Videos stay on Udemy. A private curriculum manifest adds direct lesson links and captured transcripts for preparing key takeaways and knowledge checks. Lesson notes publish straight to the learner’s portal. It contains no Udemy password, cookies or video files.</p>
    <label htmlFor="external-manifest">Private course manifest (.json)</label><input id="external-manifest" type="file" accept=".json,application/json" disabled={busy} onChange={async e=>{const file=e.target.files?.[0];setManifest('');if(file){if(file.size>15000000){setFeedback('Choose a manifest smaller than 15 MB.');return;}try{setManifest(await file.text());setFeedback('File ready. Import to save it on this computer.');}catch{setFeedback('Could not read the file.');}}}}/>
    <button disabled={busy||!manifest} onClick={()=>void importManifest()}>{busy?'Importing…':'Import / update Udemy manifest'}</button><p role="status">{feedback}</p>
    <label htmlFor="transcript-course">Review captured transcripts</label><select id="transcript-course" value={courseId} onChange={e=>setCourseId(e.target.value)}><option value="">Choose a Udemy course</option>{courses.map(c=><option key={c.id} value={c.id}>{c.title}</option>)}</select>
    {courseId&&<><p>{items.filter(l=>l.transcript_status==='captured').length} of {items.filter(l=>l.item_kind==='video').length} video transcripts captured. Readings and Udemy quizzes do not have video transcripts.</p><label htmlFor="transcript-lesson">Lesson transcript</label><select id="transcript-lesson" value={lessonId} onChange={e=>setLessonId(e.target.value)}><option value="">Choose a captured transcript</option>{items.filter(l=>l.transcript_status==='captured').map(l=><option key={l.id} value={l.id}>{l.title}</option>)}</select></>}
    {transcript&&<details open><summary>Captured transcript · {transcript.cues.length} cues</summary><p className="muted">Captured {transcript.captured_at}. Automatic captions may contain errors. These ordered cues have no verified timestamps.</p><a href={transcript.source_url} target="_blank" rel="noopener noreferrer">Check the source on Udemy</a><div className="transcript-review">{transcript.cues.map((cue,i)=><p key={i}>{cue}</p>)}</div></details>}
    {error&&<p role="alert">{error}</p>}<p className="muted">Transcript capture does not automatically publish a lesson or award XP. Keep this purchased material in local private storage.</p>
  </section>;
}
