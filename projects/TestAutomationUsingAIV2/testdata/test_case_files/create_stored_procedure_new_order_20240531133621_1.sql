-- Test case for uspPlaceNewOrder
EXEC tsqlt.NewTestClass 'TestSalesProcedure';
GO

CREATE PROCEDURE TestSalesProcedure.[test uspPlaceNewOrder inserts new order]
AS
BEGIN
    -- Assemble
    DECLARE @CustomerID INT = 1;
    DECLARE @Amount INT = 100;
    DECLARE @OrderDate DATETIME = GETDATE();
    
    -- Act
    EXEC Sales.uspPlaceNewOrder @CustomerID, @Amount, @OrderDate;
    
    -- Assert
    EXEC tsqlt.AssertEqualsTable 'Sales.Orders', 1, 
        (SELECT COUNT(*) FROM Sales.Orders WHERE CustomerID = @CustomerID AND Amount = @Amount AND OrderDate = @OrderDate);
END;
GO

-- Run the test
EXEC tsqlt.Run 'TestSalesProcedure';