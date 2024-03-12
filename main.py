from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import NullPool

from sqlalchemy.orm import Session
from typing import List, Union
from typing_extensions import Annotated
from decimal import Decimal

from models import Bet, Base, BetState


app = FastAPI()

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:pass@postgres/bets"


engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    future=True,
    poolclass=NullPool
    )


class BetRequest(BaseModel):
    event_id: str
    amount: Annotated[Decimal, Field(decimal_places=2, gt=0)]


class BetResponse(BaseModel):
    id: Union[int, None]
    message: str

def get_db():
    return async_sessionmaker(bind=engine, expire_on_commit=False)


@app.post("/bets", response_model=BetResponse)
async def create_bet(bet: BetRequest, db: Session = Depends(get_db)):
    async with db() as session:
        db_bet = Bet(event_id=bet.event_id, amount=bet.amount)
        session.add(db_bet)
        try:
            await session.commit()
            await session.refresh(db_bet)
            return {"id": db_bet.id, "message":"bet added"}
        except IntegrityError as e:
            return {"id": None, "message": e.args[0]}        


class BetResp(BaseModel):
    id: int
    event_id: str
    status: str


@app.get("/bets")
async def get_bets(db: Session = Depends(get_db)) -> List[BetResp]:
    async with db() as session:
        result = await session.execute(Bet.__table__.select())
        result = result.all()
        return result


class EventsRequest(BaseModel):
    status: str


@app.put("/events/{event_id}")
async def update_event_status(event_id: str, event: EventsRequest, db: Session = Depends(get_db)):
    async with db() as session:
        await session.execute(
            Bet.__table__.update().
            where(Bet.event_id == event_id).
            values(status=event.status)
        )
        await session.commit()
    return {"message": "Event status updated successfully"}


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
