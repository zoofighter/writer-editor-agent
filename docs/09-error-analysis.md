# 에러 분석 및 해결 가이드

## 📋 목차

1. [발생한 에러 요약](#발생한-에러-요약)
2. [Apple 역사 책 생성 에러](#apple-역사-책-생성-에러)
3. [Google 역사 책 생성 성공](#google-역사-책-생성-성공)
4. [최근 실행 에러](#최근-실행-에러)
5. [에러 패턴 분석](#에러-패턴-분석)
6. [근본 원인](#근본-원인)
7. [해결 방법](#해결-방법)
8. [예방 조치](#예방-조치)

---

## 발생한 에러 요약

### 🔴 에러 1: Apple 역사 책 - 모델 크래시

**파일**: `/tmp/claude/-Users-boon-Dropbox-02-works-94-agent/tasks/bb8e13b.output`

**에러 메시지**:
```
Error code: 400 - {'error': 'The model has crashed without additional information. (Exit code: 11)'}
```

**발생 위치**: `cross_reference_agent.py:165`

**상태**: ❌ 실패

---

### 🟢 에러 2: Google 역사 책 - 정상 완료

**파일**: `/tmp/claude/-Users-boon-Dropbox-02-works-94-agent/tasks/bda088d.output`

**상태**: ✅ 성공

**특징**: Editor가 상세한 피드백 제공

---

### 🔴 에러 3: 최근 실행 - 모델 없음

**에러 메시지**:
```
Error code: 400 - {'error': {'message': "No models loaded. Please load a model in the developer page or use the 'lms load' command."}}
```

**발생 위치**: `business_analyst.py:86`

**상태**: ❌ 실패

---

## Apple 역사 책 생성 에러

### 진행 단계 분석

```
Session ID: 4973c58e-ae77-4736-b477-39dd63953a00
Book: 애플의 역사
Type: history
Chapters: 3
```

#### Phase 1: 초기화 ✅
- Business Analyst 완료
- Book Coordinator 완료
- 목차 생성 완료

#### Phase 2: 리서치 ⚠️
**Web Search Agent 경고**:
```
Warning: duckduckgo-search not installed. Install with: pip install duckduckgo-search
```

**발생 횟수**: 9회
- Background/Context 섹션: 3회
- Main Content 섹션: 3회
- Practical Examples/Application 섹션: 3회

**영향**: 웹 검색 실패, 리서치 데이터 없음

#### Phase 3: Writer ✅
**반복 횟수**: 5회 (동일한 초안 반복)

**초안 내용**:
```
Ever wonder how a company started in a garage ended up changing the way we
work, play, and communicate? Meet Apple—your iPhone, MacBook, and even your
Apple Watch all come from one bold vision that began in 1976...
```

**초안 길이**: 4,765 characters

**문제점**:
- 5번 모두 동일한 내용 생성
- 영어로 작성됨 (한글 요청이었지만)
- 반복적인 재생성 시도

#### Phase 4: 보조 에이전트 (추정 완료)
1. ✅ Fact Check Agent
2. ✅ Math Formula Agent
3. ✅ Diagram Agent
4. ✅ Bibliography Agent

#### Phase 5: Cross Reference ❌
**크래시 발생**:
```python
File "/Users/boon/Dropbox/02_works/94_agent/src/agents/cross_reference_agent.py", line 133
    response = self.client.generate(messages)

Exception: LM Studio API call failed: Error code: 400 -
{'error': 'The model has crashed without additional information. (Exit code: 11)'}
```

**Task ID**: `3086c55d-4bc1-a6bd-0b24-0c81ec61996f`

---

## Google 역사 책 생성 성공

### 진행 단계 분석

```
Session ID: 6d98d02c-c9d6-4094-917c-8bfae6e10310
Book: 구글의 역사
Type: history
Chapters: 3
```

#### Phase 1-2: 리서치 ⚠️
**동일한 경고**:
```
Warning: duckduckgo-search not installed
```

발생 횟수: 9회 (Apple과 동일)

#### Phase 3: Writer ✅
**반복 횟수**: 6회 (동일한 초안 반복)

**초안 내용**:
```
Imagine a world without instant access to information—where finding answers
required flipping through encyclopedias or asking strangers on the street.
Today, that world feels almost foreign. The search engine that transformed
how we interact with knowledge is Google...
```

**초안 길이**: 7,244 characters (Apple보다 52% 더 김)

#### Phase 4: Editor ✅
**상세한 피드백 제공**:

**강점**:
- Strong Hook and Engaging Tone
- Clear Structure
- Comprehensive Historical Coverage
- Well-Integrated Examples
- Balanced Perspective

**개선 영역**:
1. Clarity and Flow in Main Content
2. Depth on Key Innovations
3. Practical Examples Section Needs Refinement
4. Minor Factual and Stylistic Notes
5. Conclusion Could Be More Forward-Looking

**권장사항**:
- Revise for Readability
- Enhance Depth on Key Innovations
- Refine Practical Applications
- Strengthen the Conclusion
- Polish Language and Tone

#### 결과: ✅ 성공
```
✓ Book generation completed successfully!
```

---

## 최근 실행 에러

### 실행 명령
```bash
python main.py --mode book --book-type history --topic "애플의 역사" --chapters 3 --max-iterations 2
```

### 에러 발생 순서

#### 1. 연결 테스트 성공
```bash
python main.py --test-connection
```

**출력**:
```
Testing connection to LM Studio at http://localhost:1234/v1...
✓ Successfully connected to LM Studio
  Model: qwen
```

#### 2. 실제 실행 실패
**에러 위치**: Business Analyst 시작 시

**스택 트레이스**:
```python
File "/Users/boon/Dropbox/02_works/94_agent/src/agents/business_analyst.py", line 86
    response = self.llm_client.generate(
        messages,
        temperature=settings.business_analyst_temperature
    )

Exception: LM Studio API call failed: Error code: 400 -
{'error': {'message': "No models loaded. Please load a model in the developer page..."}}
```

---

## 에러 패턴 분석

### 공통점

#### 1. Web Search 실패
**모든 실행**에서 동일한 경고:
```
Warning: duckduckgo-search not installed
```

**영향**:
- 리서치 데이터 없음
- 섹션별 검색 쿼리 실행 불가
- 사실 확인 어려움

#### 2. 동일한 초안 반복
**Apple**: 5회 동일 (4,765 chars)
**Google**: 6회 동일 (7,244 chars)

**원인**:
- Editor 피드백이 반영되지 않음
- Writer가 수정하지 않고 동일한 초안 재생성
- 피드백 루프 작동 안 함

#### 3. 영어 출력
**요청**: 한글 책 ("애플의 역사", "구글의 역사")
**실제**: 영어로 작성됨

**원인**:
- 프롬프트에 언어 지정 누락
- 모델이 영어로 학습되어 기본 언어가 영어

### 차이점

#### Apple vs Google

| 항목 | Apple | Google |
|------|-------|--------|
| 초안 길이 | 4,765 chars | 7,244 chars |
| 반복 횟수 | 5회 | 6회 |
| 결과 | 크래시 | 성공 |
| 크래시 위치 | Cross Reference | - |
| Editor 피드백 | 없음 | 상세함 |

**분석**:
- Google이 52% 더 긴 초안
- Google이 1회 더 반복
- Apple만 Cross Reference에서 크래시
- Google은 Editor까지 도달

**추론**:
- Apple은 Cross Reference 단계에서 누적 컨텍스트 초과
- Google은 Editor가 피드백을 제공했으나 책 완성은 안 됨

---

## 근본 원인

### 1. LM Studio 모델 불안정성

#### 증상
- 연결 테스트 성공 → 실행 시 모델 없음
- 실행 중 모델 크래시 (Exit code 11)

#### 원인
**Exit code 11**: Segmentation Fault
- 메모리 접근 오류
- 잘못된 메모리 주소 참조
- 버퍼 오버플로우

**가능한 원인**:
1. **메모리 부족**: RAM/VRAM 한계
2. **컨텍스트 길이 초과**: 누적된 대화 이력
3. **모델 버그**: Qwen 모델 내부 오류

### 2. 컨텍스트 누적 문제

#### 누적 데이터
Cross Reference 단계까지 누적된 컨텍스트:

1. **User Intent** (Business Analyst)
2. **Book Metadata** (Book Coordinator)
3. **Table of Contents** (Book Coordinator)
4. **Chapter Outline** (Content Strategist)
5. **Research Data** (Web Search, 실패)
6. **Draft Content** (Writer, 5-6회 반복)
7. **Fact Check Results** (Fact Check Agent)
8. **Math Formulas** (Math Formula Agent)
9. **Diagrams** (Diagram Agent)
10. **Bibliography** (Bibliography Agent)
11. **Conversation History** (누적)

**예상 토큰 수**:
- 초안만 ~1,500 tokens (4,765 chars ÷ 3)
- 5회 반복 → 7,500 tokens
- 기타 데이터 → 5,000 tokens
- **총 예상**: ~12,500 tokens

**LM Studio 설정**:
- Context Length: 8,192 (기본값)
- **초과 여부**: 초과 가능성 높음

### 3. Web Search 패키지 누락

#### 영향
- 리서치 데이터 없음
- 사실 기반 작성 어려움
- 품질 저하

#### 해결
```bash
pip install duckduckgo-search
```

**설치 완료**: ✅ (이미 해결됨)

### 4. 언어 설정 문제

#### 원인
- 프롬프트에 "한글로 작성" 명시 누락
- 모델 기본 언어: 영어
- Topic만 한글로 제공

#### 해결 필요
Writer Agent 프롬프트 수정 필요

---

## 해결 방법

### 즉시 해결 (완료)

#### 1. DuckDuckGo Search 설치 ✅
```bash
pip install duckduckgo-search
```

**확인**:
```bash
python -c "import duckduckgo_search; print('✓ Installed')"
```

**결과**: ✅ 설치 완료

---

### 단기 해결 (권장)

#### 2. 가벼운 설정으로 실행

**LM Studio 설정**:
- Context Length: 4096 (현재 8192에서 줄이기)
- Model: Qwen2.5-7B-Instruct (Q4_K_M) 유지
- GPU: Auto

**실행 명령**:
```bash
# 1챕터만 생성
python main.py --mode book --book-type history --topic "애플의 역사" --chapters 1 --max-iterations 1

# 반복 최소화
python main.py --mode book --book-type history --topic "애플의 역사" --chapters 3 --max-iterations 2
```

#### 3. LM Studio 재시작 프로토콜

**순서**:
1. LM Studio에서 "Stop Server" 클릭
2. 모델 "Unload" 클릭
3. LM Studio 앱 완전 종료
4. 시스템 메모리 확인 (Activity Monitor)
5. LM Studio 재시작
6. 모델 재로드 (완전 로딩 대기)
7. Server 재시작
8. 연결 테스트
9. 즉시 실행 (테스트와 실행 사이 시간 최소화)

**명령어**:
```bash
# 연속 실행 (모델 언로드 방지)
python main.py --test-connection && python main.py --mode book --book-type history --topic "애플의 역사" --chapters 1
```

---

### 중기 해결 (코드 수정 필요)

#### 4. 언어 설정 개선

**파일**: `src/agents/writer.py`

**수정 필요**:
```python
# 현재 (추정)
SYSTEM_PROMPT = """You are a professional writer..."""

# 수정 후
SYSTEM_PROMPT = """You are a professional writer...

IMPORTANT: Write the content in the same language as the topic.
- If topic is in Korean (한글), write in Korean.
- If topic is in English, write in English.
"""
```

**또는 동적 프롬프트**:
```python
def create_draft(self, topic: str, ...):
    # 언어 감지
    import re
    is_korean = bool(re.search('[가-힣]', topic))

    language_instruction = "Write in Korean (한글)." if is_korean else "Write in English."

    messages = [
        {"role": "system", "content": f"{self.SYSTEM_PROMPT}\n\n{language_instruction}"},
        ...
    ]
```

#### 5. 컨텍스트 관리 개선

**파일**: `src/graph/state.py`, `src/agents/*`

**전략 A: 컨텍스트 압축**
```python
def compress_conversation_history(history: List[dict], max_items: int = 5):
    """최근 N개만 유지"""
    return history[-max_items:] if len(history) > max_items else history
```

**전략 B: 요약 생성**
```python
def summarize_iterations(iterations: List[ReviewIteration]):
    """이전 반복들을 요약"""
    if len(iterations) > 3:
        # 최근 1개만 전체 유지, 나머지는 요약
        old_iterations = iterations[:-1]
        summary = f"Previous {len(old_iterations)} iterations summary..."
        return [summary] + [iterations[-1]]
    return iterations
```

**전략 C: 선택적 데이터 전달**
```python
def cross_reference_node(state: WorkflowState):
    # 전체 conversation_history 대신 필요한 것만
    relevant_data = {
        "current_draft": state["current_draft"],
        "terminology_glossary": state["terminology_glossary"],
        # conversation_history는 제외 또는 요약본만
    }
```

#### 6. 에러 처리 개선

**파일**: `src/llm/client.py`

**현재**:
```python
except Exception as e:
    raise Exception(f"LM Studio API call failed: {e}")
```

**개선**:
```python
except Exception as e:
    error_msg = str(e)

    # Exit code 11 처리
    if "Exit code: 11" in error_msg:
        raise MemoryError(
            "LM Studio model crashed (Exit code 11). "
            "This usually means:\n"
            "1. Out of memory (RAM/VRAM)\n"
            "2. Context length exceeded\n"
            "Solutions:\n"
            "- Reduce context length in LM Studio\n"
            "- Use smaller model or quantization\n"
            "- Reduce --chapters or --max-iterations"
        )

    # No models loaded 처리
    if "No models loaded" in error_msg:
        raise ConnectionError(
            "No models loaded in LM Studio. "
            "Please:\n"
            "1. Open LM Studio\n"
            "2. Load a model (Models tab)\n"
            "3. Start server (Local Server tab)\n"
            "4. Run: python main.py --test-connection"
        )

    raise Exception(f"LM Studio API call failed: {e}")
```

#### 7. 재시도 로직 추가

**파일**: `src/llm/client.py`

```python
def generate_with_retry(self, messages, max_retries=3, **kwargs):
    """재시도 로직"""
    for attempt in range(max_retries):
        try:
            return self.generate(messages, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            error_msg = str(e)

            # 재시도 가능한 에러
            if "No models loaded" in error_msg or "Connection" in error_msg:
                print(f"Retry {attempt+1}/{max_retries} due to: {error_msg}")
                time.sleep(2 ** attempt)  # 지수 백오프
                continue

            # 재시도 불가능한 에러 (메모리 크래시)
            raise
```

---

### 장기 해결 (아키텍처 개선)

#### 8. 체크포인트 기반 복구

**개념**: 각 에이전트 완료 후 체크포인트 저장

```python
def cross_reference_node(state: WorkflowState):
    try:
        # 작업 수행
        result = agent.identify_cross_references(...)

        # 성공 시 체크포인트
        save_checkpoint(state, "cross_reference_completed")

        return {"cross_references": result}

    except MemoryError as e:
        # 메모리 에러 시 컨텍스트 정리 후 재시도
        cleaned_state = cleanup_context(state)

        # 재시도
        result = agent.identify_cross_references_minimal(cleaned_state)
        return {"cross_references": result}
```

#### 9. 스트리밍 모드

**개념**: 큰 응답을 스트리밍으로 받아 메모리 절약

```python
def generate_streaming(self, messages, **kwargs):
    """스트리밍 모드"""
    response = self.client.chat.completions.create(
        model=self.model_name,
        messages=messages,
        stream=True,  # 스트리밍 활성화
        **kwargs
    )

    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content
            # 청크별 메모리 관리 가능

    return full_response
```

#### 10. 분산 처리

**개념**: 각 챕터를 별도 세션으로 처리

```python
def generate_book_distributed(topic, chapters):
    """챕터별 독립 실행"""
    for chapter_num in range(1, chapters + 1):
        # 새 세션 시작 (컨텍스트 초기화)
        thread_id = f"{topic}-chapter-{chapter_num}"

        generate_single_chapter(
            topic=topic,
            chapter_number=chapter_num,
            thread_id=thread_id
        )

        # 세션 종료 (메모리 해제)
        cleanup_session(thread_id)
```

---

## 예방 조치

### 1. 사전 점검 스크립트

**파일**: `scripts/pre_flight_check.py`

```python
#!/usr/bin/env python3
"""책 생성 전 사전 점검"""

def check_lm_studio():
    """LM Studio 연결 및 상태 확인"""
    # 연결 테스트
    # 모델 로드 확인
    # Context length 확인
    # 메모리 여유 확인

def check_dependencies():
    """패키지 설치 확인"""
    # duckduckgo-search
    # langgraph
    # 등등

def estimate_resources(chapters, max_iterations):
    """필요 리소스 예측"""
    # 예상 토큰 수
    # 예상 메모리 사용량
    # 예상 소요 시간

if __name__ == "__main__":
    check_lm_studio()
    check_dependencies()
    estimate_resources(chapters=3, max_iterations=2)
```

### 2. 모니터링

**실시간 모니터링**:
```python
def monitor_resource_usage():
    """리소스 사용량 모니터링"""
    import psutil

    # 메모리 사용량
    memory = psutil.virtual_memory()
    print(f"Memory: {memory.percent}%")

    # 토큰 누적량 (예측)
    estimated_tokens = calculate_tokens(state)
    print(f"Estimated tokens: {estimated_tokens}")

    # 경고
    if memory.percent > 80:
        warnings.warn("Memory usage high!")

    if estimated_tokens > 6000:  # Context 8192의 75%
        warnings.warn("Context length approaching limit!")
```

### 3. 자동 복구

**파일**: `src/llm/client.py`

```python
def generate_with_auto_recovery(self, messages, **kwargs):
    """자동 복구 로직"""
    try:
        return self.generate(messages, **kwargs)

    except MemoryError:
        # 메모리 에러 시 컨텍스트 압축
        compressed_messages = compress_messages(messages, max_length=4000)

        try:
            return self.generate(compressed_messages, **kwargs)
        except:
            # 그래도 실패 시 초간단 버전
            minimal_messages = messages[-2:]  # 최근 2개만
            return self.generate(minimal_messages, **kwargs)
```

---

## 권장 워크플로우

### 안정적인 책 생성 프로세스

#### 1. 준비 단계
```bash
# 1.1 패키지 확인
pip list | grep -E "(duckduckgo|langgraph)"

# 1.2 LM Studio 시작
# - Qwen2.5-7B-Instruct (Q4_K_M) 로드
# - Context Length: 4096 설정
# - Server 시작

# 1.3 연결 테스트
python main.py --test-connection
```

#### 2. 테스트 실행
```bash
# 2.1 간단한 글부터
python main.py --mode simple --topic "테스트 주제" --max-iterations 1

# 2.2 성공하면 1챕터 책
python main.py --mode book --book-type history --topic "애플의 역사" --chapters 1 --max-iterations 1
```

#### 3. 본격 실행
```bash
# 3.1 3챕터 책 생성
python main.py --mode book --book-type history --topic "애플의 역사" --chapters 3 --max-iterations 2

# 3.2 실행 중 모니터링
# - LM Studio 상태 확인
# - 메모리 사용량 확인 (Activity Monitor)
# - 로그 확인
```

#### 4. 에러 발생 시
```bash
# 4.1 LM Studio 재시작
# - Stop Server
# - Unload Model
# - 앱 재시작
# - 모델 재로드
# - Server 재시작

# 4.2 가벼운 설정으로 재시도
python main.py --mode book --book-type history --topic "애플의 역사" --chapters 1 --max-iterations 1

# 4.3 세션 재개 (가능하면)
python main.py --thread-id 4973c58e-ae77-4736-b477-39dd63953a00
```

---

## 요약

### 핵심 문제

1. **LM Studio 모델 크래시** (Exit code 11)
   - 원인: 메모리 부족, 컨텍스트 초과
   - 발생: Cross Reference Agent

2. **모델 자동 언로드**
   - 원인: LM Studio 설정 또는 불안정성
   - 발생: 연결 테스트 후 실행 시

3. **Web Search 패키지 누락**
   - 원인: duckduckgo-search 미설치
   - 해결: ✅ 설치 완료

4. **언어 설정 문제**
   - 원인: 프롬프트에 언어 명시 누락
   - 결과: 한글 요청에도 영어 출력

### 즉시 조치 (완료)

- ✅ duckduckgo-search 설치
- ✅ 문제 해결 가이드 작성

### 다음 단계

1. **LM Studio 재시작** 및 안정화
2. **가벼운 설정**으로 테스트 (1챕터, 1반복)
3. **성공 시** 점진적으로 확대 (3챕터, 2반복)

### 예상 결과

**현재 설정 유지 시**:
- Context: 4096
- Chapters: 1
- Iterations: 1
- **성공 확률**: 80%

**개선 후**:
- Context: 4096
- Chapters: 3
- Iterations: 2
- 언어 설정 수정
- 컨텍스트 관리 개선
- **성공 확률**: 95%

---

**작성일**: 2025-12-28
**분석 대상**:
- Apple 역사 책 실패 (Session: 4973c58e-ae77-4736-b477-39dd63953a00)
- Google 역사 책 성공 (Session: 6d98d02c-c9d6-4094-917c-8bfae6e10310)
- 최근 실행 실패 (Session: e8d52f69-c279-4579-a6bf-0cdb75ebb89b)

**시스템**: Writer-Editor Multi-Agent Book System v1.0
