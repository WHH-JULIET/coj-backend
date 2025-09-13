from app.db.session import SessionLocal
from app.models.problems import Problem

db = SessionLocal()
try:
    print("Connected to DB, querying Problems...")
    problems = db.query(Problem).all()
    print(f"Found {len(problems)} problems.")
    for problem in problems:
        print(problem.problem_id, problem.difficulty, problem.prob_stmt)
except Exception as e:
    print("Error:", e)
finally:
    db.close()