import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from io import BytesIO
import datetime
import re
import hashlib
import hmac
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

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.is_premium = False
    st.session_state.plan = "Free Trial"

def login_user(username, password):
    """Verify login credentials"""
    if username in USERS and USERS[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.is_premium = username in PREMIUM_USERS
        return True
    return False

def logout_user():
    """Log out current user"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.is_premium = False

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
    }
    
    .main-header {
        font-size: 3rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .pricing-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
    }
    
    .premium-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    
    .user-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
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
                if st.button("Login", use_container_width=True):
                    if login_user(username, password):
                        st.success(f"Welcome {username}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            
            with col2:
                if st.button("Guest", use_container_width=True):
                    st.session_state.logged_in = False
                    st.rerun()
            
            st.caption("Demo: demo/demo123")
    else:
        st.markdown('<div class="user-info">', unsafe_allow_html=True)
        st.markdown(f"**Logged in as:** {st.session_state.username}")
        
        if st.session_state.is_premium:
            st.markdown('<span class="premium-badge">⭐ PREMIUM MEMBER</span>', unsafe_allow_html=True)
        else:
            st.markdown("**Status:** Free Member")
        
        if st.button("Logout", use_container_width=True):
            logout_user()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📞 Contact")
    st.markdown("**Email:** mwangomanicholas@gmail.com")
    st.markdown("**WhatsApp:** +265 886867758")
    st.markdown("🇲🇼 **Built in Malawi**")

# ============================================================================
# HEADER
# ============================================================================

st.markdown('<h1 class="main-header">🌍 NGO Impact Dashboard</h1>', unsafe_allow_html=True)
st.markdown("### 🎯 Turn your survey data into donor-ready reports in seconds")

# ============================================================================
# MAIN PLAN SELECTION
# ============================================================================

st.markdown("## 💎 Choose Your Plan")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="pricing-card">', unsafe_allow_html=True)
    st.markdown("### 🆓 Free Trial")
    st.markdown("**MWK 0**")
    st.markdown("""
    ✓ Basic charts  
    ✓ 3 reports/month  
    ✗ No PDF export  
    ✗ No budget calculator
    """)
    if st.button("Select Free Trial", key="free_btn", use_container_width=True):
        st.session_state.plan = "Free Trial"
        st.success("Free Trial selected!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="pricing-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Basic")
    st.markdown("**MWK 50,000/month**")
    st.markdown("""
    ✓ All charts  
    ✓ PDF reports  
    ✓ Excel export  
    ✓ Email support
    """)
    
    if st.session_state.logged_in:
        if st.button("Select Basic", key="basic_btn", use_container_width=True):
            st.session_state.plan = "Basic - MWK 50,000/mo"
            st.success("Basic plan selected!")
            st.rerun()
    else:
        st.button("Login to Select", key="basic_disabled", disabled=True, use_container_width=True)
        st.caption("🔒 Login required")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="pricing-card">', unsafe_allow_html=True)
    st.markdown("### ⭐ Premium")
    st.markdown("**MWK 100,000/month**")
    st.markdown("""
    ✓ Everything in Basic  
    ✓ SDG comparison  
    ✓ Budget calculator  
    ✓ ROI analysis  
    ✓ Priority support
    """)
    
    if st.session_state.logged_in:
        if st.session_state.is_premium:
            st.button("✅ Premium Active", key="premium_active", disabled=True, use_container_width=True)
            st.session_state.plan = "Premium - MWK 100,000/mo"
        else:
            if st.button("Upgrade to Premium", key="premium_btn", use_container_width=True):
                st.info("Contact admin for payment")
    else:
        st.button("Login to Upgrade", key="premium_disabled", disabled=True, use_container_width=True)
        st.caption("🔒 Login required")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.caption(f"Current selected plan: **{st.session_state.plan}**")

if st.session_state.logged_in and st.session_state.is_premium:
    st.markdown('<span class="premium-badge">⭐ PREMIUM MEMBER</span>', unsafe_allow_html=True)

st.markdown("---")

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
        'nutrition': find_column(df, ['nutrition_status', 'nutrition', 'malnourished', 'status', 'outcome']),
        'district': find_column(df, ['district', 'region', 'location', 'area', 'zone']),
        'gender': find_column(df, ['gender', 'sex']),
        'age': find_column(df, ['age', 'age_group', 'age_years']),
        'water': find_column(df, ['has_clean_water', 'water', 'clean_water', 'water_access']),
        'household': find_column(df, ['household_size', 'household', 'hh_size']),
    }
    return col_types

# ============================================================================
# MAIN CONTENT - FILE UPLOAD
# ============================================================================

uploaded_file = st.file_uploader("📤 Upload your survey data (CSV or Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Loaded {len(df)} records from {uploaded_file.name}")
        
        with st.expander("📋 View Raw Data & Detected Columns"):
            st.dataframe(df.head(100))
            detected = detect_columns(df)
            st.markdown("**🔍 Detected Columns:**")
            for key, value in detected.items():
                if value:
                    st.markdown(f"✅ **{key}**: '{value}'")
                else:
                    st.markdown(f"❌ **{key}**: Not found")
        
        def clean_data(df):
            df_clean = df.copy()
            for col in df_clean.columns:
                if df_clean[col].dtype == 'object':
                    df_clean[col].fillna('Unknown', inplace=True)
                else:
                    df_clean[col].fillna(df_clean[col].median(), inplace=True)
            return df_clean
        
        df_clean = clean_data(df)
        detected = detect_columns(df_clean)
        total = len(df_clean)
        
        malnutrition_rate = None
        malnourished = None
        
        if detected['nutrition']:
            nutrition_col = detected['nutrition']
            if df_clean[nutrition_col].dtype == 'object':
                malnourished_keywords = ['malnourished', 'malnutrition', 'stunted', 'wasted', 'underweight']
                mask = df_clean[nutrition_col].astype(str).str.lower().str.contains('|'.join(malnourished_keywords), na=False)
                malnourished = mask.sum()
                malnutrition_rate = (malnourished / total) * 100 if total > 0 else 0
        
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
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Analysis", "🎯 SDG Goals", "💰 Budget", "📄 Reports"])
        
        with tab1:
            st.markdown("### 📊 Data Analysis")
            
            # District analysis
            if detected['district'] and detected['nutrition']:
                st.markdown("#### 🏘️ District Analysis")
                district_col = detected['district']
                nutrition_col = detected['nutrition']
                
                if df_clean[nutrition_col].dtype == 'object':
                    district_data = df_clean.groupby(district_col)[nutrition_col].apply(
                        lambda x: (x.astype(str).str.lower().str.contains('|'.join(['malnourished', 'malnutrition']), na=False).sum() / len(x)) * 100
                    ).reset_index()
                    district_data.columns = [district_col, 'Malnutrition Rate (%)']
                    
                    fig = px.bar(district_data, x=district_col, y='Malnutrition Rate (%)',
                                 title=f'Malnutrition Rate by {district_col}',
                                 color='Malnutrition Rate (%)', color_continuous_scale='reds')
                    st.plotly_chart(fig, use_container_width=True)
            
            # Gender analysis
            if detected['gender']:
                st.markdown("#### 👥 Gender Distribution")
                gender_col = detected['gender']
                gender_counts = df_clean[gender_col].value_counts().reset_index()
                gender_counts.columns = [gender_col, 'Count']
                
                fig = px.pie(gender_counts, values='Count', names=gender_col,
                             title=f'Distribution by {gender_col}')
                st.plotly_chart(fig, use_container_width=True)
            
            # Age analysis
            if detected['age']:
                st.markdown("#### 📊 Age Distribution")
                age_col = detected['age']
                fig = px.histogram(df_clean, x=age_col, nbins=20,
                                   title=f'Distribution of {age_col}')
                st.plotly_chart(fig, use_container_width=True)
            
            # Water impact
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
        
        with tab2:
            if st.session_state.plan == "Premium - MWK 100,000/mo" or st.session_state.is_premium:
                st.markdown("### 🎯 SDG Progress Report")
                
                if malnutrition_rate is not None:
                    # Create SDG metrics
                    sdg_data = pd.DataFrame({
                        'SDG Goal': ['Zero Hunger (SDG 2)', 'Good Health (SDG 3)', 'Gender Equality (SDG 5)', 'Clean Water (SDG 6)'],
                        'Current Progress (%)': [malnutrition_rate, 65, 48, 60],
                        'Target (%)': [5, 100, 50, 100],
                        'Gap': [malnutrition_rate - 5, 35, 2, 40]
                    })
                    
                    st.dataframe(sdg_data, use_container_width=True)
                    
                    # Create comparison chart
                    fig = go.Figure()
                    fig.add_trace(go.Bar(name='Current', x=sdg_data['SDG Goal'], y=sdg_data['Current Progress (%)'],
                                         marker_color='steelblue'))
                    fig.add_trace(go.Bar(name='SDG Target', x=sdg_data['SDG Goal'], y=sdg_data['Target (%)'],
                                         marker_color='green'))
                    fig.update_layout(title='Progress Towards SDG Goals', barmode='group',
                                     yaxis_title='Percentage (%)')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Key insight
                    st.info(f"🔍 **Key Insight:** Malnutrition rate is {malnutrition_rate:.1f}% vs SDG target of 5%. Gap: {malnutrition_rate-5:.1f}%")
                else:
                    st.warning("No nutrition data found to calculate SDG progress")
            else:
                st.warning("⚠️ SDG Goal analysis is available in **Premium Plan**")
        
        with tab3:
            if st.session_state.plan == "Premium - MWK 100,000/mo" or st.session_state.is_premium:
                st.markdown("### 💰 Budget Calculator")
                
                target_pop = malnourished if malnourished else int(total * 0.3)
                num_regions = len(df_clean[detected['district']].unique()) if detected['district'] else 1
                
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
                    st.metric("Basic Intervention", f"MWK {basic_cost:,.0f}")
                with col2:
                    st.metric("Comprehensive", f"MWK {comprehensive_cost:,.0f}", 
                             delta=f"Save MWK {basic_cost - comprehensive_cost:,.0f}")
                
                if target_pop > 0:
                    roi = ((target_pop * 0.6 * 45000) / comprehensive_cost) * 100
                    st.metric("Projected ROI", f"{roi:.1f}%")
                    
                    st.markdown(f"""
                    **📈 Expected Impact:**
                    - Cases prevented: {int(target_pop * 0.6)}
                    - Cost per case: MWK {int(comprehensive_cost / (target_pop * 1.6)):,}
                    """)
            else:
                st.warning("⚠️ Budget calculator is available in **Premium Plan**")
        
        with tab4:
            if st.session_state.plan != "Free Trial":
                st.markdown("### 📄 Generate Reports")
                if st.button("📥 Generate Report", use_container_width=True):
                    st.success("✅ Report generated!")
                    
                    # Create summary
                    summary = f"""
NGO IMPACT DASHBOARD REPORT
===========================
File: {uploaded_file.name}
Records: {total}
Generated: {datetime.datetime.now().strftime('%Y-%m-%d')}

KEY METRICS:
- Malnutrition Rate: {malnutrition_rate:.1f}% if malnutrition_rate else 'N/A'}
- Malnourished: {malnourished if malnourished else 'N/A'}
- Districts: {len(df_clean[detected['district']].unique()) if detected['district'] else 'N/A'}
                    """
                    
                    csv = df_clean.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="cleaned_data.csv">📥 Download Cleaned Data</a>'
                    st.markdown(href, unsafe_allow_html=True)
            else:
                st.info("📌 Reports are available in **Basic** and **Premium** plans")
    
    except Exception as e:
        st.error(f"Error: {e}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("© 2024 Impact Data Dashboard")
with col2:
    st.markdown("🇲🇼 **Built in Malawi**")
with col3:
    st.markdown("📱 **WhatsApp:** +265 886867758")

st.markdown("<div style='text-align: center; color: gray; padding: 1rem;'>Developed by <strong>Nicholas Mwangomba</strong></div>", unsafe_allow_html=True)
