import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Earthquake Analytics Dashboard",
    page_icon="🌍",
    layout="centered"
)

# ---------------------------------------------------------
# PROFESSIONAL UI STYLE
# ---------------------------------------------------------

st.markdown("""
<style>

.stApp{
    background: linear-gradient(180deg,#0f172a,#020617);
    color:white;
}

h1{
    text-align:center;
    font-size:48px !important;
    font-weight:800;
}

.subtitle{
    text-align:center;
    color:#cbd5e1;
    margin-bottom:30px;
}

/* dropdown center */
div[data-baseweb="select"]{
    max-width:600px;
    margin:auto;
}

/* dropdown style */
.stSelectbox div div{
    background-color:#f1f5f9;
    border-radius:10px;
}

/* center button */
div.stButton{
    display:flex;
    justify-content:center;
}

/* button style */
div.stButton > button{
    background:#1e293b;
    border:2px solid #ef4444;
    color:white;
    border-radius:10px;
    height:45px;
    width:170px;
    font-weight:bold;
}

div.stButton > button:hover{
    background:#334155;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

TIDB_HOST = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
TIDB_PORT = 4000
TIDB_USER = "31PZhzCNeELY4jm.root"
TIDB_PASSWORD = "O8N8mrUbCKtnPi7G"
TIDB_DATABASE = "earthquake"

SSL_CA_PATH = "/content/isrgrootx1 (3).pem"

engine = create_engine(
    f"mysql+pymysql://{TIDB_USER}:{TIDB_PASSWORD}@{TIDB_HOST}:{TIDB_PORT}/{TIDB_DATABASE}",
    connect_args={"ssl": {"ca": SSL_CA_PATH}},
)

def run_query(sql):
    return pd.read_sql(sql, engine)

# ---------------------------------------------------------
# QUESTIONS
# ---------------------------------------------------------

QUESTIONS = {

"1. Top 10 strongest earthquakes":
"SELECT * FROM earthquake ORDER BY mag DESC LIMIT 10;",

"2. Top 10 deepest earthquake":
"SELECT * FROM earthquake ORDER BY depth_km DESC LIMIT 10;",

"3. Shallow earthquake < 50km & mag > 7.5":
"SELECT * FROM earthquake WHERE depth_km < 50 AND mag > 7.5;",

"4. Average depth per country":
"""
SELECT country, AVG(depth_km) AS avg_depth
FROM earthquake GROUP BY country ORDER BY avg_depth DESC;
""",

"5. Average magnitude by magType":
"""
SELECT magType, AVG(mag) AS avg_mag
FROM earthquake GROUP BY magType ORDER BY avg_mag DESC;
""",

"6. Year with most earthquake":
"""
SELECT year, COUNT(*) AS total
FROM earthquake GROUP BY year
ORDER BY total DESC LIMIT 1;
""",

"7. Month with highest earthquake":
"""
SELECT year, month, COUNT(*) AS total
FROM earthquake GROUP BY year, month
ORDER BY total DESC LIMIT 1;
""",

"8. Most common day of week":
"""
SELECT day_of_week, COUNT(*) AS total
FROM earthquake GROUP BY day_of_week ORDER BY total DESC;
""",

"9. Earthquakes per hour":
"""
SELECT hour, COUNT(*) AS total
FROM earthquake GROUP BY hour ORDER BY hour;
""",

"10. Most active reporting network":
"""
SELECT net, COUNT(*) AS total
FROM earthquake GROUP BY net ORDER BY total DESC LIMIT 1;
""",

"11. Top 5 locations with highest casualties":
"""
SELECT place, SUM(casualties) AS total
FROM earthquake GROUP BY place
ORDER BY total DESC LIMIT 5;
""",

"12. Total economic loss per country":
"""
SELECT country, SUM(economic_loss) AS total
FROM earthquake GROUP BY country ORDER BY total DESC;
""",

"13. Avg economic loss by alert level":
"""
SELECT alert, AVG(economic_loss) AS avg_loss
FROM earthquake GROUP BY alert ORDER BY avg_loss DESC;
""",

"14. Reviewed vs Automatic":
"""
SELECT status, COUNT(*) AS total
FROM earthquake GROUP BY status;
""",

"15. Earthquake type count":
"""
SELECT type, COUNT(*) AS total
FROM earthquake GROUP BY type ORDER BY total DESC;
""",

"16. Data type counts":
"""
SELECT
SUM(CASE WHEN types LIKE '%dyfi%' THEN 1 END) AS dyfi_count,
SUM(CASE WHEN types LIKE '%shakemap%' THEN 1 END) AS shakemap_count,
COUNT(*) AS total_events
FROM earthquake;
""",

"17. Average RMS and gap per country":
"""
SELECT country, AVG(rms) AS avg_rms, AVG(gap) AS avg_gap
FROM earthquake GROUP BY country ORDER BY avg_rms DESC;
""",

"18. Events with nst > 50":
"SELECT * FROM earthquake WHERE nst > 50;",

"19. Tsunami events per year":
"""
SELECT year, COUNT(*) AS tsunami_events
FROM earthquake WHERE tsunami=1 GROUP BY year;
""",

"20. Earthquake per alert level":
"""
SELECT alert, COUNT(*) AS total
FROM earthquake GROUP BY alert;
""",

"21. Top 5 countries by avg magnitude (past 10 years)":
"""
SELECT country, AVG(mag) AS avg_mag, COUNT(*) AS events
FROM earthquake
WHERE year >= YEAR(CURDATE()) - 10
GROUP BY country HAVING events >= 10
ORDER BY avg_mag DESC LIMIT 5;
""",

"22. Countries with shallow & deep same month":
"""
SELECT country, year, month
FROM earthquake
GROUP BY country, year, month
HAVING SUM(CASE WHEN depth_category='shallow' THEN 1 END) > 0
AND SUM(CASE WHEN depth_category='deep' THEN 1 END) > 0;
""",

"23. Year-over-year growth":
"""
WITH y AS (
 SELECT year, COUNT(*) total FROM earthquake GROUP BY year
),
g AS (
 SELECT year, total,
 LAG(total) OVER (ORDER BY year) AS prev_total
 FROM y
)
SELECT year, total, prev_total,
((total - prev_total) / prev_total) * 100 AS growth_rate
FROM g;
""",

"24. Top 3 most active countries":
"""
SELECT country, COUNT(*) AS total, AVG(mag) AS avg_mag,
COUNT(*) * AVG(mag) AS score
FROM earthquake GROUP BY country ORDER BY score DESC LIMIT 3;
""",

"25. Avg depth near equator":
"""
SELECT country, AVG(depth_km) AS avg_depth
FROM earthquake WHERE latitude BETWEEN -5 AND 5
GROUP BY country ORDER BY avg_depth DESC;
""",

"26. Shallow to deep ratio":
"""
SELECT country,
SUM(CASE WHEN depth_category='shallow' THEN 1 END) AS shallow,
SUM(CASE WHEN depth_category='deep' THEN 1 END) AS deep
FROM earthquake GROUP BY country;
""",

"27. Magnitude difference (tsunami vs non)":
"""
SELECT
AVG(CASE WHEN tsunami=1 THEN mag END) AS tsunami_mag,
AVG(CASE WHEN tsunami=0 THEN mag END) AS non_tsunami_mag
FROM earthquake;
""",

"28. Worst reliability":
"SELECT * FROM earthquake ORDER BY rms DESC, gap DESC LIMIT 50;",

"29. Consecutive quakes within 1 hour":
"""
SELECT e1.id, e2.id, e1.country
FROM earthquake e1
JOIN earthquake e2
ON e2.time > e1.time
AND TIMESTAMPDIFF(MINUTE, e1.time, e2.time) <= 60
AND e1.country = e2.country
LIMIT 100;
""",

"30. Countries with most deep quakes":
"""
SELECT country, COUNT(*) AS deep_count
FROM earthquake WHERE depth_km > 300
GROUP BY country ORDER BY deep_count DESC LIMIT 10;
"""
}

# ---------------------------------------------------------
# UI
# ---------------------------------------------------------

st.markdown("# 🌍 Earthquake Analytics Dashboard (TiDB)")
st.markdown('<p class="subtitle">Select a question to view the results below</p>', unsafe_allow_html=True)

selected_question = st.selectbox(
    "Choose a question:",
    list(QUESTIONS.keys())
)

if st.button("Run Query"):

    try:
        df = run_query(QUESTIONS[selected_question])

        st.success("Query executed successfully!")

        st.markdown("---")
        st.subheader("📊 Query Result")

        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
