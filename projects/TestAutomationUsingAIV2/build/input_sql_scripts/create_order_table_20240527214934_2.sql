
CREATE PROCEDURE testSalesOrdersTable
AS
BEGIN
    -- Assemble
    EXEC tSQLt.FakeTable @TableName = N'Sales.Orders';
    
    -- Act
    INSERT INTO Sales.Orders (CustomerID, OrderDate, FilledDate, Status, Amount)
    VALUES (1, '2022-01-01', NULL, 'P', 100);
    
    -- Assert
    EXEC tSQLt.AssertEqualsTable @Expected = N'SELECT CustomerID, OrderID, OrderDate, FilledDate, Status, Amount FROM Sales.Orders',
                                 @Actual = N'SELECT CustomerID, OrderID, OrderDate, FilledDate, Status, Amount FROM Sales.Orders';
END;
GO

-- Run the test
EXEC tSQLt.Run 'testSalesOrdersTable';
