import streamlit as st
import pandas as pd
import datetime

# --- १. डिजाइन, ब्याकग्राउन्ड र वाटरमार्क (Sky Blue Theme + Mithila Logo Watermark) ---
st.markdown("""
    <style>
    .stApp { background-color: #e0f2fe; }
    .watermark {
        position: fixed;
        bottom: 20px;
        right: 20px;
        opacity: 0.08;
        font-size: 70px;
        font-weight: bold;
        color: #0284c7;
        font-family: 'Helvetica', sans-serif;
        pointer-events: none;
        z-index: -1;
    }
    </style>
    <div class="watermark">Mithila Logo</div>
""", unsafe_allow_html=True)

# --- २. सिस्टम डाटाबेस सेटअप ---
if 'users' not in st.session_state:
    st.session_state['users'] = [
        {"username": "admin", "password": "123", "role": "super", "branch": "All"},
        {"username": "client1", "password": "123", "role": "client", "branch": "Dhalkewar"},
        {"username": "client2", "password": "123", "role": "client", "branch": "Janakpur"}
    ]
if 'user_logs' not in st.session_state:
    st.session_state['user_logs'] = []
if 'logged_in_user' not in st.session_state:
    st.session_state['logged_in_user'] = None

# --- ३. सुरक्षा र लगइन मेकानिजम (Sign In / User Category Access Control) ---
if st.session_state['logged_in_user'] is None:
    st.title("Mithila Inventory Web Management")
    st.subheader("🔐 Sign In / Security Control")
    
    input_user = st.text_input("Username / Email")
    input_pass = st.text_input("Password", type="password")
    
    if st.button("🔐 Sign In"):
        matched_user = next((u for u in st.session_state['users'] if u['username'] == input_user and u['password'] == input_pass), None)
        if matched_user:
            st.session_state['logged_in_user'] = matched_user
            st.session_state['user_logs'].append({
                "User": matched_user['username'],
                "Action": "Log In",
                "Date/Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Branch": matched_user['branch']
            })
            st.rerun()
        else:
            st.error("गलत युजरनेम वा पासवर्ड!")
