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
# In production, use a real database
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

def show_login_form():
    """Display login form in sidebar"""
    with st.sidebar:
        st.markdown("### 🔐 Member Login")
        
        with st.expander("Login to your account", expanded=not st.session_state.logged_in):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
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
                if st.button("Guest Mode", use_container_width=True):
                    st.session_state.logged_in = False
                    st.rerun()
            
            st.caption("Demo: demo/demo123")

def show_user_info():
    """Show logged in user info in sidebar"""
    with st.sidebar:
        if st.session_state.logged_in:
            # User info card
            if st.session_state.is_premium:
                st.markdown("""
                <div style="background-color: #d4edda; padding: 1rem; border-radius: 10px; border-left: 5px solid #28a745;">
                    <span style="font-size: 1.2rem;">⭐ PREMIUM MEMBER</span><br>
                    <span style="font-size: 0.9rem;">All features unlocked</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #e2f0f9; padding: 1rem; border-radius: 10px; border-left: 5px solid #17a2b8;">
                    <span style="font-size: 1.2rem;">👤 Free Member</span><br>
                    <span style="font-size: 0.9rem;">Upgrade for premium features</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"**Username:** {st.session_state.username}")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
                st.rerun()
        else:
            st.info("👋 Guest mode - Login for more features")

# ============================================================================
# MOBILE-RESPONSIVE CSS
# ============================================================================

st.markdown("""
<style>
    /* Mobile first design */
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
        
        h3 {
            font-size: 1.3rem !important;
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
        transition: transform 0.2s;
    }
    
    .pricing-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .selected-plan {
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    
    .success {
        color: #27ae60;
        font-weight: bold;
    }
    
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    
    .premium-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.markdown('<h1 class="main-header">🌍 NGO Impact Dashboard</h1>', unsafe_allow_html=True)
st.markdown("### 🎯 Turn your survey data into donor-ready reports in seconds")

# ============================================================================
# SIDEBAR - AUTHENTICATION
# ============================================================================

with st.sidebar:
    st.markdown("## 👥 Account")
    
    # Show login form or user info
    if not st.session_state.logged_in:
        show_login_form()
    else:
        show_user_info()
    
    st.markdown("---")
    st.markdown("### 📞 Contact")
    st.markdown("**Email:** mwangomanicholas@gmail.com")
    st.markdown("**WhatsApp:** +265 886867758")
    st.markdown("🇲🇼 **Built in Malawi**")

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
    
    # Check if user can select Basic
    if st.session_state.logged_in:
        if st.button("Select Basic", key="basic_btn", use_container_width=True):
            st.session_state.plan = "Basic - MWK 50,000/mo"
            st.success("Basic plan selected!")
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
    
    # Check if user can select Premium
    if st.session_state.logged_in:
        if st.session_state.is_premium:
            if st.button("✅ Premium Active", key="premium_active", disabled=True, use_container_width=True):
                pass
            st.session_state.plan = "Premium - MWK 100,000/mo"
        else:
            if st.button("💰 Upgrade to Premium", key="premium_btn", use_container_width=True):
                # Show payment modal
                st.session_state.show_payment = True
    else:
        st.button("Login to Upgrade", key="premium_disabled", disabled=True, use_container_width=True)
        st.caption("🔒 Login required")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# PAYMENT MODAL
# ============================================================================

if 'show_payment' in st.session_state and st.session_state.show_payment:
    with st.expander("💳 Complete Your Payment", expanded=True):
        st.markdown("### Premium Plan - MWK 100,000/month")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Payment Options:**
            - Airtel Money: +265 886867758
            - Mpamba: +265 886867758
            - Bank Transfer (upon request)
            """)
            
            payment_method = st.selectbox("Select Payment Method", 
                                          ["Airtel Money", "Mpamba", "Bank Transfer"])
            
            if st.button("✅ Confirm Payment", use_container_width=True):
                # In production, this would integrate with payment API
                st.success("Payment initiated! You'll receive confirmation via WhatsApp.")
                st.info("📱 After payment, your account will be upgraded within 1 hour.")
                
                # For demo, instantly upgrade
                if st.session_state.username == "demo":
                    PREMIUM_USERS.append("demo")
                    st.session_state.is_premium = True
                    st.session_state.plan = "Premium - MWK 100,000/mo"
                    st.balloons()
                    st.rerun()
        
        with col2:
            st.markdown("""
            **What happens next:**
            1. Complete payment via selected method
            2. Send confirmation to WhatsApp
            3. Account upgraded within 1 hour
            4. Access all premium features
            """)
            
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_payment = False
                st.rerun()

# Get current plan from session state
if 'plan' not in st.session_state:
    st.session_state.plan = "Free Trial"

plan = st.session_state.plan
st.caption(f"Current selected plan: **{plan}**")

# Show premium status for logged in users
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

# Function to detect column types
def detect_columns(df):
    """Detect what types of columns are in the dataframe"""
    col_types = {
        'nutrition': find_column(df, ['nutrition_status', 'nutrition', 'malnourished', 'status', 'outcome', 'nutrition status']),
        'district': find_column(df, ['district', 'region', 'location', 'area', 'zone', 'village', 'dist']),
        'gender': find_column(df, ['gender', 'sex']),
        'age': find_column(df, ['age', 'age_group', 'age_years', 'age_months', 'years']),
        'water': find_column(df, ['has_clean_water', 'water', 'clean_water', 'water_access', 'has water']),
        'household': find_column(df, ['household_size', 'household', 'hh_size', 'family_size', 'hhsize']),
    }
    return col_types

# ============================================================================
# MAIN CONTENT - FILE UPLOAD
# ============================================================================

uploaded_file = st.file_uploader("📤 Upload your survey data (CSV or Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Read file
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Loaded {len(df)} records from {uploaded_file.name}")
        
        # Show detected columns
        with st.expander("📋 View Raw Data & Detected Columns"):
            st.dataframe(df.head(100))
            st.caption(f"Total rows: {len(df)} | Total columns: {len(df.columns)}")
            
            # Detect columns
            detected = detect_columns(df)
            st.markdown("**🔍 Detected Columns:**")
            for key, value in detected.items():
                if value:
                    st.markdown(f"✅ **{key}**: '{value}'")
                else:
                    st.markdown(f"❌ **{key}**: Not found")
        
        # Data cleaning
        def clean_data(df):
            df_clean = df.copy()
            for col in df_clean.columns:
                if df_clean[col].dtype == 'object':
                    df_clean[col].fillna('Unknown', inplace=True)
                else:
                    df_clean[col].fillna(df_clean[col].median(), inplace=True)
            return df_clean
        
        df_clean = clean_data(df)
        
        # Get detected columns
        detected = detect_columns(df_clean)
        
        # Calculate metrics based on available data
        total = len(df_clean)
        
        # Try to calculate malnutrition rate if nutrition column exists
        malnutrition_rate = None
        malnourished = None
        
        if detected['nutrition']:
            nutrition_col = detected['nutrition']
            # Check if it's binary (Malnourished/Healthy) or continuous
            if df_clean[nutrition_col].dtype == 'object':
                # Look for malnourished keywords
                malnourished_keywords = ['malnourished', 'malnutrition', 'stunted', 'wasted', 'underweight', 'severe', 'moderate', 'yes', '1', 'true']
                mask = df_clean[nutrition_col].astype(str).str.lower().str.contains('|'.join(malnourished_keywords), na=False)
                malnourished = mask.sum()
                malnutrition_rate = (malnourished / total) * 100 if total > 0 else 0
            elif pd.api.types.is_numeric_dtype(df_clean[nutrition_col]):
                # Assume it's a score or percentage
                malnutrition_rate = df_clean[nutrition_col].mean()
                malnourished = (df_clean[nutrition_col] > df_clean[nutrition_col].median()).sum()
        
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
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Analysis", "🎯 SDG Goals", "💰 Budget", "📄 Reports"])
        
        with tab1:
            st.markdown("### 📊 Data Analysis")
            
            # District/Region analysis if available
            if detected['district'] and detected['nutrition']:
                st.markdown("#### 🏘️ District Analysis")
                district_col = detected['district']
                nutrition_col = detected['nutrition']
                
                # Calculate rates by district
                if df_clean[nutrition_col].dtype == 'object':
                    district_data = df_clean.groupby(district_col)[nutrition_col].apply(
                        lambda x: (x.astype(str).str.lower().str.contains('malnourished|malnutrition', na=False).sum() / len(x)) * 100
                    ).reset_index()
                else:
                    district_data = df_clean.groupby(district_col)[nutrition_col].mean().reset_index()
                
                district_data.columns = [district_col, 'Value']
                district_data = district_data.sort_values('Value', ascending=False)
                
                fig = px.bar(district_data, x=district_col, y='Value',
                             title=f'Analysis by {district_col}',
                             color='Value', color_continuous_scale='reds')
                st.plotly_chart(fig, use_container_width=True)
            elif detected['district']:
                # Just show district counts if no nutrition data
                st.markdown("#### 🏘️ District Distribution")
                district_col = detected['district']
                district_counts = df_clean[district_col].value_counts().reset_index()
                district_counts.columns = [district_col, 'Count']
                
                fig = px.bar(district_counts, x=district_col, y='Count',
                             title=f'Distribution by {district_col}',
                             color='Count', color_continuous_scale='blues')
                st.plotly_chart(fig, use_container_width=True)
            
            # Gender analysis if available
            if detected['gender']:
                st.markdown("#### 👥 Gender Distribution")
                gender_col = detected['gender']
                gender_counts = df_clean[gender_col].value_counts().reset_index()
                gender_counts.columns = [gender_col, 'Count']
                
                fig = px.pie(gender_counts, values='Count', names=gender_col,
                             title=f'Distribution by {gender_col}')
                st.plotly_chart(fig, use_container_width=True)
            
            # Age analysis if available
            if detected['age']:
                st.markdown("#### 📊 Age Distribution")
                age_col = detected['age']
                
                fig = px.histogram(df_clean, x=age_col, nbins=20,
                                   title=f'Distribution of {age_col}')
                st.plotly_chart(fig, use_container_width=True)
            
            # Water access analysis if available
            if detected['water'] and detected['nutrition']:
                st.markdown("#### 💧 Water Access Impact")
                water_col = detected['water']
                nutrition_col = detected['nutrition']
                
                # Calculate malnutrition rate by water access
                if df_clean[nutrition_col].dtype == 'object':
                    water_impact = df_clean.groupby(water_col)[nutrition_col].apply(
                        lambda x: (x.astype(str).str.lower().str.contains('malnourished|malnutrition', na=False).sum() / len(x)) * 100
                    ).reset_index()
                else:
                    water_impact = df_clean.groupby(water_col)[nutrition_col].mean().reset_index()
                
                water_impact.columns = [water_col, 'Malnutrition Rate']
                
                fig = px.bar(water_impact, x=water_col, y='Malnutrition Rate',
                             title=f'Impact of {water_col} on Nutrition',
                             color='Malnutrition Rate', color_continuous_scale='viridis')
                st.plotly_chart(fig, use_container_width=True)
            
            # If specific columns were found, show data preview
            if any([detected['district'], detected['gender'], detected['age'], detected['water'], detected['nutrition']]):
                st.markdown("#### 📋 Data Preview")
                st.dataframe(df_clean.head(10))
            else:
                # If no specific columns found, show general overview
                st.markdown("#### 📈 General Data Overview")
                
                # Show numeric columns summary
                numeric_df = df_clean.select_dtypes(include=['number'])
                if not numeric_df.empty:
                    st.markdown("**Numeric Columns Summary:**")
                    st.dataframe(numeric_df.describe())
                
                # Show top categories for text columns
                text_df = df_clean.select_dtypes(include=['object'])
                if not text_df.empty:
                    for col in text_df.columns[:3]:  # Show first 3 text columns
                        st.markdown(f"**Top values in {col}:**")
                        st.dataframe(text_df[col].value_counts().head(5))
        
        with tab2:
            if plan == "Premium - MWK 100,000/mo" or st.session_state.is_premium:
                st.markdown("### 🎯 SDG Progress Report")
                
                # Create SDG metrics based on available data
                sdg_data = []
                
                if malnutrition_rate is not None:
                    sdg_data.append({
                        'Indicator': 'Malnutrition (SDG 2.2)',
                        'Current': round(malnutrition_rate, 1),
                        'SDG Target': 5,
                        'Gap': round(malnutrition_rate - 5, 1)
                    })
                
                if detected['water']:
                    water_col = detected['water']
                    if df_clean[water_col].dtype == 'object':
                        water_access = (df_clean[water_col].astype(str).str.lower().str.contains('yes|true|1|access', na=False).sum() / total) * 100
                    else:
                        water_access = df_clean[water_col].mean() * 100
                    
                    sdg_data.append({
                        'Indicator': 'Clean Water (SDG 6)',
                        'Current': round(water_access, 1),
                        'SDG Target': 100,
                        'Gap': round(100 - water_access, 1)
                    })
                
                if detected['gender']:
                    gender_col = detected['gender']
                    # Check if it's binary or categorical
                    if df_clean[gender_col].nunique() == 2:
                        # Assume it's male/female
                        female_keywords = ['female', 'f', 'woman', 'girl', '2']
                        female_mask = df_clean[gender_col].astype(str).str.lower().isin(female_keywords)
                        female_pct = (female_mask.sum() / total) * 100
                    else:
                        female_pct = 50  # Default
                    
                    sdg_data.append({
                        'Indicator': 'Gender Balance (SDG 5)',
                        'Current': round(female_pct, 1),
                        'SDG Target': 50,
                        'Gap': round(abs(female_pct - 50), 1)
                    })
                
                if sdg_data:
                    sdg_df = pd.DataFrame(sdg_data)
                    st.dataframe(sdg_df, use_container_width=True)
                    
                    # Create chart
                    fig = go.Figure()
                    fig.add_trace(go.Bar(name='Current', x=sdg_df['Indicator'], y=sdg_df['Current'],
                                         marker_color='steelblue'))
                    fig.add_trace(go.Bar(name='SDG Target', x=sdg_df['Indicator'], y=sdg_df['SDG Target'],
                                         marker_color='green'))
                    fig.update_layout(title='Progress Towards SDG Goals', barmode='group',
                                     yaxis_title='Percentage (%)')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("ℹ️ No SDG-related columns detected in your data.")
            else:
                st.warning("⚠️ SDG Goal analysis is available in **Premium Plan** (MWK 100,000/month)")
                if not st.session_state.logged_in:
                    st.info("👆 Login to upgrade")
                else:
                    st.info("👆 Select Premium from the buttons above to access this feature")
        
        with tab3:
            if plan == "Premium - MWK 100,000/mo" or st.session_state.is_premium:
                st.markdown("### 💰 Budget Calculator")
                
                # Use available data for budget calculations
                target_pop = malnourished if malnourished else int(total * 0.3)  # Assume 30% if unknown
                num_regions = len(df_clean[detected['district']].unique()) if detected['district'] else 1
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Target Population", f"{target_pop:,}")
                with col2:
                    st.metric("Regions", num_regions)
                with col3:
                    st.metric("Total Population", total)
                
                st.markdown("---")
                
                # Calculate scenarios
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
            else:
                st.warning("⚠️ Budget calculator is available in **Premium Plan** (MWK 100,000/month)")
                if not st.session_state.logged_in:
                    st.info("👆 Login to upgrade")
                else:
                    st.info("👆 Select Premium from the buttons above to access this feature")
        
        with tab4:
            st.markdown("### 📄 Generate Reports")
            if plan != "Free Trial" or st.session_state.is_premium:
                if st.button("📥 Generate Report", use_container_width=True):
                    st.success("✅ Report generated successfully!")
                    
                    # Create summary text
                    summary = f"""
NGO IMPACT DASHBOARD - DATA SUMMARY
====================================
File: {uploaded_file.name}
Total Records: {total}
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
Plan: {plan}
User: {st.session_state.username if st.session_state.logged_in else 'Guest'}

KEY METRICS:
"""
                    if malnutrition_rate is not None:
                        summary += f"Malnutrition Rate: {malnutrition_rate:.1f}%\n"
                        summary += f"Malnourished Children: {malnourished}\n"
                    
                    if detected['district']:
                        summary += f"Districts Covered: {len(df_clean[detected['district']].unique())}\n"
                    
                    summary += f"\nCOLUMNS FOUND:\n"
                    for col in df.columns:
                        summary += f"  - {col}\n"
                    
                    summary += f"\nDATA PREVIEW:\n"
                    summary += df.head(10).to_string()
                    
                    # Download as CSV
                    csv = df_clean.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="cleaned_data.csv" style="background-color: #28a745; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; display: inline-block; margin: 10px 0; font-size: 16px;">📥 Download Cleaned Data (CSV)</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    
                    # Download summary as txt
                    b64_summary = base64.b64encode(summary.encode()).decode()
                    href_summary = f'<a href="data:file/txt;base64,{b64_summary}" download="data_summary.txt" style="background-color: #17a2b8; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; display: inline-block; margin: 10px 0; font-size: 16px;">📥 Download Summary Report (TXT)</a>'
                    st.markdown(href_summary, unsafe_allow_html=True)
            else:
                st.info("📌 Reports are available in **Basic** and **Premium** plans")
                if not st.session_state.logged_in:
                    st.info("👆 Login to access reports")
                else:
                    st.info("👆 Select Basic or Premium from the buttons above")
    
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.info("Please make sure your file is a valid CSV or Excel file.")

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

st.markdown("<div style='text-align: center; color: gray; font-size: 0.9rem; padding: 1rem;'>Developed by <strong>Nicholas Mwangomba</strong> | Works on ALL devices</div>", unsafe_allow_html=True)
