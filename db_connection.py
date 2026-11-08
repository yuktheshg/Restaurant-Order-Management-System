import mysql.connector
import streamlit as st


def get_connection():
    try:
        connection = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )

        return connection

    except mysql.connector.Error as error:
        st.error(f"Database connection failed: {error}")
        return None