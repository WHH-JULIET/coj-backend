from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.problems import Problem, ProblemTopicMap
from app.models.schemas import ProblemCreate, ProblemOut
import uuid

router = APIRouter()

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


@router.post("/", response_model=ProblemOut)
def create_problem(problem: ProblemCreate, db: Session = Depends(get_db)):
	problem_id = str(uuid.uuid4())
	db_problem = Problem(
		problem_id=problem_id,
		difficulty=problem.difficulty,
		prob_stmt=problem.prob_stmt
	)
	db.add(db_problem)
	db.commit()
	db.refresh(db_problem)

	# Link topics
	for topic_id in problem.topic_ids:
		db_topic_map = ProblemTopicMap(
			id=str(uuid.uuid4()),
			problem_id=problem_id,
			topic_id=topic_id
		)
		db.add(db_topic_map)
	db.commit()

	return ProblemOut(
		problem_id=db_problem.problem_id,
		difficulty=db_problem.difficulty,
		prob_stmt=db_problem.prob_stmt,
		topic_ids=problem.topic_ids
	)

# GET route to fetch all problems

@router.get("/", response_model=list[ProblemOut])
def get_problems(db: Session = Depends(get_db)):
    problems = db.query(Problem).all()
    result = []
    for problem in problems:
        topic_maps = db.query(ProblemTopicMap).filter_by(problem_id=problem.problem_id).all()
        topic_ids = [str(tm.topic_id) for tm in topic_maps] 
        result.append(ProblemOut(
            problem_id=str(problem.problem_id), 
            difficulty=problem.difficulty,
            prob_stmt=problem.prob_stmt,
            topic_ids=topic_ids
        ))
    return result