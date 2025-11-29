
-- Use tSQLt framework
EXEC tSQLt.NewTestClass 'TestSales';

-- Mock data setup
CREATE PROCEDURE TestSales.[Setup]
AS
BEGIN
    -- Create a test customer
    INSERT INTO [Sales].[Customer] (CustomerID, YTDOrders)
    VALUES (999, 0);
END;

-- Test case for uspPlaceNewOrder
CREATE PROCEDURE TestSales.[test uspPlaceNewOrder - VerifyOrderPlacement]
AS
BEGIN
    -- Arrange
    DECLARE @CustomerID INT = 999;
    DECLARE @Amount INT = 100;
    DECLARE @OrderDate DATETIME = GETDATE();
    DECLARE @Status CHAR(1) = 'O';

    -- Act
    DECLARE @ReturnValue INT;
    EXEC @ReturnValue = [Sales].[uspPlaceNewOrder] @CustomerID, @Amount, @OrderDate, @Status;

    -- Assert
    EXEC tSQLt.AssertEquals 1, @ReturnValue; -- Check if SCOPE_IDENTITY is returned
    DECLARE @YTDOrders INT;
    SELECT @YTDOrders = YTDOrders
    FROM [Sales].[Customer]
    WHERE CustomerID = @CustomerID;
    EXEC tSQLt.AssertEquals @Amount, @YTDOrders; -- Check if YTDOrders is updated

END;
