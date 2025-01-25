from youtube_transcript_api import YouTubeTranscriptApi


def get_video_id(url):
    return url.split("=")[-1]


def get_youtube_transcript(url: str) -> str:
    video_id = get_video_id(url)
    try:
        # Get the list of available transcript languages
        transcript_languages = YouTubeTranscriptApi.list_transcripts(video_id)
        result = ""
        for transcript in transcript_languages:
            for i in transcript.fetch():
                result += i["text"] + "\n"
            break
        return result
    except Exception as e:
        print("Error getting YouTube transcript:", e)
        return ""
