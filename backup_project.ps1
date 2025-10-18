param(
    [string]$ProjectPath = "J:\_Proiect_Nursing_training_AI",
    [string]$BackupRoot = "J:\_Proiect_Nursing_training_AI\_backups",
    [int]$Keep = 2
)

$ErrorActionPreference = 'Stop'
if(-not (Test-Path $ProjectPath)) { throw "Project path not found: $ProjectPath" }
if(-not (Test-Path $BackupRoot)) { New-Item -ItemType Directory -Path $BackupRoot | Out-Null }

$timestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$dest = Join-Path $BackupRoot "snapshot_$timestamp"

# Create new snapshot
New-Item -ItemType Directory -Path $dest | Out-Null

# Use robocopy to mirror project into snapshot (exclude backups and node_modules/.git large caches if present)
$robocopyLog = Join-Path $BackupRoot "robocopy_$timestamp.log"
$excludeDirs = @('_backups','.git','node_modules','dist','build','.venv','.mypy_cache','__pycache__')
$exclude = @()
foreach($d in $excludeDirs){ $exclude += @('/XD', (Join-Path $ProjectPath $d)) }

$cmd = @(
    'robocopy',
    '"' + $ProjectPath + '"',
    '"' + $dest + '"',
    '/E',               # copy subdirs incl. empty
    '/R:1','/W:1',      # retry/wait minimal
    '/NFL','/NDL',      # no file/dir listing
    '/NP',              # no progress per file
    '/MT:16',           # multithread
    '/XJ'               # exclude junctions
) + $exclude

# Start robocopy
$process = Start-Process -FilePath $cmd[0] -ArgumentList $cmd[1..($cmd.Length-1)] -NoNewWindow -PassThru -Wait -RedirectStandardOutput $robocopyLog

# Prune old snapshots (keep most recent $Keep)
$snapshots = Get-ChildItem -Path $BackupRoot -Directory | Where-Object { $_.Name -like 'snapshot_*' } | Sort-Object Name -Descending
if($snapshots.Count -gt $Keep){
    $toDelete = $snapshots[$Keep..($snapshots.Count-1)]
    foreach($s in $toDelete){
        try { Remove-Item -Recurse -Force -LiteralPath $s.FullName } catch { Write-Warning "Failed to delete $($s.FullName): $($_.Exception.Message)" }
    }
}

Write-Output "Backup completed: $dest"