else:
    current_user = st.session_state['logged_in_user']
    role = current_user['role']
    assigned_branch = current_user['branch']
    
    col_title, col_logout = st.columns()
    with col_title:
        st.title("🏛️ Mithila Dashboard")
        st.caption(f"Logged in as: **{current_user['username']}** | Role: **{role.upper()}** | Branch: **{assigned_branch}**")
    with col_logout:
        if st.button("🚪 Log Out"):
            st.session_state['user_logs'].append({
                "User": current_user['username'],
                "Action": "Log Out",
                "Date/Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Branch": assigned_branch
            })
            st.session_state['logged_in_user'] = None
            st.rerun()
            
    st.write("---")

    # --- ४. मेनु र सब-मेनु संरचना ---
    menu_options = ["Dashboard", "Transaction", "Reports"]
    if role == 'super':
        menu_options.extend(["Utilities", "Setup"])
        
    main_menu = st.sidebar.selectbox("📂 Main Menu", menu_options)

    # ==================== A) DASHBOARD VIEW ====================
    if main_menu == "Dashboard":
        st.header("📈 Business Summary Dashboard")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total Stock In", "1,250 Pcs")
        col_b.metric("Total Stock Out", "450 Pcs")
        col_c.metric("Active Branches", f"{len(st.session_state.get('branch_database', [])) if 'branch_database' in st.session_state else 46}")

    # ==================== B) TRANSACTION SUB-MENU ====================
    elif main_menu == "Transaction":
        st.header("🔄 Transaction Entries")
        tx_sub = st.selectbox("Sub-Menu", ["Stock In (From Parties)", "Stock Out (Expenses)", "Stock Transfer (To Branch)"])
        
        if tx_sub == "Stock In (From Parties)":
            st.subheader("📝 Stock In Entry (Kharid Format)")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.text_input("Voucher Number", "STK-IN-2026-001", disabled=True)
                if role == 'super':
                    st.date_input("Entry Date (Super Override)", datetime.date.today())
                else:
                    st.date_input("Entry Date", datetime.date.today(), disabled=True)
            with c2:
                st.selectbox("Select Party Name", ["ABC Suppliers", "Mithila Traders", "Local Party"])
                st.text_input("Purchase Bill / Challan No")
            with c3:
                if role == 'super':
                    st.selectbox("Received Branch (Super Override)", ["Head office", "Dhalkewar", "Nawalpur", "Janakpur"])
                else:
                    st.text_input("Received Branch", assigned_branch, disabled=True)
            
            st.write("**Items Entry Grid Table**")
            gc1, gc2, gc3, gc4, gc5 = st.columns(5)
            item_name = gc1.selectbox("Item Name / SKU", ["Cement (Sona)", "Iron Rod 12mm", "Bricks", "Tiles"])
            unit = gc2.text_input("Unit", "Pcs", disabled=True)
            qty = gc3.number_input("Quantity (Qty)", min_value=1, value=100)
            rate = gc4.number_input("Rate (Per Unit)", min_value=0.0, value=750.0)
            total_amt = qty * rate
            gc5.text_input("Total Amount (Rs.)", f"{total_amt:,.2f}", disabled=True)
            
            st.text_input("Remarks / Batch Note")
            if st.button("💾 Save Voucher"):
                st.success("स्टक भौचर सुरक्षित भयो! इन्भेन्टरी र पार्टी लेजर स्वतः अपडेट भयो।")

    # ==================== C) REPORTS SUB-MENU ====================
    elif main_menu == "Reports":
        st.header("📊 Financial & Inventory Reports")
        rep_sub = st.selectbox("Select Report Type", ["Ledger", "Inventory Report", "Parties Report", "Branch Report", "Backup"])
        
        if rep_sub != "Backup":
            cc1, cc2, cc3 = st.columns(3)
            cc1.date_input("Date-wise From")
            cc2.date_input("Date-wise To")
            cc3.selectbox("Item/Filter Wise", ["All Items", "Specific Item", "Month-wise Summary"])
            
            dummy_data = pd.DataFrame({
                'Date': ['2026-05-20', '2026-05-22'],
                'Particulars/Party': ['Mithila Traders', 'Office Expenses'],
                'Item Name': ['Cement', 'Iron Rod'],
                'Qty In': [500, 0],
                'Qty Out': [0, 200],
                'Balance': [500, -200]
            })
            st.table(dummy_data)
            
            st.write("📥 **Export Report Format:**")
            exp_c1, exp_c2, exp_c3 = st.columns(3)
            exp_c1.button("🖨️ Print Report")
            exp_c2.download_button("📊 Download in Excel", data=dummy_data.to_csv().encode('utf-8'), file_name='report.csv', mime='text/csv')
            exp_c3.button("📄 Download PDF")
            
        elif rep_sub == "Backup":
            st.subheader("💾 System Database Backup")
            st.info("कम्प्युटरमा तत्कालको अप-टु-डेट डाटाबेस फाइल ब्याकअप डाउनलोड गर्नुहोस्।")
            st.button("📥 Download Up-to-Date Database (.JSON)")

    # ==================== D) UTILITIES SUB-MENU ====================
    elif main_menu == "Utilities" and role == 'super':
        st.header("🛠️ Utilities Menu")
        util_sub = st.radio("Sub Actions", ["User Log Details", "Add Items", "Add Parties"])
        
        if util_sub == "User Log Details":
            st.subheader("📋 User Log Details (Date-wise Report)")
            if len(st.session_state['user_logs']) == 0:
                st.write("अहिलेसम्म कुनै लग रेकर्ड छैन।")
            else:
                st.table(pd.DataFrame(st.session_state['user_logs']))
        elif util_sub == "Add Items":
            st.text_input("New Item Name")
            st.text_input("SKU Code")
            st.button("Add Item")
        elif util_sub == "Add Parties":
            st.text_input("Party Name")
            st.text_input("Contact/Address")
            st.button("Add Party")
    # ==================== E) SETUP SUB-MENU ====================
    elif main_menu == "Setup" and role == 'super':
        st.header("⚙️ System Setup (Unlimited Admin Privileges)")
        set_sub = st.selectbox("Setup Sub-Menu", ["User Management", "Branch Management", "Upload Database", "Query and Coding"])
        
        if set_sub == "User Management":
            st.subheader("👤 Add, Edit, Delete User & Reset Password")
            new_u = st.text_input("New Username")
            new_p = st.text_input("Password")
            new_r = st.selectbox("Role", ["client", "super"])
            new_b = st.selectbox("Assign Branch", ["Head office", "Dhalkewar", "Nawalpur", "Janakpur", "All"])
            if st.button("Create User"):
                st.session_state['users'].append({"username": new_u, "password": new_p, "role": new_r, "branch": new_b})
                st.success(f"युजर {new_u} सफलतापूर्वक थपियो!")
                
        elif set_sub == "Branch Management":
            st.subheader("🏢 Area & Branch Management System")
            
            if 'branch_database' not in st.session_state:
                st.session_state['branch_database'] = [
                    {"sno": 1, "area": "Head Office", "branch": "Head office"},
                    {"sno": 2, "area": "Janakpur", "branch": "Dhalkewar"},
                    {"sno": 3, "area": "Mahamadpur", "branch": "Nawalpur"},
                    {"sno": 4, "area": "Janakpur", "branch": "Janakpur"},
                    {"sno": 5, "area": "Choharwa", "branch": "Godar"},
                    {"sno": 6, "area": "Janakpur", "branch": "Prakauli"},
                    {"sno": 7, "area": "Janakpur", "branch": "Nigaul"},
                    {"sno": 8, "area": "Choharwa", "branch": "Padariya"},
                    {"sno": 9, "area": "Choharwa", "branch": "Bhediya"},
                    {"sno": 10, "area": "Choharwa", "branch": "Laxmipur"},
                    {"sno": 11, "area": "Choharwa", "branch": "Chhoharwa"},
                    {"sno": 12, "area": "Mahamadpur", "branch": "Mohamadpur"},
                    {"sno": 13, "area": "Mahamadpur", "branch": "Nijgadh"},
                    {"sno": 14, "area": "Mahamadpur", "branch": "Solti"},
                    {"sno": 15, "area": "Mahamadpur", "branch": "Babargunj"},
                    {"sno": 16, "area": "Mahamadpur", "branch": "Valuhi"},
                    {"sno": 17, "area": "Janakpur", "branch": "Ramgopalpur"},
                    {"sno": 18, "area": "Janakpur", "branch": "Khariyani"},
                    {"sno": 19, "area": "Janakpur", "branch": "Hanspur"},
                    {"sno": 20, "area": "Janakpur", "branch": "Sonama"},
                    {"sno": 21, "area": "Choharwa", "branch": "Dhabauli"},
                    {"sno": 22, "area": "Janakpur", "branch": "Bahurwa"},
                    {"sno": 23, "area": "Janakpur", "branch": "Sangrampur"},
                    {"sno": 24, "area": "Mahamadpur", "branch": "Dhangada"},
                    {"sno": 25, "area": "Mahamadpur", "branch": "Chakarghata"},
                    {"sno": 26, "area": "Janakpur", "branch": "Laxminiya"},
                    {"sno": 27, "area": "Janakpur", "branch": "Sarpallo"},
                    {"sno": 28, "area": "Choharwa", "branch": "Khairbona"},
                    {"sno": 29, "area": "Choharwa", "branch": "Chajana"},
                    {"sno": 30, "area": "Janakpur", "branch": "Mahdaiya"},
                    {"sno": 31, "area": "Janakpur", "branch": "Bijalpura"},
                    {"sno": 32, "area": "Mahamadpur", "branch": "Harnaiya"},
                    {"sno": 33, "area": "Choharwa", "branch": "Bhokraha"},
                    {"sno": 34, "area": "Choharwa", "branch": "Kathauna"},
                    {"sno": 35, "area": "Mahamadpur", "branch": "Naukelwa"},
                    {"sno": 36, "area": "Choharwa", "branch": "Saghara"},
                    {"sno": 37, "area": "Mahamadpur", "branch": "Batraul"},
                    {"sno": 38, "area": "Mahamadpur", "branch": "Auraiya"},
                    {"sno": 39, "area": "Janakpur", "branch": "Singyahi"},
                    {"sno": 40, "area": "Mahamadpur", "branch": "Bageshwori"},
                    {"sno": 41, "area": "Mahamadpur", "branch": "Nichuta"},
                    {"sno": 42, "area": "Mahamadpur", "branch": "Inarwari"},
                    {"sno": 43, "area": "Choharwa", "branch": "Bhagani"},
                    {"sno": 44, "area": "Choharwa", "branch": "Ganeshpur"},
                    {"sno": 45, "area": "Choharwa", "branch": "Dumariya"},
                    {"sno": 46, "area": "Janakpur", "branch": "Parbata"}
                ]

            if "show_add_form" not in st.session_state:
                st.session_state["show_add_form"] = False
            if "edit_index" not in st.session_state:
                st.session_state["edit_index"] = None

            col_btn1, _ = st.columns(2)
            with col_btn1:
                if st.button("➕ Add New Branch", use_container_width=True):
                    st.session_state["show_add_form"] = True
                    st.session_state["edit_index"] = None

            if st.session_state["show_add_form"] or st.session_state["edit_index"] is not None:
                st.write("---")
                is_edit = st.session_state["edit_index"] is not None
                st.markdown(f"### {'✏️ Edit Branch Details' if is_edit else '📥 Insert New Branch Details'}")
                
                default_area = "Janakpur"
                default_branch = ""
                if is_edit:
                    idx = st.session_state["edit_index"]
                    default_area = st.session_state['branch_database'][idx]["area"]
                    default_branch = st.session_state['branch_database'][idx]["branch"]
                
                area_list = ["Head Office", "Janakpur", "Mahamadpur", "Choharwa"]
                chosen_area = st.selectbox("Choose Area Office", area_list, index=area_list.index(default_area) if default_area in area_list else 0)
                chosen_branch_name = st.text_input("Enter Branch Name", value=default_branch)
                
                c_save, c_cancel = st.columns(2)
                with c_save:
                    if st.button("💾 Save to Insert/Update", type="primary"):
                        if chosen_branch_name.strip() == "":
                            st.error("ब्रान्चको नाम खाली हुनुहुँदैन!")
                        else:
                            if is_edit:
                                idx = st.session_state["edit_index"]
                                st.session_state['branch_database'][idx]["area"] = chosen_area
                                st.session_state['branch_database'][idx]["branch"] = chosen_branch_name
                                st.success("विवरण परिमार्जन भयो!")
                            else:
                                new_sno = len(st.session_state['branch_database']) + 1
                                st.session_state['branch_database'].append({
                                    "sno": new_sno,
                                    "area": chosen_area,
                                    "branch": chosen_branch_name
                                })
                                st.success(f"शाखा '{chosen_branch_name}' थपियो!")
                            
                            st.session_state["show_add_form"] = False
                            st.session_state["edit_index"] = None
                            st.rerun()
                with c_cancel:
                    if st.button("❌ Cancel"):
                        st.session_state["show_add_form"] = False
                        st.session_state["edit_index"] = None
                        st.rerun()
                st.write("---")

            st.write("### 🔍 Filter and View Branches")
            filter_area = st.selectbox("Select Area Office to View Respective Branches", ["All Areas", "Head Office", "Janakpur", "Mahamadpur", "Choharwa"])
            
            if filter_area == "All Areas":
                filtered_list = st.session_state['branch_database']
            else:
                filtered_list = [b for b in st.session_state['branch_database'] if b["area"] == filter_area]

            if len(filtered_list) == 0:
                st.warning("यो एरिया भित्र कुनै शाखाहरू भेटिएनन्।")
            else:
                h1, h2, h3, h4 = st.columns(4)
                h1.markdown("**S.No**")
                h2.markdown("**Area Office**")
                h3.markdown("**Branch Name**")
                h4.markdown("**Actions**")
                st.write("---")
                
                for b in filtered_list:
                    actual_idx = next(i for i, item in enumerate(st.session_state['branch_database']) if item["sno"] == b["sno"])
                    
                    r1, r2, r3, r4 = st.columns(4)
                    r1.write(str(b["sno"]))
                    r2.write(b["area"])
                    r3.write(b["branch"])
                    
                    btn_edit, btn_del = r4.columns(2)
                    with btn_edit:
                        if st.button("✏️", key=f"edit_{b['sno']}", help="Edit"):
                            st.session_state["edit_index"] = actual_idx
                            st.session_state["show_add_form"] = False
                            st.rerun()
                    with btn_del:
                        if st.button("🗑️", key=f"del_{b['sno']}", help="Delete"):
                            st.session_state['branch_database'].pop(actual_idx)
                            for count, item in enumerate(st.session_state['branch_database'], 1):
                                item["sno"] = count
                            st.rerun()

             elif set_sub == "Upload Database":
            st.subheader("📤 Upload Database File from Computer")
            st.file_uploader("कम्प्युटरबाट .json वा .csv डाटाबेस फाइल लोड गर्नुहोस्")
            
        elif set_sub == "Query and Coding":
            st.subheader("💻 Download System Code & Related Files")
            st.info("यो एपको पूर्ण सोर्स कोड स्थानीय कम्प्युटरमा सुरक्षित गर्नुहोस्।")
            st.button("📥 Download App Source Files (.ZIP)")

