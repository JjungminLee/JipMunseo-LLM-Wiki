# Dashboard

Dataview로 렌더링되는 라이브 대시보드. 이 파일은 쿼리 코드만 담고 있어 public으로 커밋해도
안전하다 — 실제 개인 데이터는 `case/`(gitignore 대상)에서만 읽어온다. `case/*.md`를 아직
만들지 않았다면(README "시작하는 법" 참고) 아래 케이스 섹션은 비어 보이는 게 정상이다.

## 📚 최근 개정/확인된 위키

```dataview
TABLE category AS 카테고리, 최종개정_시행일 AS 시행일, 최종확인일 AS 확인일
FROM "wiki"
SORT 최종개정_시행일 DESC, 최종확인일 DESC
```

## 🏗️ 진행 중인 케이스

```dataview
TABLE type AS 타입, status AS 상태, linked_case AS 연결케이스
FROM "case/cases"
WHERE status != "closed"
SORT status ASC
```

## 📦 종료된 케이스

```dataview
LIST
FROM "case/archived"
```

## ⚠️ 점검 필요 (SCHEMA.md §11 lint 일부 자동화)

**`linked_case` 없는 갈아타기 케이스:**

```dataview
LIST
FROM "case/cases"
WHERE contains(type, "갈아타기") AND !linked_case
```

**어느 wiki 페이지도 링크하지 않는 고아 페이지:**

```dataview
LIST
FROM "wiki"
WHERE length(file.inlinks) = 0
```

**`최종개정_시행일`이 오래된(1년 이상 미확인) 위키 페이지:**

```dataview
LIST
FROM "wiki"
WHERE 최종개정_시행일 AND date(최종개정_시행일) < date(today) - dur(365 days)
```
