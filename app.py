import streamlit as st
import pandas as pd
import plotly.express as px

# ── LOAD DATA ────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.title("Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload your chess_games.csv", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("File uploaded successfully!")
else:
    df = pd.read_csv("chess_games.csv")
    st.sidebar.info("Showing default data (888yashu888)")

df['date'] = pd.to_datetime(df['date'])
df['month'] = pd.to_datetime(df['month'])

# ── PAGE CONFIG ──────────────────────────────────────────────────────────
st.set_page_config(page_title="Chess Dashboard", page_icon="♟️", layout="wide")
st.title("♟️ Chess Dashboard ♟️")

# ── SIDEBAR ───────────────────────────────────────────────────────────────
st.sidebar.title("Filters")

# Time control filter
time_controls = ['All'] + list(df['time_class'].unique())
selected_tc = st.sidebar.selectbox("Time Control", time_controls)

# Apply filter
if selected_tc != 'All':
    df = df[df['time_class'] == selected_tc]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Total games shown:** {len(df)}")
st.sidebar.markdown(f"**Date range:** {df['date'].min().strftime('%b %Y')} → {df['date'].max().strftime('%b %Y')}")

# ── OVERVIEW + PIE CHART ─────────────────────────────────────────────────
st.header("Overview")

total_games    = len(df)
wins           = (df['outcome'] == 'Win').sum()
losses         = (df['outcome'] == 'Loss').sum()
draws          = (df['outcome'] == 'Draw').sum()
win_rate       = round((wins / total_games) * 100, 1)
best_rating    = df['my_rating'].max()
current_rating = df.sort_values('date').iloc[-1]['my_rating']

left, right = st.columns([1.5, 1])

with left:
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Games", total_games)
    c2.metric("Wins",        wins)
    c3.metric("Losses",      losses)

    c4, c5, c6 = st.columns(3)
    c4.metric("Draws",       draws)
    c5.metric("Win Rate",    f"{win_rate}%")
    c6.metric("Best Rating", best_rating)

