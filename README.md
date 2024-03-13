# ShareSpell- Resource_Sharing_App

<br>

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Customization](#customization)
6. [Dependencies](#dependencies)
7. [Contributing](#contributing)
8. [Acknowledgments](#acknowledgments)
   <br>

## 1. Introduction <a name="introduction"></a>

ShareSpell is a web-based platform designed for sharing educational resources within an educational institution or any other community. It provides a user-friendly interface for users to create, share, and discover resources categorized by topics and tags. Users can interact with posts by upvoting/downvoting, commenting, and more.

Technologies Used
HTML
CSS
JavaScript
Bootstrap
Flask
PyMySQL
MySQL
Features
User Authentication: Users can register, login, and logout securely.
Post Creation: Users can create posts containing information about shared resources. Each post must be related to one of the defined categories.
Category Management: Admin users can create or delete categories for organizing posts.
Tagging: Posts can be tagged with relevant keywords for easy search and categorization.
Interactions: Users can upvote/downvote posts, comment on posts, and like/dislike comments.
Post Listing: Posts are listed according to categories and popular tags for easy navigation.
Search Functionality: Users can search for posts based on keywords or tags.
Admin Dashboard: Admin users have access to a dashboard for managing categories, viewing reported posts, and more.
Setup Instructions
Clone the repository:

bash
Copy code
git clone https://github.com/ps1231/sharespell.git
Install dependencies:

Copy code
pip install -r requirements.txt
Configure the database:

Create a MySQL database and configure the connection settings in config.py.
Run the application:

Copy code
python app.py
Access the application in your web browser at http://localhost:5000.

Contributing
Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgements
Special thanks to Bootstrap for providing a responsive front-end framework, Flask for the web framework, and all other open-source libraries used in this project.
