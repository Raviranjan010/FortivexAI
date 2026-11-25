import React,{useEffect,useRef,useState} from 'react';import{createRoot}from'react-dom/client';import{BarChart3,BookOpen,Calendar,History,LayoutDashboard,Mic,Settings as SettingsIcon,Users,UserRound,Square,VolumeX,Send,Trash2,Download}from'lucide-react';import{BarChart,Bar,XAxis,YAxis,Tooltip,ResponsiveContainer,PieChart,Pie,Cell}from'recharts';import{api}from'./api';import type{VoiceState}from'./voice';import'./styles.css';
type Page='Overview'|'Live Agent'|'Leads'|'CRM'|'Appointments'|'Knowledge Base'|'Conversations'|'Analytics'|'Settings';
const pages:[Page,React.ElementType][]=[['Overview',LayoutDashboard],['Live Agent',Mic],['Leads',Users],['CRM',UserRound],['Appointments',Calendar],['Knowledge Base',BookOpen],['Conversations',History],['Analytics',BarChart3],['Settings',SettingsIcon]];
function useLoad<T>(path: string, seed: T) {
  const [data, setData] = useState(seed);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    let current = true;
    setLoading(true);
    setError('');
    api.get<T>(path).then(value => { if (current) setData(value); })
      .catch(failure => { if (current) setError(failure.message); })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [path, revision]);
  return {data, error, loading, load: () => setRevision(value => value + 1)};
}
const Empty=({children}:{children:string})=><div className="empty">{children}</div>;const ErrorBox=({text}:{text:string})=>text?<div className="error" role="alert">{text}</div>:null;
function Overview(){const{data:a,loading,error}=useLoad<any>('/api/analytics',{});if(loading)return <p>Loading business data…</p>;const metrics=[['Conversations',a.total_conversations],['Leads',a.total_leads],['Qualified',a.qualified_leads],['Appointments',a.confirmed_appointments]];return <><ErrorBox text={error}/><div className="metrics">{metrics.map(x=><article><span>{x[0]}</span><strong>{x[1]??0}</strong></article>)}</div><section><h2>Pipeline snapshot</h2>{a.total_leads?<ResponsiveContainer width="100%" height={260}><BarChart data={Object.entries(a.lead_distribution).map(([name,value])=>({name,value}))}><XAxis dataKey="name"/><YAxis allowDecimals={false}/><Tooltip/><Bar dataKey="value" fill="#2563eb"/></BarChart></ResponsiveContainer>:<Empty>No lead activity yet. Start a conversation or add a lead.</Empty>}</section></>}
type AgentEvent = {id?: string; tool_name: string; status: string; timestamp?: string; duration_ms?: number; result: {starts_at?: string; error?: string; score?: number}};
type AgentReply = {response: string; sources: {filename: string}[]; tool_events: AgentEvent[]};

function AgentActivity({events, sessionId}: {events: AgentEvent[]; sessionId: string}) {
  const [booking, setBooking] = useState<Record<string, string>>({});
  if (!events.length) return null;
  async function confirmProposal(id: string) {
    setBooking(previous => ({...previous, [id]: 'Booking…'}));
    try {
      const appointment = await api.post<{status: string}>(`/api/conversations/${sessionId}/proposals/${id}/confirm`);
      setBooking(previous => ({...previous, [id]: appointment.status === 'confirmed' ? 'Confirmed' : appointment.status}));
    } catch (error) {
      setBooking(previous => ({...previous, [id]: error instanceof Error ? error.message : 'Booking failed'}));
    }
  }
  return <span className="agent-activity"><strong>Agent activity</strong>{events.map((event, index) =>
    <span key={event.id ?? index}>
      {event.tool_name} · {event.status}
      {event.duration_ms != null && <> · {Math.round(event.duration_ms)} ms</>}
      {event.timestamp && <> · {new Date(event.timestamp + 'Z').toLocaleTimeString()}</>}
      {event.result.error && <> · {event.result.error}</>}
      {event.id && event.tool_name === 'propose_appointment' && event.status === 'success' &&
        <> · {new Date(event.result.starts_at!).toLocaleString()}
          <button disabled={['Booking…', 'Confirmed'].includes(booking[event.id])} onClick={() => confirmProposal(event.id!)}>Confirm appointment</button>
          <span role="status">{booking[event.id]}</span>
        </>}
    </span>)}</span>;
}

