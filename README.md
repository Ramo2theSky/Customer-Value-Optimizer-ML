# Customer Value Optimizer (CVO) v2.0

## 🎯 Project Overview

**Customer Value Optimizer (CVO)** is an advanced Machine Learning system developed for **PLN Icon+ Marketing Planning & Analysis Division** to identify upsell and cross-sell opportunities among existing customers.

### Key Features

✅ **Supervised ML Models** (XGBoost & Random Forest)  
✅ **Dual 2×2 Strategic Matrices** (Revenue×Bandwidth, Revenue×Tenure)  
✅ **Customer Lifetime Value (CLV) Prediction**  
✅ **Interactive Next.js Dashboard**  
✅ **Comprehensive Excel Reports**  
✅ **Executive Summary with ROI Projections**

---

## 📁 Project Structure

```
D:\ICON+\
│
├── cvo_ml_engine.py              # Main ML pipeline (Python)
├── Data Sampel Machine Learning.xlsx  # Input data
│
├── cvo-dashboard/                # Next.js Dashboard
│   ├── app/                      # Next.js app directory
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Main dashboard
│   │   └── globals.css          # Global styles
│   ├── components/              # React components
│   │   ├── SummaryCards.tsx     # KPI cards
│   │   ├── StrategicMatrix.tsx  # 2x2 matrices
│   │   ├── PropensityChart.tsx  # ML predictions chart
│   │   ├── OpportunitiesTable.tsx # Top opportunities
│   │   └── ModelMetrics.tsx     # Model performance
│   ├── data/                    # Dashboard data
│   │   └── sample-data.json     # Sample data
│   ├── lib/                     # Utilities
│   │   └── utils.ts             # Helper functions
│   └── package.json             # Dependencies
│
└── reports/                      # Generated Excel reports
    ├── CVO_Master_Report.xlsx
    ├── CVO_Upsell_Opportunities.xlsx
    ├── CVO_Crosssell_Opportunities.xlsx
    ├── CVO_Strategic_Matrices.xlsx
    ├── CVO_Top_50_Opportunities.xlsx
    └── Executive_Summary.txt

└── dashboard_data/               # JSON data for dashboard
    ├── summary_metrics.json
    ├── matrix1_distribution.json
    ├── matrix2_distribution.json
    ├── top_opportunities.json
    ├── customer_scatter_data.json
    └── thresholds.json
```

---

## 🚀 Quick Start Guide

### Step 1: Run the ML Pipeline

```bash
# Navigate to the project directory
cd D:\ICON+

# Install required Python packages
pip install pandas numpy scikit-learn xgboost openpyxl matplotlib seaborn

# Run the ML pipeline
python cvo_ml_engine.py
```

This will:
- Load and clean your data
- Train ML models (XGBoost & Random Forest)
- Generate strategic matrices
- Create Excel reports in `reports/` folder
- Generate JSON data for dashboard in `dashboard_data/` folder

**🎯 The script automatically detects your data file:**
- Priority 1: `Data Penuh Pelanggan Aktif.xlsx` (Full data)
- Priority 2: `Data Sampel Machine Learning.xlsx` (Sample data)
- Priority 3: Any other .xlsx/.csv file found

### 📊 Running with Full Sales Data

To analyze your complete customer database:

1. **Ensure your full data file is in the folder:**
   ```
   D:\ICON+\
   ├── cvo_ml_engine.py
   ├── Data Penuh Pelanggan Aktif.xlsx   ← Full dataset (50k+ customers)
   └── ...
   ```

2. **Run the pipeline** (same command):
   ```bash
   python cvo_ml_engine.py
   ```

3. **For large datasets (50k+ rows):**
   - Processing time: 2-5 minutes
   - Memory needed: 2-4 GB RAM
   - The script auto-optimizes memory usage

📖 **See `RUNNING_FULL_DATA_GUIDE.md` for detailed instructions on handling large datasets.**

### Step 2: Launch the Dashboard

```bash
# Navigate to dashboard directory
cd cvo-dashboard

# Install dependencies
npm install

# Run development server
npm run dev

# Open browser at http://localhost:3000
```

### Step 3: Build for Production

```bash
# Build static site
npm run build

# The built files will be in the `dist/` folder
# You can deploy these to any static hosting service
```

---

## 🤖 Machine Learning Pipeline

### Models Implemented

1. **Upsell Prediction Model** (XGBoost Classifier)
   - Predicts probability of successful bandwidth upgrades
   - Features: Revenue, bandwidth, tenure, value score
   - Target: Customers in "Sniper Zone" (High BW, Low Revenue)

2. **Cross-sell Prediction Model** (Random Forest Classifier)
   - Predicts readiness for additional products
   - Features: Product diversity, contract length, segment
   - Target: Customers in "Risk Area" (High Revenue, Low BW)

