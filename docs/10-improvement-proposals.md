# 프로젝트 개선 제안서

## 📋 목차

1. [현재 시스템 평가](#현재-시스템-평가)
2. [우선순위별 개선 제안](#우선순위별-개선-제안)
3. [기술적 개선](#기술적-개선)
4. [기능 확장](#기능-확장)
5. [사용자 경험 개선](#사용자-경험-개선)
6. [성능 최적화](#성능-최적화)
7. [품질 보증](#품질-보증)
8. [배포 및 운영](#배포-및-운영)
9. [구현 로드맵](#구현-로드맵)

---

## 현재 시스템 평가

### ✅ 잘 구현된 부분

#### 1. 아키텍처
- **LangGraph 기반 워크플로우**: 명확한 에이전트 분리와 상태 관리
- **TypedDict 상태 스키마**: 타입 안전성 확보
- **Reducer 패턴**: 효율적인 상태 누적
- **SQLite Checkpointing**: 세션 영속화 및 재개 기능

#### 2. 에이전트 시스템
- **6개 전문 에이전트**: Business Analyst, Book Coordinator, Content Strategist, Writer, Editor, Web Search
- **5개 보조 에이전트**: Fact Check, Math Formula, Diagram, Bibliography, Cross Reference
- **에이전트별 Temperature 설정**: 역할에 맞는 창의성/정확성 조정

#### 3. 템플릿 시스템
- **7가지 문서 타입** 지원
- **구조화된 목차 생성**
- **섹션별 리서치 쿼리**

#### 4. 내보내기
- **Markdown 출력**
- **PDF 생성 지원** (pandoc)
- **챕터별/완전한 책 조립**

### ⚠️ 개선 필요 부분

#### 1. 안정성 문제
- **모델 크래시**: Exit code 11 (메모리 부족)
- **모델 자동 언로드**: 연결 테스트 후 실행 시 실패
- **컨텍스트 누적**: Cross Reference 단계에서 한계 도달

#### 2. 기능 제한
- **언어 설정 누락**: 한글 요청에도 영어 출력
- **피드백 루프 미작동**: Writer가 Editor 피드백 미반영
- **웹 검색 선택지 제한**: DuckDuckGo만 (Tavily, Serper 미구현)

#### 3. 사용자 경험
- **에러 메시지 불친절**: 기술적 스택 트레이스만
- **진행 상황 시각화 부족**: 어느 단계인지 불명확
- **중단 시 복구 어려움**: Thread ID 수동 입력

#### 4. 성능
- **반복 생성**: 동일 초안 5-6회 반복
- **불필요한 컨텍스트 전달**: 모든 에이전트에 전체 히스토리
- **병렬 처리 미활용**: 독립적인 작업도 순차 실행

---

## 우선순위별 개선 제안

### 🔴 긴급 (1-2주)

#### 1. 안정성 확보
**문제**: 모델 크래시로 책 생성 실패
**해결**:
- [ ] 컨텍스트 관리 개선
- [ ] 에러 처리 강화
- [ ] 재시도 로직 추가
- [ ] 메모리 모니터링

#### 2. 언어 설정 수정
**문제**: 한글 주제에도 영어로 작성
**해결**:
- [ ] 언어 감지 로직
- [ ] 프롬프트에 언어 명시
- [ ] 다국어 템플릿

#### 3. 피드백 루프 수정
**문제**: Writer가 Editor 피드백 미반영
**해결**:
- [ ] Writer revise 로직 개선
- [ ] 피드백 파싱 강화
- [ ] 반복 조건 명확화

---

### 🟡 중요 (2-4주)

#### 4. 웹 검색 확장
**현재**: DuckDuckGo만 지원
**개선**:
- [ ] Tavily API 통합
- [ ] Serper API 통합
- [ ] 검색 결과 캐싱
- [ ] 출처 검증 강화

#### 5. 사용자 경험 개선
**개선 사항**:
- [ ] 진행 상황 바
- [ ] 친절한 에러 메시지
- [ ] 자동 세션 재개
- [ ] 중간 결과 미리보기

#### 6. 성능 최적화
**개선 사항**:
- [ ] 병렬 에이전트 실행
- [ ] 컨텍스트 압축
- [ ] 스트리밍 모드
- [ ] 캐싱 전략

---

### 🟢 일반 (4-8주)

#### 7. 새로운 기능
**확장 기능**:
- [ ] 이미지 생성 통합
- [ ] 음성 출력 (TTS)
- [ ] 다국어 번역
- [ ] 협업 모드

#### 8. 품질 보증
**QA 개선**:
- [ ] 유닛 테스트 확대
- [ ] 통합 테스트
- [ ] E2E 테스트
- [ ] 성능 벤치마크

#### 9. 배포 개선
**DevOps**:
- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인
- [ ] 클라우드 배포
- [ ] 모니터링 시스템

---

## 기술적 개선

### 1. 컨텍스트 관리 개선

#### 문제점
현재 모든 에이전트에 전체 `conversation_history` 전달:
```python
# 현재 (문제)
state = {
    "conversation_history": [...],  # 모든 대화
    "iterations": [...],            # 모든 반복
    ...
}
```

#### 해결 방안 A: 컨텍스트 압축

**파일**: `src/utils/context_manager.py` (신규)

```python
from typing import List, Dict, Any

class ContextManager:
    """컨텍스트 관리 및 압축"""

    @staticmethod
    def compress_conversation_history(
        history: List[Dict],
        max_items: int = 5,
        summary_threshold: int = 10
    ) -> List[Dict]:
        """
        대화 히스토리 압축.

        전략:
        1. 최근 N개는 전체 유지
        2. 오래된 것들은 요약
        """
        if len(history) <= max_items:
            return history

        # 오래된 메시지들 요약
        old_messages = history[:-max_items]
        recent_messages = history[-max_items:]

        summary = {
            "role": "system",
            "content": f"[Summary of {len(old_messages)} previous messages]"
        }

        return [summary] + recent_messages

    @staticmethod
    def compress_iterations(
        iterations: List[Dict],
        keep_last_n: int = 2
    ) -> List[Dict]:
        """
        반복 이력 압축.

        최근 N개만 유지, 나머지는 요약
        """
        if len(iterations) <= keep_last_n:
            return iterations

        old_iterations = iterations[:-keep_last_n]
        recent_iterations = iterations[-keep_last_n:]

        summary = {
            "iteration": "summary",
            "content": f"Previous {len(old_iterations)} iterations",
            "final_draft_length": old_iterations[-1].get("draft_length", 0)
        }

        return [summary] + recent_iterations

    @staticmethod
    def get_relevant_context_for_agent(
        state: Dict[str, Any],
        agent_name: str
    ) -> Dict[str, Any]:
        """
        에이전트별 필요한 컨텍스트만 추출.

        예:
        - Writer: topic, outline, research_data, last_feedback
        - Editor: current_draft, outline
        - Cross Reference: current_draft, terminology_glossary (conversation_history 제외)
        """
        common = {
            "topic": state.get("topic"),
        }

        agent_specific = {
            "writer": {
                **common,
                "current_outline": state.get("current_outline"),
                "research_by_section": state.get("research_by_section"),
                "current_feedback": state.get("current_feedback"),
                "iteration_count": state.get("iteration_count"),
            },
            "editor": {
                **common,
                "current_draft": state.get("current_draft"),
                "current_outline": state.get("current_outline"),
                "iteration_count": state.get("iteration_count"),
            },
            "cross_reference": {
                "current_draft": state.get("current_draft"),
                "terminology_glossary": state.get("terminology_glossary"),
                "completed_chapters": state.get("completed_chapters"),
                # conversation_history 제외!
            },
            "fact_check": {
                "current_draft": state.get("current_draft"),
                "research_data": state.get("research_data"),
            }
        }

        return agent_specific.get(agent_name, common)
```

**적용**:
```python
# src/agents/cross_reference_agent.py

from src.utils.context_manager import ContextManager

def cross_reference_node(state: WorkflowState) -> Dict[str, Any]:
    """Cross Reference Agent 노드 (개선)"""

    # 필요한 컨텍스트만 추출
    context = ContextManager.get_relevant_context_for_agent(state, "cross_reference")

    agent = CrossReferenceAgent(client)

    # 전체 state 대신 필요한 것만
    identified_refs = agent.identify_cross_references(
        current_draft=context["current_draft"],
        terminology_glossary=context["terminology_glossary"],
        # conversation_history는 전달 안 함 -> 메모리 절약
    )

    return {"cross_references": identified_refs}
```

#### 해결 방안 B: 스트리밍 모드

**파일**: `src/llm/client.py`

```python
def generate_streaming(
    self,
    messages: List[Dict],
    temperature: float = None,
    max_tokens: int = None,
    callback: callable = None
) -> str:
    """
    스트리밍 모드로 응답 생성.

    Args:
        messages: 메시지 리스트
        temperature: 온도
        max_tokens: 최대 토큰
        callback: 청크별 콜백 (진행 상황 표시용)

    Returns:
        전체 응답 문자열
    """
    try:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            stream=True  # 스트리밍 활성화
        )

        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content

                # 콜백 호출 (UI 업데이트)
                if callback:
                    callback(content)

        return full_response

    except Exception as e:
        raise Exception(f"Streaming generation failed: {e}")
```

**사용 예**:
```python
# src/agents/writer.py

def create_draft(self, topic: str, ...):
    """초안 작성 (스트리밍)"""

    def on_chunk(text: str):
        print(text, end="", flush=True)  # 실시간 출력

    response = self.llm_client.generate_streaming(
        messages=messages,
        callback=on_chunk
    )

    return response
```

---

### 2. 언어 설정 개선

#### 파일: `src/utils/language_detector.py` (신규)

```python
import re
from typing import Literal

Language = Literal["ko", "en", "ja", "zh"]

class LanguageDetector:
    """언어 감지"""

    @staticmethod
    def detect(text: str) -> Language:
        """
        텍스트에서 언어 감지.

        우선순위:
        1. 한글 (가-힣)
        2. 일본어 (ぁ-ん, ァ-ヶ, 一-龯)
        3. 중국어 (简体/繁体)
        4. 기본: 영어
        """
        # 한글
        if re.search(r'[가-힣]', text):
            return "ko"

        # 일본어 (히라가나, 카타카나, 한자)
        if re.search(r'[ぁ-んァ-ヶ]', text):
            return "ja"

        # 중국어 (한자)
        if re.search(r'[\u4e00-\u9fff]', text):
            return "zh"

        # 기본: 영어
        return "en"

    @staticmethod
    def get_language_instruction(lang: Language) -> str:
        """언어별 프롬프트 지시사항"""
        instructions = {
            "ko": "IMPORTANT: Write ALL content in Korean (한글). Do not use English.",
            "en": "Write in English.",
            "ja": "IMPORTANT: Write ALL content in Japanese (日本語).",
            "zh": "IMPORTANT: Write ALL content in Chinese (中文)."
        }
        return instructions.get(lang, instructions["en"])

    @staticmethod
    def get_language_name(lang: Language) -> str:
        """언어 이름"""
        names = {
            "ko": "Korean (한국어)",
            "en": "English",
            "ja": "Japanese (日本語)",
            "zh": "Chinese (中文)"
        }
        return names.get(lang, "English")
```

#### 적용: Writer Agent

**파일**: `src/agents/writer.py`

```python
from src.utils.language_detector import LanguageDetector

class WriterAgent:
    """Writer Agent (언어 감지 추가)"""

    def create_initial_draft(
        self,
        topic: str,
        user_intent: Optional[Dict] = None,
        outline: Optional[Dict] = None,
        research_data: Optional[Dict] = None
    ) -> str:
        """초안 작성 (언어 감지)"""

        # 언어 감지
        detected_lang = LanguageDetector.detect(topic)
        lang_instruction = LanguageDetector.get_language_instruction(detected_lang)
        lang_name = LanguageDetector.get_language_name(detected_lang)

        # 시스템 프롬프트에 언어 지시 추가
        system_prompt = f"""{self.SYSTEM_PROMPT}

{lang_instruction}

The topic is in {lang_name}, so your output MUST be in {lang_name}.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Topic: {topic}\n\nCreate a draft."}
        ]

        return self.llm_client.generate(messages)
```

---

### 3. 에러 처리 강화

#### 파일: `src/llm/client.py` (개선)

```python
import time
from typing import Optional, List, Dict

class LMStudioError(Exception):
    """LM Studio 관련 에러 기본 클래스"""
    pass

class ModelCrashError(LMStudioError):
    """모델 크래시 에러 (Exit code 11)"""
    pass

class ModelNotLoadedError(LMStudioError):
    """모델 미로드 에러"""
    pass

class ContextLengthExceededError(LMStudioError):
    """컨텍스트 길이 초과"""
    pass


class LMStudioClient:
    """LM Studio Client (에러 처리 강화)"""

    def generate(
        self,
        messages: List[Dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: float = 2.0
    ) -> str:
        """
        LLM 응답 생성 (재시도 로직 포함).

        Args:
            messages: 메시지 리스트
            temperature: 온도
            max_tokens: 최대 토큰
            max_retries: 최대 재시도 횟수
            retry_delay: 재시도 간격 (초)

        Returns:
            생성된 텍스트

        Raises:
            ModelCrashError: 모델 크래시
            ModelNotLoadedError: 모델 미로드
            ContextLengthExceededError: 컨텍스트 초과
            LMStudioError: 기타 LM Studio 에러
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature or self.temperature,
                    max_tokens=max_tokens or self.max_tokens
                )

                return response.choices[0].message.content

            except Exception as e:
                error_msg = str(e)

                # 에러 분류
                if "Exit code: 11" in error_msg or "crashed" in error_msg.lower():
                    raise ModelCrashError(
                        "LM Studio model crashed (Exit code 11).\n\n"
                        "Possible causes:\n"
                        "1. Out of memory (RAM/VRAM)\n"
                        "2. Context length exceeded\n"
                        "3. Model internal error\n\n"
                        "Solutions:\n"
                        "- Restart LM Studio\n"
                        "- Reduce context length (8192 → 4096)\n"
                        "- Use smaller model or quantization\n"
                        "- Reduce --chapters or --max-iterations"
                    ) from e

                if "No models loaded" in error_msg:
                    # 재시도 가능
                    if attempt < max_retries - 1:
                        print(f"⚠️  Model not loaded. Retrying {attempt+1}/{max_retries}...")
                        time.sleep(retry_delay * (2 ** attempt))  # 지수 백오프
                        continue

                    raise ModelNotLoadedError(
                        "No models loaded in LM Studio.\n\n"
                        "Please:\n"
                        "1. Open LM Studio application\n"
                        "2. Load a model (Models tab)\n"
                        "3. Start local server (Local Server tab)\n"
                        "4. Verify: python main.py --test-connection"
                    ) from e

                if "context length" in error_msg.lower():
                    raise ContextLengthExceededError(
                        "Context length exceeded.\n\n"
                        "Solutions:\n"
                        "- Reduce context in LM Studio settings\n"
                        "- Reduce iteration count\n"
                        "- Enable context compression"
                    ) from e

                # 기타 에러
                if attempt < max_retries - 1:
                    print(f"⚠️  API call failed. Retrying {attempt+1}/{max_retries}...")
                    time.sleep(retry_delay)
                    continue

                raise LMStudioError(f"LM Studio API call failed: {e}") from e

        raise LMStudioError(f"Failed after {max_retries} attempts")
```

#### 적용: 에이전트 노드

```python
# src/agents/writer.py

def writer_node(state: WorkflowState) -> Dict[str, Any]:
    """Writer 노드 (에러 처리)"""

    try:
        agent = WriterAgent(client)

        if state["iteration_count"] == 0:
            draft = agent.create_initial_draft(...)
        else:
            draft = agent.revise_draft(...)

        return {"current_draft": draft}

    except ModelCrashError as e:
        # 모델 크래시 시 상태 저장 후 종료
        print(f"\n❌ {e}")
        print("\n💾 Session saved. Resume with:")
        print(f"   python main.py --thread-id {state.get('thread_id')}")

        # 상태 저장은 LangGraph checkpointer가 자동 처리
        raise  # 워크플로우 중단

    except ContextLengthExceededError:
        # 컨텍스트 초과 시 압축 후 재시도
        print("⚠️  Context length exceeded. Compressing...")

        compressed_state = ContextManager.compress_state(state)

        agent = WriterAgent(client)
        draft = agent.create_initial_draft_minimal(compressed_state)

        return {"current_draft": draft}

    except ModelNotLoadedError as e:
        print(f"\n❌ {e}")
        raise  # 워크플로우 중단
```

---

### 4. 진행 상황 시각화

#### 파일: `src/ui/progress_tracker.py` (신규)

```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
from rich.console import Console
from typing import Optional

class ProgressTracker:
    """진행 상황 추적 및 표시"""

    def __init__(self):
        self.console = Console()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        )
        self.tasks = {}

    def start(self):
        """진행 바 시작"""
        self.progress.start()

    def stop(self):
        """진행 바 종료"""
        self.progress.stop()

    def add_book_task(self, book_title: str, total_chapters: int) -> TaskID:
        """책 생성 작업 추가"""
        task_id = self.progress.add_task(
            f"📚 {book_title}",
            total=total_chapters
        )
        self.tasks["book"] = task_id
        return task_id

    def add_chapter_task(self, chapter_number: int) -> TaskID:
        """챕터 작업 추가"""
        task_id = self.progress.add_task(
            f"  📝 Chapter {chapter_number}",
            total=10  # 10 단계 (에이전트 수)
        )
        self.tasks[f"chapter_{chapter_number}"] = task_id
        return task_id

    def update_chapter(self, chapter_number: int, agent_name: str):
        """챕터 진행 업데이트"""
        task_id = self.tasks.get(f"chapter_{chapter_number}")
        if task_id:
            self.progress.update(
                task_id,
                advance=1,
                description=f"  📝 Chapter {chapter_number} - {agent_name}"
            )

    def complete_chapter(self, chapter_number: int):
        """챕터 완료"""
        # 챕터 작업 완료
        chapter_task_id = self.tasks.get(f"chapter_{chapter_number}")
        if chapter_task_id:
            self.progress.update(chapter_task_id, completed=10)

        # 책 전체 진행 업데이트
        book_task_id = self.tasks.get("book")
        if book_task_id:
            self.progress.update(book_task_id, advance=1)
```

#### 적용: CLI

**파일**: `src/ui/cli.py`

```python
from src.ui.progress_tracker import ProgressTracker

class CLI:
    """CLI (진행 상황 추가)"""

    def start_book_session(self, ...):
        """책 생성 세션 (진행 바 추가)"""

        # 진행 바 초기화
        tracker = ProgressTracker()
        tracker.start()

        book_task = tracker.add_book_task(topic, estimated_chapters)
        current_chapter_task = None

        try:
            for event in self.app.stream(initial_state, config, stream_mode="values"):
                # 현재 단계 감지
                current_stage = event.get("current_stage")
                chapter_number = event.get("chapter_number", 0)

                # 새 챕터 시작
                if current_stage == "writing_chapter" and current_chapter_task is None:
                    current_chapter_task = tracker.add_chapter_task(chapter_number)

                # 에이전트 진행
                if current_stage and "node:" in current_stage:
                    agent_name = current_stage.split(":")[1]
                    tracker.update_chapter(chapter_number, agent_name)

                # 챕터 완료
                if chapter_number in event.get("completed_chapters", []):
                    tracker.complete_chapter(chapter_number)
                    current_chapter_task = None

        finally:
            tracker.stop()
```

**출력 예**:
```
📚 애플의 역사 ████████░░ 80% (2/3 chapters)
  📝 Chapter 2 - Editor ██████████ 100%
  📝 Chapter 3 - Writer ████░░░░░░ 40%
```

---

### 5. 자동 세션 재개

#### 파일: `src/utils/session_manager.py` (신규)

```python
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

class SessionManager:
    """세션 관리"""

    def __init__(self, sessions_dir: str = "data/sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def save_session_info(
        self,
        thread_id: str,
        topic: str,
        mode: str,
        book_type: Optional[str] = None,
        chapters: Optional[int] = None
    ):
        """세션 정보 저장"""
        session_file = self.sessions_dir / f"{thread_id}.json"

        session_data = {
            "thread_id": thread_id,
            "topic": topic,
            "mode": mode,
            "book_type": book_type,
            "chapters": chapters,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

    def get_latest_session(self) -> Optional[Dict]:
        """최근 세션 가져오기"""
        session_files = list(self.sessions_dir.glob("*.json"))

        if not session_files:
            return None

        # 최근 파일
        latest_file = max(session_files, key=lambda p: p.stat().st_mtime)

        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_sessions(self, limit: int = 10) -> List[Dict]:
        """세션 목록"""
        session_files = sorted(
            self.sessions_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]

        sessions = []
        for file in session_files:
            with open(file, 'r', encoding='utf-8') as f:
                sessions.append(json.load(f))

        return sessions
```

#### 적용: main.py

```python
# main.py

from src.utils.session_manager import SessionManager

def main():
    parser = argparse.ArgumentParser(...)

    # 자동 재개 옵션 추가
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume latest session automatically"
    )

    args = parser.parse_args()

    session_manager = SessionManager()

    # 자동 재개
    if args.resume and not args.thread_id:
        latest = session_manager.get_latest_session()

        if latest:
            print(f"📂 Resuming latest session:")
            print(f"   Topic: {latest['topic']}")
            print(f"   Mode: {latest['mode']}")
            print(f"   Created: {latest['created_at']}")
            print()

            args.thread_id = latest["thread_id"]
            args.topic = latest.get("topic")
            args.mode = latest.get("mode", "multi-agent")
        else:
            print("⚠️  No previous sessions found")
            sys.exit(1)

    # CLI 실행
    try:
        cli = CLI(mode=args.mode)

        # 세션 정보 저장
        if not args.thread_id:
            thread_id = str(uuid.uuid4())
            session_manager.save_session_info(
                thread_id=thread_id,
                topic=args.topic,
                mode=args.mode,
                book_type=args.book_type,
                chapters=args.chapters
            )
        ...
```

**사용 예**:
```bash
# 자동으로 최근 세션 재개
python main.py --resume

# 세션 목록 보기
python main.py --list-sessions
```

---

## 기능 확장

### 6. 이미지 생성 통합

#### 파일: `src/tools/image_generator.py` (신규)

```python
from typing import Optional, List
import requests
from pathlib import Path

class ImageGenerator:
    """이미지 생성 (DALL-E, Stable Diffusion 등)"""

    def __init__(self, provider: str = "stability", api_key: Optional[str] = None):
        """
        Args:
            provider: 'openai' (DALL-E), 'stability' (Stable Diffusion)
            api_key: API 키
        """
        self.provider = provider
        self.api_key = api_key

    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str = "natural"
    ) -> str:
        """
        이미지 생성.

        Args:
            prompt: 이미지 설명
            size: 크기
            style: 스타일

        Returns:
            생성된 이미지 URL 또는 로컬 경로
        """
        if self.provider == "openai":
            return self._generate_with_openai(prompt, size)
        elif self.provider == "stability":
            return self._generate_with_stability(prompt, size)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _generate_with_openai(self, prompt: str, size: str) -> str:
        """DALL-E로 생성"""
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1
        )

        return response.data[0].url

    def _generate_with_stability(self, prompt: str, size: str) -> str:
        """Stable Diffusion으로 생성"""
        # Stability AI API 호출
        # ...
        pass
```

#### 에이전트: Image Generator Agent

**파일**: `src/agents/image_generator_agent.py` (신규)

```python
class ImageGeneratorAgent:
    """이미지 생성 에이전트"""

    def __init__(self, generator: ImageGenerator):
        self.generator = generator

    def identify_image_needs(self, draft: str, outline: dict) -> List[Dict]:
        """
        초안에서 이미지가 필요한 부분 식별.

        Returns:
            [
                {
                    "section": "Introduction",
                    "description": "Company timeline infographic",
                    "prompt": "A clean timeline showing Apple's history from 1976 to 2020"
                },
                ...
            ]
        """
        # LLM을 사용하여 이미지 필요 부분 식별
        pass

    def generate_images(self, image_specs: List[Dict]) -> List[Dict]:
        """이미지 생성"""
        generated = []

        for spec in image_specs:
            image_url = self.generator.generate_image(
                prompt=spec["prompt"],
                size="1024x1024"
            )

            generated.append({
                **spec,
                "image_url": image_url
            })

        return generated
```

---

### 7. 음성 출력 (TTS)

#### 파일: `src/tools/text_to_speech.py` (신규)

```python
from pathlib import Path
from typing import Optional

class TextToSpeech:
    """텍스트 음성 변환"""

    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key

    def convert_to_speech(
        self,
        text: str,
        output_path: str,
        voice: str = "alloy",
        language: str = "ko"
    ) -> str:
        """
        텍스트를 음성으로 변환.

        Args:
            text: 변환할 텍스트
            output_path: 출력 파일 경로
            voice: 음성 (alloy, echo, fable, onyx, nova, shimmer)
            language: 언어

        Returns:
            생성된 오디오 파일 경로
        """
        if self.provider == "openai":
            return self._convert_with_openai(text, output_path, voice)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _convert_with_openai(self, text: str, output_path: str, voice: str) -> str:
        """OpenAI TTS로 변환"""
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)

        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )

        response.stream_to_file(output_path)

        return output_path

    def convert_book_to_audiobook(
        self,
        book_path: str,
        output_dir: str,
        voice: str = "alloy"
    ) -> List[str]:
        """
        책 전체를 오디오북으로 변환.

        챕터별로 분리된 오디오 파일 생성.
        """
        import re

        with open(book_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 챕터별로 분리
        chapters = re.split(r'^#\s+Chapter\s+\d+', content, flags=re.MULTILINE)

        audio_files = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for i, chapter_text in enumerate(chapters[1:], 1):  # 첫 번째는 제목
            audio_file = output_path / f"chapter_{i:02d}.mp3"

            self.convert_to_speech(
                text=chapter_text,
                output_path=str(audio_file),
                voice=voice
            )

            audio_files.append(str(audio_file))

        return audio_files
```

**사용 예**:
```bash
# 책을 오디오북으로 변환
python main.py --mode book --topic "애플의 역사" --chapters 3 --generate-audiobook
```

---

### 8. 다국어 번역

#### 파일: `src/tools/translator.py` (신규)

```python
from typing import List, Dict

class Translator:
    """다국어 번역"""

    def __init__(self, client):
        self.client = client

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        텍스트 번역.

        Args:
            text: 원문
            source_lang: 원문 언어 (ko, en, ja, zh)
            target_lang: 대상 언어

        Returns:
            번역된 텍스트
        """
        lang_names = {
            "ko": "Korean",
            "en": "English",
            "ja": "Japanese",
            "zh": "Chinese"
        }

        prompt = f"""Translate the following {lang_names[source_lang]} text to {lang_names[target_lang]}.

Maintain the original formatting, structure, and markdown syntax.

Original text:
{text}

Translated text:"""

        messages = [
            {"role": "user", "content": prompt}
        ]

        return self.client.generate(messages, temperature=0.3)

    def translate_book(
        self,
        book_path: str,
        target_lang: str,
        output_path: str
    ):
        """책 전체 번역"""
        with open(book_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 언어 감지
        from src.utils.language_detector import LanguageDetector
        source_lang = LanguageDetector.detect(content)

        # 번역
        translated = self.translate(content, source_lang, target_lang)

        # 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)

        return output_path
```

**사용 예**:
```bash
# 한글 책을 영어로 번역
python main.py --translate output/books/애플의_역사/complete_book.md --lang en

# 출력: output/books/애플의_역사/complete_book_en.md
```

---

## 성능 최적화

### 9. 병렬 에이전트 실행

현재 모든 에이전트가 순차 실행되지만, 일부는 병렬 실행 가능:

```python
# 현재 (순차)
writer → fact_check → math → diagram → bibliography → cross_ref

# 개선 (병렬)
writer → [fact_check, math, diagram, bibliography] (병렬) → cross_ref
```

#### 파일: `src/graph/workflow.py` (수정)

```python
from langgraph.graph import StateGraph, END
from langgraph.constants import Send

def create_book_workflow_parallel() -> StateGraph:
    """책 워크플로우 (병렬 처리)"""

    workflow = StateGraph(WorkflowState)

    # 노드 추가
    workflow.add_node("writer", writer_node)
    workflow.add_node("fact_check", fact_check_node)
    workflow.add_node("math_formula", math_formula_node)
    workflow.add_node("diagram", diagram_node)
    workflow.add_node("bibliography", bibliography_node)
    workflow.add_node("cross_reference", cross_reference_node)
    workflow.add_node("editor", editor_node)

    # Writer → 병렬 처리 노드들
    def route_to_parallel_agents(state: WorkflowState):
        """Writer 후 병렬 에이전트들에게 분배"""
        return [
            Send("fact_check", state),
            Send("math_formula", state),
            Send("diagram", state),
            Send("bibliography", state)
        ]

    workflow.add_conditional_edges(
        "writer",
        route_to_parallel_agents
    )

    # 모든 병렬 에이전트 → Cross Reference
    workflow.add_edge("fact_check", "cross_reference")
    workflow.add_edge("math_formula", "cross_reference")
    workflow.add_edge("diagram", "cross_reference")
    workflow.add_edge("bibliography", "cross_reference")

    # Cross Reference → Editor
    workflow.add_edge("cross_reference", "editor")

    return workflow
```

**예상 성능 향상**: 4개 에이전트를 병렬 실행 시 ~4배 빠름

---

### 10. 캐싱 전략

#### 파일: `src/utils/cache.py` (신규)

```python
import hashlib
import json
from pathlib import Path
from typing import Optional, Any

class Cache:
    """간단한 파일 기반 캐시"""

    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_key(self, data: Any) -> str:
        """데이터로부터 캐시 키 생성"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """캐시 조회"""
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """캐시 저장"""
        cache_file = self.cache_dir / f"{key}.json"

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, indent=2)

    def get_or_compute(self, key: str, compute_fn: callable) -> Any:
        """캐시 조회 또는 계산"""
        cached = self.get(key)

        if cached is not None:
            return cached

        # 계산
        result = compute_fn()

        # 캐시 저장
        self.set(key, result)

        return result
```

#### 적용: Web Search

```python
# src/agents/web_search_agent.py

from src.utils.cache import Cache

class WebSearchAgent:
    """Web Search Agent (캐싱 추가)"""

    def __init__(self, provider, cache: Optional[Cache] = None):
        self.provider = provider
        self.cache = cache or Cache()

    def search_section(self, section: dict) -> List[dict]:
        """섹션 검색 (캐싱)"""

        queries = section.get("search_queries", [])
        results = []

        for query in queries:
            # 캐시 키 생성
            cache_key = self.cache._get_key({"query": query, "provider": self.provider.provider_type})

            # 캐시 조회 또는 검색
            result = self.cache.get_or_compute(
                cache_key,
                lambda: self.provider.search(query, max_results=5)
            )

            results.extend(result)

        return results
```

**효과**: 동일한 쿼리 재검색 방지 → 속도 향상 + API 비용 절감

---

## 품질 보증

### 11. 테스트 확대

#### 구조
```
tests/
├── unit/
│   ├── test_agents/
│   │   ├── test_writer.py
│   │   ├── test_editor.py
│   │   └── ...
│   ├── test_utils/
│   │   ├── test_language_detector.py
│   │   ├── test_context_manager.py
│   │   └── ...
│   └── test_tools/
│       ├── test_search_tools.py
│       └── ...
├── integration/
│   ├── test_simple_workflow.py
│   ├── test_multi_agent_workflow.py
│   └── test_book_workflow.py
├── e2e/
│   ├── test_book_generation.py
│   └── test_error_recovery.py
└── fixtures/
    ├── sample_topics.py
    └── mock_responses.py
```

#### 예: 유닛 테스트

**파일**: `tests/unit/test_utils/test_language_detector.py`

```python
import pytest
from src.utils.language_detector import LanguageDetector

class TestLanguageDetector:
    """LanguageDetector 테스트"""

    def test_detect_korean(self):
        """한글 감지"""
        assert LanguageDetector.detect("애플의 역사") == "ko"
        assert LanguageDetector.detect("안녕하세요") == "ko"

    def test_detect_english(self):
        """영어 감지"""
        assert LanguageDetector.detect("History of Apple") == "en"
        assert LanguageDetector.detect("Hello World") == "en"

    def test_detect_japanese(self):
        """일본어 감지"""
        assert LanguageDetector.detect("こんにちは") == "ja"
        assert LanguageDetector.detect("アップルの歴史") == "ja"

    def test_detect_chinese(self):
        """중국어 감지"""
        assert LanguageDetector.detect("你好") == "zh"
        assert LanguageDetector.detect("苹果的历史") == "zh"

    def test_get_language_instruction(self):
        """언어별 지시사항"""
        ko_inst = LanguageDetector.get_language_instruction("ko")
        assert "Korean" in ko_inst
        assert "한글" in ko_inst

    def test_mixed_language_priority(self):
        """혼합 언어 - 우선순위 확인"""
        # 한글이 포함되면 한글
        assert LanguageDetector.detect("Apple 애플") == "ko"
```

#### 예: 통합 테스트

**파일**: `tests/integration/test_simple_workflow.py`

```python
import pytest
from src.graph.workflow import compile_workflow, create_initial_state
from src.llm.client import LMStudioClient
from src.config.settings import settings

@pytest.mark.integration
class TestSimpleWorkflow:
    """단순 워크플로우 통합 테스트"""

    @pytest.fixture
    def app(self):
        """워크플로우 앱"""
        return compile_workflow("simple")

    @pytest.fixture
    def config(self):
        """설정"""
        return {"configurable": {"thread_id": "test-session"}}

    def test_simple_workflow_runs(self, app, config):
        """단순 워크플로우 실행"""
        initial_state = create_initial_state(
            topic="Test Topic",
            mode="simple",
            max_iterations=1
        )

        # 실행
        events = list(app.stream(initial_state, config, stream_mode="values"))

        # 검증
        assert len(events) > 0
        final_state = events[-1]

        assert "current_draft" in final_state
        assert len(final_state["current_draft"]) > 0

    def test_writer_editor_cycle(self, app, config):
        """Writer-Editor 사이클"""
        initial_state = create_initial_state(
            topic="Artificial Intelligence",
            mode="simple",
            max_iterations=2
        )

        events = list(app.stream(initial_state, config))

        # Writer 실행 확인
        writer_events = [e for e in events if "writer" in str(e)]
        assert len(writer_events) > 0

        # Editor 실행 확인
        editor_events = [e for e in events if "editor" in str(e)]
        assert len(editor_events) > 0
```

---

## 배포 및 운영

### 12. Docker 컨테이너화

#### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 시스템 의존성
RUN apt-get update && apt-get install -y \
    pandoc \
    texlive-xetex \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 복사
COPY . .

# 데이터 디렉토리
RUN mkdir -p data output

ENTRYPOINT ["python", "main.py"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  writer-editor:
    build: .
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    environment:
      - LM_STUDIO_BASE_URL=${LM_STUDIO_BASE_URL}
      - LM_STUDIO_MODEL=${LM_STUDIO_MODEL}
    command: --mode book --topic "AI History" --chapters 5

  lm-studio:
    image: lmstudio/server:latest
    ports:
      - "1234:1234"
    volumes:
      - ./models:/models
```

**사용**:
```bash
docker-compose up
```

---

### 13. CI/CD 파이프라인

#### .github/workflows/test.yml

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -e ".[dev]"

    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=src

    - name: Run integration tests
      run: |
        pytest tests/integration/ -v

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## 구현 로드맵

### Phase 1: 안정성 (1-2주) 🔴

**목표**: 책 생성 실패율 0%

- [ ] 컨텍스트 관리 개선 (`ContextManager`)
- [ ] 언어 설정 수정 (`LanguageDetector`)
- [ ] 에러 처리 강화 (커스텀 예외)
- [ ] 재시도 로직 추가
- [ ] 피드백 루프 수정

**완료 기준**:
- [ ] 3챕터 책 생성 성공률 95% 이상
- [ ] 한글 주제 → 한글 출력 100%
- [ ] 모델 크래시 시 자동 복구 또는 명확한 안내

---

### Phase 2: 사용자 경험 (2-3주) 🟡

**목표**: 사용하기 쉽고 직관적인 시스템

- [ ] 진행 상황 바 (`ProgressTracker`)
- [ ] 친절한 에러 메시지
- [ ] 자동 세션 재개 (`SessionManager`)
- [ ] 중간 결과 미리보기
- [ ] 웹 검색 확장 (Tavily, Serper)

**완료 기준**:
- [ ] 사용자가 진행 상황을 실시간으로 확인
- [ ] 에러 발생 시 해결 방법 명확히 제시
- [ ] `--resume` 옵션으로 간편 재개

---

### Phase 3: 성능 최적화 (3-4주) 🟡

**목표**: 생성 속도 2-3배 향상

- [ ] 병렬 에이전트 실행
- [ ] 컨텍스트 압축
- [ ] 캐싱 전략
- [ ] 스트리밍 모드

**완료 기준**:
- [ ] 3챕터 책 생성 시간 < 10분 (현재 ~30분)
- [ ] 메모리 사용량 50% 감소

---

### Phase 4: 기능 확장 (4-8주) 🟢

**목표**: 멀티미디어 및 다국어 지원

- [ ] 이미지 생성 통합
- [ ] 음성 출력 (TTS)
- [ ] 다국어 번역
- [ ] 협업 모드

**완료 기준**:
- [ ] 이미지 포함 책 생성
- [ ] 오디오북 생성
- [ ] 한 → 영, 영 → 한 번역

---

### Phase 5: 품질 보증 (병행) 🟢

**목표**: 높은 코드 품질 유지

- [ ] 유닛 테스트 (커버리지 80%)
- [ ] 통합 테스트
- [ ] E2E 테스트
- [ ] 성능 벤치마크

**완료 기준**:
- [ ] 테스트 커버리지 80% 이상
- [ ] 모든 PR에 자동 테스트

---

### Phase 6: 배포 (6-8주) 🟢

**목표**: 프로덕션 배포

- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인
- [ ] 클라우드 배포 (AWS/GCP)
- [ ] 모니터링 시스템

**완료 기준**:
- [ ] `docker-compose up`으로 실행
- [ ] 자동 배포 파이프라인
- [ ] 로그 및 메트릭 수집

---

## 예상 효과

### 안정성
- **현재**: 책 생성 실패율 ~30%
- **개선 후**: 책 생성 실패율 <5%

### 성능
- **현재**: 3챕터 책 생성 ~30분
- **개선 후**: 3챕터 책 생성 <10분 (병렬 처리)

### 사용자 경험
- **현재**: 에러 발생 시 포기율 높음
- **개선 후**: 자동 복구 또는 명확한 가이드

### 기능
- **현재**: 텍스트 전용
- **개선 후**: 이미지, 오디오, 다국어 지원

---

## 결론

이 개선 제안서는 현재 시스템의 주요 문제점을 해결하고, 새로운 기능을 추가하여 더욱 강력하고 사용하기 쉬운 시스템으로 발전시키는 로드맵을 제시합니다.

**우선순위**:
1. **안정성** (긴급) - 책 생성 실패 방지
2. **사용자 경험** (중요) - 진행 상황, 에러 메시지
3. **성능** (중요) - 병렬 처리, 캐싱
4. **기능 확장** (일반) - 이미지, 오디오, 번역

**예상 개발 기간**: 8-12주

**핵심 가치**:
- ✅ **안정적**: 항상 작동하는 시스템
- ✅ **빠름**: 병렬 처리로 3배 빠른 생성
- ✅ **사용하기 쉬움**: 직관적인 인터페이스
- ✅ **확장 가능**: 새로운 기능 추가 용이

---

**작성일**: 2025-12-28
**버전**: 1.0
**시스템**: Writer-Editor Multi-Agent Book System
**작성자**: Claude Sonnet 4.5
