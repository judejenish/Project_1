
CREATE DATABASE scrape_db;


USE scrape_db;


CREATE TABLE movies (
    movie_name VARCHAR(1000),
    year INT,
    duration INT,
    rating FLOAT,
    vote_count INT,
    genre VARCHAR(100)
);

SET SQL_SAFE_UPDATES = 0;
DELETE FROM movies;
SET SQL_SAFE_UPDATES = 1; 
SELECT distinct(duration)  FROM movies where genre='Unknown';
 where vote_count <100000;
