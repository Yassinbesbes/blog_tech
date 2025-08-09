import requests
from bs4 import BeautifulSoup
import json
import time
from tqdm import tqdm

def scrape_techcrunch_blogs(url, max_posts=100):
    headers = {'User-Agent': 'Mozilla/5.0'}
    print(f"\nFetching blog list from {url}...")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    blog_links = []
    for post_li in soup.find_all('li', class_='wp-block-post'):
        if len(blog_links) >= max_posts:
            break
        title_tag = post_li.find('h3', class_='loop-card__title')
        link_tag = title_tag.find('a') if title_tag else None
        if link_tag:
            blog_links.append({
                'url': link_tag['href'],
                'title': link_tag.get_text(strip=True)
            })

    print(f"Found {len(blog_links)} blogs to process.\n")
    
    blogs = []
    for idx, blog in enumerate(tqdm(blog_links, desc="Processing blogs"), 1):
        print(f"\nProcessing blog {idx}/{len(blog_links)}: {blog['title']}")
        print("-" * 50)
        
        # Get detailed content for each blog post
        print("Fetching content...")
        detailed_content = get_detailed_content(blog['url'])
        
        # Get author and date info from the detail page
        author_name, date = get_author_and_date(blog['url'])
        
        blogs.append({
            'title': blog['title'],
            'url': blog['url'],
            'author': author_name,
            'date': date,
            'content': detailed_content
        })
        
        print(f"✅ Completed: {blog['title']}")
        print("-" * 50)
        time.sleep(1)  # Be polite with requests

    return blogs

def get_author_and_date(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        author_tag = soup.find('a', class_='loop-card__author')
        author_name = author_tag.get_text(strip=True) if author_tag else "Unknown"
        
        date_tag = soup.find('time')
        date = date_tag['datetime'] if date_tag else "Unknown"
        
        return author_name, date
    except Exception as e:
        print(f"Error getting author/date for {url}: {str(e)}")
        return "Unknown", "Unknown"

def get_detailed_content(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        print("Extracting content details...")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content = {}
        
        # Extract the speakable summary
        print(" - Getting summary...")
        speakable_summary = soup.find('p', id='speakable-summary')
        content['summary'] = speakable_summary.get_text(strip=True) if speakable_summary else ""
        
        # Extract all paragraphs from the main content
        print(" - Extracting paragraphs...")
        entry_content = soup.find('div', class_='entry-content')
        if entry_content:
            paragraphs = []
            images = []
            
            for element in entry_content.find_all(['p', 'img']):
                if element.name == 'p':
                    paragraphs.append(element.get_text(strip=True))
                elif element.name == 'img':
                    images.append({
                        'src': element.get('src', ''),
                        'alt': element.get('alt', '')
                    })
            
            content['paragraphs'] = paragraphs
            content['images'] = images
        
        # Extract topics/tags
        print(" - Collecting tags...")
        topics = []
        topics_div = soup.find('div', class_='wp-block-tc23-post-relevant-terms')
        if topics_div:
            for topic in topics_div.find_all('a'):
                topics.append(topic.get_text(strip=True))
        content['topics'] = topics
        
        # Extract author bio
        print(" - Getting author bio...")
        author_bio = ""
        author_bio_div = soup.find('div', class_='wp-block-tc23-author-card-bio')
        if author_bio_div:
            author_bio = author_bio_div.get_text(strip=True)
        content['author_bio'] = author_bio
        
        return content
        
    except Exception as e:
        print(f"❌ Error scraping {url}: {str(e)}")
        return {}

def save_blogs_to_file(data, filename='blogs_data.json'):
    print(f"\nSaving data to {filename}...")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Data saved successfully!")

if __name__ == "__main__":
    url = "https://techcrunch.com/tag/blog/"
    max_posts = 100  # Set the maximum number of posts to scrape
    
    print("="*50)
    print(f"TechCrunch Blog Scraper - Max Posts: {max_posts}")
    print("="*50)
    
    blogs = scrape_techcrunch_blogs(url, max_posts)

    if not blogs:
        print("\nNo blogs were scraped. The page structure might have changed.")
    else:
        save_blogs_to_file(blogs)
        print(f"\nSuccessfully scraped {len(blogs)} blog posts with detailed content!")