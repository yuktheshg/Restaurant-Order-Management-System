USE RestaurantDB;

INSERT INTO Customers
(CustomerName, Phone, Email)
VALUES
('Rahul', '9876543210', 'rahul@gmail.com'),
('Priya', '9876543211', 'priya@gmail.com'),
('Arjun', '9876543212', 'arjun@gmail.com'),
('Sneha', '9876543213', 'sneha@gmail.com'),
('Kiran', '9876543214', 'kiran@gmail.com');

INSERT INTO Menu
(ItemName, Category, Price)
VALUES
('Chicken Biryani', 'Main Course', 250),
('Veg Biryani', 'Main Course', 180),
('Paneer Tikka', 'Starter', 200),
('Cold Coffee', 'Beverage', 100),
('Ice Cream', 'Dessert', 80),
('Chicken 65', 'Starter', 180),
('Masala Dosa', 'Breakfast', 90),
('Mutton Biryani', 'Main Course', 320);

INSERT INTO Orders
(CustomerID, OrderDate, OrderStatus)
VALUES
(1, '2026-11-01', 'Completed'),
(2, '2026-11-01', 'Pending'),
(3, '2026-11-02', 'Completed'),
(4, '2026-11-02', 'Preparing'),
(5, '2026-11-02', 'Completed');

INSERT INTO Order_Details
(OrderID, ItemID, Quantity)
VALUES
(1, 1, 2),
(1, 4, 1),
(2, 2, 1),
(3, 3, 2),
(4, 6, 1),
(4, 5, 2),
(5, 8, 1);

INSERT INTO Payments
(OrderID, Amount, PaymentMethod, PaymentStatus)
VALUES
(1, 600, 'UPI', 'Paid'),
(2, 180, 'Cash', 'Pending'),
(3, 400, 'Card', 'Paid'),
(4, 340, 'UPI', 'Pending'),
(5, 320, 'Cash', 'Paid');