from io import BytesIO

import streamlit as st
import pandas as pd
import plotly.express as px

from db_connection import get_connection

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet


st.set_page_config(
    page_title="Restaurant Management System",
    page_icon="🍽️",
    layout="wide"
)

def load_css():
    with open("style.css") as file:
        st.markdown(
            f"<style>{file.read()}</style>",
            unsafe_allow_html=True
        )

load_css()

st.title("🍽️ Restaurant Order Management System")

st.sidebar.markdown("""
    <h2 style="color:#00B4D8; text-align:center;">
        🍽️ RESTAURANT PRO
    </h2>
    <p style="color:#B8C7D9; text-align:center;">
        Management Dashboard
    </p>
    <hr style="border-color:#294363;">
""", unsafe_allow_html=True)

page = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Customers", "Menu", "Orders", "Payments", "Analytics"]
)

connection = get_connection()

if connection:
    customers = pd.read_sql("SELECT * FROM Customers", connection)
    menu = pd.read_sql("SELECT * FROM Menu", connection)

if connection:

    
    if page == "Dashboard":

        # Welcome Banner
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #142B49, #087E9B);
                padding: 28px;
                border-radius: 15px;
                margin-bottom: 25px;
            ">
                <h1 style="color: white; margin-bottom: 8px;">
                    🍽️ Welcome to Restaurant Management System
                </h1>
                <p style="color: #E6EDF7; font-size: 16px;">
                    Manage customers, food menus, orders and payments
                    all in one place.
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.subheader("📊 Business Overview")

        # Load Database Records
        customers = pd.read_sql(
            "SELECT * FROM Customers", connection
        )

        menu = pd.read_sql(
            "SELECT * FROM Menu", connection
        )

        orders = pd.read_sql(
            "SELECT * FROM Orders", connection
        )

        payments = pd.read_sql(
            "SELECT * FROM Payments", connection
        )

        # Calculate Paid Revenue
        paid_revenue = payments.loc[
            payments["PaymentStatus"] == "Paid", "Amount"
        ].sum()

        # Dashboard Statistics
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("👥 Customers", len(customers))
        col2.metric("📦 Total Orders", len(orders))
        col3.metric("🍕 Menu Items", len(menu))
        col4.metric("💰 Paid Revenue", f"₹{paid_revenue:,.2f}")

        st.divider()

        # Order Status Chart
        st.markdown("### 📈 Order Status Overview")

        if not orders.empty:

            status_data = orders["OrderStatus"].value_counts().reset_index()
            status_data.columns = ["OrderStatus", "TotalOrders"]

            fig = px.pie(
                status_data,
                names="OrderStatus",
                values="TotalOrders",
                title="Restaurant Order Status Distribution",
                hole=0.45
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0B1B33",
                plot_bgcolor="#142B49",
                font_color="white",
                title_font_color="#00B4D8"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.info("No orders available yet.")

        st.divider()

        # Recent Orders
        st.markdown("### 🧾 Recent Orders")
        st.caption("Latest 5 restaurant orders")

        recent_orders = pd.read_sql("""
            SELECT
                o.OrderID,
                c.CustomerName,
                o.OrderDate,
                o.OrderStatus,
                COALESCE(
                    SUM(od.Quantity * m.Price), 0
                ) AS OrderTotal
            FROM Orders o
            JOIN Customers c
                ON o.CustomerID = c.CustomerID
            LEFT JOIN Order_Details od
                ON o.OrderID = od.OrderID
            LEFT JOIN Menu m
                ON od.ItemID = m.ItemID
            GROUP BY
                o.OrderID,
                c.CustomerName,
                o.OrderDate,
                o.OrderStatus
            ORDER BY o.OrderDate DESC, o.OrderID DESC
            LIMIT 5
        """, connection)

        if not recent_orders.empty:

            recent_orders["OrderTotal"] = recent_orders[
                "OrderTotal"
            ].apply(lambda x: f"₹{x:,.2f}")

            st.dataframe(
                recent_orders,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No recent orders to display.")


    

    elif page == "Customers":
        st.subheader("👥 Customer Management")

        st.markdown("### ➕ Add New Customer")

        with st.form("add_customer_form"):
            customer_name = st.text_input("Customer Name")
            phone = st.text_input("Phone Number")
            email = st.text_input("Email Address")

            submit = st.form_submit_button("Add Customer")

            if submit:
                if customer_name.strip():
                    cursor = connection.cursor()

                    query = """
                        INSERT INTO Customers
                        (CustomerName, Phone, Email)
                        VALUES (%s, %s, %s)
                    """

                    cursor.execute(
                        query,
                        (customer_name, phone, email)
                    )
                    connection.commit()
                    cursor.close()

                    st.success("Customer added successfully!")
                    st.rerun()
                else:
                    st.warning("Please enter the customer name.")

        st.divider()

        st.markdown("### 📋 Customer Records")

        customers = pd.read_sql(
            "SELECT * FROM Customers",
            connection
        )
        st.dataframe(customers, use_container_width=True)


        st.divider()

        st.markdown("### 🔎 Search Customers")

        search_customer = st.text_input(
            "Search by name, phone or email",
            placeholder="Enter customer details..."
        )

        customer_records = pd.read_sql(
            "SELECT * FROM Customers",
            connection
        )

        if not customer_records.empty:

            filtered_customers = customer_records.copy()

            if search_customer:
                search_value = search_customer.strip()

                mask = (
                    filtered_customers["CustomerName"].astype(str).str.contains(
                        search_value, case=False, na=False
                    )
                    | filtered_customers["Phone"].astype(str).str.contains(
                        search_value, case=False, na=False
                    )
                    | filtered_customers["Email"].astype(str).str.contains(
                        search_value, case=False, na=False
                    )
                )

                filtered_customers = filtered_customers[mask]

            st.caption(
                f"Found {len(filtered_customers)} customer(s)"
            )

            st.dataframe(
                filtered_customers,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No customers found.")


        st.divider()

        st.markdown("### 📜 Customer Order History")

        history_customers = pd.read_sql("""
            SELECT CustomerID, CustomerName
            FROM Customers
            ORDER BY CustomerName
        """, connection)

        if not history_customers.empty:

            customer_options = dict(
                zip(
                    history_customers["CustomerName"],
                    history_customers["CustomerID"]
                )
            )

            selected_history_customer = st.selectbox(
                "Select Customer",
                list(customer_options.keys()),
                key="customer_order_history"
            )

            customer_history = pd.read_sql("""
                SELECT
                    o.OrderID,
                    o.OrderDate,
                    o.OrderStatus,
                    m.ItemName,
                    od.Quantity,
                    m.Price,
                    (od.Quantity * m.Price) AS Subtotal
                FROM Orders o
                JOIN Order_Details od
                    ON o.OrderID = od.OrderID
                JOIN Menu m
                    ON od.ItemID = m.ItemID
                WHERE o.CustomerID = %s
                ORDER BY o.OrderDate DESC, o.OrderID DESC
            """, connection, params=(
                customer_options[selected_history_customer],
            ))

            if not customer_history.empty:

                st.write(
                    f"Order history for **{selected_history_customer}**"
                )

                st.dataframe(
                    customer_history,
                    use_container_width=True,
                    hide_index=True
                )

                st.metric(
                    "Total Orders",
                    customer_history["OrderID"].nunique()
                )

                st.metric(
                    "Total Order Value",
                    f"₹{customer_history['Subtotal'].sum():,.2f}"
                )

            else:
                st.info("This customer has not placed any orders yet.")

        else:
            st.info("Please add customers first.")





    elif page == "Menu":
        st.subheader("🍔 Menu Management")

        st.markdown("### ➕ Add New Menu Item")

        with st.form("add_menu_form"):
            item_name = st.text_input("Food Item Name")

            category = st.selectbox(
                "Category",
                ["Breakfast", "Starter", "Main Course", "Beverage", "Dessert"]
            )

            price = st.number_input(
                "Price (₹)",
                min_value=1.0,
                step=10.0
            )

            submit = st.form_submit_button("Add Menu Item")

            if submit:
                if item_name.strip():
                    cursor = connection.cursor()

                    query = """
                        INSERT INTO Menu (ItemName, Category, Price)
                        VALUES (%s, %s, %s)
                    """

                    cursor.execute(
                        query,
                        (item_name, category, price)
                    )

                    connection.commit()
                    cursor.close()

                    st.success("Menu item added successfully!")
                    st.rerun()
                else:
                    st.warning("Please enter the food item name.")

        st.divider()

        
        st.markdown("### ➕ Create Order with Multiple Food Items")

        if not customers.empty and not menu.empty:

            customer_options = dict(
                zip(customers["CustomerName"], customers["CustomerID"])
            )

            selected_customer = st.selectbox(
                "Select Customer",
                list(customer_options.keys())
            )

            item_options = {
                f"{row.ItemName} - ₹{row.Price:.2f}": (
                    row.ItemID, row.Price
                )
                for row in menu.itertuples()
            }

            selected_items = st.multiselect(
                "Select Food Items",
                list(item_options.keys()),
                placeholder="Choose one or more food items"
            )

            quantities = {}

            for item in selected_items:
                item_id, price = item_options[item]

                quantities[item_id] = st.number_input(
                    f"Quantity for {item}",
                    min_value=1,
                    max_value=50,
                    value=1,
                    key=f"quantity_{item_id}"
                )

            if selected_items:
                order_total = sum(
                    item_options[item][1] * quantities[item_options[item][0]]
                    for item in selected_items
                )

                st.metric("Calculated Order Total", f"₹{order_total:,.2f}")

            order_date = st.date_input("Order Date")

            if st.button("Place Order"):

                if not selected_items:
                    st.warning("Please select at least one food item.")

                else:
                    cursor = connection.cursor()

                    try:
                        cursor.execute(
                            """
                            INSERT INTO Orders
                            (CustomerID, OrderDate, OrderStatus)
                            VALUES (%s, %s, %s)
                            """,
                            (
                                customer_options[selected_customer],
                                order_date,
                                "Pending"
                            )
                        )

                        new_order_id = cursor.lastrowid

                        order_details = [
                            (new_order_id, item_options[item][0],
                             quantities[item_options[item][0]])
                            for item in selected_items
                        ]

                        cursor.executemany(
                            """
                            INSERT INTO Order_Details
                            (OrderID, ItemID, Quantity)
                            VALUES (%s, %s, %s)
                            """,
                            order_details
                        )

                        connection.commit()

                        st.success(
                            f"Order #{new_order_id} placed successfully!"
                        )
                        st.rerun()

                    except Exception as error:
                        connection.rollback()
                        st.error(f"Could not place order: {error}")

                    finally:
                        cursor.close()

        else:
            st.warning(
                "Please add at least one customer and one menu item."
            )


        st.divider()

        st.markdown("### 🔎 Search and Filter Menu")

        menu_records = pd.read_sql(
            "SELECT * FROM Menu",
            connection
        )

        if not menu_records.empty:

            col1, col2, col3 = st.columns(3)

            with col1:
                search_item = st.text_input(
                    "Search Food Item",
                    placeholder="Enter food name..."
                )

            with col2:
                categories = ["All"] + sorted(
                    menu_records["Category"].dropna().unique().tolist()
                )

                selected_category = st.selectbox(
                    "Filter by Category",
                    categories
                )

            with col3:
                sort_order = st.selectbox(
                    "Sort by Price",
                    ["Default", "Low to High", "High to Low"]
                )

            filtered_menu = menu_records.copy()

            if search_item:
                filtered_menu = filtered_menu[
                    filtered_menu["ItemName"].str.contains(
                        search_item,
                        case=False,
                        na=False
                    )
                ]

            if selected_category != "All":
                filtered_menu = filtered_menu[
                    filtered_menu["Category"] == selected_category
                ]

            if sort_order == "Low to High":
                filtered_menu = filtered_menu.sort_values(
                    by="Price", ascending=True
                )

            elif sort_order == "High to Low":
                filtered_menu = filtered_menu.sort_values(
                    by="Price", ascending=False
                )

            st.caption(
                f"Showing {len(filtered_menu)} menu item(s)"
            )

            st.dataframe(
                filtered_menu,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No menu items available.")



        st.divider()

        st.markdown("### ✏️ Edit Menu Item")

        editable_menu = pd.read_sql(
            "SELECT * FROM Menu ORDER BY ItemID",
            connection
        )

        if not editable_menu.empty:

            item_options = {
                f"{row.ItemName} (ID: {row.ItemID})": row.ItemID
                for row in editable_menu.itertuples()
            }

            selected_item = st.selectbox(
                "Select Food Item to Edit",
                list(item_options.keys()),
                key="edit_menu_item"
            )

            selected_id = item_options[selected_item]

            current_item = editable_menu[
                editable_menu["ItemID"] == selected_id
            ].iloc[0]

            with st.form("edit_menu_form"):

                updated_name = st.text_input(
                    "Food Item Name",
                    value=str(current_item["ItemName"])
                )

                categories = [
                    "Starters", "Main Course",
                    "Desserts", "Beverages", "Snacks"
                ]

                current_category = str(current_item["Category"])

                if current_category not in categories:
                    categories.append(current_category)

                updated_category = st.selectbox(
                    "Category",
                    categories,
                    index=categories.index(current_category)
                )

                updated_price = st.number_input(
                    "Price (₹)",
                    min_value=0.01,
                    value=float(current_item["Price"]),
                    step=10.0
                )

                update_button = st.form_submit_button(
                    "Update Menu Item"
                )

                if update_button:

                    if not updated_name.strip():
                        st.warning("Food item name cannot be empty.")

                    else:
                        cursor = connection.cursor()

                        try:
                            cursor.execute("""
                                UPDATE Menu
                                SET ItemName = %s,
                                    Category = %s,
                                    Price = %s
                                WHERE ItemID = %s
                            """, (
                                updated_name.strip(),
                                updated_category,
                                updated_price,
                                selected_id
                            ))

                            connection.commit()

                            st.success(
                                "Menu item updated successfully!"
                            )

                            st.rerun()

                        except Exception as error:
                            connection.rollback()
                            st.error(f"Update failed: {error}")

                        finally:
                            cursor.close()

        else:
            st.info("No menu items available to edit.")






    
    elif page == "Orders":

        st.subheader("📦 Order Management")

        if not customers.empty and not menu.empty:

            with st.form("complete_order_form"):

                customer_options = dict(
                    zip(customers["CustomerName"], customers["CustomerID"])
                )

                selected_customer = st.selectbox(
                    "Select Customer",
                    list(customer_options.keys())
                )

                item_options = {
                    f'{row.ItemName} - ₹{row.Price:.2f}': row.ItemID
                    for row in menu.itertuples()
                }

                selected_item = st.selectbox(
                    "Select Food Item",
                    list(item_options.keys())
                )

                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    max_value=50,
                    value=1
                )

                order_date = st.date_input("Order Date")

                submit = st.form_submit_button("Place Order")

                if submit:
                    cursor = connection.cursor()

                    try:
                        cursor.execute(
                            """
                            INSERT INTO Orders
                            (CustomerID, OrderDate, OrderStatus)
                            VALUES (%s, %s, %s)
                            """,
                            (
                                customer_options[selected_customer],
                                order_date,
                                "Pending"
                            )
                        )

                        new_order_id = cursor.lastrowid

                        cursor.execute(
                            """
                            INSERT INTO Order_Details
                            (OrderID, ItemID, Quantity)
                            VALUES (%s, %s, %s)
                            """,
                            (
                                new_order_id,
                                item_options[selected_item],
                                quantity
                            )
                        )

                        connection.commit()

                        st.success(
                            f"Order #{new_order_id} placed successfully!"
                        )
                        st.rerun()

                    except Exception as error:
                        connection.rollback()
                        st.error(f"Could not place order: {error}")

                    finally:
                        cursor.close()

        else:
            st.warning("Please add at least one customer and one menu item.")

        st.divider()

        st.markdown("### 📋 Order Summary")

        order_summary = pd.read_sql(
            """
            SELECT
                o.OrderID,
                c.CustomerName,
                o.OrderDate,
                o.OrderStatus,
                GROUP_CONCAT(
                    CONCAT(m.ItemName, ' (Qty: ', od.Quantity, ')')
                    SEPARATOR ', '
                ) AS FoodItems,
                SUM(od.Quantity * m.Price) AS OrderTotal
            FROM Orders o
            JOIN Customers c ON o.CustomerID = c.CustomerID
            LEFT JOIN Order_Details od ON o.OrderID = od.OrderID
            LEFT JOIN Menu m ON od.ItemID = m.ItemID
            GROUP BY
                o.OrderID,
                c.CustomerName,
                o.OrderDate,
                o.OrderStatus
            ORDER BY o.OrderID DESC
            """,
            connection
        )

        st.dataframe(order_summary, use_container_width=True)

        if not order_summary.empty:
            st.metric(
                "Total Order Value",
                f"₹{order_summary['OrderTotal'].fillna(0).sum():,.2f}"
            )

        st.divider()

        st.markdown("### 🔄 Update Order Status")

        if not order_summary.empty:

            order_id = st.selectbox(
                "Select Order ID",
                order_summary["OrderID"].tolist()
            )

            new_status = st.selectbox(
                "New Status",
                ["Pending", "Preparing", "Completed", "Cancelled"]
            )

            if st.button("Update Status"):
                cursor = connection.cursor()

                cursor.execute(
                    """
                    UPDATE Orders
                    SET OrderStatus = %s
                    WHERE OrderID = %s
                    """,
                    (new_status, int(order_id))
                )

                connection.commit()
                cursor.close()

                st.success("Order status updated!")
                st.rerun()



        st.divider()

        st.markdown("### 🔎 Search and Filter Orders")

        search_text = st.text_input(
            "Search by Order ID or Customer Name",
            placeholder="Enter order ID or customer name..."
        )

        all_orders = pd.read_sql("""
            SELECT
                o.OrderID,
                c.CustomerName,
                o.OrderDate,
                o.OrderStatus,
                COALESCE(
                    SUM(od.Quantity * m.Price), 0
                ) AS OrderTotal
            FROM Orders o
            JOIN Customers c
                ON o.CustomerID = c.CustomerID
            LEFT JOIN Order_Details od
                ON o.OrderID = od.OrderID
            LEFT JOIN Menu m
                ON od.ItemID = m.ItemID
            GROUP BY
                o.OrderID,
                c.CustomerName,
                o.OrderDate,
                o.OrderStatus
            ORDER BY o.OrderID DESC
        """, connection)

        if not all_orders.empty:

            status_options = ["All"] + sorted(
                all_orders["OrderStatus"].dropna().unique().tolist()
            )

            selected_status = st.selectbox(
                "Filter by Order Status",
                status_options
            )

            filtered_orders = all_orders.copy()

            if search_text:
                filtered_orders = filtered_orders[
                    filtered_orders["OrderID"].astype(str).str.contains(
                        search_text, case=False
                    )
                    | filtered_orders["CustomerName"].str.contains(
                        search_text, case=False, na=False
                    )
                ]

            if selected_status != "All":
                filtered_orders = filtered_orders[
                    filtered_orders["OrderStatus"] == selected_status
                ]

            st.caption(
                f"Showing {len(filtered_orders)} matching orders"
            )

            st.dataframe(
                filtered_orders,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No orders available to search.")


        st.divider()

        st.markdown("### 🍽️ View Individual Order Details")

        order_list = pd.read_sql("""
            SELECT OrderID
            FROM Orders
            ORDER BY OrderID DESC
        """, connection)

        if not order_list.empty:

            selected_order = st.selectbox(
                "Select Order ID to View",
                order_list["OrderID"].tolist(),
                key="view_order_details"
            )

            details = pd.read_sql("""
                SELECT
                    m.ItemName,
                    m.Category,
                    m.Price,
                    od.Quantity,
                    (m.Price * od.Quantity) AS Subtotal
                FROM Order_Details od
                JOIN Menu m
                    ON od.ItemID = m.ItemID
                WHERE od.OrderID = %s
            """, connection, params=(selected_order,))

            if not details.empty:

                st.markdown(
                    f"#### 🧾 Items in Order #{selected_order}"
                )

                display_details = details.copy()

                display_details["Price"] = display_details[
                    "Price"
                ].apply(lambda x: f"₹{x:,.2f}")

                display_details["Subtotal"] = display_details[
                    "Subtotal"
                ].apply(lambda x: f"₹{x:,.2f}")

                st.dataframe(
                    display_details,
                    use_container_width=True,
                    hide_index=True
                )

                total = details["Subtotal"].sum()

                st.metric(
                    "Total Order Amount",
                    f"₹{total:,.2f}"
                )

            else:
                st.info("No food items found for this order.")

        else:
            st.info("No orders available yet.")






    elif page == "Payments":
        st.subheader("💳 Payment Management")

        st.markdown("### ➕ Add New Payment")

        orders = pd.read_sql(
            "SELECT OrderID FROM Orders",
            connection
        )

        if not orders.empty:
            with st.form("add_payment_form"):

                order_id = st.selectbox(
                    "Select Order ID",
                    orders["OrderID"].tolist()
                )

                amount = st.number_input(
                    "Payment Amount (₹)",
                    min_value=1.0,
                    step=10.0
                )

                payment_method = st.selectbox(
                    "Payment Method",
                    ["UPI", "Cash", "Card", "Net Banking"]
                )

                payment_status = st.selectbox(
                    "Payment Status",
                    ["Pending", "Paid", "Failed"]
                )

                submit = st.form_submit_button("Add Payment")

                if submit:
                    cursor = connection.cursor()

                    cursor.execute(
                        """
                        INSERT INTO Payments
                        (OrderID, Amount, PaymentMethod, PaymentStatus)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (order_id, amount, payment_method, payment_status)
                    )

                    connection.commit()
                    cursor.close()

                    st.success("Payment added successfully!")
                    st.rerun()
        else:
            st.warning("Create an order before adding a payment.")

        st.divider()

        st.markdown("### 📋 Payment Records")

        payments = pd.read_sql(
            """
            SELECT
                PaymentID,
                OrderID,
                Amount,
                PaymentMethod,
                PaymentStatus
            FROM Payments
            ORDER BY PaymentID DESC
            """,
            connection
        )

        st.dataframe(payments, use_container_width=True)

        paid_total = payments.loc[
            payments["PaymentStatus"] == "Paid", "Amount"
        ].sum()

        st.metric("Total Paid Amount", f"₹{paid_total:,.2f}")

    
        
    elif page == "Analytics":

        st.subheader("📊 Restaurant Analytics")
        st.markdown(
            "Explore revenue, order status and popular food items."
        )

        # 1. Revenue by Payment Method
        revenue_data = pd.read_sql("""
            SELECT
                PaymentMethod,
                SUM(Amount) AS TotalRevenue
            FROM Payments
            WHERE PaymentStatus = 'Paid'
            GROUP BY PaymentMethod
        """, connection)

        # 2. Orders by Status
        status_data = pd.read_sql("""
            SELECT
                OrderStatus,
                COUNT(*) AS TotalOrders
            FROM Orders
            GROUP BY OrderStatus
        """, connection)

        # 3. Popular Food Items
        popular_data = pd.read_sql("""
            SELECT
                m.ItemName,
                SUM(od.Quantity) AS TotalQuantity
            FROM Order_Details od
            JOIN Menu m ON od.ItemID = m.ItemID
            GROUP BY m.ItemID, m.ItemName
            ORDER BY TotalQuantity DESC
        """, connection)

        # Revenue Chart
        st.markdown("### 💰 Revenue by Payment Method")

        if not revenue_data.empty:
            fig1 = px.bar(
                revenue_data,
                x="PaymentMethod",
                y="TotalRevenue",
                color="PaymentMethod",
                title="Revenue by Payment Method",
                text_auto=".2f"
            )

            fig1.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0B1B33",
                plot_bgcolor="#142B49",
                font_color="white",
                title_font_color="#00B4D8",
                showlegend=False
            )

            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No paid payment records available yet.")

        st.divider()

        # Order Status Chart
        st.markdown("### 📦 Orders by Status")

        if not status_data.empty:
            fig2 = px.pie(
                status_data,
                names="OrderStatus",
                values="TotalOrders",
                title="Order Status Distribution",
                hole=0.4
            )

            fig2.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0B1B33",
                font_color="white",
                title_font_color="#00B4D8"
            )

            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No orders available yet.")

        st.divider()

        # Popular Food Items Chart
        st.markdown("### 🍕 Popular Food Items")

        if not popular_data.empty:
            fig3 = px.bar(
                popular_data,
                x="ItemName",
                y="TotalQuantity",
                title="Most Ordered Food Items",
                text_auto=True
            )

            fig3.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0B1B33",
                plot_bgcolor="#142B49",
                font_color="white",
                title_font_color="#00B4D8",
                xaxis_title="Food Items",
                yaxis_title="Quantity Ordered"
            )

            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No food order details available yet.")


        st.divider()

        st.markdown("### 📥 Download Restaurant Reports")
        st.write("Export your restaurant database records into one Excel workbook.")

        if st.button("Generate Excel Report"):

            customers_report = pd.read_sql(
                "SELECT * FROM Customers", connection
            )

            menu_report = pd.read_sql(
                "SELECT * FROM Menu", connection
            )

            orders_report = pd.read_sql(
                "SELECT * FROM Orders", connection
            )

            order_details_report = pd.read_sql(
                "SELECT * FROM Order_Details", connection
            )

            payments_report = pd.read_sql(
                "SELECT * FROM Payments", connection
            )

            excel_data = BytesIO()

            with pd.ExcelWriter(
                excel_data,
                engine="openpyxl"
            ) as writer:

                customers_report.to_excel(
                    writer, sheet_name="Customers", index=False
                )

                menu_report.to_excel(
                    writer, sheet_name="Menu", index=False
                )

                orders_report.to_excel(
                    writer, sheet_name="Orders", index=False
                )

                order_details_report.to_excel(
                    writer, sheet_name="Order Details", index=False
                )

                payments_report.to_excel(
                    writer, sheet_name="Payments", index=False
                )

            st.download_button(
                label="⬇️ Download Excel Report",
                data=excel_data.getvalue(),
                file_name="Restaurant_Management_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


        st.divider()

        st.markdown("### 💰 Restaurant Sales Summary")

        sales_data = pd.read_sql("""
            SELECT
                COALESCE(SUM(Amount), 0) AS TotalRevenue,
                COUNT(*) AS TotalPayments
            FROM Payments
            WHERE PaymentStatus = 'Paid'
        """, connection)

        order_values = pd.read_sql("""
            SELECT
                o.OrderID,
                COALESCE(
                    SUM(od.Quantity * m.Price), 0
                ) AS OrderTotal
            FROM Orders o
            LEFT JOIN Order_Details od
                ON o.OrderID = od.OrderID
            LEFT JOIN Menu m
                ON od.ItemID = m.ItemID
            GROUP BY o.OrderID
        """, connection)

        total_revenue = float(
            sales_data.loc[0, "TotalRevenue"]
        )

        total_payments = int(
            sales_data.loc[0, "TotalPayments"]
        )

        average_order_value = (
            order_values["OrderTotal"].mean()
            if not order_values.empty else 0
        )

        highest_order = (
            order_values["OrderTotal"].max()
            if not order_values.empty else 0
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "💵 Total Paid Revenue",
            f"₹{total_revenue:,.2f}"
        )

        col2.metric(
            "💳 Paid Transactions",
            total_payments
        )

        col3.metric(
            "📊 Average Order Value",
            f"₹{average_order_value:,.2f}"
        )

        col4.metric(
            "🏆 Highest Order Value",
            f"₹{highest_order:,.2f}"
        )



        st.divider()

        st.markdown("### 📄 Download PDF Report")

        if st.button("Generate PDF Report"):

            pdf_buffer = BytesIO()

            document = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4
            )

            styles = getSampleStyleSheet()
            elements = []

            elements.append(
                Paragraph(
                    "Restaurant Management Report",
                    styles["Title"]
                )
            )

            elements.append(Spacer(1, 15))

            elements.append(
                Paragraph(
                    "Business Summary",
                    styles["Heading2"]
                )
            )

            elements.append(Spacer(1, 10))

            customers_pdf = pd.read_sql(
                "SELECT * FROM Customers", connection
            )

            orders_pdf = pd.read_sql(
                "SELECT * FROM Orders", connection
            )

            menu_pdf = pd.read_sql(
                "SELECT * FROM Menu", connection
            )

            payments_pdf = pd.read_sql(
                "SELECT * FROM Payments", connection
            )

            paid_revenue_pdf = payments_pdf.loc[
                payments_pdf["PaymentStatus"] == "Paid",
                "Amount"
            ].sum()

            summary_data = [
                ["Metric", "Value"],
                ["Total Customers", str(len(customers_pdf))],
                ["Total Orders", str(len(orders_pdf))],
                ["Total Menu Items", str(len(menu_pdf))],
                ["Paid Revenue", f"Rs. {paid_revenue_pdf:,.2f}"]
            ]

            summary_table = Table(summary_data)

            summary_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#142B49")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]))

            elements.append(summary_table)

            elements.append(Spacer(1, 20))

            elements.append(
                Paragraph("Recent Orders", styles["Heading2"])
            )

            recent_pdf = pd.read_sql("""
                SELECT
                    o.OrderID,
                    c.CustomerName,
                    o.OrderDate,
                    o.OrderStatus
                FROM Orders o
                JOIN Customers c
                    ON o.CustomerID = c.CustomerID
                ORDER BY o.OrderID DESC
                LIMIT 10
            """, connection)

            order_table_data = [
                ["Order ID", "Customer", "Date", "Status"]
            ]

            for _, row in recent_pdf.iterrows():
                order_table_data.append([
                    str(row["OrderID"]),
                    str(row["CustomerName"]),
                    str(row["OrderDate"]),
                    str(row["OrderStatus"])
                ])

            order_table = Table(
                order_table_data,
                repeatRows=1
            )

            order_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#087E9B")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]))

            elements.append(order_table)

            document.build(elements)

            st.download_button(
                "⬇️ Download PDF Report",
                data=pdf_buffer.getvalue(),
                file_name="Restaurant_Management_Report.pdf",
                mime="application/pdf"
            )







else:
    st.error("Database connection failed.")



