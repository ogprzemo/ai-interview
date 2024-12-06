from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
DATABASE_URL = "sqlite:///./interview.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    correct_example = Column(String, nullable=False)

initial_questions = [
    {
        "id": 1,
        "text": "Wann kommt meine Tochter? Ich vermisse sie schon. Können wir sie heute anrufen",
        "correct_example": "Ihre Tochter Helena kommt morgen. Wir können sie heute anrufen, wenn Sie möchten. Bitte machen Sie sich keine Sorgen, Sie werden sie schon morgen sehen.",
    },
    {
        "id": 2,
        "text": "Ich möchte aufstehen. Bring mir dieses Gerät näher, mit dem du mich umsetzen kannst. Wie hieß es noch?",
        "correct_example": "Das Gerät heißt Patientenlifter. Ich werde Sie damit umsetzen. In einem Moment können Sie dann im Rollstuhl sitzen.",
    },
]

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    for question in initial_questions:
        db_question = Question(
            id=question["id"],
            text=question["text"],
            correct_example=question["correct_example"],
        )
        db.add(db_question)
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized and questions added!")