function LiveAgent({active}: {active: boolean}){const[session,setSession]=useState<any>(undefined),[messages,setMessages]=useState<any[]>([]),[input,setInput]=useState(''),[state,setState]=useState<VoiceState>('IDLE'),[language,setLanguage]=useState('en'),[error,setError]=useState(''),[consent,setConsent]=useState(false),recognition=useRef<any>(undefined);
 const [starting, setStarting] = useState(false);
 const start = async () => {
   if (!consent || busy.current) return;
   busy.current = true;
   setStarting(true);
   setError('');
   try {
     setSession(await api.post('/api/conversations', {language}));
     setMessages([]);
     setEvents([]);
     setCustomer({});
     setScore(undefined);
     setState('LISTENING');
   } catch (error) { setError(error instanceof Error ? error.message : 'Could not start the session'); }
   finally { busy.current = false; setStarting(false); }
 };
 const busy = useRef(false);
 const [capturing, setCapturing] = useState(false);
 const [level, setLevel] = useState(0);
 const [meterError, setMeterError] = useState(false);
 const [customer, setCustomer] = useState<Record<string, string>>({});
 const [score, setScore] = useState<number>();
 const [events, setEvents] = useState<AgentEvent[]>([]);
 const transcript = useRef<HTMLDivElement>(null);
 useEffect(() => {
   if (!capturing || !consent || !active) return;
   return monitorMicrophone(setLevel, () => setMeterError(true));
 }, [capturing, consent, active]);
 useEffect(() => {
   if (!active) {
     recognition.current?.abort();
     setCapturing(false);
     window.speechSynthesis?.cancel();
     setState(current => current === 'SPEAKING' ? 'LISTENING' : current);
   }
 }, [active]);
 const activePage = useRef(active);
 activePage.current = active;
 useEffect(() => {
   if (transcript.current) transcript.current.scrollTop = transcript.current.scrollHeight;
 }, [messages]);
 const submit = async (text = input) => {
   if (!session || !text.trim() || !consent || busy.current || state === 'ENDED' || state === 'SPEAKING') return;
   busy.current = true;
   recognition.current?.stop();
   setCapturing(false);
   setError('');
   setInput('');
   setMessages(items => [...items, {role: 'user', content: text}]);
   setState('PROCESSING');
   try {
     const reply = await api.post<AgentReply>(`/api/conversations/${session.id}/messages`, {content: text});
     setMessages(items => [...items, {role: 'assistant', sources: reply.sources, content: reply.response}]);
     setEvents(items => [...items, ...reply.tool_events]);
     for (const event of reply.tool_events) {
       if (event.status === 'success' && typeof event.result.score === 'number') setScore(event.result.score);
     }
     void api.get<{extracted: Record<string, string>}>(`/api/conversations/${session.id}`)
       .then(result => setCustomer(result.extracted)).catch(() => {});
     if (!activePage.current || !('speechSynthesis' in window)) { setState('LISTENING'); return; }
     const utterance = new SpeechSynthesisUtterance(reply.response);
     utterance.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
     utterance.onend = utterance.onerror = () => setState(current => current === 'SPEAKING' ? 'LISTENING' : current);
     setState('SPEAKING');
     speechSynthesis.speak(utterance);
   } catch (error) {
     setError(error instanceof Error ? error.message : 'Message could not be sent');
     setState('ERROR');
   } finally { busy.current = false; }
 };
 useEffect(() => () => {
   recognition.current?.abort();
   window.speechSynthesis?.cancel();
 }, []);
 const listen = () => {
   if (!consent || busy.current || recognition.current || state === 'SPEAKING' || state === 'ENDED') return;
   const Recognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
   if (!Recognition) return setError('Speech recognition is unsupported. Use text input.');
   const recognizer = new Recognition();
   recognizer.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
   recognizer.interimResults = false;
   recognizer.onresult = (event: any) => void submit(event.results[0][0].transcript);
   recognizer.onend = () => {
     if (recognition.current === recognizer) {
       recognition.current = undefined;
       setCapturing(false);
     }
   };
   recognizer.onerror = (event: any) => {
     if (event.error === 'aborted') return;
     setError(`Microphone error: ${event.error}. You can type your message.`);
     setState('ERROR');
   };
   try {
     recognition.current = recognizer;
     recognizer.start();
     setLevel(0);
     setMeterError(false);
     setCapturing(true);
     setError('');
     setState('LISTENING');
   } catch {
     recognition.current = undefined;
     setError('Microphone could not be started. You can type your message.');
     setState('ERROR');
   }
 };
 const end = async () => {
   if (!session || busy.current) return;
   busy.current = true;
   recognition.current?.abort();
   setCapturing(false);
   window.speechSynthesis?.cancel();
   try {
     await api.post(`/api/conversations/${session.id}/end`);
     setSession(undefined);
     setState('ENDED');
   } catch (error) {
     setError(error instanceof Error ? error.message : 'Session could not be ended');
     setState('ERROR');
   } finally { busy.current = false; }
 };
 const status = capturing ? 'Listening' : {IDLE: 'Ready', LISTENING: 'Ready for input', PROCESSING: 'Processing', SPEAKING: 'Speaking', ERROR: 'Needs attention', ENDED: 'Session ended'}[state];
 const setPermission = (checked: boolean) => {
   setConsent(checked);
   if (!checked) { recognition.current?.abort(); setCapturing(false); }
 };
 return <div className="voice-layout">
   <div className="agent">
     <div className="agentTop">
       <div className="identity"><span className="agent-icon"><Headphones size={23}/></span><div><h2>NovaCRM sales agent</h2><span>Customer conversation</span></div></div>
       <span className={`status ${capturing ? 'is-live' : ''}`} role="status"><i/>{status}</span>
     </div>
     <div className="voice-strip">
       <div className="identity"><Radio size={20}/><div><strong>Microphone</strong><small>{capturing ? meterError ? 'Signal meter unavailable' : 'Live input level' : 'Microphone off'}</small></div></div>
       <div className="signal" role="meter" aria-label="Microphone input level" aria-valuemin={0} aria-valuemax={100} aria-valuenow={capturing && !meterError ? Math.round(level * 100) : 0}>
         {Array.from({length: 21}, (_, index) => <i key={index} className={capturing && !meterError && level * 21 > index ? 'lit' : ''} style={{height: `${10 + (10 - Math.abs(10 - index)) * 2}px`}}/>)}
       </div>
       <label className="language"><span>Language</span><select value={language} onChange={event => setLanguage(event.target.value)} disabled={!!session}><option value="en">English</option><option value="hi">हिन्दी</option></select></label>
     </div>
     <div className="transcript-heading"><h2>Transcript</h2><span>{messages.length} {messages.length === 1 ? 'message' : 'messages'}</span></div>
     <div ref={transcript} className="transcript" role="log" aria-label="Conversation transcript">
       {messages.length ? messages.map((message, index) => <div className={`bubble ${message.role}`} key={index}>
         <b>{message.role === 'user' ? 'Customer' : 'SalesPilot'}</b><p>{message.content}</p>
         {!!message.sources?.length && <small>Sources: {[...new Set(message.sources.map((source: {filename:string}) => source.filename))].join(', ')}</small>}
       </div>) : <div className="transcript-empty"><AudioLines size={28}/><strong>No messages yet</strong><span>Start a conversation, then speak or type your first message.</span></div>}
       {state === 'PROCESSING' && <p className="muted" role="status">Waiting for the agent’s reply…</p>}
     </div>
     <div className="agent-bottom">
       <ErrorBox text={error}/>
       <form className="composer" onSubmit={event => {event.preventDefault(); void submit();}}>
         <input aria-label="Message" value={input} onChange={event => setInput(event.target.value)} placeholder="Type a message…" disabled={!session || !consent || state === 'PROCESSING' || state === 'SPEAKING'}/>
         <button aria-label="Send message" disabled={!session || !consent || !input.trim() || state === 'PROCESSING' || state === 'SPEAKING'}><Send size={17}/></button>
       </form>
       <div className="actions">{!session ? <button onClick={start} disabled={!consent || starting}><Mic size={17}/> {starting ? 'Starting…' : 'Start conversation'}</button> : <>
         <button onClick={listen} disabled={!consent || capturing || state === 'PROCESSING' || state === 'SPEAKING'}><Mic size={17}/> {capturing ? 'Listening…' : 'Listen'}</button>
         {capturing && <button className="secondary" onClick={() => {recognition.current?.abort(); setCapturing(false);}}>Stop listening</button>}
         {state === 'SPEAKING' && <button className="secondary" onClick={() => {window.speechSynthesis.cancel(); setState('LISTENING');}}><VolumeX size={17}/> Stop speaking</button>}
         <button onClick={end} className="danger" disabled={state === 'PROCESSING'}><Square size={15}/> End session</button>
       </>}</div>
       <label className="consent"><input type="checkbox" checked={consent} onChange={event => setPermission(event.target.checked)}/> I consent to transcript processing by the configured AI provider. Raw audio is not stored.</label>
     </div>
   </div>
   <div className="insights">
     <section><div className="panel-title"><UserRound size={18}/><h2>Customer profile</h2></div>
       <dl className="customer-fields">{[['Name','name'],['Company','company'],['Email','email'],['Product interest','product_interest']].map(([label,key]) => <div key={key}><dt>{label}</dt><dd>{customer[key] || 'Not captured'}</dd></div>)}</dl>
       <div className="score-heading"><strong>Lead score</strong><span>{score == null ? 'Not scored' : `${score} / 100`}</span></div>
       {score != null && <meter min={0} max={100} value={score} aria-label="Lead score"/>}
     </section>
     <section><div className="panel-title"><AudioLines size={18}/><h2>Agent activity</h2></div>
       {events.length && session ? <AgentActivity events={events} sessionId={session.id}/> : <Empty>{events.length ? 'Session ended. Review the conversation in history.' : 'Tool actions appear here as the agent runs them.'}</Empty>}
     </section>
   </div>
 </div>;
}
function Leads(){const [query,setQuery]=useState('');const{data,loading,error,load}=useLoad<any[]>(`/api/leads?q=${encodeURIComponent(query)}`,[]);const[form,setForm]=useState({name:'',email:'',company:'',requirements:'',budget:'',authority:'',timeline:''});const [failure,setFailure]=useState('');const [saving,setSaving]=useState(false);const save=async(e:React.FormEvent)=>{e.preventDefault();if(saving)return;setSaving(true);setFailure('');try{await api.post('/api/leads',form);setForm({name:'',email:'',company:'',requirements:'',budget:'',authority:'',timeline:''});load()}catch(error){setFailure(error instanceof Error?error.message:'Lead could not be saved')}finally{setSaving(false)}};return <><ErrorBox text={error || failure}/><section><h2>Add or update lead</h2><form className="gridform" onSubmit={save}>{Object.keys(form).map(k=><input key={k} aria-label={k} required={k==='email'} placeholder={k.replace('_',' ')} value={(form as any)[k]} onChange={e=>setForm({...form,[k]:e.target.value})}/>)}<button disabled={saving}>{saving ? "Saving…" : "Save lead"}</button></form></section><section><div className="sectionTitle"><h2>Lead pipeline</h2><a className="button" href="/api/leads-export.csv"><Download size={16}/> Export CSV</a></div><label className="field">Search leads<input type="search" value={query} onChange={event=>setQuery(event.target.value)} placeholder="Name, company or email"/></label>{loading?<p>Loading…</p>:data.length?<table><thead><tr><th>Name</th><th>Company</th><th>Status</th><th>Score</th><th>Class</th><th></th></tr></thead><tbody>{data.map(x=><tr key={x.id}><td>{x.name||'Not provided'}<small>{x.email}</small></td><td>{x.company||'—'}</td><td>{x.status}</td><td><meter min={0} max={100} value={x.score} aria-label="Lead score"/> {x.score}/100</td><td><span className={`badge ${x.classification}`}>{x.classification}</span></td><td><button className="icon" aria-label="Delete" onClick={async()=>{if(confirm('Delete this lead?')){try{await api.del(`/api/leads/${x.id}`);load()}catch(error){setFailure(error instanceof Error?error.message:"Lead could not be deleted")}}}}><Trash2 size={16}/></button></td></tr>)}</tbody></table>:<Empty>No leads have been saved.</Empty>}</section></>}
function CRM(){return <Leads/>}
function Appointments() {
  const {data, load, loading, error} = useLoad<{id:string; lead_id:string; starts_at:string; status:string}[]>('/api/appointments', []);
  const leads = useLoad<{id:string; name?:string; email?:string}[]>('/api/leads', []);
  const [day, setDay] = useState('');
  const [failure, setFailure] = useState('');
  const [pending, setPending] = useState(false);
  const asDate = (value: string) => new Date(/Z$|[+-]\d\d:\d\d$/.test(value) ? value : value + 'Z');
  const visible = data.filter(item => !day || new Intl.DateTimeFormat('en-CA', {year:'numeric', month:'2-digit', day:'2-digit'}).format(asDate(item.starts_at)) === day);
  async function cancel(id: string) {
    if (!window.confirm('Cancel this appointment?')) return;
    setFailure('');
    setPending(true);
    try { await api.post(`/api/appointments/${id}/cancel`); load(); }
    catch (error) { setFailure(error instanceof Error ? error.message : 'Cancellation failed'); }
    finally { setPending(false); }
  }
  return <section>
    <div className="sectionTitle"><h2>Appointment calendar</h2><label className="field">Filter by date<input type="date" value={day} onChange={event => setDay(event.target.value)}/></label>{day && <button className="secondary" onClick={() => setDay('')}>All dates</button>}</div>
    <ErrorBox text={error || failure}/>
    {loading ? <p role="status">Loading appointments…</p> : visible.length ? <div className="table-scroll"><table><thead><tr><th>Start</th><th>Customer</th><th>Status</th><th>Actions</th></tr></thead><tbody>
      {visible.map(item => {
        const lead = leads.data.find(record => record.id === item.lead_id);
        return <tr key={item.id}><td>{asDate(item.starts_at).toLocaleString()}</td><td>{lead?.name || lead?.email || item.lead_id}</td><td><span className="status">{item.status}</span></td><td>{item.status === 'confirmed' && <button className="secondary" disabled={pending} onClick={() => void cancel(item.id)}>Cancel</button>}</td></tr>;
      })}
    </tbody></table></div> : <Empty>{day ? 'No appointments on this date.' : 'No appointments yet. Confirm a proposed slot in Live Agent to add one.'}</Empty>}
  </section>;
}
function Knowledge(){const{data,load,error}=useLoad<any[]>('/api/documents',[]);const[busy,setBusy]=useState(false);return <section><h2>Knowledge base</h2><p>TXT and text-based PDF, maximum 5 MB. Uploaded content is chunked and indexed.</p><ErrorBox text={error}/><input type="file" accept=".txt,.pdf" disabled={busy} onChange={async e=>{const f=e.target.files?.[0];if(!f)return;setBusy(true);const fd=new FormData();fd.append('file',f);try{const r=await fetch('/api/documents',{method:'POST',body:fd});if(!r.ok)throw new Error((await r.json()).detail);load()}catch(e:any){alert(e.message)}finally{setBusy(false)}}}/>{data.length?<table><thead><tr><th>Document</th><th>Status</th><th>Chunks</th><th></th></tr></thead><tbody>{data.map(x=><tr><td>{x.filename}</td><td>{x.status}</td><td>{x.chunks}</td><td><button className="icon" onClick={async()=>{if(confirm('Delete document and its index?')){await api.del(`/api/documents/${x.id}`);load()}}}><Trash2 size={16}/></button></td></tr>)}</tbody></table>:<Empty>No knowledge documents indexed.</Empty>}</section>}
function Conversations(){const{data,loading}=useLoad<any[]>('/api/conversations',[]);return <section><h2>Conversation history</h2>{loading?<p>Loading…</p>:data.length?<div className="list">{data.map(x=><article><b>{x.id.slice(0,8)}</b><span>{x.language.toUpperCase()} · {x.status}</span><small>{new Date(x.started_at).toLocaleString()}</small>{x.summary&&<p>{x.summary.purpose} · Score {x.summary.lead_score}</p>}</article>)}</div>:<Empty>No conversation history.</Empty>}</section>}
function Analytics() {
  const {data, loading, error} = useLoad<{lead_distribution?:Record<string,number>; sentiment_distribution?:Record<string,number>}>('/api/analytics', {});
  if (loading) return <p role="status">Loading analytics…</p>;
  if (error) return <ErrorBox text={error}/>;
  return <div className="two">{[['Lead qualification', data.lead_distribution], ['Transcript sentiment', data.sentiment_distribution]].map(([label, distribution]) => {
    const rows = Object.entries(distribution ?? {}).map(([name,value]) => ({name,value}));
    return <section key={String(label)}><h2>{String(label)}</h2>
      {rows.some(row => row.value > 0) ? <>
        <ResponsiveContainer width="100%" height={240}><BarChart data={rows} accessibilityLayer><XAxis dataKey="name"/><YAxis allowDecimals={false}/><Tooltip/><Bar dataKey="value" fill="#2456cc" radius={[5,5,0,0]}/></BarChart></ResponsiveContainer>
        <dl className="customer-fields">{rows.map(row => <div key={row.name}><dt>{row.name}</dt><dd>{row.value}</dd></div>)}</dl>
      </> : <Empty>No records yet.</Empty>}
    </section>;
  })}</div>;
}
function Settings() {
  const {data, loading, error, load} = useLoad<Record<string, string | number>>('/api/settings', {});
  const [form, setForm] = useState(data);
  const [notice, setNotice] = useState('');
  const [failure, setFailure] = useState('');
  const [saving, setSaving] = useState(false);
  useEffect(() => setForm(data), [data]);
  async function save(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    setNotice('');
    setFailure('');
    try { await api.put('/api/settings', form); setNotice('Settings saved.'); load(); }
    catch (error) { setFailure(error instanceof Error ? error.message : 'Settings could not be saved'); }
    finally { setSaving(false); }
  }
  if (loading) return <p role="status">Loading settings…</p>;
  if (error) return <ErrorBox text={error}/>;
  return <section><h2>Business settings</h2><ErrorBox text={failure}/><form className="gridform" onSubmit={save}>
    {Object.entries(form).map(([key,value]) => <label key={key}>{key.replaceAll('_',' ')}
      {key === 'default_language' ? <select value={value} onChange={event => setForm({...form, [key]:event.target.value})}><option value="en">English</option><option value="hi">Hindi</option></select> :
      <input value={value} type={typeof value === 'number' ? 'number' : 'text'} required={typeof value === 'number'} onChange={event => setForm({...form, [key]:typeof value === 'number' ? Number(event.target.value) : event.target.value})}/>}
    </label>)}
    <button disabled={saving}>{saving ? 'Saving…' : 'Save settings'}</button>
  </form><p role="status">{notice}</p></section>;
}
function App() {
  const [page, setPage] = useState<Page>('Live Agent');
  const config = useLoad<{ai_configured: boolean}>('/api/config/status', {ai_configured: false});
  const content: Record<Page, React.ReactNode> = {Overview:<Overview/>, 'Live Agent':<LiveAgent active={page === 'Live Agent'}/>, Leads:<Leads/>, CRM:<CRM/>, Appointments:<Appointments/>, 'Knowledge Base':<Knowledge/>, Conversations:<Conversations/>, Analytics:<Analytics/>, Settings:<Settings/>};
  return <div className="shell">
    <a className="skip-link" href="#workspace">Skip to workspace</a>
    <aside>
      <div className="brand"><div><AudioLines size={23}/></div><span>SalesPilot AI<small>NovaCRM workspace</small></span></div>
      <nav aria-label="Workspace navigation">
        {[['Workspace', ['Live Agent','Overview','Conversations']], ['Sales operations', ['Leads','CRM','Appointments','Analytics']], ['Configuration', ['Knowledge Base','Settings']]].map(([group, names]) =>
          <div className="nav-group" key={String(group)}><p>{group}</p>{(names as Page[]).map(name => {
            const Icon = pages.find(([label]) => label === name)![1];
            return <button key={name} title={name} aria-label={name} aria-current={page === name ? 'page' : undefined} className={page === name ? 'active' : ''} onClick={() => setPage(name)}><Icon size={18}/><span>{name}</span></button>;
          })}</div>)}
      </nav>
      <footer><ShieldCheck size={16}/> Local workspace</footer>
    </aside>
    <main id="workspace" tabIndex={-1}>
      <header><div><small>NovaCRM / Workspace</small><h1>{page === 'Live Agent' ? 'Live Voice Agent' : page}</h1></div>
        <span className={`status ${config.data.ai_configured && !config.error ? 'is-live' : ''}`}><i/>{config.loading ? 'Checking connection' : config.error ? 'API unavailable' : config.data.ai_configured ? 'AI configured' : 'AI setup required'}</span>
      </header>
      <div hidden={page !== 'Live Agent'}>{content['Live Agent']}</div>
      {page !== 'Live Agent' && content[page]}
    </main>
  </div>;
}
createRoot(document.getElementById('root')!).render(<App/>);
import {AudioLines, Headphones, Radio, ShieldCheck} from 'lucide-react';
import {monitorMicrophone} from './microphone';
import './workspace.css';
