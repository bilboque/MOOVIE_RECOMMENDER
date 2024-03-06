# Conceptual database diagram 

This conceptual diagram report illustrates the key components of a movie database management system.

## Entities

* Title (movie): focuses on movies and their attributes
    - Attributes: 
        - Title_id
        - Title_type
        - Primary_title
        - Original_title
        - Is adult: boolean
        - Start_year
        - End_year
        - Number_of_votes
        - Average rating
        - Genres: array[]

* Person (Name): focuses on specific people
    - Attributes
        - Name_id
        - Primary_name
        - Birth_year
        - Death_year
        - Primary_professions: array[]

* Aliases: focuses on alternative titles associated with a specific movie
    - Attributes
        - Ordering
        - Title
        - Region
        - Language
        - Is_original_title
        - Types
        - Attributes 

* Principal: focuses on principal actors and crew members associated with specific movies
    - Attributes:
        - Title_id
        - Ordering
        - Name_id
        - Job
        - Job_category
        - Character

* Episode: focuses on specific episodes
    - Attributes:
        - Episode_id
        - Episode_number
        - Season_number

## Relationships

* "Is_writer_of" links person and title:
    - A person can be a writer for a movie, and a movie can be associated with a certain writer.

* "Is_director_of" links person and title:
    - A person can be a director for a movie, and a movie can be associated with a certain director.

* "Is_known_for" links person and title:
    - A person can be known for having played in a certain movie, and a movie can be known for having had a certain person playing in it.

* "Also_known_as" links titles with aliases:
    - A single movie can have multiple aliases. The "Also known as" relationship points from a specific movie to its various alternative titles.

* "Has_principals" links person and title:
    - A person could also be associated with a specific movie because they were part of the crew or acted in it (but not known for it).

* "Episode_belongs_to" links a title with its episode:
    - A series has multiple episodes, and an episode is part of a series





