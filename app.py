import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from io import BytesIO
import datetime
import re
import time

# Page config
st.set_page_config(page_title="NGO Impact Dashboard", page_icon="📊", layout="wide")

# ============================================================================
# SIMPLE AUTHENTICATION SYSTEM
# ============================================================================

# Simple user database (username: password)
USERS = {
    "demo": "demo123",
    "admin": "admin123",
    "test": "test123"
}

# Premium users (users who have paid)
PREMIUM_USERS = ["admin"]  # Usernames who have premium access

# Initialize ALL session state variables at the start
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.is_premium = False
    st.session_state.plan = "Free Trial"
    st.session_state.show_payment = False
    st.session_state.plan_selected = False
    
# File persistence variables - initialize separately to ensure they exist
if 'uploaded_file_data' not in st.session_state:
    st.session_state.uploaded_file_data = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None
if 'df_raw' not in st.session_state:
    st.session_state.df_raw = None
if 'df_clean' not in st.session_state:
    st.session_state.df_clean = None
if 'file_loaded' not in st.session_state:
    st.session_state.file_loaded = False
if 'detected_columns' not in st.session_state:
    st.session_state.detected_columns = {}
if 'malnutrition_rate' not in st.session_state:
    st.session_state.malnutrition_rate = None
if 'malnourished' not in st.session_state:
    st.session_state.malnourished = None

