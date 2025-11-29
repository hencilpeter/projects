CREATE PROCEDURE [Sales].[uspPlaceNewOrder]
@CustomerID INT, @Amount INT, @OrderDate DATETIME, @Status CHAR (1)='O'
AS
BEGIN
DECLARE @RC INT
BEGIN TRANSACTION
INSERT INTO [Sales].[Orders] (CustomerID, OrderDate, FilledDate, Status, Amount) 
     VALUES (@CustomerID, @OrderDate, NULL, @Status, @Amount)
COMMIT TRANSACTION
RETURN @RC
END
