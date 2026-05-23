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

# --- २. सिस्टम डाटाबेस सेटअप (नयाँ भएकोले नमुना डाटा राखेको) ---
if 'users' not in st.session_state:
    st.session_state['users'] = [
        {"username": "admin", "password": "123", "role": "super", "branch": "All"},
        {"username": "client1", "password": "123", "role": "client", "branch": "Dhalkebar Branch"},
        {"username": "client2", "password": "123", "role": "client", "branch": "Janakpur Branch"}
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
            # युजर लग रेकर्ड राख्ने
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
    # युजर रोल र ब्रान्च निर्धारण गर्ने
    current_user = st.session_state['logged_in_user']
    role = current_user['role']
    assigned_branch = current_user['branch']
    
    # माथि दायाँ कुनामा लगआउट बटन
    col_title, col_logout = st.columns([4, 1])
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

    # --- ४. मेनु र सब-मेनु संरचना (Role-Based Filtering) ---
    # कन्डिसन: Client User ले Setup र Utilities मेनु देख्न पाउने छैन
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
        col_c.metric("Active Branches", "2")

    # ==================== B) TRANSACTION SUB-MENU ====================
    elif main_menu == "Transaction":
        st.header("🔄 Transaction Entries")
        tx_sub = st.selectbox("Sub-Menu", ["Stock In (From Parties)", "Stock Out (Expenses)", "Stock Transfer (To Branch)"])
        
        # ३. a) Stock In (From Parties) को पूर्ण फङ्सन र लेआउट
        if tx_sub == "Stock In (From Parties)":
            st.subheader("📝 Stock In Entry (Kharid Format)")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.text_input("Voucher Number", "STK-IN-2026-001", disabled=True)
                # कन्डिसन: Super User ले मात्र मिति सच्याउन पाउने
                if role == 'super':
                    st.date_input("Entry Date (Super Override)", datetime.date.today())
                else:
                    st.date_input("Entry Date", datetime.date.today(), disabled=True)
            with c2:
                st.selectbox("Select Party Name", ["ABC Suppliers", "Mithila Traders", "Local Party"])
                st.text_input("Purchase Bill / Challan No")
            with c3:
                # कन्डिसन: Client ले आफ्नै ब्रान्च मात्र देख्ने, Super ले परिवर्तन गर्न पाउने
                if role == 'super':
                    st.selectbox("Received Branch (Super Override)", ["Dhalkebar Branch", "Janakpur Branch"])
                else:
                    st.text_input("Received Branch", assigned_branch, disabled=True)
            
            st.write("**Items Entry Grid Table**")
            # ग्रीड लेआउट संरचना
            gc1, gc2, gc3, gc4, gc5 = st.columns([2, 1, 1, 1, 2])
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
            
            # नमुना रिपोर्ट डाटा टेबल
            dummy_data = pd.DataFrame({
                'Date': ['2026-05-20', '2026-05-22'],
                'Particulars/Party': ['Mithila Traders', 'Office Expenses'],
                'Item Name': ['Cement', 'Iron Rod'],
                'Qty In': [500, 0],
                'Qty Out': [0, 50],
                'Balance': [500, 450]
            })
            st.table(dummy_data)
            
            # प्रिन्ट, पीडीएफ र एक्सेल डाउनलोड बटनहरू
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
            new_b = st.selectbox("Assign Branch", ["Dhalkebar Branch", "Janakpur Branch", "All"])
            if st.button("Create User"):
                st.session_state['users'].append({"username": new_u, "password": new_p, "role": new_r, "branch": new_b})
                st.success(f"युजर {new_u} सफलतापूर्वक थपियो!")
                
        elif set_sub == "Branch Management":
            st.subheader("🏢 Add, Edit, Delete Branch")
            st.text_input("Branch Name (e.g., Bardibas Branch)")
            st.button("Add Branch")
            
        elif set_sub == "Upload Database":
            st.subheader("📤 Upload Database File from Computer")
            st.file_uploader("कम्प्युटरबाट .json वा .csv डाटाबेस फाइल लोड गर्नुहोस्")
