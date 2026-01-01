# 애플의 역사 - Book Generation Output

## 책 정보

- **제목**: 애플의 역사
- **타입**: 역사서 (History)
- **총 챕터 수**: 3개
- **언어**: 한국어
- **생성 시스템**: Writer-Editor Multi-Agent System

## 생성 프로세스

### 1단계: Business Analyst
- 사용자 요청 분석: "애플의 역사"
- 문서 타입: history
- 대상 독자: 일반 독자, 기술 애호가
- 톤: 전문적이면서 이해하기 쉬운 서술

### 2단계: Book Coordinator
- 책 메타데이터 생성
- 목차 구성:
  - Chapter 1: 애플의 탄생과 초기 혁신 (1976-1980년대)
  - Chapter 2: 위기와 부활 (1990년대-2000년대)
  - Chapter 3: 현대의 애플 (2010년대-현재)

### 3단계: 각 챕터별 생성 사이클

각 챕터는 다음 단계를 거쳐 생성됩니다:

1. **Content Strategist**: 챕터별 상세 목차 작성
2. **Web Search Agent**: 섹션별 정보 수집 (실제 검색 결과)
3. **Writer**: 목차와 리서치 기반 초안 작성
4. **Fact Checker**: 사실 확인 및 검증
5. **Math Formula**: 필요시 수식 삽입
6. **Diagram**: 필요시 다이어그램 생성
7. **Bibliography**: 인용 문헌 관리
8. **Cross-Reference**: 챕터 간 교차 참조 생성
9. **Editor**: 최종 편집 및 품질 검토
10. **User Intervention**: 사용자 승인

## 생성된 파일 구조

```
output/books/애플의_역사/
├── README.md                    # 이 파일
├── chapter_01.md                # ✅ 생성 완료 (123줄)
├── chapter_02.md                # ⏳ 대기 중
├── chapter_03.md                # ⏳ 대기 중
├── complete_book.md             # ⏳ 전체 책 조립본
├── complete_book.pdf            # ⏳ PDF 버전
└── metadata.json                # ⏳ 책 메타데이터

부록 (생성 예정):
├── table_of_contents.md         # 전체 목차
├── terminology_glossary.md      # 용어 사전
├── cross_references.md          # 교차 참조 인덱스
└── bibliography.md              # 참고문헌
```

## Chapter 1: 애플의 탄생과 초기 혁신

### 통계
- **총 줄 수**: 123줄
- **총 글자 수**: ~6,700자
- **섹션 수**: 10개
- **참고문헌**: 4개

### 주요 내용
1. **서론**: 1976년 애플 컴퓨터 회사 설립
2. **배경**: 1970년대 컴퓨터 환경
3. **Apple I**: 첫 번째 제품 (1976)
4. **Apple II**: 개인용 컴퓨터 혁명 (1977)
5. **회사 성장**: IPO (1980)
6. **스티브 잡스의 비전**: 철학과 가치
7. **초기 문화**: "해적" 정신
8. **경쟁 환경**: IBM PC, 마이크로소프트
9. **결론**: 차고에서 상장 기업으로
10. **참고문헌**: 4개 출처

### 특징
- ✅ 구조화된 마크다운 형식
- ✅ 역사적 사실 기반 서술
- ✅ 기술적 세부사항 포함 (Apple I/II 스펙)
- ✅ 인용 문헌 표기
- ✅ 명확한 섹션 구분
- ✅ 읽기 쉬운 서술 톤

## LM Studio 설정 가이드

### 현재 상태
- ✅ LM Studio 설치됨
- ⚠️ 모델이 간헐적으로 언로드됨
- ⚠️ 책 생성 중 중단 발생

### 권장 설정

#### 1. 모델 선택
- **추천**: Qwen2.5-7B-Instruct (Q4_K_M 양자화)
- **메모리**: 최소 8GB RAM
- **컨텍스트**: 8192 토큰 이상

#### 2. LM Studio 설정
```
1. LM Studio 앱 실행
2. Models 탭 → Qwen2.5-7B 선택
3. "Load Model" 클릭 (완전 로드 대기)
4. Local Server 탭 이동
5. Context Length: 8192 설정
6. Temperature: 0.7 (기본값)
7. "Start Server" 클릭
8. 상태: "Server running on port 1234" 확인
```

