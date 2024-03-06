# Conceptual database diagram 

This conceptual diagram report illustrates the key components of a movie database management system.

## Entities

* Title (movie): focuses on movies and their attributes
    - Attributes: 
        - Title id
        - Title type
        - Primary title
        - Original title
        - Is adult: boolean
        - Start year
        - End year
        - Number of votes
        - Average rating
        - Genres: array[]

* Person (Name): focuses on specific people
    - Attributes
        - Name id
        - Primary name
        - Birth year
        - Death year
        - Primary professions: array[]

* Aliases: focuses on alternative titles associated with a specific movie
    - Attributes
        - Ordering
        - Title
        - Region
        - Language
        - Is original title
        - Types
        - Attributes 

* Principal: focuses on principal actors and crew members associated with specific movies
    - Attributes:
        - Title id
        - Ordering
        - Name id
        - Job
        - Job category
        - Character

## Relationships

* "Is writer of" links person and title:
    - A person can be a writer for a movie, and a movie can be associated with a certain writer.

* "Is director of" links person and title:
    - A person can be a director for a movie, and a movie can be associated with a certain director.

* "Is known for" links person and title:
    - A person can be known for having played in a certain movie, and a movie can be known for having had a certain person playing in it.

* "Also known as" links titles with aliases:
    - A single movie can have multiple aliases. The "Also known as" relationship points from a specific movie to its various alternative titles.

* "Has principals" links person and title:
    - A person could also be associated with a specific movie because they were part of the crew or acted in it (but not known for it).
