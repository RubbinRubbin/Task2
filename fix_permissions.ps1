Get-ChildItem -Path $PSScriptRoot -Recurse -File | ForEach-Object { $_.IsReadOnly = $false }
Write-Host "All files are now writable."
