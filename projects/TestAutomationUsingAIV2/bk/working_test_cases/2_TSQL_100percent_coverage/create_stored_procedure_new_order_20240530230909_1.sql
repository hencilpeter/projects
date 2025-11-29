EXEC tsqlt.NewTestClass 'SalesTests';
GO

CREATE PROCEDURE SalesTests.[test uspPlaceNewOrder should insert new order]
AS
BEGIN
    -- Assemble
    DECLARE @CustomerID INT = 1;
    DECLARE @Amount INT = 100;
    DECLARE @OrderDate DATETIME = GETDATE();
    
    -- Act
    EXEC Sales.uspPlaceNewOrder @CustomerID, @Amount, @OrderDate;
    
    -- Assert
    DECLARE @recordCount INT = 0;
	SELECT @recordCount=COUNT(*) FROM [Sales].[Orders] WHERE CustomerID = @CustomerID AND Amount = @Amount;
    EXEC tSQLt.AssertEquals 1, @recordCount;
END;
GO

EXEC tsqlt.Run 'SalesTests';
GO
