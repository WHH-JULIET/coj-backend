from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
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


# -------------------- CREATE --------------------
@router.post("/", response_model=ProblemOut, status_code=201)
def create_problem(problem: ProblemCreate, db: Session = Depends(get_db)):
    problem_id = uuid.uuid4()
    db_problem = Problem(
        problem_id=problem_id,
        difficulty=problem.difficulty,
        prob_stmt=problem.prob_stmt
    )
    db.add(db_problem)

    topic_ids = []
    try:
        topic_id_list = problem.topic_ids if problem.topic_ids is not None else []
        for topic_id in topic_id_list:
            try:
                topic_uuid = uuid.UUID(str(topic_id))
            except ValueError:
                db.rollback()
                raise HTTPException(status_code=400, detail=f"Invalid topic_id: {topic_id}")
            db_topic_map = ProblemTopicMap(
                id=uuid.uuid4(),
                problem_id=problem_id,
                topic_id=topic_uuid
            )
            db.add(db_topic_map)
            topic_ids.append(str(topic_uuid))

        db.commit()
        db.refresh(db_problem)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate problem-topic mapping or invalid topic_id")

    return ProblemOut(
        problem_id=str(db_problem.problem_id),
        difficulty=db_problem.difficulty,
        prob_stmt=db_problem.prob_stmt,
        topic_ids=topic_ids
    )


# -------------------- READ --------------------
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


# -------------------- UPDATE (PUT) --------------------
@router.put("/{problem_id}", response_model=ProblemOut)
def update_problem(problem_id: str, problem: ProblemCreate, db: Session = Depends(get_db)):
    db_problem = db.query(Problem).filter_by(problem_id=uuid.UUID(problem_id)).first()
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    db_problem.difficulty = problem.difficulty
    db_problem.prob_stmt = problem.prob_stmt

    # Remove old mappings
    db.query(ProblemTopicMap).filter_by(problem_id=db_problem.problem_id).delete()

    topic_ids = []
    try:
        for topic_id in problem.topic_ids:
            topic_uuid = uuid.UUID(str(topic_id))
            db_topic_map = ProblemTopicMap(
                id=uuid.uuid4(),
                problem_id=db_problem.problem_id,
                topic_id=topic_uuid
            )
            db.add(db_topic_map)
            topic_ids.append(str(topic_uuid))

        db.commit()
        db.refresh(db_problem)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate problem-topic mapping or invalid topic_id")

    return ProblemOut(
        problem_id=str(db_problem.problem_id),
        difficulty=db_problem.difficulty,
        prob_stmt=db_problem.prob_stmt,
        topic_ids=topic_ids
    )


# -------------------- PARTIAL UPDATE (PATCH) --------------------
@router.patch("/{problem_id}", response_model=ProblemOut)
def patch_problem(
    problem_id: str,
    problem_update: dict = Body(...),
    db: Session = Depends(get_db)
):
    db_problem = db.query(Problem).filter_by(problem_id=uuid.UUID(problem_id)).first()
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    topic_ids = []
    try:
        # Update only provided fields
        if "difficulty" in problem_update:
            db_problem.difficulty = problem_update["difficulty"]

        if "prob_stmt" in problem_update:
            db_problem.prob_stmt = problem_update["prob_stmt"]

        if "topic_ids" in problem_update:
            db.query(ProblemTopicMap).filter_by(problem_id=db_problem.problem_id).delete()

            for topic_id in problem_update["topic_ids"]:
                try:
                    topic_uuid = uuid.UUID(str(topic_id))
                except ValueError:
                    db.rollback()
                    raise HTTPException(status_code=400, detail=f"Invalid topic_id: {topic_id}")
                db_topic_map = ProblemTopicMap(
                    id=uuid.uuid4(),
                    problem_id=db_problem.problem_id,
                    topic_id=topic_uuid
                )
                db.add(db_topic_map)
                topic_ids.append(str(topic_uuid))
        else:
            # keep existing topics if not updated
            topic_maps = db.query(ProblemTopicMap).filter_by(problem_id=db_problem.problem_id).all()
            topic_ids = [str(tm.topic_id) for tm in topic_maps]

        db.commit()
        db.refresh(db_problem)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate problem-topic mapping or invalid topic_id")

    return ProblemOut(
        problem_id=str(db_problem.problem_id),
        difficulty=db_problem.difficulty,
        prob_stmt=db_problem.prob_stmt,
        topic_ids=topic_ids
    )


# -------------------- DELETE --------------------
@router.delete("/{problem_id}", status_code=204)
def delete_problem(problem_id: str, db: Session = Depends(get_db)):
    db_problem = db.query(Problem).filter_by(problem_id=uuid.UUID(problem_id)).first()
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    db.query(ProblemTopicMap).filter_by(problem_id=db_problem.problem_id).delete()
    db.delete(db_problem)
    db.commit()
    return
