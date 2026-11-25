import io, re
from datetime import datetime, timezone
from pathlib import Path
from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pypdf import PdfReader
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from . import ai, models, schemas, services, tools
from .config import get_settings
from .database import Base, engine, get_db

cfg=get_settings(); Base.metadata.create_all(engine)
app=FastAPI(title="SalesPilot AI API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=[cfg.frontend_origin],allow_credentials=False,allow_methods=["*"],allow_headers=["*"])

@app.get("/api/health")
def health(): return {"status":"ok","database":"connected","service":cfg.app_name}
@app.get("/api/config/status")
def config_status(): return {"ai_configured":bool(cfg.gemini_api_key),"model":cfg.gemini_model,"timezone":cfg.business_timezone}

@app.post("/api/conversations",response_model=schemas.SessionOut)
def create_session(body:schemas.SessionCreate,db:Session=Depends(get_db)):
    row=models.Conversation(language=body.language); db.add(row); db.commit(); db.refresh(row); return row
@app.get("/api/conversations",response_model=list[schemas.SessionOut])
def conversations(db:Session=Depends(get_db)): return db.scalars(select(models.Conversation).order_by(models.Conversation.started_at.desc())).unique().all()
@app.get("/api/conversations/{sid}",response_model=schemas.SessionOut)
def conversation(sid:str,db:Session=Depends(get_db)):
    row=db.get(models.Conversation,sid)
    if not row: raise HTTPException(404,"Conversation not found")
    return row

@app.post("/api/conversations/{sid}/messages",response_model=schemas.ChatOut)
def chat(sid:str,body:schemas.ChatIn,db:Session=Depends(get_db)):
    session=db.get(models.Conversation,sid)
    if not session or session.status!="active": raise HTTPException(404,"Active conversation not found")
    user=models.Message(conversation_id=sid,role="user",content=body.content); db.add(user); db.commit()
    sources=services.retrieve(db,body.content,cfg.rag_top_k)
    history=[{"role":m.role,"content":m.content} for m in session.messages[-12:]]
    try: result=ai.get_provider().respond(history,sources,session.language)
    except RuntimeError as exc: raise HTTPException(503,str(exc))
    events=[]
    for call in result.tool_calls[:3]:
        try:
            outcome,event=tools.execute(db,sid,call.name,call.arguments); events.append({"tool_name":event.tool_name,"status":event.status,"result":outcome,"duration_ms":event.duration_ms,"timestamp":event.created_at.isoformat()})
        except ValueError as exc:
            events.append({"tool_name":call.name,"status":"failed","result":{"error":str(exc)}})
    if events:
        history.append({"role":"system","content":"Observable tool results: "+str(events)})
        try: result=ai.get_provider().respond(history,sources,session.language)
        except RuntimeError as exc: raise HTTPException(503,str(exc))
    session.extracted={**session.extracted,**{k:v for k,v in result.extracted.items() if v not in (None,"")}}
    assistant=models.Message(conversation_id=sid,role="assistant",content=result.response); db.add(assistant); db.commit()
    return {"session_id":sid,"response":result.response,"sources":sources,"tool_events":events}

@app.post("/api/conversations/{sid}/end",response_model=schemas.SessionOut)
def end_session(sid:str,db:Session=Depends(get_db)):
    row=db.get(models.Conversation,sid)
    if not row: raise HTTPException(404,"Conversation not found")
    row.status="ended"; row.ended_at=datetime.now(timezone.utc)
    lead=db.scalar(select(models.Lead).where(models.Lead.conversation_id==sid))
    row.summary={"customer":lead.name if lead else row.extracted.get("name"),"purpose":"NovaCRM sales enquiry","product_interest":lead.product_interest if lead else row.extracted.get("product_interest"),"requirements":lead.requirements if lead else row.extracted.get("requirements"),"budget":lead.budget if lead else row.extracted.get("budget"),"timeline":lead.timeline if lead else row.extracted.get("timeline"),"objections":lead.objections if lead else None,"sentiment":lead.sentiment if lead else "Neutral","lead_score":lead.score if lead else 0,"actions":[e.tool_name for e in db.scalars(select(models.ToolEvent).where(models.ToolEvent.conversation_id==sid))],"appointment_status":"confirmed" if lead and db.scalar(select(models.Appointment).where(models.Appointment.lead_id==lead.id,models.Appointment.status=="confirmed")) else "not booked","recommended_follow_up":"Review the enquiry and contact the customer if consent was provided."}
    db.commit(); db.refresh(row); return row

@app.get("/api/leads",response_model=list[schemas.LeadOut])
def leads(q:str="",status:str="",db:Session=Depends(get_db)):
    stmt=select(models.Lead).order_by(models.Lead.updated_at.desc())
    if q: stmt=stmt.where(or_(models.Lead.name.ilike(f"%{q}%"),models.Lead.email.ilike(f"%{q}%"),models.Lead.company.ilike(f"%{q}%")))
    if status: stmt=stmt.where(models.Lead.status==status)
    return db.scalars(stmt).all()
@app.post("/api/leads",response_model=schemas.LeadOut)
def add_lead(body:schemas.LeadIn,db:Session=Depends(get_db)): return services.create_lead(db,body.model_dump())
@app.put("/api/leads/{lid}",response_model=schemas.LeadOut)
def update_lead(lid:str,body:schemas.LeadIn,db:Session=Depends(get_db)):
    row=db.get(models.Lead,lid)
    if not row: raise HTTPException(404,"Lead not found")
    for k,v in body.model_dump(exclude_unset=True).items(): setattr(row,k,v)
    score,c,b=services.bant(body.model_dump()); row.score,row.classification,row.score_breakdown=score,c,b; db.commit(); db.refresh(row); return row
@app.delete("/api/leads/{lid}",status_code=204)
def delete_lead(lid:str,db:Session=Depends(get_db)):
    row=db.get(models.Lead,lid)
    if not row: raise HTTPException(404,"Lead not found")
    db.delete(row); db.commit()
@app.get("/api/leads-export.csv")
def export_leads(db:Session=Depends(get_db)):
    out=io.StringIO(); w=__import__('csv').writer(out); w.writerow(["name","email","company","status","score","classification"])
    for x in db.scalars(select(models.Lead)): w.writerow([x.name,x.email,x.company,x.status,x.score,x.classification])
    return StreamingResponse(iter([out.getvalue()]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=leads.csv"})

@app.get("/api/appointments",response_model=list[schemas.AppointmentOut])
def appointments(db:Session=Depends(get_db)): return db.scalars(select(models.Appointment).order_by(models.Appointment.starts_at)).all()
@app.get("/api/appointments/slots")
def available_slots(day:datetime=Query(...),db:Session=Depends(get_db)): return {"slots":services.slots(db,day)}
@app.post("/api/appointments",response_model=schemas.AppointmentOut)
def create_appointment(body:schemas.BookingIn,db:Session=Depends(get_db)):
    try:return services.book(db,body.lead_id,body.starts_at,body.confirmed,body.idempotency_key)
    except ValueError as exc: raise HTTPException(409,str(exc))
@app.post("/api/appointments/{aid}/cancel",response_model=schemas.AppointmentOut)
def cancel(aid:str,db:Session=Depends(get_db)):
    row=db.get(models.Appointment,aid)
    if not row: raise HTTPException(404,"Appointment not found")
    row.status="cancelled"; db.commit(); db.refresh(row); return row

def chunks(text,size=800,overlap=100):
    clean=re.sub(r"\s+"," ",text).strip(); return [clean[i:i+size] for i in range(0,len(clean),size-overlap) if clean[i:i+size].strip()]
@app.get("/api/documents")
def documents(db:Session=Depends(get_db)): return [{"id":d.id,"filename":d.filename,"status":d.status,"chunks":len(d.chunks)} for d in db.scalars(select(models.Document)).unique()]
@app.post("/api/documents")
async def upload(file:UploadFile=File(...),db:Session=Depends(get_db)):
    suffix=Path(file.filename or "").suffix.lower()
    if suffix not in {".txt",".pdf"}: raise HTTPException(415,"Only TXT and PDF files are supported")
    data=await file.read(cfg.max_upload_mb*1024*1024+1)
    if len(data)>cfg.max_upload_mb*1024*1024: raise HTTPException(413,"File is too large")
    try:text=data.decode("utf-8") if suffix==".txt" else "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages)
    except Exception: raise HTTPException(422,"Document text could not be extracted")
    safe=Path(file.filename or "document").name; doc=models.Document(filename=safe); db.add(doc); db.flush()
    for i,value in enumerate(chunks(text)): db.add(models.Chunk(document_id=doc.id,ordinal=i,text=value))
    db.commit(); return {"id":doc.id,"filename":safe,"status":"indexed"}
@app.delete("/api/documents/{did}",status_code=204)
def delete_document(did:str,db:Session=Depends(get_db)):
    row=db.get(models.Document,did)
    if not row: raise HTTPException(404,"Document not found")
    db.delete(row); db.commit()
@app.get("/api/retrieval")
def search_knowledge(q:str=Query(min_length=2),db:Session=Depends(get_db)): return {"results":services.retrieve(db,q,cfg.rag_top_k)}
@app.get("/api/analytics")
def get_analytics(db:Session=Depends(get_db)): return services.analytics(db)
@app.get("/api/settings")
def get_settings_api(db:Session=Depends(get_db)): return services.business_settings(db)
@app.put("/api/settings")
def put_settings(body:schemas.SettingsIn,db:Session=Depends(get_db)):
    row=db.get(models.Setting,"business") or models.Setting(key="business",value={}); row.value=body.model_dump(); db.add(row); db.commit(); return row.value
