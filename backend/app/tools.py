import time
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session
from . import models, services

class SearchArgs(BaseModel): query: str = Field(min_length=2, max_length=500)
class QualifyArgs(BaseModel): budget: str | None=None; authority: str | None=None; requirements: str | None=None; timeline: str | None=None
class SentimentArgs(BaseModel): text: str = Field(min_length=1, max_length=4000)
class ProfileArgs(BaseModel): name:str|None=None; email:str|None=None; phone:str|None=None; company:str|None=None; company_size:int|None=None; product_interest:str|None=None; requirements:str|None=None; budget:str|None=None; timeline:str|None=None; authority:str|None=None; objections:str|None=None; purchase_intent:str|None=None
class AvailabilityArgs(BaseModel): day: datetime
class ProposalArgs(BaseModel): starts_at: datetime; lead_id: str|None=None
class ConfirmArgs(BaseModel): lead_id:str; starts_at:datetime; confirmed:bool; idempotency_key:str|None=None
class SaveLeadArgs(ProfileArgs): pass
class SummaryArgs(BaseModel): customer:str|None=None; purpose:str|None=None; product_interest:str|None=None; requirements:str|None=None; budget:str|None=None; timeline:str|None=None; objections:str|None=None; sentiment:str="Neutral"; recommended_follow_up:str|None=None

SCHEMAS={"search_knowledge_base":SearchArgs,"get_product_information":SearchArgs,"update_customer_profile":ProfileArgs,"qualify_lead":QualifyArgs,"analyze_sentiment":SentimentArgs,"check_appointment_availability":AvailabilityArgs,"propose_appointment":ProposalArgs,"confirm_appointment":ConfirmArgs,"save_lead_to_crm":SaveLeadArgs,"generate_call_summary":SummaryArgs}

def execute(db: Session, session_id: str, name: str, arguments: dict):
    if not db.get(models.Conversation, session_id): raise ValueError("Invalid conversation session")
    if name not in SCHEMAS: raise ValueError("Unknown tool")
    start=time.perf_counter()
    try:
        args=SCHEMAS[name].model_validate(arguments)
        if name in {"search_knowledge_base","get_product_information"}: result={"sources":services.retrieve(db,args.query)}
        elif name=="qualify_lead":
            score,classification,breakdown=services.bant(args.model_dump()); result={"score":score,"classification":classification,"breakdown":breakdown}
        elif name=="analyze_sentiment": result={"sentiment":services.sentiment(args.text)}
        elif name=="update_customer_profile":
            session=db.get(models.Conversation,session_id); session.extracted={**session.extracted,**{k:v for k,v in args.model_dump().items() if v is not None}}; db.flush(); result={"updated_fields":[k for k,v in args.model_dump().items() if v is not None]}
        elif name=="check_appointment_availability": result={"slots":[x.isoformat() for x in services.slots(db,args.day)[:8]]}
        elif name=="propose_appointment": result={"proposed":True,"starts_at":args.starts_at.isoformat(),"requires_explicit_confirmation":True}
        elif name=="confirm_appointment":
            appointment=services.book(db,args.lead_id,args.starts_at,args.confirmed,args.idempotency_key); result={"appointment_id":appointment.id,"status":appointment.status,"starts_at":appointment.starts_at.isoformat()}
        elif name=="save_lead_to_crm":
            lead=services.create_lead(db,{**args.model_dump(),"conversation_id":session_id}); result={"lead_id":lead.id,"saved":True,"score":lead.score,"classification":lead.classification}
        else:
            session=db.get(models.Conversation,session_id); session.summary=args.model_dump(); db.flush(); result={"summary_saved":True}
        status="success"
    except ValidationError as exc:
        result={"error":"Invalid tool arguments","details":exc.errors(include_input=False)}; status="failed"
    event=models.ToolEvent(conversation_id=session_id,tool_name=name,status=status,result=result,duration_ms=(time.perf_counter()-start)*1000)
    db.add(event); db.commit(); db.refresh(event)
    return result,event
