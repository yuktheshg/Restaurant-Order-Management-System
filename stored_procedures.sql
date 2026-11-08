USE RestaurantDB;

DROP PROCEDURE IF EXISTS GetAllCustomers;

CREATE PROCEDURE GetAllCustomers()
SELECT * FROM Customers;
