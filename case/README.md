# case/ — private

이 디렉토리는 `.gitignore`로 커밋에서 제외된다 (`*.template` 파일만 예외).
`profile.md`, `case-index.md`, `cases/*.md`, `archived/*.md`, `fieldnotes/*.md`는
개인 재무·거주 정보를 담으므로 이 레포를 공개(오픈소스)로 유지하는 동안 절대 커밋되면 안 된다.

## 시작하는 법

```
cp case/profile.md.template case/profile.md
cp case/case-index.md.template case/case-index.md
```

이후 케이스가 생기면 `case/cases/`에 [SCHEMA.md §6](../SCHEMA.md#6-케이스-타입-taxonomy)의
프론트매터 스키마를 따라 파일을 추가한다.