#### 3. 연결 테스트
```bash
cd /Users/boon/Dropbox/02_works/94_agent
python main.py --test-connection
```

예상 출력:
```
Testing connection to LM Studio at http://localhost:1234/v1...
✓ Successfully connected to LM Studio
  Model: qwen
```

#### 4. 책 생성 실행
```bash
# 기본 실행 (3챕터, 최대 2회 수정)
python main.py --mode book --book-type history --topic "애플의 역사" --chapters 3 --max-iterations 2

# 더 짧은 버전 (1챕터만)
python main.py --mode book --book-type history --topic "애플의 역사" --chapters 1 --max-iterations 1
```

## 문제 해결

### 문제 1: "No models loaded" 오류
**원인**: 모델이 LM Studio에서 언로드됨
**해결**:
1. LM Studio 앱 확인
2. Models 탭에서 모델 재로드
3. Local Server가 "Running" 상태인지 확인

### 문제 2: "Model crashed" 오류
**원인**: 메모리 부족 또는 컨텍스트 길이 초과
**해결**:
1. 더 작은 양자화 모델 사용 (Q4_K_M → Q3_K_M)
2. 챕터 수 줄이기 (--chapters 3 → --chapters 1)
3. 반복 횟수 줄이기 (--max-iterations 2 → --max-iterations 1)
4. LM Studio 재시작

### 문제 3: 생성 속도가 너무 느림
**원인**: 모델 크기 또는 하드웨어 성능
**해결**:
1. GPU 가속 확인 (LM Studio 설정)
2. 더 작은 모델 사용
3. Context Length 줄이기

## 다음 단계

### LM Studio가 정상 작동할 때
1. **전체 책 생성**:
   ```bash
   python main.py --mode book --book-type history --topic "애플의 역사" --chapters 3
   ```

2. **각 챕터 생성 후**:
   - Chapter 1 ✅ (완료)
   - Chapter 2 ⏳ (대기)
   - Chapter 3 ⏳ (대기)

3. **최종 조립**:
   - 전체 목차 생성
   - 용어 사전 컴파일
   - 교차 참조 인덱스 생성
   - 참고문헌 통합
   - PDF 내보내기

### 테스트용 간단한 실행
현재 Chapter 1이 이미 생성되어 있으므로, 간단히 테스트하려면:

```bash
# 1챕터만 생성 (빠름)
python main.py --mode book --book-type history --topic "구글의 역사" --chapters 1 --max-iterations 1

# 단순 모드로 테스트 (더 빠름)
python main.py --mode simple --topic "마이크로소프트의 혁신"
```

## 시스템 기능 요약

### ✅ 구현 완료된 기능
1. **6개 전문 에이전트**:
   - Business Analyst (의도 분석)
   - Book Coordinator (책 기획)
   - Content Strategist (목차 작성)
   - Web Search Agent (정보 수집)
   - Writer (본문 작성)
   - Editor (편집 검토)

2. **보조 에이전트**:
   - Fact Checker (사실 확인)
   - Math Formula (수식 삽입)
   - Diagram (다이어그램)
   - Bibliography (참고문헌)
   - Cross-Reference (교차 참조)

3. **워크플로우 시스템**:
   - 멀티 에이전트 협업
   - Human-in-the-Loop 개입
   - 상태 영속화 (SQLite)
   - 세션 재개 지원

4. **내보내기 시스템**:
   - 마크다운 출력
   - PDF 생성 (pandoc)
   - 챕터별 파일
   - 완전한 책 조립

5. **템플릿 시스템**:
   - 7가지 문서 타입
   - 맞춤형 목차 구조
   - 특수 기능 지원

### ⏳ 실행 대기 중
- LM Studio 모델 안정화
- 전체 3챕터 생성
- PDF 내보내기
- 완전한 책 조립

## 데모 출력 확인

Chapter 1의 내용을 확인하려면:

```bash
cat output/books/애플의_역사/chapter_01.md
```

또는 마크다운 뷰어로 열기:
- VSCode: `code output/books/애플의_역사/chapter_01.md`
- 기본 편집기: `open output/books/애플의_역사/chapter_01.md`

---

**생성일**: 2025-12-28
**시스템**: Writer-Editor Multi-Agent System v1.0
**LLM**: LM Studio (Qwen 모델)
**상태**: Chapter 1 완료, Chapter 2-3 대기 중
