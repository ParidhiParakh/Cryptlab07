# Generate 1 MiB of random data with the Windows/.NET cryptographic RNG.
# Run in Windows PowerShell (NOT in WSL):  .\generate_random_windows.ps1
# On Windows, RandomNumberGenerator uses the CNG generator (BCryptGenRandom).

$size  = 1048576                                   # 1 MiB
$bytes = New-Object byte[] $size

$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes)
$rng.Dispose()

$out = Join-Path $env:USERPROFILE "Downloads\windows_cng.bin"
[System.IO.File]::WriteAllBytes($out, $bytes)

Write-Host "PowerShell version : $($PSVersionTable.PSVersion)"
Write-Host "Saved $size bytes to: $out"
Get-Item $out | Select-Object Name, Length
Get-FileHash $out -Algorithm SHA256
