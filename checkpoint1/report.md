# Introduction

This report provides an overview of the database design for our bDMI project, as well as its functional and non-functional requirements and use cases. A conceptual and logical database schema will set the foundation for the database's structure.

# Conceptual database diagram

<image conceptual diagram png>

We have identified the following entities relevant to our project:

* universe : will contain a bundle of movies belonging to the same universe and its description. For example, Star Wars, Harry Potter, Transformers, Lord Of The Rings etc.  
* title : contains all movie titles
* award : contains all movie awards
* category : contains the different categories
* people : contains the people involved with the production/making of the movie (directors, producers, writers, actors, etc.)
* watchlist : contains the watchlist of users
* user : contains all users of the service 
* review : contains all reviews of movies and shows
* role : contains the character played by a person in a movie
* job : contains the jobs people had for a movie

Furthermore, we have identified the following relationships between those entities:

* universe "0..1" -- "2..*" title : for a universe to exist, it must contain at least two movies. A title can belong to no universe.
* title "0..*" -- "1..*" people : a movie necessarily has people (crew and actors).
* title "1" -- "0..*" review : a movie can have 0 or more reviews.
* title "0..1" -- "0..*" award : a movie can have 0 or more awards.
* title "1..*" -- "1..*" category : a title must have 1 or more categories, and a category must have at least one title.
* review "0..*" -- "1" user : a user can write none or more reviews for a title.
* user "0..*" -- "0..*" title | (title, user) .. watchlist : a title and a user are in relation with each other through a watchlist. A user can have no movies in their watchlist or more.
* role "1" -- "0..*" job : an actor can also be an a director or producer.

* (title, people) .. role : a title and a person will be related through the role table
* (title, category) .. title_category : a title and its category will be related through the title_category table.

# Logical database diagram

<insert logical diagram png>

# Objectifs analysis



# Use cases (UML)

<insert usecase png>

We identified the following use cases:
* A user can:
    * create a watchlist
    * add a movie to their watchlist
    * manipulate their watchlist
    * remove a movie from their watchlist
    * create a user profile
    * search for a movie
    * search for a movie using different filters like actor, category, date
    * view a movie's details
    * review a movie
    * get movie recommendations

* An administrator can:
    * add and remove movies to and from the database

