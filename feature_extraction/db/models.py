from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Paper(Base):
    __tablename__ = 'paper'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    link = Column(String(255), nullable=False)
    conf = Column(String(15), nullable=False)
    code_link = Column(String(255), nullable=False)
    repo_name = Column(String(255), nullable=False)
    repo_owner = Column(String(127), nullable=False)
    year = Column(Integer, nullable=False)


class Repo(Base):
    __tablename__ = 'repo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, nullable=False)
    repo_name = Column(String(127), nullable=False)
    repo_owner = Column(String(127), nullable=False)
    created_at = Column(DateTime, nullable=False)
    stars_count = Column(Integer, nullable=False)
    forks_count = Column(Integer, nullable=False)
    subscribers_count = Column(Integer, nullable=False)
    network_count = Column(Integer, nullable=False)
    language = Column(String(31))
    license = Column(String(63))
    organization = Column(String(31))


class StarEvent(Base):
    __tablename__ = 'star_event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    repo_name = Column(String(255), nullable=False)
    repo_owner = Column(String(127), nullable=False)
    star_user = Column(String(255), nullable=False)
    timestamp = Column(DateTime, nullable=False)


def model_from_name(model_name):
    m = {
        'paper': Paper,
        'repo': Repo,
        'star_event': StarEvent
    }

    try:
        return m[model_name]
    except KeyError:
        raise
