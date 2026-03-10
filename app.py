import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from io import BytesIO
import datetime

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

# Main content
uploaded_file = st.file_uploader("📤 Upload your survey data (CSV or Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Read file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.success(f"✅ Loaded {len(df)} records from {uploaded_file.name}")
    
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
    
    # Calculate metrics
    total = len(df_clean)
    
    if 'nutrition_status' in df_clean.columns:
        malnourished = len(df_clean[df_clean['nutrition_status'].str.contains('Malnourished', case=False, na=False)])
        malnutrition_rate = (malnourished / total) * 100
    else:
        st.warning("⚠️ No 'nutrition_status' column found. Using sample data.")
        malnutrition_rate = 50.0
        malnourished = 250
    
    if 'district' in df_clean.columns:
        districts = len(df_clean['district'].unique())
    else:
        districts = 3
    
    # Key metrics
    st.markdown("## 📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Children", f"{total:,}")
    with col2:
        st.metric("Malnutrition Rate", f"{malnutrition_rate:.1f}%")
    with col3:
        st.metric("Malnourished", f"{malnourished:,}")
    with col4:
        st.metric("Districts", districts)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Analysis", "🎯 SDG Goals", "💰 Budget", "📄 Reports"])
    
    with tab1:
        st.markdown("### 📊 District Analysis")
        
        if 'district' in df_clean.columns and 'nutrition_status' in df_clean.columns:
            district_data = df_clean.groupby('district')['nutrition_status'].apply(
                lambda x: (x.str.contains('Malnourished', case=False).sum() / len(x)) * 100
            ).reset_index()
            district_data.columns = ['District', 'Malnutrition Rate']
            
            fig = px.bar(district_data, x='District', y='Malnutrition Rate',
                         title='Malnutrition Rate by District',
                         color='Malnutrition Rate', color_continuous_scale='reds')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if plan == "Premium - MWK 40,000/mo":
            st.markdown("### 🎯 SDG Progress Report")
            
            water_access = len(df_clean[df_clean['has_clean_water'] == 'Yes']) / total * 100 if 'has_clean_water' in df_clean.columns else 60
            gender_balance = len(df_clean[df_clean['gender'] == 'Female']) / total * 100 if 'gender' in df_clean.columns else 50
            
            sdg_data = pd.DataFrame({
                'Indicator': ['Malnutrition Rate', 'Clean Water Access', 'Gender Balance'],
                'Current': [malnutrition_rate, water_access, gender_balance],
                'SDG Target': [5, 100, 50]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Current', x=sdg_data['Indicator'], y=sdg_data['Current'],
                                 marker_color='steelblue'))
            fig.add_trace(go.Bar(name='SDG Target', x=sdg_data['Indicator'], y=sdg_data['SDG Target'],
                                 marker_color='green'))
            fig.update_layout(title='Progress Towards SDG Goals', barmode='group',
                             yaxis_title='Percentage (%)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ SDG Goal analysis is available in Premium plan")
    
    with tab3:
        if plan == "Premium - MWK 40,000/mo":
            st.markdown("### 💰 Budget Calculator")
            
            basic_cost = malnourished * 45000
            comprehensive_cost = (total * 15000) + (malnourished * 45000) + (districts * 5000000)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Basic Intervention", f"MWK {basic_cost:,.0f}")
            with col2:
                st.metric("Comprehensive", f"MWK {comprehensive_cost:,.0f}", 
                         delta=f"Save MWK {basic_cost - comprehensive_cost:,.0f}")
            
            roi = ((malnourished * 0.6 * 45000) / comprehensive_cost) * 100
            st.metric("ROI", f"{roi:.1f}%")
        else:
            st.warning("⚠️ Budget calculator is available in Premium plan")
    
    with tab4:
        st.markdown("### 📄 Generate Reports")
        if plan != "Free Trial":
            if st.button("📥 Generate Sample Report"):
                st.success("✅ Report ready! (Download in production)")
                csv = df_clean.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="cleaned_data.csv">📥 Download Cleaned Data</a>'
                st.markdown(href, unsafe_allow_html=True)
        else:
            st.info("📌 Reports available in Basic and Premium plans")

st.markdown("---")
st.markdown("© 2024 Impact Data Dashboard | Built for NGOs")
