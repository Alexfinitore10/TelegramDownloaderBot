from urlextract import URLExtract

class LinkExtractor:
    def __init__(self):
        self.extractor = URLExtract()
        self.video_domains = [
            'youtube.com', 'youtu.be', 
            'instagram.com', 'tiktok.com', 
            'twitter.com', 'x.com', 
            'vimeo.com', 'facebook.com'
        ]

    def extract_links(self, text):
        return self.extractor.find_urls(text)

    def filter_video_links(self, links):
        return [l for l in links if any(domain in l.lower() for domain in self.video_domains)]
