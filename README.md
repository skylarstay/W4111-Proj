# W4111-proj
# PostgreSQL Account Information

- **Username:** yc4387
- **Password:** 221558

# Web Application URL

[Link to Web Application](URL_of_Web_Application)

# Implementation Description

We have successfully executed all the plans outlined in Part 1. Our implementation includes the following steps:

1. **Database Setup**: We have established an SQL schema containing 7 required entities and various relationships, and imported the appropriate data.

2. **Data Analysis**: By synthesizing data from various entities, we have analyzed to achieve the goal mentioned in the proposal of resonating with individual players and providing personalized recommendations.

3. **Web Front-End Option**: We have adopted the Web Front-End Option, allowing users to input information via the web interface and receive game recommendations based on the provided information.

4. **Recommendation System**: Through the design of web pages, we have provided game recommendations under different considerations, and ultimately analyzed the top games that users are most likely to like and download, and offered special discount offers for these games that users are most likely to enjoy.

5. **Additional Features**: Additionally, we have implemented some additional features, primarily in the design of the website. These features include:
   - Providing game recommendations based on user requirements for specific game-related information.
   - Showing specific comments about the games users are interested in, facilitating users to better understand the games.

# Two Most Interesting Web Pages

## 1. recommend_games
This page aims to recommend games to users based on an analysis of their preferences and activities, alongside offering a significant discount to incentivize purchases. The recommendations are personalized based on the user's interaction with games (tags of games they own or have shown interest in), games published by developers or publishers of games they own, games popular among their friends, and items on their wishlist. All the user needs to do is enter their id and they will be returned with the most frequent game and an exclusive 70% discount.

## 2. multiple_search_results
The page is designed to help users find games that fit their specific preferences and constraints. This level of customization enhances user experience by tailoring the search results to individual needs, making the process of finding new games more efficient and satisfying. Users can enter whether they want to have derivative games (there are three options to choose from, including "Yes","No" and "Don't care"), how many gigabytes of memory they have on their computer, how much they have in their budget, and then click search to get games that matches the requirements.

Both web pages show a high degree of personalization and SQL complexity. Meanwhile, both mirror real-world scenarios where applications need to offer dynamic content based on varied and complex user preferences.