def login_user(username, password):
    """Verify login credentials"""
    if username in USERS and USERS[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.is_premium = username in PREMIUM_USERS
        if st.session_state.is_premium:
            st.session_state.plan = "Premium - MWK 100,000/mo"
        return True
    return False

def logout_user():
    """Log out current user"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.is_premium = False
    st.session_state.plan = "Free Trial"
    st.session_state.show_payment = False
    st.session_state.plan_selected = False
    # Don't clear file data on logout

def set_plan(plan_name):
    """Set the current plan"""
    st.session_state.plan = plan_name
    st.session_state.plan_selected = True
    if plan_name == "Premium - MWK 100,000/mo" and not st.session_state.is_premium:
        st.session_state.show_payment = True

# ============================================================================
# MOBILE-RESPONSIVE CSS
# ============================================================================

st.markdown("""
<style>
    @media (max-width: 768px) {
        .stButton button {
            min-height: 48px !important;
            font-size: 16px !important;
            width: 100% !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            gap: 15px !important;
            padding-bottom: 10px !important;
        }
        
        .main-header {
            font-size: 2rem !important;
        }
        
        .stExpander {
            width: 100% !important;
        }
    }
    
    .main-header {
        font-size: 3rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    .pricing-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
        transition: transform 0.2s;
        border: 2px solid transparent;
    }
    
    .pricing-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .pricing-card.selected {
        border: 2px solid #28a745;
        background-color: #f0fff0;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.2);
    }
    
    .premium-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    .user-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #667eea;
    }
    
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .selected-indicator {
        color: #28a745;
        font-weight: bold;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .file-status {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #0288d1;
        margin: 1rem 0;
    }
    
    .locked-feature {
        background-color: #f8f9fa;
        padding: 3rem;
        border-radius: 10px;
        text-align: center;
        border: 2px dashed #dc3545;
        margin: 1rem 0;
    }
    
    .locked-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .upgrade-btn {
        background-color: #28a745;
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        text-decoration: none;
        display: inline-block;
        margin: 1rem 0;
        font-weight: bold;
        border: none;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - AUTHENTICATION
# ============================================================================

with st.sidebar:
    st.markdown("## 👤 Account")
    st.markdown("---")
    
    if not st.session_state.logged_in:
        with st.container():
            st.markdown("### 🔐 Login")
            username = st.text_input("Username", key="sidebar_username")
            password = st.text_input("Password", type="password", key="sidebar_password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔑 Login", use_container_width=True):
                    if login_user(username, password):
                        st.success(f"Welcome {username}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            
            with col2:
                if st.button("👤 Guest", use_container_width=True):
                    st.session_state.logged_in = False
                    st.rerun()
            
            st.caption("Demo accounts: demo/demo123, admin/admin123")
    else:
        st.markdown('<div class="user-info">', unsafe_allow_html=True)
        st.markdown(f"**👋 Welcome, {st.session_state.username}!**")
        
        if st.session_state.is_premium:
            st.markdown('<span class="premium-badge">⭐ PREMIUM MEMBER</span>', unsafe_allow_html=True)
        else:
            st.markdown("**Status:** Free Member")
        
        st.markdown(f"**Current Plan:** {st.session_state.plan}")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📞 Contact")
    st.markdown("**Email:** mwangomanicholas@gmail.com")
    st.markdown("**WhatsApp:** +265 886867758")
    st.markdown("🇲🇼 **Built in Malawi**")
    
    # Show file status in sidebar if file is loaded
    if st.session_state.get('file_loaded', False) and st.session_state.get('uploaded_file_name'):
        st.markdown("---")
        st.markdown("### 📁 Current File")
        st.markdown(f"**{st.session_state.uploaded_file_name}**")
        if st.session_state.df_raw is not None:
            st.markdown(f"Records: {len(st.session_state.df_raw)}")

# ============================================================================
# HEADER
# ============================================================================

st.markdown('<h1 class="main-header">🌍 NGO Impact Dashboard</h1>', unsafe_allow_html=True)
st.markdown("### 🎯 Turn your survey data into donor-ready reports in seconds")

# ============================================================================
# MAIN PLAN SELECTION
# ============================================================================

st.markdown("## 💎 Choose Your Plan")
st.markdown("Select a plan to access features. Your selection will be highlighted.")

col1, col2, col3 = st.columns(3)

# Free Trial Card
with col1:
    card_class = "pricing-card selected" if st.session_state.plan == "Free Trial" else "pricing-card"
    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
    st.markdown("### 🆓 Free Trial")
    st.markdown("**MWK 0/month**")
    st.markdown("""
    ✓ Basic charts  
    ✓ 3 reports/month  
    ✗ No PDF export  
    ✗ No budget calculator
    """)
    
    if st.session_state.plan == "Free Trial":
        st.markdown('<div class="selected-indicator">✅ CURRENT PLAN</div>', unsafe_allow_html=True)
    
    if st.button("Select Free Trial", key="free_btn", use_container_width=True):
        set_plan("Free Trial")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Basic Card
with col2:
    card_class = "pricing-card selected" if st.session_state.plan == "Basic - MWK 50,000/mo" else "pricing-card"
    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
    st.markdown("### 📊 Basic")
    st.markdown("**MWK 50,000/month**")
    st.markdown("""
    ✓ All charts  
    ✓ PDF reports  
    ✓ Excel export  
    ✓ Email support
    """)
    
    if st.session_state.plan == "Basic - MWK 50,000/mo":
        st.markdown('<div class="selected-indicator">✅ CURRENT PLAN</div>', unsafe_allow_html=True)
    
    if st.session_state.logged_in:
        if st.button("Select Basic", key="basic_btn", use_container_width=True):
            set_plan("Basic - MWK 50,000/mo")
            st.rerun()
    else:
        st.button("🔒 Login to Select", key="basic_disabled", disabled=True, use_container_width=True)
        st.caption("Login required")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Premium Card
with col3:
    card_class = "pricing-card selected" if st.session_state.plan == "Premium - MWK 100,000/mo" else "pricing-card"
    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
    st.markdown("### ⭐ Premium")
    st.markdown("**MWK 100,000/month**")
    st.markdown("""
    ✓ Everything in Basic  
    ✓ SDG comparison  
    ✓ Budget calculator  
    ✓ ROI analysis  
    ✓ Priority support
    """)
    
    if st.session_state.plan == "Premium - MWK 100,000/mo":
        st.markdown('<div class="selected-indicator">✅ CURRENT PLAN</div>', unsafe_allow_html=True)
    
    if st.session_state.logged_in:
        if st.session_state.is_premium:
            st.button("✅ Premium Active", key="premium_active", disabled=True, use_container_width=True)
        else:
            if st.button("Upgrade to Premium", key="premium_btn", use_container_width=True):
                set_plan("Premium - MWK 100,000/mo")
                st.rerun()
    else:
        st.button("🔒 Login to Upgrade", key="premium_disabled", disabled=True, use_container_width=True)
        st.caption("Login required")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Payment modal
if st.session_state.get('show_payment', False):
    with st.expander("💳 Complete Payment", expanded=True):
        st.markdown("### Premium Plan - MWK 100,000/month")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Payment Options:**
            - Airtel Money: +265 886867758
            - Mpamba: +265 886867758
            - Bank Transfer (request)
            """)
            
            payment_method = st.selectbox("Select Payment Method", 
                                        ["Airtel Money", "Mpamba", "Bank Transfer"])
            
            if st.button("✅ Confirm Payment", use_container_width=True):
                st.session_state.is_premium = True
                st.session_state.plan = "Premium - MWK 100,000/mo"
                st.session_state.show_payment = False
                if st.session_state.username not in PREMIUM_USERS:
                    PREMIUM_USERS.append(st.session_state.username)
                st.success("🎉 Payment successful! You now have Premium access!")
                st.balloons()
                time.sleep(2)
                st.rerun()
        
        with col2:
            st.markdown("""
            **What you get:**
            - ✓ SDG Goal tracking
            - ✓ Budget calculator
            - ✓ ROI analysis
            - ✓ Priority support
            - ✓ Unlimited reports
            """)
            
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_payment = False
                st.rerun()

# Display current plan status
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.caption(f"Current selected plan: **{st.session_state.plan}**")
with col2:
    if st.session_state.logged_in and st.session_state.is_premium:
        st.markdown('<span class="premium-badge">⭐ PREMIUM MEMBER</span>', unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# PERSISTENT FILE UPLOAD
# ============================================================================

# File uploader
uploaded_file = st.file_uploader("📤 Upload your survey data (CSV or Excel)", type=['csv', 'xlsx'], key="file_uploader")

# If new file uploaded, save to session state
if uploaded_file is not None:
    try:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            st.session_state.df_raw = pd.read_csv(uploaded_file)
        else:
            st.session_state.df_raw = pd.read_excel(uploaded_file)
        
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.uploaded_file_data = uploaded_file.getvalue()
        st.session_state.file_loaded = True
        
        st.success(f"✅ Loaded {len(st.session_state.df_raw)} records from {uploaded_file.name}")
        
        # Clean the data
        def clean_data(df):
            df_clean = df.copy()
            for col in df_clean.columns:
                if df_clean[col].dtype == 'object':
                    df_clean[col].fillna('Unknown', inplace=True)
                else:
                    df_clean[col].fillna(df_clean[col].median(), inplace=True)
            return df_clean
        
        st.session_state.df_clean = clean_data(st.session_state.df_raw)
        st.rerun()  # Rerun to update the display
        
    except Exception as e:
        st.error(f"Error reading file: {e}")

# Only proceed if we have loaded data
if st.session_state.get('file_loaded', False) and st.session_state.df_raw is not None:
    # Show file status
    st.markdown(f"""
    <div class="file-status">
        📁 <strong>File loaded:</strong> {st.session_state.uploaded_file_name}<br>
        📊 <strong>Records:</strong> {len(st.session_state.df_raw)} | 
        <strong>Columns:</strong> {len(st.session_state.df_raw.columns)}
    </div>
    """, unsafe_allow_html=True)
    
    # Use the stored data
    df = st.session_state.df_raw
    df_clean = st.session_state.df_clean
    total = len(df)
    
    # ============================================================================
    # FUNCTION TO FIND MATCHING COLUMNS
    # ============================================================================
    
    def find_column(df, possible_names):
        """Find a column that matches any of the possible names"""
        df_cols_lower = {col.lower().strip(): col for col in df.columns}
        for name in possible_names:
            name_lower = name.lower().strip()
            if name_lower in df_cols_lower:
                return df_cols_lower[name_lower]
        return None
    
    def detect_columns(df):
        """Detect what types of columns are in the dataframe"""
        col_types = {
            'nutrition': find_column(df, ['nutrition_status', 'nutrition', 'malnourished', 'status', 'outcome', 'health_status']),
            'district': find_column(df, ['district', 'region', 'location', 'area', 'zone', 'village']),
            'gender': find_column(df, ['gender', 'sex']),
            'age': find_column(df, ['age', 'age_group', 'age_years', 'years']),
            'water': find_column(df, ['has_clean_water', 'water', 'clean_water', 'water_access', 'water_source']),
            'household': find_column(df, ['household_size', 'household', 'hh_size', 'family_size', 'hh_members']),
        }
        return col_types
    
    # Detect columns
    detected = detect_columns(df_clean)
    st.session_state.detected_columns = detected
    
    # Show detected columns
    with st.expander("📋 View Raw Data & Detected Columns"):
        st.dataframe(df.head(100))
        st.markdown("**🔍 Detected Columns:**")
        for key, value in detected.items():
            if value:
                st.markdown(f"✅ **{key}**: '{value}'")
            else:
                st.markdown(f"❌ **{key}**: Not found")
    
    # Calculate metrics
    malnutrition_rate = None
    malnourished = None
    
    if detected['nutrition']:
        nutrition_col = detected['nutrition']
        if df_clean[nutrition_col].dtype == 'object':
            malnourished_keywords = ['malnourished', 'malnutrition', 'stunted', 'wasted', 'underweight']
            mask = df_clean[nutrition_col].astype(str).str.lower().str.contains('|'.join(malnourished_keywords), na=False)
            malnourished = int(mask.sum())
            malnutrition_rate = (malnourished / total) * 100 if total > 0 else 0
            st.session_state.malnutrition_rate = malnutrition_rate
            st.session_state.malnourished = malnourished
    
    # Key metrics display
    st.markdown("## 📊 Key Metrics")
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("Total Records", f"{total:,}")
    
    with cols[1]:
        if malnutrition_rate is not None:
            st.metric("Malnutrition Rate", f"{malnutrition_rate:.1f}%")
        else:
            st.metric("Total Columns", len(df.columns))
    
    with cols[2]:
        if malnourished is not None:
            st.metric("Malnourished", f"{malnourished:,}")
        else:
            numeric_cols = len(df_clean.select_dtypes(include=['number']).columns)
            st.metric("Numeric Columns", numeric_cols)
    
    with cols[3]:
        if detected['district']:
            districts = len(df_clean[detected['district']].unique())
            st.metric("Districts/Regions", districts)
        else:
            text_cols = len(df_clean.select_dtypes(include=['object']).columns)
            st.metric("Categories", text_cols)
    
    # ============================================================================
    # TABS WITH DIFFERENT FEATURES PER PLAN
    # ============================================================================
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Analysis", "🎯 SDG Goals", "💰 Budget", "📄 Reports"])
    
    with tab1:
        st.markdown("### 📊 Data Analysis")
        st.info("✅ Basic charts available in all plans")
        
        # District analysis - available to all plans
        if detected['district'] and detected['nutrition']:
            st.markdown("#### 🏘️ District Analysis")
            district_col = detected['district']
            nutrition_col = detected['nutrition']
            
            if df_clean[nutrition_col].dtype == 'object':
                district_data = df_clean.groupby(district_col)[nutrition_col].apply(
                    lambda x: (x.astype(str).str.lower().str.contains('malnourished', na=False).sum() / len(x)) * 100
                ).reset_index()
                district_data.columns = [district_col, 'Malnutrition Rate (%)']
                district_data = district_data.sort_values('Malnutrition Rate (%)', ascending=False)
                
                fig = px.bar(district_data, x=district_col, y='Malnutrition Rate (%)',
                             title=f'Malnutrition Rate by {district_col}',
                             color='Malnutrition Rate (%)', color_continuous_scale='reds')
                st.plotly_chart(fig, use_container_width=True)
        
        # Gender analysis - available to all plans
        if detected['gender']:
            st.markdown("#### 👥 Gender Distribution")
            gender_col = detected['gender']
            gender_counts = df_clean[gender_col].value_counts().reset_index()
            gender_counts.columns = [gender_col, 'Count']
            
            fig = px.pie(gender_counts, values='Count', names=gender_col,
                         title=f'Distribution by {gender_col}')
            st.plotly_chart(fig, use_container_width=True)
        
        # Age analysis - available to all plans
        if detected['age']:
            st.markdown("#### 📊 Age Distribution")
            age_col = detected['age']
            fig = px.histogram(df_clean, x=age_col, nbins=20,
                               title=f'Distribution of {age_col}')
            st.plotly_chart(fig, use_container_width=True)
        
        # Water impact - available to all plans
        if detected['water'] and detected['nutrition']:
            st.markdown("#### 💧 Water Access Impact")
            water_col = detected['water']
            nutrition_col = detected['nutrition']
            
            if df_clean[nutrition_col].dtype == 'object':
                water_impact = df_clean.groupby(water_col)[nutrition_col].apply(
                    lambda x: (x.astype(str).str.lower().str.contains('malnourished', na=False).sum() / len(x)) * 100
                ).reset_index()
                water_impact.columns = [water_col, 'Malnutrition Rate (%)']
                
                fig = px.bar(water_impact, x=water_col, y='Malnutrition Rate (%)',
                             title=f'Impact of {water_col} on Nutrition',
                             color='Malnutrition Rate (%)', color_continuous_scale='viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        # Data preview - available to all plans
        st.markdown("#### 📋 Data Preview")
        st.dataframe(df_clean.head(10))
    
    with tab2:
        # SDG Goals - PREMIUM ONLY
        if st.session_state.plan in ["Premium - MWK 100,000/mo"] or st.session_state.is_premium:
            st.markdown("### 🎯 SDG Progress Report")
            st.success("✅ Premium feature unlocked!")
            
            if malnutrition_rate is not None:
                # Create SDG data
                sdg_data = pd.DataFrame({
                    'SDG Goal': [
                        'Zero Hunger (SDG 2)', 
                        'Good Health (SDG 3)', 
                        'Gender Equality (SDG 5)', 
                        'Clean Water (SDG 6)'
                    ],
                    'Current (%)': [
                        round(malnutrition_rate, 1), 
                        round(malnutrition_rate * 1.3, 1),
                        round(malnutrition_rate * 0.8, 1),
                        round(malnutrition_rate * 1.2, 1)
                    ],
                    'Target (%)': [5, 100, 50, 100],
                    'Gap': [
                        round(malnutrition_rate - 5, 1),
                        round(100 - (malnutrition_rate * 1.3), 1),
                        round(50 - (malnutrition_rate * 0.8), 1),
                        round(100 - (malnutrition_rate * 1.2), 1)
                    ]
                })
                
                st.dataframe(sdg_data, use_container_width=True)
                
                # Create comparison chart
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Current', 
                    x=sdg_data['SDG Goal'], 
                    y=sdg_data['Current (%)'],
                    marker_color='steelblue',
                    text=sdg_data['Current (%)'],
                    textposition='auto'
                ))
                fig.add_trace(go.Bar(
                    name='SDG Target', 
                    x=sdg_data['SDG Goal'], 
                    y=sdg_data['Target (%)'],
                    marker_color='green',
                    text=sdg_data['Target (%)'],
                    textposition='auto'
                ))
                fig.update_layout(
                    title='Progress Towards SDG Goals',
                    barmode='group',
                    yaxis_title='Percentage (%)',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Key insight
                gap = malnutrition_rate - 5
                if gap > 0:
                    st.warning(f"⚠️ **Critical Gap:** Malnutrition rate is {malnutrition_rate:.1f}% - needs to reduce by {gap:.1f}% to meet SDG 2 target")
                else:
                    st.success(f"✅ **On Track:** Malnutrition rate of {malnutrition_rate:.1f}% meets SDG 2 target!")
            else:
                st.info("ℹ️ Upload data with nutrition information to see SDG analysis")
        else:
            # Show locked message for non-premium users
            st.markdown("""
            <div class="locked-feature">
                <div class="locked-icon">🔒</div>
                <h3>SDG Goals Analysis is Premium Feature</h3>
                <p style="color: #666; margin: 1rem 0;">Upgrade to Premium to track your progress against UN Sustainable Development Goals</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.logged_in:
                if st.button("⭐ Upgrade to Premium Now", key="upgrade_from_sdg", use_container_width=True):
                    set_plan("Premium - MWK 100,000/mo")
                    st.rerun()
            else:
                st.info("👆 Login first to upgrade")
    
    with tab3:
        # Budget Calculator - PREMIUM ONLY
        if st.session_state.plan in ["Premium - MWK 100,000/mo"] or st.session_state.is_premium:
            st.markdown("### 💰 Budget Calculator")
            st.success("✅ Premium feature unlocked!")
            
            # Calculate target population
            target_pop = malnourished if malnourished else int(total * 0.3)
            num_regions = len(df_clean[detected['district']].unique()) if detected['district'] else 1
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Target Population", f"{target_pop:,}")
            with col2:
                st.metric("Regions", num_regions)
            with col3:
                st.metric("Total Population", total)
            
            st.markdown("---")
            
            # Calculate costs
            basic_cost = target_pop * 45000
            comprehensive_cost = (total * 15000) + (target_pop * 45000) + (num_regions * 5000000)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Basic Intervention", 
                    f"MWK {basic_cost:,.0f}",
                    help="Treatment only for malnourished children"
                )
            with col2:
                savings = basic_cost - comprehensive_cost
                st.metric(
                    "Comprehensive", 
                    f"MWK {comprehensive_cost:,.0f}", 
                    delta=f"Save MWK {savings:,.0f}" if savings > 0 else None,
                    help="Prevention + Treatment program"
                )
            
            if target_pop > 0:
                roi = ((target_pop * 0.6 * 45000) / comprehensive_cost) * 100
                cases_prevented = int(target_pop * 0.6)
                cost_per_case = int(comprehensive_cost / (target_pop * 1.6))
                
                st.markdown("---")
                st.markdown("### 📈 Expected Impact")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Cases Prevented", f"{cases_prevented:,}")
                with col2:
                    st.metric("Cost per Case", f"MWK {cost_per_case:,}")
                with col3:
                    st.metric("ROI", f"{roi:.1f}%")
        else:
            # Show locked message for non-premium users
            st.markdown("""
            <div class="locked-feature">
                <div class="locked-icon">🔒</div>
                <h3>Budget Calculator is Premium Feature</h3>
                <p style="color: #666; margin: 1rem 0;">Upgrade to Premium to calculate intervention costs and ROI</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.logged_in:
                if st.button("⭐ Upgrade to Premium Now", key="upgrade_from_budget", use_container_width=True):
                    set_plan("Premium - MWK 100,000/mo")
                    st.rerun()
            else:
                st.info("👆 Login first to upgrade")
    
    with tab4:
        # Reports - BASIC AND PREMIUM only (not Free Trial)
        if st.session_state.plan != "Free Trial":
            st.markdown("### 📄 Generate Reports")
            if st.session_state.plan == "Premium - MWK 100,000/mo" or st.session_state.is_premium:
                st.success("✅ Premium plan - Full report access")
            else:
                st.info("✅ Basic plan - Report access enabled")
            
            if st.button("📥 Generate Report", use_container_width=True, type="primary"):
                # Format values for report
                malnutrition_text = f"{malnutrition_rate:.1f}%" if malnutrition_rate is not None else "N/A"
                malnourished_text = f"{malnourished}" if malnourished is not None else "N/A"
                districts_text = f"{len(df_clean[detected['district']].unique())}" if detected['district'] else "N/A"
                
                # Create report
                summary = f"""
╔══════════════════════════════════════════════════════════╗
║              NGO IMPACT DASHBOARD REPORT                 ║
╠══════════════════════════════════════════════════════════╣
║ File: {st.session_state.uploaded_file_name:<35} ║
║ Records: {total:<5}                                     ║
║ Date: {datetime.datetime.now().strftime('%Y-%m-%d')}            ║
╠══════════════════════════════════════════════════════════╣
║                    KEY METRICS                           ║
╠══════════════════════════════════════════════════════════╣
║ Malnutrition Rate: {malnutrition_text:<10}                    ║
║ Malnourished: {malnourished_text:<10}                          ║
║ Districts: {districts_text:<10}                                 ║
╠══════════════════════════════════════════════════════════╣
║ Plan: {st.session_state.plan}          ║
║ User: {st.session_state.username if st.session_state.logged_in else 'Guest'}                          ║
╚══════════════════════════════════════════════════════════╝
                """
                
                st.success("✅ Report generated successfully!")
                
                # Download buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = df_clean.to_csv(index=False)
                    b64_csv = base64.b64encode(csv.encode()).decode()
                    href_csv = f'<a href="data:file/csv;base64,{b64_csv}" download="cleaned_data.csv" style="background-color: #28a745; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; display: inline-block; margin: 10px 0; font-weight: bold;">📥 Download Cleaned Data (CSV)</a>'
                    st.markdown(href_csv, unsafe_allow_html=True)
                
                with col2:
                    b64_txt = base64.b64encode(summary.encode()).decode()
                    href_txt = f'<a href="data:file/txt;base64,{b64_txt}" download="report.txt" style="background-color: #17a2b8; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; display: inline-block; margin: 10px 0; font-weight: bold;">📥 Download Report (TXT)</a>'
                    st.markdown(href_txt, unsafe_allow_html=True)
        else:
            # Show locked message for Free Trial users
            st.markdown("""
            <div class="locked-feature" style="border-color: #ffc107;">
                <div class="locked-icon">📄</div>
                <h
