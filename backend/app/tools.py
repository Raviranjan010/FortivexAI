import time
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session
from . import models, services

class SearchArgs(BaseModel): query: str = Field(min_length=2, max_length=500)
class QualifyArgs(BaseModel): budget: str | None=None; authority: str | None=None; requirements: str | None=None; timeline: str | None=None
class SentimentArgs(BaseModel): text: str = Field(min_length=1, max_length=4000)

SCHEMAS={"search_knowledge_base":SearchArgs,"get_product_information":SearchArgs,"qualify_lead":QualifyArgs,"analyze_sentiment":SentimentArgs}

def execute(db: Session, session_id: str, name: str, arguments: dict):
    if not db.get(models.Conversation, session_id): raise ValueError("Invalid conversation session")
    if name not in SCHEMAS: raise ValueError("Unknown tool")
    start=time.perf_counter()
    try:
        args=SCHEMAS[name].model_validate(arguments)
        if name in {"search_knowledge_base","get_product_information"}: result={"sources":services.retrieve(db,args.query)}
        elif name=="qualify_lead":
            score,classification,breakdown=services.bant(args.model_dump()); result={"score":score,"classification":classification,"breakdown":breakdown}
        else: result={"sentiment":services.sentiment(args.text)}
        status="success"
    except ValidationError as exc:
        result={"error":"Invalid tool arguments","details":exc.errors(include_input=False)}; status="failed"
    event=models.ToolEvent(conversation_id=session_id,tool_name=name,status=status,result=result,duration_ms=(time.perf_counter()-start)*1000)
    db.add(event); db.commit(); db.refresh(event)
    return result,event
