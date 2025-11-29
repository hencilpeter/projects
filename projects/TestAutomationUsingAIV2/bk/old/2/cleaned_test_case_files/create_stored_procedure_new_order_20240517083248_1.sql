
-- Assuming the target database is named 'YourDatabaseName'
USE YourDatabaseName;
GO

-- Create a temporary table to store the test results
CREATE TABLE #TestResults
(
    Result INT
);

-- Execute the stored procedure with test data
INSERT INTO #TestResults (Result)
EXEC [Sales].[uspPlaceNewOrder] @CustomerID = 1, @Amount = 100, @OrderDate = '2022-01-01', @Status = 'O';

-- Check the results of the test
SELECT * FROM #TestResults;

-- Clean up temp table
DROP TABLE #TestResults;
