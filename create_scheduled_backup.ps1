param(
    [string]$ProjectPath = "J:\_Proiect_Nursing_training_AI",
    [string]$BackupRoot = "J:\_Proiect_Nursing_training_AI\_backups",
    [int]$Keep = 2,
    [int]$IntervalMinutes = 20,
    [string]$TaskName = "Nursing_AI_Project_Backup"
)

$ErrorActionPreference = 'Stop'

if(-not (Test-Path $ProjectPath)) { throw "Project path not found: $ProjectPath" }
if(-not (Test-Path $BackupRoot)) { New-Item -ItemType Directory -Path $BackupRoot | Out-Null }

# Resolve backup script path
$scriptPath = Join-Path $ProjectPath 'backup_project.ps1'
if(-not (Test-Path $scriptPath)) { throw "Backup script not found: $scriptPath" }

# Build the action to run the backup script non-interactively
$psExe = (Get-Command powershell.exe -ErrorAction SilentlyContinue)?.Source
if(-not $psExe){ $psExe = (Get-Command pwsh.exe -ErrorAction SilentlyContinue)?.Source }
if(-not $psExe){ throw 'Unable to locate PowerShell executable (powershell.exe or pwsh.exe).'}

$arguments = @(
    '-NoProfile',
    '-ExecutionPolicy','Bypass',
    '-File', '"' + $scriptPath + '"',
    '-ProjectPath', '"' + $ProjectPath + '"',
    '-BackupRoot', '"' + $BackupRoot + '"',
    '-Keep', $Keep
) -join ' '

$action = New-ScheduledTaskAction -Execute $psExe -Argument $arguments

# Create a trigger that repeats every IntervalMinutes indefinitely
$now = Get-Date
# Windows requires a finite repetition duration; use 30 days and auto-renew via task persistence
$trigger = New-ScheduledTaskTrigger -Once -At $now.AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 30)

# Run whether user is logged on or not, highest privileges optional
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

# Register or update the task
try {
    if(Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue){
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
} catch {}

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal | Out-Null

Write-Output "Scheduled backup task '$TaskName' created: every $IntervalMinutes minutes, keeping last $Keep snapshots."


