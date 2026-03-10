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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .highlight {
        color: #e74c3c;
        font-weight: bold;
    }
    .success {
        color: #27ae60;
        font-weight: bold;
    }
    .info-box {
        background-color: #e1f5fe;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #0288d1;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🌍 NGO Impact Dashboard</h1>', unsafe_allow_html=True)
st.markdown("### 🎯 Turn your survey data into donor-ready reports in seconds")

# Sidebar - Pricing
with st.sidebar:
    st.markdown("## 💎 Pricing Plans")
    
    plan = st.radio(
        "Select Plan",
        ["Free Trial", "Basic - MWK 10,000/mo", "Premium - MWK 40,000/mo"]
    )
    
    if plan == "Free Trial":
        st.info("""
        **Includes:**
        ✓ Basic charts
        ✓ 3 reports/month
        × No PDF export
        × No budget calculator
        """)
    elif plan == "Basic - MWK 10,000/mo":
        st.success("""
        **Includes:**
        ✓ All charts
        ✓ PDF reports
        ✓ Excel export
        ✓ Email support
        """)
    else:
        st.success("""
        **Includes:**
        ✓ Everything in Basic
        ✓ SDG comparison
        ✓ Budget calculator
        ✓ ROI analysis
        ✓ Priority support
        """)
    
    st.markdown("---")
    st.markdown("### 📞 Contact")
    st.markdown("Email: mwangomanicholas@gmail.com")
    st.markdown("📱 WhatsApp: +265 [Your Number]")

# Function to find matching columns
def find_column(df, possible_names):
    """Find a column that matches any of the possible names"""
    df_cols_lower = {col.lower(): col for col in df.columns}
    for name in possible_names:
        if name.lower() in df_cols_lower:
            return df_cols_lower[name.lower()]
    return None

# Function to detect column types
def detect_columns(df):
    """Detect what types of columns are in the dataframe"""
    col_types = {
        'nutrition': find_column(df, ['nutrition', 'nutrition_status', 'malnourished', 'status', 'outcome']),
        'district': find_column(df, ['district', 'region', 'location', 'area', 'zone', 'village']),
        'gender': find_column(df, ['gender', 'sex']),
        'age': find_column(df, ['age', 'age_group', 'age_years', 'age_months']),
        'water': find_column(df, ['water', 'clean_water', 'water_access', 'has_water']),
        'household': find_column(df, ['household', 'hh_size', 'family_size', 'hh_members']),
        'income': find_column(df, ['income', 'wealth', 'socioeconomic', 'ses']),
        'education': find_column(df, ['education', 'edu', 'school']),
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
                    st.markdown(f"✅ {key}: '{value}'")
                else:
                    st.markdown(f"❌ {key}: Not found")
        
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
                malnutrition_rate = (malnourished / total) * 100
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
                st.metric("Text Columns", text_cols)
        
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
            
            # Gender analysis if available
            if detected['gender']:
                st.markdown("#### 👥 Gender Distribution")
                gender_col = detected['gender']
                gender_counts = df_clean[gender_col].value_counts()
                
                fig = px.pie(values=gender_counts.values, names=gender_counts.index,
                             title=f'Distribution by {gender_col}')
                st.plotly_chart(fig, use_container_width=True)
            
            # Age analysis if available
            if detected['age']:
                st.markdown("#### 📊 Age Distribution")
                age_col = detected['age']
                
                fig = px.histogram(df_clean, x=age_col, nbins=20,
                                   title=f'Distribution of {age_col}')
                st.plotly_chart(fig, use_container_width=True)
            
            # If no specific columns found, show general overview
            if not any([detected['district'], detected['gender'], detected['age']]):
                st.markdown("#### 📈 General Data Overview")
                
                # Show numeric columns summary
                numeric_df = df_clean.select_dtypes(include=['number'])
                if not numeric_df.empty:
                    st.dataframe(numeric_df.describe())
                
                # Show top categories for text columns
                text_df = df_clean.select_dtypes(include=['object'])
                if not text_df.empty:
                    for col in text_df.columns[:3]:  # Show first 3 text columns
                        st.markdown(f"**Top values in {col}:**")
                        st.dataframe(text_df[col].value_counts().head(5))
        
        with tab2:
            if plan == "Premium - MWK 40,000/mo":
                st.markdown("### 🎯 SDG Progress Report")
                
                # Create SDG metrics based on available data
                sdg_data = []
                
                if malnutrition_rate is not None:
                    sdg_data.append({
                        'Indicator': 'Malnutrition (SDG 2.2)',
                        'Current': malnutrition_rate,
                        'SDG Target': 5,
                        'Gap': malnutrition_rate - 5
                    })
                
                if detected['water']:
                    water_col = detected['water']
                    if df_clean[water_col].dtype == 'object':
                        water_access = (df_clean[water_col].astype(str).str.lower().str.contains('yes|true|1|access', na=False).sum() / total) * 100
                    else:
                        water_access = df_clean[water_col].mean() * 100
                    
                    sdg_data.append({
                        'Indicator': 'Clean Water (SDG 6)',
                        'Current': water_access,
                        'SDG Target': 100,
                        'Gap': 100 - water_access
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
                        'Current': female_pct,
                        'SDG Target': 50,
                        'Gap': abs(female_pct - 50)
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
                    st.info("No SDG-related columns detected in your data.")
            else:
                st.warning("⚠️ SDG Goal analysis is available in Premium plan")
        
        with tab3:
            if plan == "Premium - MWK 40,000/mo":
                st.markdown("### 💰 Budget Calculator")
                
                # Use available data for budget calculations
                target_pop = malnourished if malnourished else int(total * 0.3)  # Assume 30% if unknown
                num_regions = len(df_clean[detected['district']].unique()) if detected['district'] else 1
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Target Population", f"{target_pop:,}")
                with col2:
                    st.metric("Regions", num_regions)
                
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
                    st.metric("ROI", f"{roi:.1f}%")
            else:
                st.warning("⚠️ Budget calculator is available in Premium plan")
        
        with tab4:
            st.markdown("### 📄 Generate Reports")
            if plan != "Free Trial":
                if st.button("📥 Generate Sample Report"):
                    st.success("✅ Report ready! (Download in production)")
                    
                    # Create summary text
                    summary = f"""
NGO IMPACT DASHBOARD - DATA SUMMARY
====================================
File: {uploaded_file.name}
Total Records: {total}
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

COLUMNS FOUND:
{', '.join(df.columns.tolist())}

DATA PREVIEW:
{df.head(10).to_string()}
                    """
                    
                    # Download as CSV
                    csv = df_clean.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="cleaned_data.csv">📥 Download Cleaned Data (CSV)</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    
                    # Download summary as txt
                    b64_summary = base64.b64encode(summary.encode()).decode()
                    href_summary = f'<a href="data:file/txt;base64,{b64_summary}" download="data_summary.txt">📥 Download Summary (TXT)</a>'
                    st.markdown(href_summary, unsafe_allow_html=True)
            else:
                st.info("📌 Reports available in Basic and Premium plans")
    
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.info("Please make sure your file is a valid CSV or Excel file.")

# Footer
st.markdown("---")
st.markdown("© 2024 Impact Data Dashboard | Built for NGOs | Works with ANY CSV/Excel file")