with right:
    wld = df['outcome'].value_counts().reset_index()
    wld.columns = ['Outcome', 'Count']
    fig = px.pie(
        wld,
        names='Outcome',
        values='Count',
        color='Outcome',
        color_discrete_map={'Win': '#34a853', 'Loss': '#ea4335', 'Draw': '#fbbc04'},
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

# ── RATING OVER TIME ─────────────────────────────────────────────────────
st.header("Rating Over Time")

rating_df = df.sort_values('date')[['date', 'my_rating', 'time_class']]

fig2 = px.line(
    rating_df,
    x='date',
    y='my_rating',
    color='time_class',
    labels={'my_rating': 'Rating', 'date': 'Date', 'time_class': 'Time Control'},
)
st.plotly_chart(fig2, use_container_width=True)

# ── PERFORMANCE BY TIME CONTROL ───────────────────────────────────────────
st.header("Performance by Time Control")

tc = df.groupby(['time_class', 'outcome']).size().reset_index(name='count')

fig3 = px.bar(
    tc,
    x='time_class',
    y='count',
    color='outcome',
    barmode='group',
    color_discrete_map={'Win': '#34a853', 'Loss': '#ea4335', 'Draw': '#fbbc04'},
    labels={'time_class': 'Time Control', 'count': 'Games', 'outcome': 'Outcome'},
)
st.plotly_chart(fig3, use_container_width=True)

# ── WIN RATE BY TIME CONTROL ──────────────────────────────────────────────
st.header("Win Rate by Time Control")

tc_winrate = df.groupby('time_class').apply(
    lambda x: round((x['outcome'] == 'Win').sum() / len(x) * 100, 1)
).reset_index(name='win_rate')

fig4 = px.bar(
    tc_winrate,
    x='time_class',
    y='win_rate',
    color='time_class',
    labels={'time_class': 'Time Control', 'win_rate': 'Win Rate %'},
    text='win_rate'
)
fig4.update_traces(texttemplate='%{text}%', textposition='outside')
st.plotly_chart(fig4, use_container_width=True)


# ── OPENINGS ANALYSIS ─────────────────────────────────────────────────────
st.header("Openings Analysis")

# Top 10 most played openings
top_openings = df['opening'].value_counts().head(10).reset_index()
top_openings.columns = ['Opening', 'Games']

fig5 = px.bar(
    top_openings,
    x='Games',
    y='Opening',
    orientation='h',
    labels={'Games': 'Games Played', 'Opening': 'Opening'},
)
fig5.update_layout(yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig5, use_container_width=True)

# Win rate by opening (min 10 games)
opening_wr = df.groupby('opening').apply(
    lambda x: round((x['outcome'] == 'Win').sum() / len(x) * 100, 1)
).reset_index(name='win_rate')
opening_count = df['opening'].value_counts().reset_index()
opening_count.columns = ['opening', 'games']
opening_wr = opening_wr.merge(opening_count, on='opening')
opening_wr = opening_wr[opening_wr['games'] >= 10].sort_values('win_rate', ascending=False).head(10)

fig6 = px.bar(
    opening_wr,
    x='win_rate',
    y='opening',
    orientation='h',
    labels={'win_rate': 'Win Rate %', 'opening': 'Opening'},
    text='win_rate'
)
fig6.update_traces(texttemplate='%{text}%', textposition='outside')
fig6.update_layout(yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig6, use_container_width=True)


# ── WORST OPENINGS ────────────────────────────────────────────────────────
st.header("Weakest Openings (min 10 games)")

# rebuild from scratch with all openings
opening_all = df.groupby('opening').apply(
    lambda x: round((x['outcome'] == 'Win').sum() / len(x) * 100, 1)
).reset_index(name='win_rate')

opening_count2 = df['opening'].value_counts().reset_index()
opening_count2.columns = ['opening', 'games']
opening_all = opening_all.merge(opening_count2, on='opening')
opening_all = opening_all[opening_all['games'] >= 10]

worst_openings = opening_all.sort_values('win_rate', ascending=True).head(10)

fig7 = px.bar(
    worst_openings,
    x='win_rate',
    y='opening',
    orientation='h',
    color='win_rate',
    color_continuous_scale='Reds_r',
    labels={'win_rate': 'Win Rate %', 'opening': 'Opening'},
    text='win_rate'
)
fig7.update_traces(texttemplate='%{text}%', textposition='outside')
fig7.update_layout(yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig7, use_container_width=True)

# ── OPPONENT ANALYSIS ─────────────────────────────────────────────────────
st.header("Opponent Analysis")

# Highest rated opponent you beat
best_win = df[df['outcome'] == 'Win'].sort_values('opp_rating', ascending=False).iloc[0]

# Win rate vs higher rated vs lower rated
df['opp_stronger'] = df['opp_rating'] > df['my_rating']
stronger = df[df['opp_stronger'] == True]
weaker   = df[df['opp_stronger'] == False]

wr_vs_stronger = round((stronger['outcome'] == 'Win').sum() / len(stronger) * 100, 1)
wr_vs_weaker   = round((weaker['outcome'] == 'Win').sum() / len(weaker) * 100, 1)

col1, col2, col3 = st.columns(3)
col1.metric("Highest Rated Opponent Beaten", best_win['opp_rating'])
col2.metric("Win Rate vs Stronger Opponents", f"{wr_vs_stronger}%")
col3.metric("Win Rate vs Weaker Opponents",   f"{wr_vs_weaker}%")

# Average opponent rating over time by month
avg_opp = df.groupby('month')['opp_rating'].mean().reset_index()
avg_opp.columns = ['month', 'avg_opp_rating']

fig8 = px.line(
    avg_opp,
    x='month',
    y='avg_opp_rating',
    labels={'month': 'Month', 'avg_opp_rating': 'Avg Opponent Rating'},
)
st.plotly_chart(fig8, use_container_width=True)

# ── ACCURACY ANALYSIS ─────────────────────────────────────────────────────
st.header("Accuracy Analysis")

acc_df = df[df['accuracy'].notna()]

avg_acc        = round(acc_df['accuracy'].mean(), 1)
avg_acc_wins   = round(acc_df[acc_df['outcome'] == 'Win']['accuracy'].mean(), 1)
avg_acc_losses = round(acc_df[acc_df['outcome'] == 'Loss']['accuracy'].mean(), 1)

col1, col2, col3 = st.columns(3)
col1.metric("Avg Accuracy",        f"{avg_acc}%")
col2.metric("Avg Accuracy (Wins)", f"{avg_acc_wins}%")
col3.metric("Avg Accuracy (Loss)", f"{avg_acc_losses}%")

# Accuracy trend over time
acc_trend = acc_df.groupby('month')['accuracy'].mean().reset_index()
acc_trend.columns = ['month', 'avg_accuracy']

fig9 = px.line(
    acc_trend,
    x='month',
    y='avg_accuracy',
    labels={'month': 'Month', 'avg_accuracy': 'Avg Accuracy %'},
)
st.plotly_chart(fig9, use_container_width=True)

# ── TIME PATTERNS ─────────────────────────────────────────────────────────
st.header("Time Patterns")

# Games per month
games_per_month = df.groupby('month').size().reset_index(name='games')

fig10 = px.bar(
    games_per_month,
    x='month',
    y='games',
    labels={'month': 'Month', 'games': 'Games Played'},
)
st.plotly_chart(fig10, use_container_width=True)

# Best and worst month by win rate
monthly_wr = df.groupby('month').apply(
    lambda x: round((x['outcome'] == 'Win').sum() / len(x) * 100, 1)
).reset_index(name='win_rate')

best_month  = monthly_wr.loc[monthly_wr['win_rate'].idxmax()]
worst_month = monthly_wr.loc[monthly_wr['win_rate'].idxmin()]

col1, col2 = st.columns(2)
col1.metric("Best Month",  f"{best_month['month'].strftime('%b %Y')}",  f"{best_month['win_rate']}% win rate")
col2.metric("Worst Month", f"{worst_month['month'].strftime('%b %Y')}", f"{worst_month['win_rate']}% win rate")