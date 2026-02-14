# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 23:23:13 2026

@author: Asus
"""

import streamlit as st
import sqlite3
from datetime import date
import pandas as pd

st.markdown("""
    <style>
    /* 字体 */
    html, body,
[class*="ViewContainer"]{
        font-size: 20px;
    }
    /* 标题 */
    h1{
        color: #ffb4b;
        font-size: 40px !important;
    }
    
    .stButton>button{
        width: 100%;
        height: 3em;
        font-size: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True
)


# 数据库连接
conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

# 创建表
c.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    date TEXT,
    work INTEGER,
    note TEXT
)
""")

conn.commit()

st.title("出勤记录系统")

menu = st.sidebar.selectbox("菜单", ["今日打卡", "员工管理", "年度统计"])

# -----------------------
# 今日打卡
# -----------------------
if menu == "今日打卡":
    selected_date = st.date_input("选择日期", date.today())
    selected_date = str(selected_date)

    c.execute("SELECT name FROM employees")
    employees = [row[0] for row in c.fetchall()]

    if not employees:
        st.warning("请先添加员工")
    else:
        for emp in employees:
            col1, col2 = st.columns([1,2])
            with col1:
                work = st.checkbox(f"{emp} 上班", key=f"{emp}_work")
            with col2:
                note = st.text_input(f"{emp} 备注", key=f"{emp}_note")

            if st.button(f"保存 {emp}", key=f"save_{emp}"):
                c.execute("""
                DELETE FROM attendance WHERE name=? AND date=?
                """, (emp, selected_date))

                c.execute("""
                INSERT INTO attendance (name, date, work, note)
                VALUES (?, ?, ?, ?)
                """, (emp, selected_date, int(work), note))

                conn.commit()
                st.success(f"{emp} 保存成功")

# -----------------------
# 员工管理
# -----------------------
elif menu == "员工管理":
    new_name = st.text_input("输入新员工姓名")

    if st.button("添加员工"):
        try:
            c.execute("INSERT INTO employees (name) VALUES (?)", (new_name,))
            conn.commit()
            st.success("添加成功")
        except:
            st.error("员工已存在")

    st.subheader("现有员工")
    c.execute("SELECT name FROM employees")
    employees = [row[0] for row in c.fetchall()]

    for emp in employees:
        col1, col2 = st.columns([3,1])
        col1.write(emp)
        if col2.button("删除", key=f"del_{emp}"):
            c.execute("DELETE FROM employees WHERE name=?", (emp,))
            conn.commit()
            st.experimental_rerun()

# -----------------------
# 年度统计
# -----------------------
elif menu == "年度统计":
    year = st.selectbox("选择年份", [str(y) for y in range(2026, 2035)])

    df = pd.read_sql_query("SELECT * FROM attendance", conn)

    if not df.empty:
        df["year"] = df["date"].str[:4]
        df_year = df[df["year"] == year]

        summary = df_year.groupby("name")["work"].sum()

        st.subheader("出勤统计")
        st.write(summary)

        st.subheader("详细记录")
        st.dataframe(df_year)
    else:

        st.info("暂无数据")

