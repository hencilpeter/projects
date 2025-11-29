-- Test to check if Orders table has all the required columns
EXEC tsqlt.NewTestClass 'TestOrdersTable';
GO

CREATE PROCEDURE TestOrdersTable.[test Orders table has all required columns]
AS
BEGIN
    -- Assemble
    DECLARE @ColumnsCount INT;

    -- Act
    SELECT @ColumnsCount = COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'Orders';

    -- Assert
    EXEC tsqlt.AssertEquals 6, @ColumnsCount;
END;
GO

-- Test to check if CustomerID column is defined as NOT NULL in Orders table
EXEC tsqlt.NewTestClass 'TestOrdersTable';
GO

CREATE PROCEDURE TestOrdersTable.[test CustomerID column is not null]
AS
BEGIN
    -- Assemble
    DECLARE @IsNullable BIT;

    -- Act
    SELECT @IsNullable = COLUMNPROPERTY(OBJECT_ID('Sales.Orders'), 'CustomerID', 'AllowsNull');

    -- Assert
    EXEC tsqlt.AssertEquals 0, @IsNullable;
END;
GO

-- Test to check if OrderID column is defined as IDENTITY in Orders table
EXEC tsqlt.NewTestClass 'TestOrdersTable';
GO

CREATE PROCEDURE TestOrdersTable.[test OrderID column is identity]
AS
BEGIN
    -- Assemble
    DECLARE @IsIdentity BIT;

    -- Act
    SELECT @IsIdentity = COLUMNPROPERTY(OBJECT_ID('Sales.Orders'), 'OrderID', 'IsIdentity');

    -- Assert
    EXEC tsqlt.AssertEquals 1, @IsIdentity;
END;
GO

-- Test to check if OrderDate column is defined as NOT NULL in Orders table
EXEC tsqlt.NewTestClass 'TestOrdersTable';
GO

CREATE PROCEDURE TestOrdersTable.[test OrderDate column is not null]
AS
BEGIN
    -- Assemble
    DECLARE @IsNullable BIT;

    -- Act
    SELECT @IsNullable = COLUMNPROPERTY(OBJECT_ID('Sales.Orders'), 'OrderDate', 'AllowsNull');

    -- Assert
    EXEC tsqlt.AssertEquals 0, @IsNullable;
END;
GO

-- Test to check if FilledDate column allows NULL values in Orders table
EXEC tsqlt.NewTestClass 'TestOrdersTable';
GO

CREATE PROCEDURE TestOrdersTable.[test FilledDate column allows null values]
AS
BEGIN
    -- Assemble
    DECLARE @IsNullable BIT;

    -- Act
    SELECT @IsNullable = COLUMNPROPERTY(OBJECT_ID('Sales.Orders'), 'FilledDate', 'AllowsNull');

    -- Assert
    EXEC tsqlt.AssertEquals 1, @IsNullable;
END;
GO

-- Test to check if Status column is defined as NOT NULL in Orders table
EXEC tsqlt.NewTestClass 'TestOrdersTable';
GO

CREATE PROCEDURE TestOrdersTable.[test Status column is not null]
AS
BEGIN
    -- Assemble
    DECLARE @IsNullable BIT;

    -- Act
    SELECT @IsNullable = COLUMNPROPERTY(OBJECT_ID('Sales.Orders'), 'Status', 'AllowsNull');

    -- Assert
    EXEC tsqlt.AssertEquals 0, @IsNullable;
END;
GO

-- Test to check if Amount column is defined as NOT NULL in Orders table
EXEC tsqlt.NewTestClass 'TestOrdersTable';
GO

CREATE PROCEDURE TestOrdersTable.[test Amount column is not null]
AS
BEGIN
    -- Assemble
    DECLARE @IsNullable BIT;

    -- Act
    SELECT @IsNullable = COLUMNPROPERTY(OBJECT_ID('Sales.Orders'), 'Amount', 'AllowsNull');

    -- Assert
    EXEC tsqlt.AssertEquals 0, @IsNullable;
END;
GO
