CREATE OR REPLACE VIEW Restaurant_Order_Summary AS
SELECT
    c.CustomerName,
    o.OrderID,
    o.OrderDate,
    o.OrderStatus,
    m.ItemName,
    od.Quantity,
    m.Price
FROM Customers c
JOIN Orders o
ON c.CustomerID = o.CustomerID
JOIN Order_Details od
ON o.OrderID = od.OrderID
JOIN Menu m
ON od.ItemID = m.ItemID;

SELECT * FROM Restaurant_Order_Summary;