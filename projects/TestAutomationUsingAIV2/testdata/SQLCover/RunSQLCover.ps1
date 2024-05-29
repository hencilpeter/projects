. .\SQLCover.ps1
$SQLCoverScriptDir = Split-Path $script:MyInvocation.MyCommand.Path
$SQLCoverDllFullPath =   $SQLCoverScriptDir  + "\SQLCover.dll"

$result = Get-CoverTSql $SQLCoverDllFullPath "server=.;integrated security=sspi;initial catalog=Automation_Test_DB_20240529232334" "Automation_Test_DB_20240529232334" "tSQLt.RunAll"

echo $result > "code_coverage_result.txt"

#Export-Html $result  $SQLCoverScriptDir