# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 22:42:52 2026

@author: Asus
"""

import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import date
# supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]


supabase: Client = create_client(url, key)

# UI
st.set_page_config(page_title = "出勤管理", layout = 'centered')
st.markdown("""
    <style>
    /* 字体 */
    .stApp{ font-size: 20px;}
    
    .stButton>button{ 
        width: 100%;
        height: 3em;
        font-size: 20px !important;
        margin-top: 10px;}
    /* 标题 */
    h1{
        text_a;ogn: center;
        color: #2E765E;
        font-size: 40px !important;
    }
    </style>
    """, unsafe_allow_html=True
)

st.title("🍎 出勤记录")

menu = st.sidebar.selectbox("🏠 功能菜单", ["今日打卡", "员工管理", "年度统计"])
# 1 今日打卡
if menu == "今日打卡":
    st.header("每日记录")
    selected_date = st.date_input("选择日期", date.today())
    res_emp = supabase.table("employees").select("name").execute()
    if res_emp and hasattr(res_emp, 'data'):
        employees = [row['name'] for row in res_emp.data]
    else:
        employees = []
        
    if not employees:
        st.warning("还没有员工，请去员工管理中添加")
    else:
        st.write("勾选上班人员")
        for emp in employees:
            with st.container():
                with st.expander(f"🕴 员工:{emp}", expanded = True):
                    c1, c2 = st.columns([1, 2])
                    is_work = c1.checkbox("已上班", key = f"check_{emp}")
                    note = c2.text_input("备注信息", key = f"note_{emp}")
                    if st.button(f"确认保存 {emp}", key=f"btn_{emp}"):
                        supabase.table("attendance").delete().eq("name",
                        emp).eq("date", str(selected_date)).execute()
                        data = {
                            "name": emp,
                            "date": str(selected_date),
                            "work": 1 if is_work else 0,
                            "note": note}
                        supabase.table("attendance").insert(data).execute()
                        st.success(f"🎉 {emp}的记录已存入")

# 2 员工管理
elif menu == "员工管理":
    st.header("人员管理")
    with st.form("add_emp", clear_on_submit=True):
        new_name = st.text_input("输入新员工姓名")
        submitted = st.form_submit_button("➕ 添加新员工")
        if submitted and new_name:
            try:
                supabase.table("employees").insert({"name": new_name}).execute()
                st.success(f"已添加:{new_name}")
                st.rerun()
            except:
                st.error("此姓名已存在，请勿重复添加")
        
    st.subheader("现有人员名单")
    res_list = supabase.table("employees").select("*").execute()
    for row in res_list.data:
        col_name, col_del = st.columns([3, 1])
        col_name.write(f"·{row['name']}")
        if col_del.button("🚮 删除", key = f"del_{row['id']}"):
            supabase.table("employees").delete().eq("id", row['id']).execute()
            supabase.table("attendance").delete().eq("name", row['name']).execute()
            st.rerun()

# 3 年度统计
elif menu == "年度统计":
    st.header("年度数据")
    year = st.selectbox("选择年份", [str(y) for y in range(2026,2030)])
    res_att = supabase.table("attendance").select("*").execute()
    if res_att.data:
        df = pd.DataFrame(res_att.data)
        df['date'] = pd.to_datetime(df['date'])
        
        df_filtered = df[df['date'].dt.year == year].copy()
        if not df_filtered.empty():
            summary = df_filtered.groupby("name")["work"].sum().reset_index()
            summary.columns = ["姓名", "累计出勤（天）"]
            df_display = df_filtered.rename(columns={
                "name": "姓名",
                "date": "日期",
                "work": "是否出勤",
                "note": "备注"})
            df_display["日期"].dt.strftime('%Y-%m-%d')

            st.dataframe(df_display[["姓名", "日期", "是否出勤", "备注"]], use_container_width=
                         True, hide_index = True)
        else:
            st.info(f"📅 {year}年暂无任何数据。")      
    else:
        st.info("数据库目前是空的，请去打卡！")                























