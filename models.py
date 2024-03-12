#from enum import Enum
from sqlalchemy import Column, Integer, String, Numeric, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

BetState = Enum("PENDING", "WIN", "LOSE", name="enum_bet_state")


class Bet(Base):
    __tablename__ = "bets"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    amount = Column(Numeric(precision=10, scale=2))
    status = Column(BetState, default="PENDING")



