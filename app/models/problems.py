
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Problem(Base):
    __tablename__ = "problems"
    problem_id = Column(String, primary_key=True)
    difficulty = Column(Integer)
    prob_stmt = Column(String)

class ProblemTopic(Base):
    __tablename__ = "problem_topics"
    topic_id = Column(String, primary_key=True)
    topic_name = Column(String(100), unique=True)

class ProblemTopicMap(Base):
    __tablename__ = "problem_topic_map"
    id = Column(String, primary_key=True)
    problem_id = Column(String, ForeignKey("Problems.problem_id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(String, ForeignKey("Problem_Topics.topic_id", ondelete="CASCADE"), nullable=False)
    __table_args__ = (UniqueConstraint('problem_id', 'topic_id', name='_problem_topic_uc'),)