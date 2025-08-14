from app.core.database import engine
from app.models.database_models import Base

def init_db():
    """데이터베이스 테이블 생성"""
    print("데이터베이스 테이블을 생성합니다...")
    Base.metadata.create_all(bind=engine)
    print("데이터베이스 테이블 생성 완료!")

if __name__ == "__main__":
    init_db() 