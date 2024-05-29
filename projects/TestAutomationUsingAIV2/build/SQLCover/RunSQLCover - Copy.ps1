. .\SQLCover.ps1
$SQLCoverScriptDir = Split-Path $script:MyInvocation.MyCommand.Path
$SQLCoverDllFullPath =   $SQLCoverScriptDir  + "\SQLCover.dll"

$result = Get-CoverTSql $SQLCoverDllFullPath "server=.;integrated security=sspi;initial catalog={}" "{}" "tSQLt.RunAll"

echo $result

#Export-Html $result  $SQLCoverScriptDir