# Writer-Editor Review Loop Agent System

LangGraph를 사용한 Writer-Editor 협업 에이전트 시스템. Writer가 초안을 작성하면 Editor가 피드백을 제공하고, 사용자 개입을 통해 반복적으로 개선하는 Human-in-the-Loop 패턴을 구현합니다.

## 🎯 프로젝트 목표

- **에이전트 간 검토 루프(Review Loop)** 패턴 학습
- **상태(State) 공유** 및 관리 방법 이해
- **Human-in-the-Loop** 패턴 구현 실습

## 🛠 기술 스택

- Python 3.10+
- LangGraph (에이전트 워크플로우)
- LM Studio (로컬 LLM - Qwen 모델)
- SQLite (상태 영속화)
- Rich (CLI 인터페이스)

## 🏗 시스템 아키텍처

### Simple Mode (Writer-Editor)
```
START → Writer → Editor → User Intervention → [조건 분기]
                                                    ↓
                                    [계속] ─────→ Writer (루프)
                                    [중단] ─────→ END
```

### Multi-Agent Mode (6 Agents)
```
START → Business Analyst → Content Strategist → Outline Reviewer
     → [Outline Review Loop] → User Approval → Web Search
     → Writer → Editor → [Draft Review Loop] → END

6개 전문 에이전트:
1. Business Analyst - 사용자 의도 분석
2. Content Strategist - 템플릿 기반 목차 작성
3. Outline Reviewer - 목차 품질 검토 (Self-Review)
4. Web Search Agent - 웹 검색 및 리서치
5. Writer - 목차와 리서치 기반 본문 작성
6. Editor - 편집 및 최종 검토
```

## 📦 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/writer-editor-agent.git
cd writer-editor-agent
```

### 2. 가상 환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 패키지 설치
```bash
pip install -e ".[dev]"
```

### 4. 환경 변수 설정
`.env.example`을 복사하여 `.env` 파일 생성:
```bash
cp .env.example .env
```

`.env` 파일 편집:
```env
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=qwen
WRITER_TEMPERATURE=0.8
EDITOR_TEMPERATURE=0.3
MAX_TOKENS=2000
MAX_ITERATIONS=10
CHECKPOINT_DB_PATH=data/checkpoints.sqlite
```

## 🚀 사용 방법

### 1. LM Studio 설정
1. [LM Studio](https://lmstudio.ai/) 다운로드 및 설치
2. Qwen 모델 다운로드
3. 로컬 서버 시작 (포트 1234)

### 2. 연결 테스트
```bash
python main.py --test-connection
```

### 3. 애플리케이션 실행
```bash
# 기본 실행 (Multi-Agent 모드)
python main.py

# 주제 지정
python main.py --topic "AI의 미래"

# Simple 모드 (Writer-Editor만)
python main.py --mode simple

# 이전 세션 재개
python main.py --thread-id "session-id"

# 반복 횟수 커스터마이징
python main.py --max-iterations 5 --max-outline-revisions 2
```

## 📚 주요 기능

### ✅ 구현 완료 (100%)

**핵심 에이전트 (6개)**
- Business Analyst - 사용자 의도 분석 (JSON 출력)
- Content Strategist - 템플릿 기반 목차 생성
- Outline Reviewer - 자동 목차 검토 (Self-Review 패턴)
- Web Search Agent - DuckDuckGo/Tavily/Serper 통합 검색
- Writer - 목차 및 리서치 기반 작성 (3가지 모드)
- Editor - 구조화된 피드백 제공

**워크플로우 시스템**
- Simple 워크플로우 (Writer-Editor, 하위 호환)
- Multi-Agent 워크플로우 (6개 에이전트 협업)
- 목차 검토 루프 (최대 3회)
- 초안 검토 루프 (최대 10회)
- 2개의 Human-in-the-Loop 개입 포인트
- SQLite 기반 세션 영속화 및 재개

**템플릿 및 도구**
- 문서 유형별 템플릿 (블로그, 기술문서, 마케팅)
- 통합 웹 검색 인터페이스
- 에이전트별 최적화된 Temperature
- Rich 기반 아름다운 CLI

**인프라**
- 확장된 상태 스키마 (멀티 에이전트 지원)
- Pydantic 기반 설정 관리
- LM Studio 클라이언트 래퍼
- 완전한 모듈화 구조

### 🔮 향후 계획
- 유닛 테스트 및 통합 테스트
- 웹 UI (FastAPI + React)
- 추가 템플릿 (이메일, 소셜 미디어 등)
- 성능 메트릭 및 분석

## 📖 문서

- [구현 가이드](docs/implementation-guide.md) - 상세한 구현 내용 및 코드
- [계획 문서](.claude/plans/) - 전체 구현 계획

## 🧪 테스트

```bash
# 유닛 테스트 실행
pytest tests/

# 커버리지 포함
pytest --cov=src tests/
```

## 🎓 학습 포인트

### 1. 에이전트 간 검토 루프
조건부 엣지를 사용한 순환 워크플로우 구현

### 2. 상태 공유
```python
# Reducer 패턴으로 리스트 누적
iterations: Annotated[List[ReviewIteration], add]
```

### 3. Human-in-the-Loop
```python
# interrupt()로 실행 중단 및 사용자 입력 대기
user_decision = interrupt(prompt)
```

## 🤝 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 글

- [LangGraph](https://github.com/langchain-ai/langgraph) - 에이전트 워크플로우 프레임워크
- [LM Studio](https://lmstudio.ai/) - 로컬 LLM 실행 환경

## 📞 문의

프로젝트에 대한 질문이나 제안이 있으시면 이슈를 등록해주세요.
