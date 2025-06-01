import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import pymysql

with pymysql.connect(
    host='localhost',
    user='root',
    password='root',
    database='scrape_db',
    port=3306
) as connection:
    query = "SELECT movie_name AS `Movie Name`, year AS `Year`, duration AS `Duration`, rating AS `Rating`, vote_count AS `Vote Count`, genre AS `Genre` FROM movies"
    df = pd.read_sql(query, connection)

st.set_page_config(page_title="IMDB Web Scraping", layout="wide")

page = st.sidebar.selectbox("Choose a Page", ["IMDB Web Scraping", "Interactive Filtering", "Interactive Visualizations"])

if page == "IMDB Web Scraping":
    st.title("IMDB Web Scraping")
   
elif page == "Interactive Filtering":
    st.title("Interactive Filtering")

    with st.form("filter_form"):
        with pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='scrape_db',
            port=3306
        ) as connection:
            genre_df = pd.read_sql("SELECT DISTINCT genre FROM movies WHERE genre IS NOT NULL", connection)
        genre_options = genre_df['genre'].tolist()
        selected_genres = st.multiselect("Select Genre(s)", genre_options, default=[])

        rating_options = ["None"] + [f"{i}+" for i in range(1, 11)]
        selected_rating = st.selectbox("Select Minimum Rating", rating_options)

        vote_options = ["None", "< 1,000", "1,000 – 10,000", "10,001 – 50,000", "50,001 – 100,000", "> 100,000"]
        selected_votes = st.selectbox("Select Vote Count", vote_options)

        duration_options = ["None", "< 1 hour", "1–2 hours", "2–3 hours", "> 3 hours"]
        selected_duration = st.selectbox("Select Duration", duration_options)

        show = st.form_submit_button("Show")

    if show:
        query = "SELECT movie_name AS `Movie Name`, year AS `Year`, duration AS `Duration`, rating AS `Rating`, vote_count AS `Vote Count`, genre AS `Genre` FROM movies WHERE 1=1"

        if selected_genres:
            genre_str = ", ".join([f"'{g}'" for g in selected_genres])
            query += f" AND genre IN ({genre_str})"

        if selected_rating != "None":
            rating_val = float(selected_rating.replace("+", ""))
            query += f" AND rating >= {rating_val}"

        if selected_votes != "None":
            if selected_votes == "< 1,000":
                query += " AND vote_count < 1000"
            elif selected_votes == "1,000 – 10,000":
                query += " AND vote_count >= 1000 AND vote_count <= 10000"
            elif selected_votes == "10,001 – 50,000":
                query += " AND vote_count >= 10001 AND vote_count <= 50000"
            elif selected_votes == "50,001 – 100,000":
                query += " AND vote_count >= 50001 AND vote_count <= 100000"
            elif selected_votes == "> 100,000":
                query += " AND vote_count > 100000"

        if selected_duration != "None":
            if selected_duration == "< 1 hour":
                query += " AND duration < 60"
            elif selected_duration == "1–2 hours":
                query += " AND duration >= 60 AND duration <= 119"
            elif selected_duration == "2–3 hours":
                query += " AND duration >= 120 AND duration <= 179"
            elif selected_duration == "> 3 hours":
                query += " AND duration >= 180"

        with pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='scrape_db',
            port=3306
        ) as connection:
            filtered_df = pd.read_sql(query, connection)
        st.dataframe(filtered_df)
        st.markdown(f"Showing {len(filtered_df)} movies matching the options.")
        
elif page == "Interactive Visualizations":
    st.title("Interactive Visualizations")

    vis_option = st.selectbox("Select Visualization", [
        "Top 10 Movies by Rating and Voting Counts",
        "Genre Distribution",
        "Average Duration by Genre",
        "Voting Trends by Genre",
        "Rating Distribution",
        "Genre-Based Rating Leaders",
        "Most Popular Genres by Voting",
        "Duration Extremes",
        "Ratings by Genre",
        "Correlation Analysis"
    ])
    if vis_option == "Top 10 Movies by Rating and Voting Counts":
        st.subheader("Top 10 Movies by Rating and Voting Counts")
        top_rated = df.sort_values(by=['Rating', 'Vote Count'], ascending=[False, False]).reset_index().head(10)
        st.dataframe(top_rated[['Movie Name', 'Rating', 'Vote Count', 'Genre']])

    elif vis_option == "Genre Distribution":
        st.subheader("Genre Distribution")
        genre_counts = df['Genre'].value_counts().reset_index()
        genre_counts.columns = ['Genre', 'Count']
        fig = px.bar(genre_counts, x='Genre', y='Count', title='Number of Movies per Genre')
        st.plotly_chart(fig)

    elif vis_option == "Average Duration by Genre":
        st.subheader("Average Duration by Genre")
        avg_duration = df.groupby('Genre')['Duration'].mean().sort_values().reset_index()
        fig = px.bar(avg_duration, x='Duration', y='Genre', orientation='h', title='Average Duration per Genre')
        st.plotly_chart(fig)

    elif vis_option == "Voting Trends by Genre":
        st.subheader("Average Voting Counts by Genre")
        avg_votes = df.groupby('Genre')['Vote Count'].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(avg_votes, x='Genre', y='Vote Count', title='Average Vote Count per Genre')
        st.plotly_chart(fig)

    elif vis_option == "Rating Distribution":
        st.subheader("Distribution of Movie Ratings")
        fig = px.histogram(df, x='Rating', nbins=20, title='Rating Distribution')
        st.plotly_chart(fig)

    elif vis_option == "Genre-Based Rating Leaders":
        st.subheader("Top-Rated Movie in Each Genre")
        top_by_genre = df.sort_values(['Genre', 'Rating'], ascending=[True, False]).drop_duplicates('Genre')
        st.dataframe(top_by_genre[['Genre', 'Movie Name', 'Rating']])

    elif vis_option == "Most Popular Genres by Voting":
        st.subheader("Genres with Highest Total Vote Counts")
        total_votes = df.groupby('Genre')['Vote Count'].sum().reset_index()
        fig = px.pie(total_votes, names='Genre', values='Vote Count', title='Total Vote Count by Genre')
        st.plotly_chart(fig)

    elif vis_option == "Duration Extremes":
        st.subheader("Shortest and Longest Movies")
        with pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='scrape_db',
            port=3306
        ) as connection:
            shortest_query = """
                SELECT movie_name AS `Movie Name`, duration AS `Duration`
                FROM movies
                WHERE duration = (SELECT MIN(duration) FROM movies)
            """
            longest_query = """
                SELECT movie_name AS `Movie Name`, duration AS `Duration`
                FROM movies
                WHERE duration = (SELECT MAX(duration) FROM movies)
            """
            shortest = pd.read_sql(shortest_query, connection)
            longest = pd.read_sql(longest_query, connection)
        st.write("Shortest Movie:")
        st.dataframe(shortest)
        st.write("Longest Movie:")
        st.dataframe(longest)

    elif vis_option == "Ratings by Genre":
        st.subheader("Average Ratings by Genre")
        genre_rating = df.groupby('Genre')['Rating'].mean().reset_index()
        fig = px.density_heatmap(genre_rating, x='Genre', y='Rating', title='Average Rating per Genre')
        st.plotly_chart(fig)

    elif vis_option == "Correlation Analysis":
        st.subheader("Ratings vs. Vote Count Correlation")
        fig = px.scatter(df, x='Vote Count', y='Rating', color='Genre', title='Rating vs. Vote Count')
        st.plotly_chart(fig)
