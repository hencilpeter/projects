/*
Run this unit test using tSQLt framework
Test objective: Ensure that a new order can be placed successfully
*/

EXEC tSQLt.NewTestClass 'PlaceNewOrderTest';
GO

-- Setup: Create necessary tables and data for testing
CREATE PROCEDURE PlaceNewOrderTest.[Setup]
AS
BEGIN
    -- Create a mock Orders table
--    CREATE TABLE Sales.Orders (
--        OrderID INT IDENTITY(1,1) PRIMARY KEY,
--        CustomerID INT,
--        OrderDate DATETIME,
--        FilledDate DATETIME,
--        Status CHAR(1),
--        Amount INT
--    );

    -- Insert test data
    INSERT INTO Sales.Orders (CustomerID, OrderDate, FilledDate, Status, Amount)
    VALUES (1, '2021-10-15', NULL, 'O', 100);
END;
GO

-- Test: Place a new order
CREATE PROCEDURE PlaceNewOrderTest.TestPlaceNewOrder
AS
BEGIN
    -- Specify the input parameters for the procedure
    DECLARE @CustomerID INT = 2;
    DECLARE @Amount INT = 150;
    DECLARE @OrderDate DATETIME = '2021-10-16';
    DECLARE @Status CHAR(1) = 'O';
    
    -- Execute the stored procedure being tested
    EXEC Sales.uspPlaceNewOrder @CustomerID, @Amount, @OrderDate, @Status;

    -- Validate the result by checking that the new order has been successfully placed
    DECLARE @OrderCount INT;
    SELECT @OrderCount = COUNT(*) 
    FROM Sales.Orders 
    WHERE CustomerID = @CustomerID
    AND Amount = @Amount
    AND OrderDate = @OrderDate
    AND Status = @Status;

    EXEC tSQLt.AssertEquals 1, @OrderCount, 'A new order was not successfully placed';
END;
GO

-- TearDown: Drop the tables created for testing
CREATE PROCEDURE PlaceNewOrderTest.[Teardown]
AS
BEGIN
    DROP TABLE Sales.Orders;
END;
GO

-- Run the tests
EXEC tSQLt.Run 'PlaceNewOrderTest';
GO