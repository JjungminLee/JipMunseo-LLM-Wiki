# scripts/

## sync-laws.ps1 — 법령 개정 배치 동기화

`raw/laws/_sources.json`에 등록된 법령·조문을 [법제처 Open API](https://open.law.go.kr)로 조회해
시행일 변경을 감지한다.

### 1) 최초 설정

1. https://open.law.go.kr 에서 회원가입 후 OC(API 인증키) 무료 발급 (승인까지 보통 1~2일)
2. 발급받은 키를 환경변수로 등록 (PowerShell 프로필에 넣어두면 매번 안 쳐도 됨):
   ```powershell
   $env:LAW_API_OC = "발급받은ID"
   ```

### 2) 수동 실행

```powershell
cd C:\Users\USER\Documents\vscode\JipMunseo-LLM-Wiki
.\scripts\sync-laws.ps1                  # 조회 + 변경 감지만
.\scripts\sync-laws.ps1 -DryRun          # 파일 변경 없이 확인만
.\scripts\sync-laws.ps1 -Commit          # 변경 감지 시 git commit까지
.\scripts\sync-laws.ps1 -Commit -AutoIngest   # + claude CLI로 wiki 재작성까지 시도 (과금 발생)
```

**필드명 검증 완료 (2026-08-06, 실제 OC로 실측):** `시행일자`/`공포일자`/`조문내용` XPath는
실제 응답과 일치하는 것으로 확인됐다. 그래도 스크립트는 매 조회마다
`raw/_api-debug/<법령명>_<JO>.xml`에 원본 응답을 남기니, 새 법령을 추가했는데 필드를 못
찾는다는 경고가 뜨면 이 파일을 열어 실제 태그명을 확인하고 `Get-XmlText $xml "//시행일자"`
같은 XPath를 맞게 고친다.

새 법령/조문을 감시 대상에 추가하려면 `raw/laws/_sources.json`에 항목을 추가한다. `JO`는
`조문번호 × 100`을 6자리로 0-padding한 값이다 (예: 제89조 → `008900`, 제154조 → `015400`).

### 3) 주기 실행 등록 (Windows 작업 스케줄러)

**이미 등록되어 있음** — `JipMunSeo-LawSync` 작업이 **매주 월요일 오전 9시**에
`sync-laws.ps1 -Commit`을 실행한다. `LAW_API_OC`는 사용자 환경변수로 영구 등록해뒀다.
등록에 쓴 명령(재등록·다른 기기 참고용):

```powershell
[Environment]::SetEnvironmentVariable("LAW_API_OC", "발급받은ID", "User")

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument '-NoProfile -ExecutionPolicy Bypass -File "C:\Users\USER\Documents\vscode\JipMunseo-LLM-Wiki\scripts\sync-laws.ps1" -Commit'
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am
Register-ScheduledTask -TaskName "JipMunSeo-LawSync" -Action $action -Trigger $trigger `
  -Description "법제처 Open API로 raw/laws 개정 감지 (JipMunSeo)"
```

확인: `Get-ScheduledTask -TaskName "JipMunSeo-LawSync"` / `schtasks /query /tn "JipMunSeo-LawSync" /v /fo list`
제거: `Unregister-ScheduledTask -TaskName "JipMunSeo-LawSync" -Confirm:$false`

### 4) macOS(맥북) — Python3 + launchd (PowerShell 불필요)

Windows는 PowerShell이 표준이라 `sync-laws.ps1`을 그대로 쓰지만, macOS는
[scripts/macos/sync_laws.py](macos/sync_laws.py)라는 별도 네이티브 버전을 쓴다 — 로직은
동일하고 Python3 표준 라이브러리(`urllib`/`json`/`xml.etree`)만 사용해서 **brew나 pwsh
설치가 전혀 필요 없다**. 스케줄러도 macOS 표준인 **launchd**(cron보다 권장됨)를 쓴다.

1. Python3 확인 (macOS에 Xcode Command Line Tools가 설치돼 있으면 기본 포함):
   ```bash
   python3 --version
   # 없다면: xcode-select --install
   ```
2. 수동 실행으로 먼저 확인:
   ```bash
   export LAW_API_OC="발급받은ID"
   python3 scripts/macos/sync_laws.py --dry-run
   ```
3. [scripts/macos/com.jipmunseo.lawsync.plist.template](macos/com.jipmunseo.lawsync.plist.template)를
   복사해서 실제 값(사용자 홈 경로, OC 키)을 채우고 **레포 밖**
   `~/Library/LaunchAgents/com.jipmunseo.lawsync.plist`로 저장한다 (OC 키가 들어가는 실제
   파일이라 레포에는 template만 두고 실제 파일은 git 대상 밖에 둔다):
   ```bash
   cp scripts/macos/com.jipmunseo.lawsync.plist.template ~/Library/LaunchAgents/com.jipmunseo.lawsync.plist
   # 에디터로 YOUR_USERNAME, YOUR_OC_KEY를 실제 값으로 수정 (python3 경로는 `which python3`로 확인)
   ```
4. 등록/시작:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.jipmunseo.lawsync.plist
   ```
5. 확인/해제:
   ```bash
   launchctl list | grep jipmunseo
   launchctl unload ~/Library/LaunchAgents/com.jipmunseo.lawsync.plist   # 해제
   ```

기본값은 Windows와 동일하게 **매주 월요일 오전 9시**(plist의 `StartCalendarInterval`)로
맞춰뒀다. 로그는 `/tmp/jipmunseo-lawsync.log`(`.err.log`)에서 확인한다. `sync_laws.py`는
Windows에서 실행할 파이썬이 없어 이번 세션에서 직접 실행 검증은 못 했다 — 맥북에서 처음
돌릴 때 `--dry-run`으로 한 번 확인해볼 것.

### 5) iTerm MOTD — 터미널 열 때 새 업데이트 알림

launchd가 매주 CHANGELOG.md에 새 항목을 추가해도, 직접 열어보지 않으면 모른다.
[scripts/macos/motd.sh](macos/motd.sh)는 새 터미널을 열 때마다 CHANGELOG.md에 **새로
추가된 줄**이 있는지 확인해서 있으면 보여주고, 없으면 아무것도 출력하지 않는다 (마지막으로
본 상태를 `.local/changelog_snapshot.txt`에 스냅샷으로 저장 — 이 파일은 기기 로컬 상태라
git에 올리지 않는다).

`~/.zshrc`에 추가:

```bash
export JIPMUNSEO_ROOT="$HOME/JipMunseo-LLM-Wiki"   # 실제 clone 경로로 수정
[ -f "$JIPMUNSEO_ROOT/scripts/macos/motd.sh" ] && source "$JIPMUNSEO_ROOT/scripts/macos/motd.sh"
```

이후 iTerm에서 새 창/탭을 열 때마다 자동 실행된다. 최초 1회는 스냅샷이 없어서 조용히
스냅샷만 생성하고, 그다음부터 변경분만 보여준다. 즉시 테스트하려면:

```bash
source scripts/macos/motd.sh   # 첫 실행: 무출력(스냅샷 생성)
echo "- test" >> CHANGELOG.md
source scripts/macos/motd.sh   # 두번째 실행: 방금 추가한 줄이 보여야 함
git checkout CHANGELOG.md      # 테스트용 줄 되돌리기
```
