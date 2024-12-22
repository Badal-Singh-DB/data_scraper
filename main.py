import pandas as pd
from data_scraper.youtube_scraper import YouTubeScraper
from dotenv import load_dotenv
import os

def main():
    
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY", "AIzaSyDhcx4j09PK8NV4IpBVB5323MJFvOFpcAM")
    if not api_key:
        raise ValueError("API key is missing. Ensure it's set in the .env file or hardcoded.")
    scraper = YouTubeScraper(api_key)
    genre = input("Enter the genre to search for: ")
    print(f"Searching for top 500 {genre} videos...")
    videos = scraper.search_videos(genre)

    if videos:
        df = pd.DataFrame(videos)
        output_file = f"youtube_{genre}_data.csv"
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Data saved to {output_file}")
    else:
        print("No videos found. Please try a different genre.")

if __name__ == "__main__":
    main()
