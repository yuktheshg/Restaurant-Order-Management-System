SELECT * FROM Customers;

SELECT *
FROM Menu
ORDER BY Price DESC
LIMIT 1;

SELECT COUNT(*) AS Total_Customers
FROM Customers;

SELECT OrderStatus, COUNT(*) AS Total_Orders
FROM Orders
GROUP BY OrderStatus;

SELECT SUM(Amount) AS Total_Revenue
FROM Payments
WHERE PaymentStatus = 'Paid';

SELECT m.ItemName,
       SUM(od.Quantity) AS Total_Quantity
FROM Menu m
JOIN Order_Details od
ON m.ItemID = od.ItemID
GROUP BY m.ItemID, m.ItemName
ORDER BY Total_Quantity DESC
LIMIT 1;


-- STEP 6: SQL JOIN OPERATIONS


SELECT
    c.CustomerName,
    o.OrderID,
    o.OrderDate,
    o.OrderStatus
FROM Customers c
INNER JOIN Orders o
ON c.CustomerID = o.CustomerID;

SELECT
    c.CustomerName,
    o.OrderID,
    o.OrderStatus
FROM Customers c
LEFT JOIN Orders o
ON c.CustomerID = o.CustomerID;

SELECT
    c.CustomerName,
    o.OrderID,
    o.OrderStatus
FROM Customers c
RIGHT JOIN Orders o
ON c.CustomerID = o.CustomerID;

SELECT
    c.CustomerName,
    o.OrderID,
    m.ItemName,
    od.Quantity,
    m.Price,
    (od.Quantity * m.Price) AS Total
FROM Customers c
JOIN Orders o
ON c.CustomerID = o.CustomerID
JOIN Order_Details od
ON o.OrderID = od.OrderID
JOIN Menu m
ON od.ItemID = m.ItemID;

SELECT COUNT(*) AS Total_Orders
FROM Orders;

SELECT SUM(Price) AS Total_Menu_Value
FROM Menu;

SELECT AVG(Price) AS Average_Price
FROM Menu;

SELECT MAX(Price) AS Highest_Price
FROM Menu;

SELECT MIN(Price) AS Lowest_Price
FROM Menu;

SELECT
    OrderStatus,
    COUNT(*) AS Total_Orders
FROM Orders
GROUP BY OrderStatus;

SELECT
    m.ItemName,
    SUM(od.Quantity) AS Total_Sold
FROM Menu m
JOIN Order_Details od
ON m.ItemID = od.ItemID
GROUP BY m.ItemName;

SELECT
    PaymentMethod,
    SUM(Amount) AS Total_Amount
FROM Payments
GROUP BY PaymentMethod;

SELECT
    m.ItemName,
    SUM(od.Quantity) AS Total_Sold
FROM Menu m
JOIN Order_Details od
ON m.ItemID = od.ItemID
GROUP BY m.ItemName
HAVING SUM(od.Quantity) > 1;

SELECT
    PaymentMethod,
    SUM(Amount) AS Total_Amount
FROM Payments
GROUP BY PaymentMethod
HAVING SUM(Amount) > 300;

SELECT *
FROM Menu
WHERE Price > (
    SELECT AVG(Price)
    FROM Menu
);

SELECT *
FROM Customers
WHERE CustomerID IN (
    SELECT CustomerID
    FROM Orders
);

SELECT CustomerName
FROM Customers
WHERE CustomerID = (
    SELECT CustomerID
    FROM Orders
    WHERE OrderID = 1
);

WITH FoodSales AS (
    SELECT
        ItemID,
        SUM(Quantity) AS Total_Sold
    FROM Order_Details
    GROUP BY ItemID
)
SELECT
    m.ItemName,
    fs.Total_Sold
FROM FoodSales fs
JOIN Menu m
ON fs.ItemID = m.ItemID;

WITH CustomerOrders AS (
    SELECT
        CustomerID,
        COUNT(*) AS Total_Orders
    FROM Orders
    GROUP BY CustomerID
)
SELECT
    c.CustomerName,
    co.Total_Orders
FROM CustomerOrders co
JOIN Customers c
ON co.CustomerID = c.CustomerID
WHERE co.Total_Orders > 1;

