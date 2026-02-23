import csv
import os
from datastructures import FastBipartite

def load_movies_graph(filepath, min_rating=4.0):
    """
    Load MovieLens graph from CSV file
    Expects columns: userId, movieId, rating, timestamp
    Only includes edges where rating >= min_rating

    Structure:
    - Online: Users (ordered by their first rating timestamp)
    - Offline: Movies
    -Edges: (user, movie) if user rated movie >= min_rating

    Args:
        filepath: Path to the ratings CSV file
        min_rating: Minimum rating threshold to include an edge
    """
    print(f"[LOADER] Loading MovieLens graph from {filepath} with min_rating={min_rating}...")

    # Reading and Parsing
    user_interactions = {}
    all_movies = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.split('\t')
            if len(parts) < 4:
                continue

            u_id = int(parts[0])  # userId
            m_id = int(parts[1])  # movieId
            rating = int(parts[2])  # rating
            timestamp = int(parts[3])  # timestamp

            if rating >= min_rating:
                all_movies.add(m_id)
                if u_id not in user_interactions:
                    user_interactions[u_id] = {'first_timestamp': timestamp, 'movies': []}
                

                if timestamp < user_interactions[u_id]['first_timestamp']:
                    user_interactions[u_id]['first_timestamp'] = timestamp

                user_interactions[u_id]['movies'].append(m_id)

    # Sort Users by first interaction timestamp
    sorted_users = sorted(user_interactions.items(), key=lambda x: x[1]['first_timestamp'])

    # Movie Map
    movie_map = {m_id: idx for idx, m_id in enumerate(sorted(all_movies))}

    n_left = len(sorted_users)
    n_right = len(movie_map)

    graph = FastBipartite(n_left, n_right)
    arrival_order = []

    print(f"[LOADER] Constructing graph with {n_left} users and {n_right} movies...")

    for internal_u, (real_u, data) in enumerate(sorted_users):
        arrival_order.append(internal_u)

        for m_id in data['movies']:
            internal_v = movie_map[m_id]
            graph.add_edge(internal_u, internal_v)

    
    print(f"[LOADER] Finished loading graph: {graph}")
    return graph, arrival_order