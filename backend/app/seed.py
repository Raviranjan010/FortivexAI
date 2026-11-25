from .database import Base,SessionLocal,engine
from . import models
CATALOG="""NovaCRM is a fictional B2B customer relationship platform. Starter costs INR 1,499 per user per month, supports up to 10 users, lead management, email tracking, and standard support. Growth costs INR 2,999 per user per month and adds workflow automation, analytics, API access, and priority support. Enterprise pricing is custom and adds SSO, audit logs, a dedicated success manager, and configurable retention. A 14-day trial is available without a credit card. Monthly plans may be cancelled before the next billing date; fees already paid are non-refundable. Standard support responds within two business days. Priority support targets one business day. NovaCRM does not promise guaranteed sales results."""
def seed():
    Base.metadata.create_all(engine); db=SessionLocal()
    if not db.query(models.Document).filter_by(filename="novacrm_catalog.txt").first():
        doc=models.Document(filename="novacrm_catalog.txt"); db.add(doc); db.flush()
        for i,part in enumerate([CATALOG[:700],CATALOG[650:]]):
            if part: db.add(models.Chunk(document_id=doc.id,ordinal=i,text=part))
        db.commit()
    db.close()
if __name__=="__main__": seed()
