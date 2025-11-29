-- Test case 1: Validate if Customer table is created successfully
SELECT * 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_NAME = 'Customer';

-- Test case 2: Validate if the CustomerID column is an identity column
SELECT COLUMN_NAME, COLUMNPROPERTY(OBJECT_ID('Sales.Customer'), COLUMN_NAME, 'IsIdentity') AS IsIdentity
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Customer' AND COLUMN_NAME = 'CustomerID';

-- Test case 3: Validate if the CustomerName column is NOT NULL
SELECT COLUMN_NAME, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Customer' AND COLUMN_NAME = 'CustomerName';

-- Test case 4: Validate if the YTDOrders column is NOT NULL
SELECT COLUMN_NAME, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Customer' AND COLUMN_NAME = 'YTDOrders';

-- Test case 5: Validate if the YTDSales column is NOT NULL
SELECT COLUMN_NAME, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Customer' AND COLUMN_NAME = 'YTDSales';