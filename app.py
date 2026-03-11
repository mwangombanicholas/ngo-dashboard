import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from io import BytesIO
import datetime
import re

# Page config
st.set_page_config(page_title="NGO Impact Dashboard", page_icon="📊", layout="wide")

# Mobile-optimized CSS
st.markdown("""
<style>
    /* Mobile first design */
    @media (max-width: 768px) {
        /* Make everything bigger for touch */
        .stButton button {
            min-height: 48px !important;
            font-size: 16px !important;
            width: 100% !important;
        }
        
        /* Make radio buttons easy to tap */
        .stRadio div[role="radiogroup"] {
            flex-direction: column !important;
            gap: 10px !important;
        }
        
        .stRadio label {
            padding: 12px !important;
            background-color: #f0f2f6;
            border-radius: 8px;
            width: 100%;
            margin: 0 !important;
        }
        
        /* Make tabs scrollable */
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            gap: 15px !important;
            padding-bottom: 10px !important;
        }
        
        /* Make metric cards stack */
        .css-1r6slb0 {
            width: 100% !important;
            margin-bottom: 10px !important;
        }
        
        /* Increase font sizes */
        .main-header {
            font-size: 2rem !important;
        }
        
        h3 {
            font-size: 1.3rem !important;
        }
        
        /* Make expander easier to tap */
        .streamlit-expanderHeader {
            font-size: 1.1rem !important;
            padding: 15px !important;
        }
        
        /* Hide sidebar on mobile by default */
        .css-1d391kg {
            display: none !important;
        }
        
        /* Show mobile menu button */
        .mobile-menu-btn {
            display: block !important;
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 999;
            background-color: #2c3e50;
            color: white;
            border: none;
            border-radius: 50px;
            padding: 15px 25px;
            font-size: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
    }
    
    /* Desktop styles */
    @media (min-width: 769px) {
        .mobile-menu-btn {
            display: none !important;
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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🌍 NGO Impact Dashboard</h1>', unsafe_allow_html=True)
st.markdown("### 🎯 Turn your survey data into donor-ready reports in seconds")

# Mobile menu button (just for show - actual functionality is now in main area)
st.markdown('<button class="mobile-menu-btn" onclick="alert(\'Select your plan from the buttons above!\')">📱 Menu</button>', unsafe_allow_html=True)

# MAIN PLAN SELECTION - Now visible on ALL devices!
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
    if st.button("Select Free Trial", key="free_btn"):
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
    if st.button("Select Basic", key="basic_btn"):
        st.session_state.plan = "Basic - MWK 50,000/mo"
        st.success("Basic plan selected!")
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
    if st.button("Select Premium", key="premium_btn"):
        st.session_state.plan = "Premium - MWK 100,000/mo"
        st.success("Premium plan selected!")
    st.markdown('</div>', unsafe_allow_html=True)

# Get current plan from session state
if 'plan' not in st.session_state:
    st.session_state.plan = "Free Trial"

plan = st.session_state.plan
st.caption(f"Current selected plan: **{plan}**")

# Contact info in a nice row
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("📧 **Email:** mwangomanicholas@gmail.com")
with col2:
    st.markdown("📱 **WhatsApp:** +265 886867758")
with col3:
    st.markdown("🇲🇼 **Built in Malawi**")

st.markdown("---")

# Function to find matching columns
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

# Main content
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
            if plan == "Premium - MWK 100,000/mo":
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
                st.info("👆 Select Premium from the buttons above to access this feature")
        
        with tab3:
            if plan == "Premium - MWK 100,000/mo":
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
                st.info("👆 Select Premium from the buttons above to access this feature")
        
        with tab4:
            st.markdown("### 📄 Generate Reports")
            if plan != "Free Trial":
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
                st.info("👆 Select Basic or Premium from the buttons above to access reports")
    
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.info("Please make sure your file is a valid CSV or Excel file.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 0.9rem; padding: 1rem;'>Developed by <strong>Nicholas Mwangomba</strong> 🇲🇼 | Works on ALL devices | WhatsApp: +265 886867758</div>", unsafe_allow_html=True)
