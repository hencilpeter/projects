To write a unit test for the provided SQL Server script, we can use plain T-SQL scripts to test the stored procedure `[Sales].[uspPlaceNewOrder]`. In the following unit test, we will test the functionality and expected behavior of the stored procedure:

```sql
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
```

In this unit test script:
1. We first switch to the target database where the stored procedure `[Sales].[uspPlaceNewOrder]` is defined.
2. We create a temporary table `#TestResults` to store the results of the test execution.
3. We execute the stored procedure `[Sales].[uspPlaceNewOrder]` with test data (CustomerID = 1, Amount = 100, OrderDate = '2022-01-01', and Status = 'O').
4. We select the results from the temporary table `#TestResults` to see the return value from the stored procedure (which is the generated identity column value).
5. Finally, we drop the temporary table to clean up.

Ensure that the test data provided in the unit test matches the data in your system to verify the stored procedure's functionality accurately. Additionally, you may need to provide appropriate permissions for executing the stored procedure based on your database security settings.