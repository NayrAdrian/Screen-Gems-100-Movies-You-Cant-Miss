from bs4 import BeautifulSoup
import requests


def scrape_rotten_tomatoes(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    movies = []

    # Find all movie containers
    movie_containers = soup.find_all('div', class_='article_movie_title')

    for container in movie_containers:
        title_element = container.find('a')
        title = title_element.text.strip() if title_element else 'No title available'
        year = container.find('span', class_='subtle start-year').text.strip() if container.find('span',
                                                                                                 class_='subtle start-year') else 'No year available'
        rating = container.find('span', class_='tMeterScore').text.strip() if container.find('span',
                                                                                             class_='tMeterScore') else 'No rating available'

        # Find the "Critics Consensus" description
        description_container = container.find_next('div', class_='info critics-consensus')
        description = description_container.get_text(
            strip=True) if description_container else 'No description available'

        # Clean up the description by removing the "Critics Consensus:" prefix
        if description.startswith('Critics Consensus:'):
            description = description.replace('Critics Consensus:', '').strip()

        movies.append({
            'Title': title,
            'Year': year,
            'Rating': rating,
            'Description': description
        })

    return movies


def scrape_top_100_movies():
    base_url = "https://editorial.rottentomatoes.com/guide/best-movies-of-all-time/"

    # Scrape the first page
    movies = scrape_rotten_tomatoes(base_url)

    # Scrape the second page
    second_page_url = f"{base_url}page/2/"
    movies += scrape_rotten_tomatoes(second_page_url)

    top_100_movies = movies[:100]

    return top_100_movies


if __name__ == "__main__":
    top_movies = scrape_top_100_movies()
    for movie in top_movies:
        print(f"Title: {movie['Title']}")
        print(f"Year: {movie['Year']}")
        print(f"Rating: {movie['Rating']}")
        print(f"Description: {movie['Description']}")
        print("-" * 40)
