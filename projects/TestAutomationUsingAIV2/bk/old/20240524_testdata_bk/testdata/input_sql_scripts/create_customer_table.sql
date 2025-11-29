CREATE SCHEMA [Sales]
    AUTHORIZATION [dbo];
GO
PRINT N'Creating Sales.Customer...';
GO
CREATE TABLE [Sales].[Customer] (
    [CustomerID]   INT           IDENTITY (1, 1) NOT NULL,
    [CustomerName] NVARCHAR (40) NOT NULL,
    [YTDOrders]    INT           NOT NULL,
    [YTDSales]     INT           NOT NULL
);
GO