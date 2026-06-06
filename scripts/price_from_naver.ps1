param(
  [string]$InputPath = "artifacts/data/products_for_price_search.json",
  [string]$OutputPath = "artifacts/data/naver_price_candidates.json",
  [int]$Start = 0,
  [int]$Limit = 0,
  [int]$DelayMs = 250,
  [int]$MinConfidence = 75
)

$ErrorActionPreference = "Stop"

function U {
  param([int[]]$Codes)
  return -join ($Codes | ForEach-Object { [char]$_ })
}

function Normalize-Text {
  param([string]$Html)
  $decoded = [System.Net.WebUtility]::HtmlDecode($Html)
  $decoded = [regex]::Replace($decoded, "<[^>]+>", " ")
  $decoded = [regex]::Replace($decoded, "\s+", " ")
  return $decoded.Trim()
}

function Get-Tokens {
  param([string]$Value)
  $cleaned = [regex]::Replace($Value.ToLower(), "[^\p{L}\p{Nd}]+", " ")
  return @($cleaned -split "\s+" | Where-Object { $_.Length -ge 2 })
}

function Test-BundleContext {
  param([string]$Context)
  $lower = $Context.ToLower()
  $byeong = U @(0xBCD1)
  $boxKo = U @(0xBC15, 0xC2A4)
  $setKo = U @(0xC138, 0xD2B8)
  $dang = U @(0xB2F9)
  $ip = U @(0xC785)
  foreach ($word in @("2$byeong", "3$byeong", "4$byeong", "5$byeong", "6$byeong", "10$byeong", "2$ip", "3$ip", "4$ip", "5$ip", "6$ip", "1box", "box", $boxKo, $setKo, "100ml$dang")) {
    if ($lower.Contains($word)) { return $true }
  }
  return $false
}

function Test-BadContext {
  param([string]$Context)
  $words = @(
    (U @(0xBC30, 0xC1A1, 0xBE44)),
    (U @(0xBB34, 0xB8CC, 0xBC30, 0xC1A1)),
    (U @(0xC801, 0xB9BD)),
    (U @(0xD3EC, 0xC778, 0xD2B8)),
    (U @(0xB9AC, 0xBDF0)),
    (U @(0xD6C4, 0xAE30))
  )
  foreach ($word in $words) {
    if ($Context.Contains($word)) { return $true }
  }
  return $false
}

function Test-OtherVolume {
  param(
    [string]$Context,
    [int]$VolumeMl
  )
  $matches = [regex]::Matches($Context.ToLower(), "(\d{3,4})\s*ml")
  foreach ($match in $matches) {
    if ([int]$match.Groups[1].Value -ne $VolumeMl) { return $true }
  }
  return $false
}

function Get-PriceCandidates {
  param(
    [object]$Product,
    [string]$Query,
    [string]$Text,
    [int]$MinConfidence
  )

  $prices = New-Object System.Collections.Generic.List[object]
  $won = U @(0xC6D0)
  $dae = U @(0xB300)
  $pattern = "(?<!\d)([1-9]\d{0,2}(?:,\d{3})+|[1-9]\d{3,6})\s*$won(?!$dae)"
  $matches = [regex]::Matches($Text, $pattern)
  $nameTokens = Get-Tokens $Product.name

  foreach ($match in $matches) {
    if ($match.Index -gt 0 -and $Text.Substring($match.Index - 1, 1) -eq (U @(0xB9CC))) {
      continue
    }
    $start = [Math]::Max(0, $match.Index - 90)
    $length = [Math]::Min($Text.Length - $start, $match.Length + 180)
    $context = $Text.Substring($start, $length)
    $after = $Text.Substring($match.Index, [Math]::Min($Text.Length - $match.Index, $match.Length + 8))
    if ($after.Contains((U @(0xC774, 0xC0C1)))) {
      continue
    }

    if (Test-BadContext $context) { continue }
    if (Test-BundleContext $context) { continue }
    if (Test-OtherVolume $context ([int]$Product.volume_ml)) { continue }

    $price = [int](($match.Groups[1].Value) -replace ",", "")
    if ($price -lt 1000 -or $price -gt 300000) { continue }

    $lower = $context.ToLower()
    $compactContext = [regex]::Replace($lower, "\s+", "")
    $compactName = [regex]::Replace($Product.name.ToLower(), "\s+", "")
    $confidence = 45
    $matched = 0
    foreach ($token in $nameTokens) {
      if ($lower.Contains($token)) { $matched += 1 }
    }
    if ($nameTokens.Count -gt 0) {
      $confidence += [int][Math]::Round(($matched / $nameTokens.Count) * 25)
      if (-not $lower.Contains($nameTokens[0])) {
        $confidence = [Math]::Min($confidence, 60)
      }
      if ($nameTokens.Count -ge 3 -and -not $compactContext.Contains($compactName)) {
        $confidence = [Math]::Min($confidence, 70)
      }
    }

    $volumeMatched = $lower.Contains("$($Product.volume_ml)ml") -or $lower.Contains("$($Product.volume_ml) ml")
    if ($volumeMatched) {
      $confidence += 18
    } else {
      $confidence = [Math]::Min($confidence, 58)
    }

    $boostWords = @(
      (U @(0xCD5C, 0xC800)),
      (U @(0xC0C1, 0xD488, 0xAC00, 0xACA9)),
      (U @(0xD310, 0xB9E4, 0xAC00, 0xACA9)),
      (U @(0xAD6C, 0xB9E4, 0xD558, 0xAE30)),
      (U @(0xC7A5, 0xBC14, 0xAD6C, 0xB2C8)),
      ((U @(0xAC00, 0xACA9)) + " :")
    )
    foreach ($word in $boostWords) {
      if ($context.Contains($word)) { $confidence += 5; break }
    }

    if ($confidence -ge $MinConfidence) {
      $prices.Add([pscustomobject]@{
        price = $price
        confidence = [Math]::Min(95, $confidence)
        query = $Query
        snippet = $context.Trim()
      })
    }
  }

  return $prices
}

