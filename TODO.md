# API RECOMMENDATION ROUTE
route: "/api/recommentation", (GET)
-> recuperer un json en entrée format : {args: movie_title_list || ['la description d'un film']}
-> appeler la fonction python get_recommendation(list: list)
-> jsonify la reponse de get_recommendation

get_recommendaiton(list) -> list


## SUR LA PAGE DU FILM EN PARTICULIER

afficher les films similaires avec la route de l'API pour obtenir des recommendations.

## RECHERCHE AVANCEE

affiche les films avec la recherche grace a la route de l'API

## DEPUIS LA WATCHLIST

Plusieurs films dans la route de l'API et afficher les resutats
