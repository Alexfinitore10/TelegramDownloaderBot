from urlextract import URLExtract
import re

def extract_links(text):
    extractor = URLExtract()
    links = extractor.find_urls(text)
    return links

def is_video_link(url):
    # Basic check for common video domains
    video_domains = [
        'youtube.com', 'youtu.be', 
        'instagram.com', 'tiktok.com', 
        'twitter.com', 'x.com', 
        'vimeo.com', 'facebook.com'
    ]
    return any(domain in url.lower() for domain in video_domains)

if __name__ == "__main__":
    message = """
    Check out this video: https://www.youtube.com/watch?v=aqz-KE-bpKQ 
    And also this one: https://www.instagram.com/reels/C8S6f-yM_q4/
    But not this: https://google.com
    """
    
    links = extract_links(message)
    print(f"Extracted links: {links}")
    
    video_links = [l for l in links if is_video_link(l)]
    print(f"Video links: {video_links}")