3. **CLV Prediction Model** (Gradient Boosting Regressor)
   - Predicts 12-month Customer Lifetime Value
   - Features: Historical revenue, tenure, growth patterns
   - Output: Rupiah value projection

### Model Performance

The pipeline automatically evaluates models and reports:
- **Accuracy**: Overall prediction correctness
- **ROC-AUC**: Ability to distinguish between classes (0.8+ = excellent)
- **Precision**: Accuracy of positive predictions
- **Recall**: Coverage of actual positives
- **MAE/MAPE**: For CLV prediction accuracy

---

## 📊 Strategic Matrices

### Matrix 1: Revenue vs Bandwidth Usage

|                    | High Bandwidth | Low Bandwidth |
|--------------------|----------------|---------------|
| **High Revenue**   | 🌟 STAR CLIENT<br>RETENTION | 🎯 RISK AREA<br>CROSS-SELL |
| **Low Revenue**    | 🔫 SNIPER ZONE<br>UPSELL | 🥚 INCUBATOR<br>NURTURE |

### Matrix 2: Revenue vs Tenure

|                    | Long Tenure | Short Tenure |
|--------------------|-------------|--------------|
| **High Revenue**   | 💎 CHAMPION<br>ADVOCACY | ⚡ HIGH POTENTIAL<br>LOCK-IN |
| **Low Revenue**    | 🎁 LOYAL<br>GRADUAL UPSELL | 🌱 NEWBIE<br>EDUCATION |

---

## 📈 Business Value

### Revenue Opportunity Calculation

The system calculates potential revenue impact:

- **Upsell Potential**: 30% revenue increase for converted customers
- **Cross-sell Potential**: 25% revenue increase for converted customers
- **Conservative Scenario** (20% conversion): Significant ROI
- **Optimistic Scenario** (40% conversion): Exceptional ROI

### ROI Projections

Generated automatically in Executive Summary:
```
Conservative (20% conversion): Rp XXX,XXX,XXX,XXX
Moderate (30% conversion): Rp XXX,XXX,XXX,XXX  
Optimistic (40% conversion): Rp XXX,XXX,XXX,XXX
```

---

## 🎨 Dashboard Features

### Interactive Components

1. **Summary Cards**
   - Total customers analyzed
   - Total revenue
   - High-propensity upsell count
   - High-propensity cross-sell count
   - Total opportunity value
   - Model accuracy scores

2. **Strategic Matrices**
   - Interactive 2×2 grids
   - Clickable quadrants
   - Customer distribution percentages
   - Revenue breakdowns
   - Strategic recommendations

3. **Propensity Charts**
   - Distribution of prediction scores
   - High/Medium/Low priority buckets
   - Visual identification of top targets

4. **Opportunities Table**
   - Sortable by any column
   - Top 20 upsell opportunities
   - Top 20 cross-sell opportunities
   - Propensity scores and potential revenue
   - Customer details

5. **Model Performance**
   - Accuracy metrics
   - ROC-AUC scores
   - Feature importance
   - Confidence indicators

### Design Features

