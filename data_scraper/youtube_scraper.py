from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import isodate

class YouTubeScraper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def search_videos(self, genre, max_results=500):
        videos = []
        next_page_token = None

        while len(videos) < max_results:
            try:
                search_response = self.youtube.search().list(
                    q=genre,
                    part='id,snippet',
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token,
                    type='video',
                    order='viewCount'
                ).execute()

                video_ids = [item['id']['videoId'] for item in search_response['items']]
                video_details = self.get_video_details(video_ids)
                videos.extend(video_details)

                next_page_token = search_response.get('nextPageToken')
                if not next_page_token:
                    break

            except HttpError as e:
                print(f'An HTTP error occurred: {e}')
                break

        return videos[:max_results]

    def get_video_details(self, video_ids):
        video_data = []

        try:
            videos_response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics,topicDetails,recordingDetails',
                id=','.join(video_ids)
            ).execute()

            for video in videos_response['items']:
                video_data.append({
                    'Video URL': f"https://www.youtube.com/watch?v={video['id']}",
                    'Title': video['snippet']['title'],
                    'Description': video['snippet']['description'],
                    'Channel Title': video['snippet']['channelTitle'],
                    'Keyword Tags': ','.join(video['snippet'].get('tags', [])),
                    'YouTube Video Category': video['snippet'].get('categoryId', 'Unknown'),
                    'Topic Details': ','.join(video.get('topicDetails', {}).get('topicCategories', [])),
                    'Video Published at': video['snippet']['publishedAt'],
                    'Video Duration': str(isodate.parse_duration(video['contentDetails']['duration'])),
                    'View Count': video['statistics'].get('viewCount', 0),
                    'Comment Count': video['statistics'].get('commentCount', 0),
                    'Captions Available': 'N/A',  # Captions feature placeholder
                    'Caption Text': 'N/A',  # Captions feature placeholder
                    'Location of Recording': self.get_location(video.get('recordingDetails', {}))
                })

        except HttpError as e:
            print(f'An HTTP error occurred: {e}')

        return video_data

    def get_location(self, recording_details):
        if not recording_details:
            return 'Unknown'

        location_parts = []
        if 'locationDescription' in recording_details:
            location_parts.append(recording_details['locationDescription'])
        if 'location' in recording_details:
            loc = recording_details['location']
            if 'latitude' in loc and 'longitude' in loc:
                location_parts.append(f"{loc['latitude']}, {loc['longitude']}")

        return ' | '.join(location_parts) if location_parts else 'Unknown'
