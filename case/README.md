# case/ — private

이 디렉토리는 `.gitignore`로 커밋에서 제외된다 (`*.template` 파일만 예외).
`profile.md`, `case-index.md`, `cases/*.md`, `archived/*.md`, `fieldnotes/*.md`는
개인 재무·거주 정보를 담으므로 이 레포를 공개(오픈소스)로 유지하는 동안 절대 커밋되면 안 된다.

## 시작하는 법

Obsidian이라면 커맨드 팔레트(`Ctrl/Cmd+P`) → **"Templater: Create 온보딩"** 실행 — 몇 가지 질문에
답하면 `profile.md`/`case-index.md`가 자동 생성된다 (`_templates/온보딩.md`). **몇 번을 다시
실행해도 안전** — 이미 채워진 필드는 다시 안 물어보고 빈 항목만 채운다. 매수 이력을 추가할 땐
아파트명·지역만 입력하면 국토교통부 실거래가 API로 가격을 자동 조회한다 (`DATA_GO_KR_KEY` 설정
필요 — [scripts/README.md](../scripts/README.md) 참고, 없으면 수동 입력으로 자동 전환). CLI로만
쓴다면:

```
cp case/profile.md.template case/profile.md
cp case/case-index.md.template case/case-index.md
```

이후 케이스가 생기면 `case/cases/`에 [SCHEMA.md §6](../SCHEMA.md#6-케이스-타입-taxonomy)의
프론트매터 스키마를 따라 파일을 추가한다. Templater 플러그인이 설정돼 있다면
`_templates/새케이스.md`로 타입 선택 → 프론트매터 자동 생성까지 가능하다.

## 케이스 보드 (선택)

`case/보드.md`는 Kanban 플러그인으로 `status`별 케이스를 시각적으로 옮겨보는 용도의 개인용
칸반이다 — `case/cases/*.md`와 마찬가지로 gitignore 대상이며, 각 케이스 파일의 `status`
필드가 진짜 소스이고 이 보드는 그걸 보기 편하게 옮겨 적는 보조 뷰일 뿐이다(자동 동기화 아님).
루트의 `Dashboard.md`(Dataview, public)가 항상 `status` 필드 기준의 진짜 최신 상태를 보여준다.
