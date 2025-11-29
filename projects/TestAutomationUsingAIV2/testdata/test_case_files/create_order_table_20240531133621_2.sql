```sql
EXEC tsqlt.NewTestClass 'Sales.Orders';
GO

CREATE PROCEDURE Sales.Orders.[test Orders column existence]
AS
BEGIN
    EXEC tsqlt.AssertColumnExists 'Sales.Orders', 'CustomerID';
    EXEC tsqlt.AssertColumnExists 'Sales.Orders', 'OrderID';
    EXEC tsqlt.AssertColumnExists 'Sales.Orders', 'OrderDate';
    EXEC tsqlt.AssertColumnExists 'Sales.Orders', 'FilledDate';
    EXEC tsqlt.AssertColumnExists 'Sales.Orders', 'Status';
    EXEC tsqlt.AssertColumnExists 'Sales.Orders', 'Amount';
END;
GO

CREATE PROCEDURE Sales.Orders.[test OrderID is identity]
AS
BEGIN
    EXEC tsqlt.AssertIdentityIs 'Sales.Orders', 'OrderID';
END;
GO

CREATE PROCEDURE Sales.Orders.[test OrderDate not null]
AS
BEGIN
    EXEC tsqlt.AssertObjectProperty @ObjectName = 'Sales.Orders', @PropertyName = 'OrderDate', @PropertyValue = 'NotNull';
END;
GO

CREATE PROCEDURE Sales.Orders.[test FilledDate can be null]
AS
BEGIN
    EXEC tsqlt.AssertObjectProperty @ObjectName = 'Sales.Orders', @PropertyName = 'FilledDate', @PropertyValue = 'Nullable';
END;
GO

CREATE PROCEDURE Sales.Orders.[test Status default value]
AS
BEGIN
    EXEC tsqlt.AssertObjectProperty @ObjectName = 'Sales.Orders', @PropertyName = 'Status', @PropertyValue = 'DefaultValueConstraint';
END;
GO

CREATE PROCEDURE Sales.Orders.[test Amount not negative]
AS
BEGIN
    EXEC tsqlt.AssertIntColumnValue @TableName = 'Sales.Orders', @ColumnName = 'Amount', @Comparison = '>=', @Value = 0;
END;
GO
```