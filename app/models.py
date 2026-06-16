from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app.database import Base

class Team(Base):
     __tablename__ = "teams"
     id = Column(Integer, primary_key=True, index=True)
     name = Column(String, index=True)
     logo_url = Column(String, nullable=True)


class Match(Base):
     __tablename__ = "matches"
     id = Column(Integer, primary_key=True, index=True)
     home_team_id = Column(Integer, ForeignKey("teams.id"))
     away_team_id = Column(Integer, ForeignKey("teams.id"))
     status = Column(String)
     minute = Column(Integer, default=0)
     home_score = Column(Integer, default=0)
     away_score = Column(Integer, default=0)
     started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

     home_team = relationship("Team", foreign_keys=[home_team_id])
     away_team = relationship("Team", foreign_keys=[away_team_id])
     statistics = relationship("Statistic", back_populates="match")
     alerts = relationship("Alert", back_populates="match")

class Statistic(Base):
     __tablename__ = "statistics"
     id = Column(Integer, primary_key=True, index=True)
     match_id = Column(Integer, ForeignKey("matches.id"))
     team_id = Column(Integer, ForeignKey("teams.id"))
     shots_on_target = Column(Integer, default=0)
     corners = Column(Integer, default=0)
     dangerous_attacks = Column(Integer, default=0)
     expected_goals = Column(Float, default=0.0)
     timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

     match = relationship("Match", back_populates="statistics")

class Alert(Base):
     __tablename__ = "alerts"
     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
     match_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("matches.id"))
     triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
     rules_fired: Mapped[Optional[str]] = mapped_column(String)
     score: Mapped[float] = mapped_column(Float, default=0.0)
     match = relationship("Match", back_populates="alerts")
     success: Mapped[int] = mapped_column(Integer, default=0)  # 0 = Pendente, 1 = Green, -1 = Red
     goal_minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Em qual minuto saiu o gol (se saiu)
     alert_minute: Mapped[int] = mapped_column(Integer, default=0)  # Em qual minuto o alerta foi disparado