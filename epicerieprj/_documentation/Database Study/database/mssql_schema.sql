-- Philippine Supplier and Product Management System - MS SQL Schema
-- Created: May 16, 2025

-- Enable foreign key constraints if not already enabled
EXEC sp_msforeachtable 'ALTER TABLE ? CHECK CONSTRAINT ALL'

-- Drop tables if they exist (in reverse order of creation to avoid FK constraint issues)
IF OBJECT_ID('dbo.SupplierProductCatalog', 'U') IS NOT NULL DROP TABLE dbo.SupplierProductCatalog;
IF OBJECT_ID('dbo.Products', 'U') IS NOT NULL DROP TABLE dbo.Products;
IF OBJECT_ID('dbo.ContactPersons', 'U') IS NOT NULL DROP TABLE dbo.ContactPersons;
IF OBJECT_ID('dbo.SupplierEmailAddresses', 'U') IS NOT NULL DROP TABLE dbo.SupplierEmailAddresses;
IF OBJECT_ID('dbo.SupplierContactNumbers', 'U') IS NOT NULL DROP TABLE dbo.SupplierContactNumbers;
IF OBJECT_ID('dbo.SupplierAddresses', 'U') IS NOT NULL DROP TABLE dbo.SupplierAddresses;
IF OBJECT_ID('dbo.Suppliers', 'U') IS NOT NULL DROP TABLE dbo.Suppliers;

-- Create Suppliers table
CREATE TABLE dbo.Suppliers (
    SupplierID INT IDENTITY(1,1) PRIMARY KEY,
    TIN VARCHAR(20) NOT NULL UNIQUE,
    CompanyName VARCHAR(255) NOT NULL,
    DateCreated DATETIME2 NOT NULL DEFAULT GETDATE(),
    DateUpdated DATETIME2 NOT NULL DEFAULT GETDATE(),
    Status VARCHAR(10) NOT NULL DEFAULT 'Active' CHECK (Status IN ('Active', 'Inactive'))
);

-- Create index on CompanyName
CREATE INDEX IX_Suppliers_CompanyName ON dbo.Suppliers(CompanyName);

-- Create SupplierAddresses table
CREATE TABLE dbo.SupplierAddresses (
    AddressID INT IDENTITY(1,1) PRIMARY KEY,
    SupplierID INT NOT NULL,
    AddressLine1 VARCHAR(255) NOT NULL,
    AddressLine2 VARCHAR(255) NULL,
    Barangay VARCHAR(100) NULL,
    CityMunicipality VARCHAR(100) NOT NULL,
    Province VARCHAR(100) NOT NULL,
    PostalCode VARCHAR(10) NULL,
    AddressType VARCHAR(50) NULL,
    IsPrimary BIT NOT NULL DEFAULT 0,
    CONSTRAINT FK_SupplierAddresses_Suppliers FOREIGN KEY (SupplierID) 
        REFERENCES dbo.Suppliers (SupplierID) ON DELETE CASCADE
);

-- Create index on SupplierID
CREATE INDEX IX_SupplierAddresses_SupplierID ON dbo.SupplierAddresses(SupplierID);

-- Create SupplierContactNumbers table
CREATE TABLE dbo.SupplierContactNumbers (
    ContactNumberID INT IDENTITY(1,1) PRIMARY KEY,
    SupplierID INT NOT NULL,
    ContactNumber VARCHAR(50) NOT NULL,
    NumberType VARCHAR(50) NULL,
    IsPrimary BIT NOT NULL DEFAULT 0,
    CONSTRAINT FK_SupplierContactNumbers_Suppliers FOREIGN KEY (SupplierID) 
        REFERENCES dbo.Suppliers (SupplierID) ON DELETE CASCADE
);

-- Create index on SupplierID
CREATE INDEX IX_SupplierContactNumbers_SupplierID ON dbo.SupplierContactNumbers(SupplierID);

-- Create SupplierEmailAddresses table
CREATE TABLE dbo.SupplierEmailAddresses (
    EmailAddressID INT IDENTITY(1,1) PRIMARY KEY,
    SupplierID INT NOT NULL,
    EmailAddress VARCHAR(255) NOT NULL,
    EmailType VARCHAR(50) NULL,
    IsPrimary BIT NOT NULL DEFAULT 0,
    CONSTRAINT FK_SupplierEmailAddresses_Suppliers FOREIGN KEY (SupplierID) 
        REFERENCES dbo.Suppliers (SupplierID) ON DELETE CASCADE
);

