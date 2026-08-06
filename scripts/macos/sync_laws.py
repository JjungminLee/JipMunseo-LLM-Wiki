#!/usr/bin/env python3
"""
raw/laws/_sources.json에 등록된 법령/조문을 법제처 Open API(law.go.kr)로 조회해서
시행일 변경을 감지한다. Windows용 scripts/sync-laws.ps1의 macOS 네이티브 버전 —
Python3 표준 라이브러리만 쓰며(urllib/json/xml.etree), brew/pwsh 설치가 필요 없다.

최초 설정:
  1) https://open.law.go.kr 에서 OC(API 인증키) 무료 발급
  2) export LAW_API_OC="발급받은ID"  (또는 --oc 로 직접 전달)

사용법:
  python3 scripts/macos/sync_laws.py                    # 조회 + 변경 감지만
  python3 scripts/macos/sync_laws.py --dry-run           # 파일 변경 없이 확인만
  python3 scripts/macos/sync_laws.py --commit            # 변경 감지 시 git commit까지
  python3 scripts/macos/sync_laws.py --commit --auto-ingest  # + claude CLI로 wiki 재작성 시도(과금 발생)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "raw" / "laws" / "_sources.json"
DEBUG_DIR = REPO_ROOT / "raw" / "_api-debug"
CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"
REFERER = "https://www.law.go.kr"


def fetch_xml(url: str) -> str:
    req = urllib.request.Request(url, headers={"Referer": REFERER})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")


def find_text(root: ET.Element, tag: str):
    node = root.find(f".//{tag}")
    return node.text.strip() if node is not None and node.text else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--oc", default=os.environ.get("LAW_API_OC"))
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--auto-ingest", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.oc:
        print(
            "OC 인증키가 없습니다. https://open.law.go.kr 에서 발급받아 "
            "'export LAW_API_OC=발급ID'로 설정하거나 --oc로 전달하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    changed = []

    for law in manifest:
        law_name = law["법령명"]
        print(f"== {law_name} 확인 중 ==")

        if not law.get("MST"):
            search_url = (
                "http://www.law.go.kr/DRF/lawSearch.do?"
                + urllib.parse.urlencode({"OC": args.oc, "target": "law", "type": "XML", "query": law_name})
            )
            try:
                search_xml = fetch_xml(search_url)
            except Exception as e:
                print(f"  검색 API 호출 실패: {e}", file=sys.stderr)
                continue
            root = ET.fromstring(search_xml)
            law_node = root.find(".//law")
            mst = law_node.findtext("법령일련번호") if law_node is not None else None
            if not mst:
                print(f"  MST(법령일련번호)를 찾지 못했습니다. raw/_api-debug/search_{law_name}.xml 확인 필요")
                (DEBUG_DIR / f"search_{law_name}.xml").write_text(search_xml, encoding="utf-8")
                continue
            law["MST"] = mst
            print(f"  MST 확인: {mst}")

        for jo in law["JO"]:
            detail_url = (
                "http://www.law.go.kr/DRF/lawService.do?"
                + urllib.parse.urlencode(
                    {"OC": args.oc, "target": "lawjosub", "MST": law["MST"], "JO": jo, "type": "XML"}
                )
            )
            try:
                detail_xml = fetch_xml(detail_url)
            except Exception as e:
                print(f"  ({jo}) 조회 실패: {e}", file=sys.stderr)
                continue

            debug_file = DEBUG_DIR / f"{law_name}_{jo}.xml"
            debug_file.write_text(detail_xml, encoding="utf-8")

            root = ET.fromstring(detail_xml)
            effective_date = find_text(root, "시행일자")
            promulgated_date = find_text(root, "공포일자")
            content = find_text(root, "조문내용")

            if not effective_date and not content:
                print(f"  ({jo}) 예상 필드를 찾지 못함 — {debug_file} 에서 실제 태그명 확인 필요")
                continue

            cache_key = f"캐시_{jo}"
            prev_value = law.get(cache_key)
            if effective_date and effective_date != prev_value:
                print(f"  변경 감지: {jo} → 시행일 {effective_date} (이전: {prev_value or '없음(최초)'})")
                changed.append(
                    {
                        "법령명": law_name,
                        "JO": jo,
                        "시행일자": effective_date,
                        "공포일자": promulgated_date,
                        "raw_file": law["raw_file"],
                        "debug": str(debug_file.relative_to(REPO_ROOT)),
                    }
                )
                if not args.dry_run:
                    law[cache_key] = effective_date
            else:
                print(f"  변경 없음 ({jo})")

    if not changed:
        print("\n변경된 조문이 없습니다.")
        return

    print("\n=== 변경 요약 ===")
    for c in changed:
        print(f"  {c['법령명']} {c['JO']} → 시행일 {c['시행일자']} (공포 {c['공포일자']})")

    if args.dry_run:
        print("\n--dry-run 이므로 파일은 갱신하지 않았습니다.")
        return

    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    entry_lines = "\n".join(
        f"  - {c['법령명']} {c['JO']} → 시행일 {c['시행일자']} (raw/_api-debug 참고, {c['raw_file']} 재검증 필요)"
        for c in changed
    )
    entry = f"\n- (minor) 법령 배치 동기화 감지 ({date.today().isoformat()}):\n{entry_lines}"
    changelog = CHANGELOG_PATH.read_text(encoding="utf-8")
    changelog = changelog.replace("## [Unreleased]", "## [Unreleased]" + entry, 1)
    CHANGELOG_PATH.write_text(changelog, encoding="utf-8")
    print("\nCHANGELOG.md에 기록했습니다.")

    if args.commit:
        law_names = ", ".join(sorted({c["법령명"] for c in changed}))
        subprocess.run(["git", "-C", str(REPO_ROOT), "add", "raw/laws/_sources.json", "CHANGELOG.md"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(REPO_ROOT),
                "commit",
                "-m",
                f"법령 배치 동기화: {law_names} 시행일 변경 감지 ({date.today().isoformat()})",
            ],
            check=True,
        )

    if args.auto_ingest:
        claude_path = shutil.which("claude")
        if not claude_path:
            print("claude CLI를 찾지 못해 --auto-ingest를 건너뜁니다.", file=sys.stderr)
        else:
            for c in changed:
                print(f"\nclaude로 {c['raw_file']} / 관련 wiki 재ingest 요청 중...")
                prompt = (
                    f"SCHEMA.md 컨벤션에 따라 {c['debug']} (법제처 API 원본 응답, "
                    f"{c['법령명']} {c['JO']})의 내용을 바탕으로 {c['raw_file']}을 갱신하고, "
                    f"source_refs로 이 파일을 참조하는 wiki/*.md 페이지를 SCHEMA.md §3, §9 규칙대로 "
                    f"재작성해줘. 새 시행일: {c['시행일자']}"
                )
                subprocess.run([claude_path, "-p", prompt])


if __name__ == "__main__":
    main()
