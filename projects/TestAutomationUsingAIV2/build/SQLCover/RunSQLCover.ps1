. .\SQLCover.ps1
$SQLCoverScriptDir = Split-Path $script:MyInvocation.MyCommand.Path
$SQLCoverDllFullPath =   $SQLCoverScriptDir  + "\SQLCover.dll"

$result = Get-CoverTSql $SQLCoverDllFullPath "server=.;integrated security=sspi;initial catalog={}" "{}" "tSQLt.RunAll"

#echo $result > "code_coverage_result.txt"

$result | Out-File -FilePath "code_coverage_result.txt" -Encoding default


#Export-Html $result  $SQLCoverScriptDir