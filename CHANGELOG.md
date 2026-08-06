# CHANGELOG

버전 규칙은 [SCHEMA.md §9](SCHEMA.md#9-버전패치-규칙) 참고. major.minor.patch =
구조변경.제도개정.표현수정.

## [Unreleased]

- (minor) `1세대1주택 비과세` 위키 페이지 최초 작성 및 원문 검증 완료 — `scripts/sync-laws.ps1`로
  법제처 Open API를 직접 조회해 소득세법 §89(법률 제21221호, 2026.1.1 시행), 시행령
  §154·§160(대통령령 제36343호, 2026.7.1 시행) verbatim 원문을 raw/laws/에 반영. 배치
  스크립트가 초안 작성 시점에는 알려지지 않았던 시행령 2026.7.1 개정을 실제로 발견함.
