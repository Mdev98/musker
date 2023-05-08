# Musker Documentation

## Overview

Musker is a web application that mimics the functionality of Twitter, allowing users to register and login to post tweets and follow other users. It is built using Flask, a Python web framework, and a SQLite database. The codebase includes both frontend and backend code, which is used to render HTML templates, process form data, and interact with the database.

## Features

### Authentication

Users can register, login, and logout using the following routes:

- `/register`: This route allows users to register by providing a username, email, and password. It checks if the user already exists and adds the user to the database if not.
- `/login`: This route allows registered users to login using their username and password. It checks if the user exists in the database and compares the provided password with the hashed password stored in the database.
- `/logout`: This route logs out the user by removing the user's session data and redirecting to the home page.
- `/forgot-password`: This route is yet to come and will allow users to reset their password. NOT IMPLEMENTED YET

- `/user/<string:username>`: This route shows the user profile of the user with the given username. It displays the user's username, email, the number of tweets they have posted, and the number of followers they have. Logged-in users can also see their own profile, which includes a button to edit their profile details.


### MUSK

Users can add, view, and interact with musks using the following routes:

- `/tweet/add`: This route allows users to add a new tweet by providing a tweet message. It checks if the user is logged in and adds the tweet to the database if the form data is valid.
- `/musks`: This route displays all the tweets added by all users. It shows the tweet's content, the author's username, and the timestamp of the tweet. Logged-in users can also post a new tweet from this page.
- `/tweet/<int:id>`: This route shows the details of a specific tweet identified by the tweet's ID. It displays the tweet's content, the author's username, the timestamp, and the number of likes the tweet has received. Logged-in users can also like or dislike the tweet from this page.
- `/api/tweet/add-like`: This route allows users to add a like to a specific tweet. It checks if the user is logged in, finds the tweet by ID, and adds a new row to the likes table if the user has not liked the tweet before.
- `/api/tweet/remove-like`: This route allows users to remove a like from a specific tweet. It checks if the user is logged in, finds the tweet by ID, and removes the corresponding row from the likes table if the user has already liked the tweet.
- `/api/follow`: This route allows users to follow another user. It checks if the user is logged in, finds the user to follow by username, and adds a new row to the followers table if the user is not already following the target user.
- `/api/unfollow`: This route allows users to unfollow another user. It checks if the user is logged in, finds the user to unfollow by username, and removes the corresponding row from the followers table if the user is already following the target user.

## Conclusion

In summary, Musker is a web application that allows users to register and login to post tweets, view tweets from other users, and follow other users. It has basic authentication and authorization features and interacts with a SQLite database to store user and tweet data.