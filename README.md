# JipMunSeo — 부동산 정책/세법 LLM Wiki Agent
![alt text](Gemini_Generated_Image_yaowl9yaowl9yaow.png)

부동산 정책과 세법을 위키처럼 찾아볼 수 있게 하는 개인용 LLM 에이전트. 법령/세법 근거와 실제
매매·임장 경험에서 나온 인사이트를 구분해서 제공하는 것이 핵심.

Karpathy 패턴(raw/wiki/index.md/SCHEMA.md, git-native, RAG 없음)을 따르는 CLI 기반 도구다.
자세한 설계 배경은 [ARCHITECTURE.md](ARCHITECTURE.md), 컨벤션은 [SCHEMA.md](SCHEMA.md) 참고.

```
raw/     — 원본 archive (법령·판례·유권해석). public.
wiki/    — LLM이 raw/를 읽고 생성한 위키 페이지. public.
index.md — 전체 위키 목차. public.
case/    — 본인 profile·케이스·임장기록. private (.gitignore).
```

## 시작하는 법

```
cp case/profile.md.template case/profile.md
cp case/case-index.md.template case/case-index.md
```

이후 Claude Code(또는 다른 에이전트)에서 [SCHEMA.md](SCHEMA.md)를 컨텍스트로 두고
`ingest`/`query`/`plan`/`notify`를 수행한다.

## .gitignore된 것들 — clone하면 없는 파일/설정

이 레포를 다른 기기(맥북 등)에 clone하면 아래는 전부 비어있다. 의도적으로 git에 올리지
않는 것들이라, 기기마다 새로 설정해야 한다.

| 안 올라오는 것 | 왜 | 새 기기에서 할 일 |
|---|---|---|
| `case/profile.md`, `case/case-index.md`, `case/cases/*.md`, `case/archived/*.md`, `case/fieldnotes/*.md` | 개인 재무·거주정보 (private, SCHEMA.md §0) | `case/*.template`를 복사해서 시작. 기존에 실제 데이터가 쌓여 있다면 git이 아닌 별도의 안전한 방법(AirDrop 등)으로 직접 옮길 것 |
| `raw/_api-debug/` | 배치 스크립트의 임시 API 응답 덤프, 큐레이션된 원본이 아님 | 신경 쓸 필요 없음. 스크립트 처음 돌리면 자동 생성됨 |
| `.obsidian/workspace.json`, `workspace-mobile.json` | Obsidian 개인 UI 상태(탭 배치 등) | Obsidian이 새로 만듦. 제외 필터가 담긴 `.obsidian/app.json`은 git에 있으므로 그대로 적용됨 |
| `LAW_API_OC` 환경변수 (파일 아님) | 법제처 API 인증키, 코드/문서에 박아두지 않음 | 기기별로 새로 설정 — [scripts/README.md](scripts/README.md) 참고 |
| 작업 스케줄러(Windows) / launchd(macOS) 등록 | OS 레벨 설정이라 git으로 옮겨지지 않음 | 기기별로 새로 등록 — [scripts/README.md](scripts/README.md) 참고 |
| Obsidian vault 등록 | Obsidian 앱 자체의 전역 설정(레포 밖에 저장됨) | Obsidian에서 이 폴더를 "Open folder as vault"로 새로 열기 |
| `.obsidian/plugins/*` (Dataview, Kanban, Templater 본체) | 3rd-party 플러그인 바이너리를 public repo에 vendor하지 않음 | Settings → Community plugins → Browse에서 "Dataview"/"Kanban"/"Templater" 검색 후 설치. `community-plugins.json`에 활성화 목록은 이미 커밋돼 있어 설치만 하면 자동 켜짐 |

## 맥북에서 시작하기

1. `git clone git@github-personal:JjungminLee/JipMunseo-LLM-Wiki.git` (SSH host alias가 맥에도
   설정돼 있어야 함 — 없으면 `https://github.com/JjungminLee/JipMunseo-LLM-Wiki.git`로 clone)
2. 위 표대로 `case/*.template` 복사
3. Obsidian에서 이 폴더를 vault로 열기
4. OC 키 설정 + 자동 동기화 등록은 [scripts/README.md](scripts/README.md)의 "macOS" 섹션 참고

## 개정 자동 감지

[scripts/sync-laws.ps1](scripts/README.md)이 법제처 Open API로 등록된 법령의 시행일 변경을
주기적으로 감지한다. 설정법은 [scripts/README.md](scripts/README.md) 참고.

## 열람 인터페이스

이 레포 폴더 자체가 Obsidian vault로 등록되어 있다 (Obsidian 실행 후 vault 전환에서 선택).
`[[위키링크]]`가 그래프 뷰·백링크로 바로 보인다. wiki/ 문서가 어느 정도 쌓이면
[Understand-Anything](https://github.com/Egonex-AI/Understand-Anything)을 얹어 지식그래프
대시보드를 추가하는 걸 고려 중 — 지금은 페이지 수가 적어 그래프가 의미 있는 크기가 아니라
보류.

프론트매터를 그래프 이상으로 활용하기 위해 Dataview/Kanban/Templater 3개 커뮤니티 플러그인을
쓴다 (설치는 위 표 참고):

- **`Dashboard.md`** (public, Dataview) — 최근 개정된 wiki, 진행 중/종료 케이스, `linked_case`
  누락·고아 페이지·오래된 `최종개정_시행일` 등 SCHEMA.md §11 lint 체크 일부를 라이브 쿼리로 보여줌
- **`case/보드.md`** (private, Kanban) — 케이스를 `status` 단계별 칸반으로. 각 케이스 파일의
  `status` 필드가 진짜 소스이며 이 보드는 보조 뷰(자동 동기화 아님, `case/README.md` 참고)
- **`_templates/새케이스.md`** (public, Templater) — 케이스 타입 선택 → SCHEMA.md §6 프론트매터
  자동 생성. Command palette → "Templater: Create new note from template"
- **`.obsidian/snippets/jipmunseo.css`** — `category`/`status`/시행일 필드를 배지로 강조하고,
  아직 안 쓰인 `[[위키링크]]` 자리표시자를 점선으로 구분. `> [!TIP]`/`[!NOTE]`/`[!WARNING]`
  콜아웃(SCHEMA.md §3)은 Obsidian에서 타입별 색이 자동 적용되고 GitHub에서도 네이티브 alert로
  렌더링됨