function Search-Naver {
  param([string]$Query)
  $encoded = [System.Uri]::EscapeDataString($Query)
  $url = "https://search.naver.com/search.naver?query=$encoded"
  $headers = @{
    "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36"
    "Accept-Language" = "ko-KR,ko;q=0.9,en-US;q=0.6,en;q=0.5"
  }
  $response = Invoke-WebRequest -Uri $url -Headers $headers -TimeoutSec 25
  return @{
    Url = $url
    Text = Normalize-Text $response.Content
  }
}

$products = Get-Content -LiteralPath $InputPath -Encoding UTF8 | ConvertFrom-Json
if ($Start -gt 0) {
  $products = @($products | Select-Object -Skip $Start)
}
if ($Limit -gt 0) {
  $products = @($products | Select-Object -First $Limit)
}

$records = New-Object System.Collections.Generic.List[object]
$index = 0

foreach ($product in $products) {
  $index += 1
  $priceWord = U @(0xAC00, 0xACA9)
  $queries = @(
    "`"$($product.name)`" $priceWord",
    "`"$($product.name)`" $($product.volume_ml)ml $priceWord",
    "$($product.name) $priceWord"
  ) | Select-Object -Unique

  $allCandidates = New-Object System.Collections.Generic.List[object]
  $lastError = $null

  foreach ($query in $queries) {
    try {
      $result = Search-Naver $query
      $candidates = Get-PriceCandidates $product $query $result.Text $MinConfidence
      foreach ($candidate in $candidates) {
        $candidate | Add-Member -NotePropertyName source_url -NotePropertyValue $result.Url
        $allCandidates.Add($candidate)
      }
      if ($allCandidates.Count -gt 0) { break }
    } catch {
      $lastError = $_.Exception.Message
    }
    Start-Sleep -Milliseconds $DelayMs
  }

  $sorted = @($allCandidates | Sort-Object -Property @{ Expression = "confidence"; Descending = $true }, price)
  $selected = $null
  if ($sorted.Count -gt 0) {
    $selected = $sorted[0]
  }

  $records.Add([pscustomobject]@{
    product_id = $product.product_id
    name = $product.name
    brewery = $product.brewery
    volume_ml = $product.volume_ml
    abv = $product.abv
    alcohol_type = $product.alcohol_type
    selected_price = if ($selected) { $selected.price } else { $null }
    confidence = if ($selected) { $selected.confidence } else { 0 }
    source_url = if ($selected) { $selected.source_url } else { "" }
    snippet = if ($selected) { $selected.snippet } else { "" }
    candidates = @($sorted | Select-Object -First 5)
    last_error = $lastError
  })

  if ($index % 25 -eq 0) {
    Write-Output "$index/$($products.Count) searched, found=$(@($records | Where-Object { $_.selected_price }).Count)"
  }
  Start-Sleep -Milliseconds $DelayMs
}

$payload = [pscustomobject]@{
  schema = "moeun.products.naver_price_candidates.v1"
  searched = $records.Count
  min_confidence = $MinConfidence
  found = @($records | Where-Object { $_.selected_price }).Count
  records = $records
}

$outputDir = Split-Path -Parent $OutputPath
if ($outputDir) {
  New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}
$payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
Write-Output "done searched=$($records.Count) found=$($payload.found) output=$OutputPath"
