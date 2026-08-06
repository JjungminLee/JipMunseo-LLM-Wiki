<#
.SYNOPSIS
  raw/laws/_sources.json에 등록된 법령/조문을 법제처 Open API(law.go.kr)로 조회해서
  시행일 변경을 감지하고, 감지되면 raw/_api-debug/에 원본 응답을 남기고 CHANGELOG.md에 기록한다.

.DESCRIPTION
  최초 실행 전 준비:
    1) https://open.law.go.kr 에서 OC(API 인증키) 무료 발급
    2) $env:LAW_API_OC = "발급받은ID"  (또는 -OC 파라미터로 직접 전달)

  이 스크립트는 조문 원문(raw/laws/*.md)을 자동으로 덮어쓰지 않는다 — 법제처 API 응답
  스키마의 정확한 태그명을 아직 실제 호출로 검증하지 못했기 때문에(SCHEMA.md의 "원문 대조 필요"
  TODO와 동일한 이유), 최초 몇 번은 raw/_api-debug/*.xml을 직접 확인하며 파싱 필드를 맞춰야 한다.
  -AutoIngest를 쓰면 변경 감지 시 claude CLI를 headless로 불러 wiki/ 재작성까지 시도한다(과금 발생, 기본 off).

.PARAMETER OC
  법제처 Open API 인증키. 생략하면 $env:LAW_API_OC 사용.

.PARAMETER Commit
  변경 감지 시 raw/laws/_sources.json, CHANGELOG.md를 git commit까지 수행.

.PARAMETER AutoIngest
  변경 감지 시 claude CLI(-p headless)로 관련 wiki 페이지 재작성을 시도.

.PARAMETER DryRun
  API만 조회하고 파일/manifest는 건드리지 않음.

.EXAMPLE
  $env:LAW_API_OC = "myid"
  .\scripts\sync-laws.ps1

.EXAMPLE
  .\scripts\sync-laws.ps1 -Commit -AutoIngest
#>

param(
    [string]$OC = $env:LAW_API_OC,
    [switch]$Commit,
    [switch]$AutoIngest,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$ManifestPath = Join-Path $RepoRoot "raw\laws\_sources.json"
$DebugDir = Join-Path $RepoRoot "raw\_api-debug"
$ChangelogPath = Join-Path $RepoRoot "CHANGELOG.md"

if (-not $OC) {
    Write-Error "OC 인증키가 없습니다. https://open.law.go.kr 에서 발급받아 `$env:LAW_API_OC = '발급ID'`로 설정하거나 -OC 파라미터로 전달하세요."
    exit 1
}

function Get-XmlText {
    param($Node, [string]$XPath)
    $found = $Node.SelectSingleNode($XPath)
    if ($null -ne $found) { return $found.InnerText }
    return $null
}

$manifest = Get-Content $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$changed = @()
New-Item -ItemType Directory -Force -Path $DebugDir | Out-Null

foreach ($law in $manifest) {
    $lawName = $law.'법령명'
    Write-Host "== $lawName 확인 중 =="

    if (-not $law.MST) {
        $searchUrl = "http://www.law.go.kr/DRF/lawSearch.do?OC=$OC&target=law&type=XML&query=$([uri]::EscapeDataString($lawName))"
        try {
            [xml]$searchResult = Invoke-RestMethod -Uri $searchUrl -Headers @{ Referer = "https://www.law.go.kr" }
        } catch {
            Write-Warning "  검색 API 호출 실패: $_"
            continue
        }
        $mst = Get-XmlText $searchResult "//law[1]/법령일련번호"
        if (-not $mst) {
            Write-Warning "  MST(법령일련번호)를 찾지 못했습니다. raw/_api-debug/search_$lawName.xml 확인 필요"
            $searchResult.OuterXml | Set-Content -Encoding utf8 (Join-Path $DebugDir "search_$lawName.xml")
            continue
        }
        $law.MST = $mst
        Write-Host "  MST 확인: $mst"
    }

    foreach ($jo in $law.JO) {
        $detailUrl = "http://www.law.go.kr/DRF/lawService.do?OC=$OC&target=lawjosub&MST=$($law.MST)&JO=$jo&type=XML"
        try {
            $rawText = Invoke-RestMethod -Uri $detailUrl -Headers @{ Referer = "https://www.law.go.kr" }
        } catch {
            Write-Warning "  ($jo) 조회 실패: $_"
            continue
        }

        [xml]$xml = $rawText
        $debugFile = Join-Path $DebugDir "$($lawName)_$jo.xml"
        $xml.OuterXml | Set-Content -Encoding utf8 $debugFile

        $시행일자 = Get-XmlText $xml "//시행일자"
        $공포일자 = Get-XmlText $xml "//공포일자"
        $조문내용 = Get-XmlText $xml "//조문내용"

        if (-not $시행일자 -and -not $조문내용) {
            Write-Warning "  ($jo) 예상 필드를 찾지 못함 — $debugFile 에서 실제 태그명 확인 필요"
            continue
        }

        $cacheKey = "캐시_$jo"
        $prevValue = $law.$cacheKey
        if ($시행일자 -and $시행일자 -ne $prevValue) {
            Write-Host "  변경 감지: $jo → 시행일 $시행일자 (이전: $(if ($prevValue) { $prevValue } else { '없음(최초)' }))"
            $changed += [pscustomobject]@{
                법령명   = $lawName
                JO       = $jo
                시행일자 = $시행일자
                공포일자 = $공포일자
                raw_file = $law.raw_file
                debug    = $debugFile
            }
            if (-not $DryRun) {
                if ($law.PSObject.Properties.Name -contains $cacheKey) {
                    $law.$cacheKey = $시행일자
                } else {
                    $law | Add-Member -NotePropertyName $cacheKey -NotePropertyValue $시행일자
                }
            }
        } else {
            Write-Host "  변경 없음 ($jo)"
        }
    }
}

if ($changed.Count -eq 0) {
    Write-Host "`n변경된 조문이 없습니다."
    exit 0
}

Write-Host "`n=== 변경 요약 ==="
$changed | Format-Table 법령명, JO, 시행일자, 공포일자 -AutoSize

if ($DryRun) {
    Write-Host "`n-DryRun 이므로 파일은 갱신하지 않았습니다."
    exit 0
}

$manifest | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 $ManifestPath

$entryLines = $changed | ForEach-Object { "  - $($_.법령명) $($_.JO) → 시행일 $($_.시행일자) (raw/_api-debug 참고, $($_.raw_file) 재검증 필요)" }
$entry = "`n- (minor) 법령 배치 동기화 감지 ($(Get-Date -Format 'yyyy-MM-dd')):`n" + ($entryLines -join "`n")
(Get-Content $ChangelogPath -Raw -Encoding UTF8) -replace [regex]::Escape("## [Unreleased]"), ("## [Unreleased]" + $entry) | Set-Content -Encoding utf8 $ChangelogPath
Write-Host "`nCHANGELOG.md에 기록했습니다."

if ($Commit) {
    git -C $RepoRoot add raw/laws/_sources.json CHANGELOG.md
    git -C $RepoRoot commit -m "법령 배치 동기화: $(($changed | ForEach-Object { $_.법령명 }) -join ', ') 시행일 변경 감지 ($(Get-Date -Format 'yyyy-MM-dd'))"
}

if ($AutoIngest) {
    $claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
    if (-not $claudeCmd) {
        Write-Warning "claude CLI를 찾지 못해 -AutoIngest를 건너뜁니다."
    } else {
        foreach ($c in $changed) {
            Write-Host "`nclaude로 $($c.raw_file) / 관련 wiki 재ingest 요청 중..."
            $prompt = "SCHEMA.md 컨벤션에 따라 $($c.debug) (법제처 API 원본 응답, $($c.법령명) $($c.JO))의 내용을 바탕으로 $($c.raw_file)을 갱신하고, source_refs로 이 파일을 참조하는 wiki/*.md 페이지를 SCHEMA.md §3, §9 규칙대로 재작성해줘. 새 시행일: $($c.시행일자)"
            & claude -p $prompt
        }
    }
}
