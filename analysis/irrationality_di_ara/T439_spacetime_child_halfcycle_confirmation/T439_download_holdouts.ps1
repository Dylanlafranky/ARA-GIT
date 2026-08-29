param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$selection = Get-Content -Raw (Join-Path $root 'T439_SAMPLE_SELECTION.json') | ConvertFrom-Json
$dataRoot = Join-Path $root 'data'
New-Item -ItemType Directory -Force $dataRoot | Out-Null

$manifest = @()

foreach ($item in $selection.holdouts) {
    $id = [string]$item.sxs_id
    $short = $id.Split(':')[-1]
    $record = [string]$item.zenodo_record
    $api = Invoke-RestMethod -Uri "https://zenodo.org/api/records/$record"

    $byLev = @{}
    foreach ($file in $api.files) {
        if ([string]$file.key -match '^Lev(\d+):(Strain_N4\.h5|Horizons\.h5|metadata\.json)$') {
            $lev = [int]$Matches[1]
            $kind = [string]$Matches[2]
            if (-not $byLev.ContainsKey($lev)) { $byLev[$lev] = @{} }
            $byLev[$lev][$kind] = $file
        }
    }

    $validLevs = @($byLev.Keys | Where-Object {
        $byLev[$_].ContainsKey('Strain_N4.h5') -and
        $byLev[$_].ContainsKey('Horizons.h5') -and
        $byLev[$_].ContainsKey('metadata.json')
    } | Sort-Object -Descending)

    if ($validLevs.Count -eq 0) {
        throw "No common Strain_N4/Horizons/metadata resolution for $id record $record"
    }

    $lev = [int]$validLevs[0]
    $outDir = Join-Path $dataRoot ("SXS_BBH_{0}_Lev{1}" -f $short, $lev)
    New-Item -ItemType Directory -Force $outDir | Out-Null

    $downloads = @()
    foreach ($kind in @('Strain_N4.h5', 'Horizons.h5', 'metadata.json')) {
        $file = $byLev[$lev][$kind]
        $target = Join-Path $outDir $kind
        if ((-not (Test-Path -LiteralPath $target)) -or ((Get-Item -LiteralPath $target).Length -ne [int64]$file.size)) {
            Invoke-WebRequest -Uri $file.links.self -OutFile $target
        }
        $actual = if ($kind.EndsWith('.h5')) {
            (Get-FileHash -Algorithm MD5 -LiteralPath $target).Hash.ToLower()
        } else {
            (Get-FileHash -Algorithm MD5 -LiteralPath $target).Hash.ToLower()
        }
        $expected = ([string]$file.checksum).Replace('md5:', '').ToLower()
        if ($actual -ne $expected) {
            throw "Checksum mismatch for $id Lev$lev $kind"
        }
        $downloads += [ordered]@{
            kind = $kind
            zenodo_key = [string]$file.key
            bytes = [int64]$file.size
            md5 = $actual
            source = [string]$file.links.self
            local_path = (Resolve-Path -LiteralPath $target).Path
        }
    }

    $manifest += [ordered]@{
        sxs_id = $id
        zenodo_record = [int64]$record
        doi = [string]$api.doi
        selected_level = $lev
        reference_mass_ratio = [double]$item.reference_mass_ratio
        reference_chi_eff = [double]$item.reference_chi_eff
        files = $downloads
    }
}

$manifestPath = Join-Path $root 'T439_DOWNLOAD_MANIFEST.json'
$manifest | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 $manifestPath
Write-Output "Downloaded and verified $($manifest.Count) SXS holdouts."
Write-Output $manifestPath