- **PLN Icon+ Branding**: Blue (#0047AB) and Gold (#FFD700) theme
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Animations**: Smooth transitions and hover effects
- **Professional UI**: Suitable for executive presentations
- **Export Ready**: Can be exported as static HTML

---

## 📋 Generated Reports

### Excel Reports

1. **CVO_Master_Report.xlsx**
   - All customers with predictions
   - Sorted by upsell propensity
   - Complete feature set

2. **CVO_Upsell_Opportunities.xlsx**
   - Customers with upsell propensity > 50%
   - Ranked by revenue potential
   - Ready for sales team

3. **CVO_Crosssell_Opportunities.xlsx**
   - Customers with cross-sell propensity > 50%
   - Ranked by revenue potential
   - Product recommendations

4. **CVO_Strategic_Matrices.xlsx**
   - Separate sheets per quadrant
   - Summary statistics
   - Strategic breakdowns

5. **CVO_Top_50_Opportunities.xlsx**
   - Highest priority targets
   - Combined upsell + cross-sell potential
   - Quick wins list

### Executive Summary

**Executive_Summary.txt** includes:
- Key business metrics
- Strategic matrix distributions
- ML model performance
- Top 10 opportunities (upsell & cross-sell)
- Recommended action plan
- ROI projections (conservative to optimistic)
- Technical notes

---

## 🔧 Customization

### Modifying Thresholds

Edit the thresholds in `cvo_ml_engine.py`:

```python
# In create_strategic_matrices() method
self.thresholds['median_revenue'] = df['revenue'].median()
self.thresholds['median_bandwidth'] = df['bandwidth_mbps'].median()
```

### Adding New Features

1. Add feature engineering in `engineer_features()` method
2. Include new features in `prepare_ml_data()` method
3. Retrain models by running the pipeline

### Customizing Dashboard

Edit components in `cvo-dashboard/components/`:
- Colors: Modify Tailwind classes
- Layout: Edit component structure
- Data: Update JSON files in `data/` folder

---

## 📊 Data Requirements

### Required Columns

The pipeline expects these columns (Indonesian naming):

- `namaPelanggan` - Customer name
- `hargaPelanggan` - Current revenue/price
- `hargaPelangganLalu` - Previous revenue (optional)
- `bandwidth` - Bandwidth usage
- `Lama_Langganan` - Tenure in months
- `segmenIcon` - Customer segment
- `WILAYAH` - Region
- `statusLayanan` - Service status

### Data Quality

The pipeline automatically:
- Cleans business titles from customer names
- Converts currency formats (removes Rp, dots)
- Standardizes bandwidth units (Mbps)
- Filters to active customers only
- Removes duplicates

---

## 🎓 For Non-Technical Stakeholders

### What is Machine Learning?

Machine Learning (ML) is a type of artificial intelligence that allows computers to learn patterns from data and make predictions. In this project:

- **Training**: The computer studies historical customer data to find patterns
- **Prediction**: It applies these patterns to predict which customers are most likely to buy more
- **Confidence**: Each prediction comes with a probability score (0-100%)

### How to Use the Results

1. **Start with Excel Reports**: Open `CVO_Top_50_Opportunities.xlsx`
2. **Focus on High Propensity**: Target customers with >70% scores first
3. **Follow the Strategy**: Each customer has a recommended approach
4. **Track Conversions**: Update the data and re-run monthly
5. **Review Dashboard**: Share interactive dashboard with management

### Interpreting Scores

- **Upsell Propensity 80%**: Customer has 80% probability of upgrading bandwidth
- **Cross-sell Propensity 65%**: Customer has 65% probability of buying additional products
- **CLV Rp 50M**: Predicted to generate Rp 50 million over next 12 months

---

## 🔒 Security & Privacy

- All data processing is local (no cloud uploads)
- No customer PII is exposed in reports
- Dashboard can be run offline
- Excel files can be password-protected before sharing

---

## 📞 Support

### For Technical Issues

1. Check Python packages are installed: `pip list | grep -E "pandas|numpy|scikit|xgboost"`
2. Verify data file format (Excel .xlsx or CSV)
3. Check console for error messages
4. Ensure sufficient RAM for large datasets (>100k rows)

### For Business Questions

1. Review `Executive_Summary.txt` first
2. Check strategic matrix logic in code comments
3. Understand that predictions are probabilities, not guarantees
4. Use conservative ROI estimates for planning

---

## 🎉 Success Metrics

After implementing CVO, track these metrics:

- **Conversion Rate**: % of predicted opportunities that convert
- **Revenue Increase**: Actual additional revenue generated
- **Model Accuracy**: How often predictions are correct
- **Sales Efficiency**: Time saved by focusing on high-probability targets
- **Customer Satisfaction**: Ensure upselling doesn't harm relationships

---

## 🚀 Future Enhancements

Potential improvements for v3.0:

- [ ] Integration with CRM systems
- [ ] Real-time prediction API
- [ ] Automated email campaigns
- [ ] Customer churn prediction
- [ ] A/B testing framework
- [ ] Natural language insights
- [ ] Mobile app for sales teams

---

## 📄 License

Internal use only - PLN Icon+ Marketing Planning & Analysis Division

---

## 🏆 Credits

**Developed by**: Computer Science Intern  
**Division**: Marketing Planning & Analysis, PLN Icon+  
**Date**: February 2026  
**Version**: 2.0  

**Technologies Used**:
- Python (Pandas, Scikit-learn, XGBoost)
- Next.js, React, TypeScript
- Tailwind CSS, Recharts
- Machine Learning (Classification & Regression)

---

## 📚 Additional Resources

### Understanding the ML Models

**XGBoost**: Extreme Gradient Boosting - An advanced algorithm that builds models sequentially, correcting errors at each step. Excellent for tabular data.

**Random Forest**: An ensemble of decision trees that vote on the final prediction. Robust and interpretable.

**Gradient Boosting**: Builds models in a stage-wise fashion, optimizing a loss function. Great for regression tasks like CLV prediction.

### Business Strategy Tips

1. **Sniper Zone First**: These customers already use bandwidth heavily but pay less - easiest upsell
2. **Protect Star Clients**: Don't push too hard on already high-value customers
3. **Educate Incubators**: Build trust before any sales attempt
4. **Track Everything**: Monitor which predictions convert to improve models

---

**🎯 Ready to maximize customer value! Run the pipeline and start converting opportunities.**
