CREATE SCHEMA [Sales]
    AUTHORIZATION [dbo];
GO
PRINT N'Creating Sales.Orders...';
GO

CREATE TABLE [Sales].[Orders] (
    [CustomerID] INT      NOT NULL,
    [OrderID]    INT      IDENTITY (1, 1) NOT NULL,
    [OrderDate]  DATETIME NOT NULL,
    [FilledDate] DATETIME NULL,
    [Status]     CHAR (1) NOT NULL,
    [Amount]     INT      NOT NULL
);
GO