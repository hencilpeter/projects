Exec sp_configure 'clr enabled', 1;
reconfigure;
GO 
declare @cmd nvarchar(max);
set @cmd = 'alter database ' + quotename(db_name()) + ' set trustworthy on;';
exec(@cmd);
GO 
