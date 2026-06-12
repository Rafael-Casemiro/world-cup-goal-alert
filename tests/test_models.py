import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Team, Match

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def db_session():
     Base.metadata.create_all(bind=engine)
     session = TestingSessionLocal()
     yield session
     session.close()
     Base.metadata.drop_all(bind=engine)


def test_create_team(db_session):
     team = Team(name="Brasil", logo_url="https://url.com/br.png")
     db_session.add(team)
     db_session.commit()

     assert team.id is not None
     assert team.name == "Brasil"

def test_create_match(db_session):
     team1 = Team(name="Brasil")
     team2 = Team(name="Argentina")
     db_session.add_all([team1, team2])
     db_session.commit()

     match = Match(home_team_id=team1.id,away_team_id=team2.id, status="LIVE")
     db_session.add(match)
     db_session.commit()

     assert match.id is not None
     assert match.home_team.name == "Brasil"
     assert match.away_team.name == "Argentina"