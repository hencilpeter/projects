-- Unit test for the script to create Sales.Customer table
-- Check if the Sales.Customer table exists
IF OBJECT_ID('Sales.Customer', 'U') IS NOT NULL
BEGIN
    PRINT 'Sales.Customer table exists - PASS';
END
ELSE
BEGIN
    PRINT 'Sales.Customer table does not exist - FAIL';
END

-- Check if the CustomerID column is of type INT
IF EXISTS (
    SELECT 1
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'Customer'
    AND COLUMN_NAME = 'CustomerID'
    AND DATA_TYPE = 'int'
)
BEGIN
    PRINT 'CustomerID column is of type INT - PASS';
END
ELSE
BEGIN
    PRINT 'CustomerID column is not of type INT - FAIL';
END

-- Check if the CustomerName column is of type NVARCHAR(40)
IF EXISTS (
    SELECT 1
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'Customer'
    AND COLUMN_NAME = 'CustomerName'
    AND DATA_TYPE = 'nvarchar'
    AND CHARACTER_MAXIMUM_LENGTH = 40
)
BEGIN
    PRINT 'CustomerName column is of type NVARCHAR(40) - PASS';
END
ELSE
BEGIN
    PRINT 'CustomerName column is not of type NVARCHAR(40) - FAIL';
END

-- Check if the YTDOrders column is of type INT
IF EXISTS (
    SELECT 1
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'Customer'
    AND COLUMN_NAME = 'YTDOrders'
    AND DATA_TYPE = 'int'
)
BEGIN
    PRINT 'YTDOrders column is of type INT - PASS';
END
ELSE
BEGIN
    PRINT 'YTDOrders column is not of type INT - FAIL';
END

-- Check if the YTDSales column is of type INT
IF EXISTS (
    SELECT 1
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'Customer'
    AND COLUMN_NAME = 'YTDSales'
    AND DATA_TYPE = 'int'
)
BEGIN
    PRINT 'YTDSales column is of type INT - PASS';
END
ELSE
BEGIN
    PRINT 'YTDSales column is not of type INT - FAIL';
END
