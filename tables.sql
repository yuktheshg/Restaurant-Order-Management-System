USE RestaurantDB;

CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerName VARCHAR(100) NOT NULL,
    Phone VARCHAR(15),
    Email VARCHAR(100)
);

CREATE TABLE Menu (
    ItemID INT PRIMARY KEY AUTO_INCREMENT,
    ItemName VARCHAR(100) NOT NULL,
    Category VARCHAR(50),
    Price DECIMAL(10,2) NOT NULL
);

CREATE TABLE Orders (
    OrderID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT,
    OrderDate DATE,
    OrderStatus VARCHAR(30),
    FOREIGN KEY (CustomerID)
    REFERENCES Customers(CustomerID)
);

CREATE TABLE Order_Details (
    OrderDetailID INT PRIMARY KEY AUTO_INCREMENT,
    OrderID INT,
    ItemID INT,
    Quantity INT,
    FOREIGN KEY (OrderID)
    REFERENCES Orders(OrderID),
    FOREIGN KEY (ItemID)
    REFERENCES Menu(ItemID)
);

CREATE TABLE Payments (
    PaymentID INT PRIMARY KEY AUTO_INCREMENT,
    OrderID INT,
    Amount DECIMAL(10,2),
    PaymentMethod VARCHAR(30),
    PaymentStatus VARCHAR(30),
    FOREIGN KEY (OrderID)
    REFERENCES Orders(OrderID)
);