-- Create index on SupplierID
CREATE INDEX IX_SupplierEmailAddresses_SupplierID ON dbo.SupplierEmailAddresses(SupplierID);

-- Create ContactPersons table
CREATE TABLE dbo.ContactPersons (
    ContactPersonID INT IDENTITY(1,1) PRIMARY KEY,
    SupplierID INT NOT NULL,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100) NOT NULL,
    Position VARCHAR(100) NULL,
    EmailAddress VARCHAR(255) NULL,
    ContactNumber VARCHAR(50) NULL,
    DateCreated DATETIME2 NOT NULL DEFAULT GETDATE(),
    DateUpdated DATETIME2 NOT NULL DEFAULT GETDATE(),
    Status VARCHAR(10) NOT NULL DEFAULT 'Active' CHECK (Status IN ('Active', 'Inactive')),
    CONSTRAINT FK_ContactPersons_Suppliers FOREIGN KEY (SupplierID) 
        REFERENCES dbo.Suppliers (SupplierID) ON DELETE CASCADE
);

-- Create index on SupplierID
CREATE INDEX IX_ContactPersons_SupplierID ON dbo.ContactPersons(SupplierID);

-- Create Products table
CREATE TABLE dbo.Products (
    ProductID INT IDENTITY(1,1) PRIMARY KEY,
    ProductName VARCHAR(255) NOT NULL UNIQUE,
    ProductDescription TEXT NULL,
    Category VARCHAR(100) NULL,
    UnitOfMeasure VARCHAR(50) NULL,
    DataEntryDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    Status VARCHAR(15) NOT NULL DEFAULT 'Active' CHECK (Status IN ('Active', 'Inactive', 'Discontinued'))
);

-- Create index on ProductName
CREATE INDEX IX_Products_ProductName ON dbo.Products(ProductName);
CREATE INDEX IX_Products_Category ON dbo.Products(Category);

-- Create SupplierProductCatalog table (junction table)
CREATE TABLE dbo.SupplierProductCatalog (
    SupplierProductCatalogID INT IDENTITY(1,1) PRIMARY KEY,
    SupplierID INT NOT NULL,
    ProductID INT NOT NULL,
    DealersPrice DECIMAL(12, 2) NOT NULL,
    PriceEntryDate DATE NOT NULL,
    SupplierProductCode VARCHAR(100) NULL,
    Notes TEXT NULL,
    CONSTRAINT FK_SupplierProductCatalog_Suppliers FOREIGN KEY (SupplierID) 
        REFERENCES dbo.Suppliers (SupplierID) ON DELETE CASCADE,
    CONSTRAINT FK_SupplierProductCatalog_Products FOREIGN KEY (ProductID) 
        REFERENCES dbo.Products (ProductID) ON DELETE CASCADE,
    CONSTRAINT UK_SupplierProductCatalog UNIQUE (SupplierID, ProductID, PriceEntryDate)
);

-- Create indexes for SupplierProductCatalog
CREATE INDEX IX_SupplierProductCatalog_SupplierID ON dbo.SupplierProductCatalog(SupplierID);
CREATE INDEX IX_SupplierProductCatalog_ProductID ON dbo.SupplierProductCatalog(ProductID);
CREATE INDEX IX_SupplierProductCatalog_PriceEntryDate ON dbo.SupplierProductCatalog(PriceEntryDate);
CREATE INDEX IX_SupplierProductCatalog_SupplierProduct ON dbo.SupplierProductCatalog(SupplierID, ProductID);

-- Create triggers for automatic DateUpdated maintenance
CREATE TRIGGER trg_Suppliers_Update
ON dbo.Suppliers
AFTER UPDATE
AS
BEGIN
    UPDATE dbo.Suppliers
    SET DateUpdated = GETDATE()
    FROM dbo.Suppliers s
    INNER JOIN inserted i ON s.SupplierID = i.SupplierID;
END;

CREATE TRIGGER trg_ContactPersons_Update
ON dbo.ContactPersons
AFTER UPDATE
AS
BEGIN
    UPDATE dbo.ContactPersons
    SET DateUpdated = GETDATE()
    FROM dbo.ContactPersons cp
    INNER JOIN inserted i ON cp.ContactPersonID = i.ContactPersonID;
END;

-- Stored Procedure to ensure only one primary address/contact/email per supplier
CREATE PROCEDURE dbo.SetPrimaryAddress
    @AddressID INT,
    @SupplierID INT
AS
BEGIN
    BEGIN TRANSACTION;
    
    -- First, set all addresses for this supplier to non-primary
    UPDATE dbo.SupplierAddresses
    SET IsPrimary = 0
    WHERE SupplierID = @SupplierID;
    
    -- Then set the specified address as primary
    UPDATE dbo.SupplierAddresses
    SET IsPrimary = 1
    WHERE AddressID = @AddressID AND SupplierID = @SupplierID;
    
    COMMIT;
END;

CREATE PROCEDURE dbo.SetPrimaryContactNumber
    @ContactNumberID INT,
    @SupplierID INT
AS
BEGIN
    BEGIN TRANSACTION;
    
    -- First, set all contact numbers for this supplier to non-primary
    UPDATE dbo.SupplierContactNumbers
    SET IsPrimary = 0
    WHERE SupplierID = @SupplierID;
    
    -- Then set the specified contact number as primary
    UPDATE dbo.SupplierContactNumbers
    SET IsPrimary = 1
    WHERE ContactNumberID = @ContactNumberID AND SupplierID = @SupplierID;
    
    COMMIT;
END;

CREATE PROCEDURE dbo.SetPrimaryEmailAddress
    @EmailAddressID INT,
    @SupplierID INT
AS
BEGIN
    BEGIN TRANSACTION;
    
    -- First, set all email addresses for this supplier to non-primary
    UPDATE dbo.SupplierEmailAddresses
    SET IsPrimary = 0
    WHERE SupplierID = @SupplierID;
    
    -- Then set the specified email address as primary
    UPDATE dbo.SupplierEmailAddresses
    SET IsPrimary = 1
    WHERE EmailAddressID = @EmailAddressID AND SupplierID = @SupplierID;
    
    COMMIT;
END;

-- Create view for supplier catalog with latest prices
CREATE VIEW dbo.vw_SupplierProductsCurrentPrices AS
WITH LatestPrices AS (
    SELECT 
        SupplierID,
        ProductID,
        MAX(PriceEntryDate) AS LatestPriceDate
    FROM 
        dbo.SupplierProductCatalog
    GROUP BY 
        SupplierID, ProductID
)
SELECT 
    s.SupplierID,
    s.CompanyName,
    s.TIN,
    s.Status AS SupplierStatus,
    p.ProductID,
    p.ProductName,
    p.Category,
    p.UnitOfMeasure,
    p.Status AS ProductStatus,
    spc.DealersPrice,
    spc.PriceEntryDate,
    spc.SupplierProductCode,
    spc.Notes
FROM 
    dbo.Suppliers s
JOIN 
    dbo.SupplierProductCatalog spc ON s.SupplierID = spc.SupplierID
JOIN 
    LatestPrices lp ON spc.SupplierID = lp.SupplierID 
                    AND spc.ProductID = lp.ProductID 
                    AND spc.PriceEntryDate = lp.LatestPriceDate
JOIN 
    dbo.Products p ON spc.ProductID = p.ProductID;

-- Create view for supplier complete information
CREATE VIEW dbo.vw_SupplierCompleteInfo AS
SELECT
    s.SupplierID,
    s.TIN,
    s.CompanyName,
    s.Status,
    sa.AddressID,
    sa.AddressLine1,
    sa.AddressLine2,
    sa.Barangay,
    sa.CityMunicipality,
    sa.Province,
    sa.PostalCode,
    sa.AddressType,
    sa.IsPrimary AS IsPrimaryAddress,
    scn.ContactNumberID,
    scn.ContactNumber,
    scn.NumberType,
    scn.IsPrimary AS IsPrimaryContactNumber,
    sea.EmailAddressID,
    sea.EmailAddress,
    sea.EmailType,
    sea.IsPrimary AS IsPrimaryEmailAddress,
    cp.ContactPersonID,
    cp.FirstName,
    cp.LastName,
    cp.Position,
    cp.EmailAddress AS ContactPersonEmail,
    cp.ContactNumber AS ContactPersonNumber,
    cp.Status AS ContactPersonStatus
FROM
    dbo.Suppliers s
LEFT JOIN
    dbo.SupplierAddresses sa ON s.SupplierID = sa.SupplierID
LEFT JOIN
    dbo.SupplierContactNumbers scn ON s.SupplierID = scn.SupplierID
LEFT JOIN
    dbo.SupplierEmailAddresses sea ON s.SupplierID = sea.SupplierID
LEFT JOIN
    dbo.ContactPersons cp ON s.SupplierID = cp.SupplierID;
