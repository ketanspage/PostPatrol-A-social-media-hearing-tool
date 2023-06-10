from flask import Flask, render_template, request
import requests
from datetime import datetime
from transformers import pipeline
import pickle
import nltk
from nltk.stem import PorterStemmer
from langdetect import detect
from googletrans import Translator
#preprocessing
def preprocess(text):
  # Convert the text to lowercase.
  text = text.lower()
  # Remove stop words.
  stop_words = nltk.corpus.stopwords.words('english')
  text = ' '.join([word for word in text.split() if word not in stop_words])
  # Stem the words.
  stemmer = PorterStemmer()
  text = ' '.join([stemmer.stem(word) for word in text.split()])
  return text
# Create a tokenizer object
with open('sentiment_tokenizer.pkl','rb') as f:
    tokenizer_sentiment = pickle.load(f)
with open('category_tokenizer.pkl','rb') as f:
    tokenizer_category = pickle.load(f)
#sentiment analysis loading
with open('sentiment_model.pkl', 'rb') as f:
    model_sentiment = pickle.load(f)
#categorization loading
with open('category_model.pkl', 'rb') as f:
    model_category = pickle.load(f)
sentiment_analysis = pipeline('text-classification', model=model_sentiment, tokenizer=tokenizer_sentiment)
category_classification = pipeline('zero-shot-classification', model=model_category, tokenizer=tokenizer_category)

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/youtube', methods=['POST'])
def searchyoutube():
    keyword = request.form['keyword']
    def is_tamil(text):
        detected_lang = detect(text)
        return detected_lang == 'ta'
    def translate_text(text, target_language):
        translator = Translator()
        translated_text = translator.translate(text, dest=target_language)
        return translated_text.text

    text = keyword
    if is_tamil(text):
        keyword=translate_text(text, "en")
    else:
        pass

    #youtube api calling 
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "maxResults": 10,
        "q": keyword,
        "type": "video",
        "key": "AIzaSyC_QlWlhXMPxQt_Qz1oW_gNSqBVXEK499Y"
    }
    response = requests.get(url, params=params)
    yt_data = response.json()
    yt_data = yt_data['items']
    video_data = []
    for data in yt_data:
        title = data['snippet']['title']
        description = data['snippet']['description']
        date_time_str = data['snippet']['publishTime']
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%SZ')
        date_time = date_time_obj.strftime('%Y-%m-%d %H:%M:%S')
        timestamp = date_time_obj.timestamp()
        channel_title = data['snippet']['channelTitle']
        text=(title+' '+description)
        text=preprocess(text)
        # Sentiment analysis
        sentiment_results = sentiment_analysis(text)
        sentiment_analysis_data = []
        for result in sentiment_results:
            if result['label'] == 'LABEL_2':
                result['label'] = 'Positive'
            elif result['label'] == 'LABEL_1':
                result['label'] = 'Neutral'
            elif result['label'] == 'LABEL_0':
                result['label'] = 'Negative'
            result['score'] = round(result['score'], 2)
            sentiment_analysis_data.append({'label': result['label'], 'score': result['score']})
        # Category classification
        
        category_results = category_classification(text, ['travel', 'cooking', 'dancing', 'politics', 'music', 'programming', 'sports', 'fashion', 'art', 'photography', 'technology', 'science', 'education', 'gaming', 'food', 'health', 'fitness', 'beauty', 'movies', 'books', 'news', 'finance', 'business', 'marketing', 'parenting', 'relationships', 'spirituality', 'pets', 'outdoors', 'cars', 'travel photography', 'fashion style', 'cooking recipes', 'fitness motivation', 'music festivals', 'political news', 'science fiction', 'art history', 'technology trends', 'business entrepreneurship', 'parenting advice', 'sports events', 'gaming reviews', 'health and wellness', 'food recipes', 'movie reviews', 'book recommendations', 'news analysis', 'finance tips', 'spirituality and meditation', 'pet care', 'outdoor adventures', 'car enthusiasts', 'travel tips'])
        scores = category_results['scores']
        max_score = max(scores)
        max_index = scores.index(max_score)
        max_category = category_results['labels'][max_index]

        video_data.append({'title': title, 'description': description, 'date_time': date_time, 'timestamp': timestamp,
                           'channel_title': channel_title, 'sentiment_analysis': sentiment_analysis_data,
                           'category': max_category})
    return render_template('result.html', video_data=video_data)
@app.route('/instagram', methods=['POST'])
def searchinstagram():
    keyword = request.form['keyword']
    def is_tamil(text):
        detected_lang = detect(text)
        return detected_lang == 'ta'
    def translate_text(text, target_language):
        translator = Translator()
        translated_text = translator.translate(text, dest=target_language)
        return translated_text.text
    def concatenate_words_with_spaces(input_string):
        words = input_string.split()
        concatenated_word = ''.join(words)
        return concatenated_word

    text = keyword
    if is_tamil(text):
        keyword=translate_text(text, "en")
    else:
        pass
    input_string = keyword
    concatenated_word = concatenate_words_with_spaces(input_string)

    if input_string != concatenated_word:
        keyword=concatenated_word
    else:
        pass
    #instagram api calling 
    url = "https://instagram-scraper-2022.p.rapidapi.com/ig/hashtag/"
    querystring = {"hashtag":keyword,"count":2}
    headers = {
    "X-RapidAPI-Key": "2171691dbbmsh1b969628c76c2d5p164aafjsnc482730e096c",
    "X-RapidAPI-Host": "instagram-scraper-2022.p.rapidapi.com"}
    response = requests.get(url, headers=headers, params=querystring)
    insta_data = response.json()
    post_data = []
    username=insta_data['data']['top']['sections'][0]['layout_content']['medias'][0]['media']['user']['username']
    full_name=insta_data['data']['top']['sections'][0]['layout_content']['medias'][0]['media']['user']['full_name']
    caption=insta_data['data']['top']['sections'][0]['layout_content']['medias'][0]['media']['caption']['text']
    timestamp=insta_data['data']['top']['sections'][0]['layout_content']['medias'][0]['media']['taken_at']

    
      
    date_time = datetime.fromtimestamp(timestamp)
    text=(caption)
    text=preprocess(text)
    # Sentiment analysis
    sentiment_results = sentiment_analysis(text)
    sentiment_analysis_data = []
    for result in sentiment_results:
        if result['label'] == 'LABEL_2':
                result['label'] = 'Positive'
        elif result['label'] == 'LABEL_1':
                result['label'] = 'Neutral'
        elif result['label'] == 'LABEL_0':
                result['label'] = 'Negative'
        result['score'] = round(result['score'], 2)
    sentiment_analysis_data.append({'label': result['label'], 'score': result['score']})
    # Category classification
    category_results = category_classification(text, ['travel', 'cooking', 'dancing', 'politics', 'music', 'programming', 'sports', 'fashion', 'art', 'photography', 'technology', 'science', 'education', 'gaming', 'food', 'health', 'fitness', 'beauty', 'movies', 'books', 'news', 'finance', 'business', 'marketing', 'parenting', 'relationships', 'spirituality', 'pets', 'outdoors', 'cars', 'travel photography', 'fashion style', 'cooking recipes', 'fitness motivation', 'music festivals', 'political news', 'science fiction', 'art history', 'technology trends', 'business entrepreneurship', 'parenting advice', 'sports events', 'gaming reviews', 'health and wellness', 'food recipes', 'movie reviews', 'book recommendations', 'news analysis', 'finance tips', 'spirituality and meditation', 'pet care', 'outdoor adventures', 'car enthusiasts', 'travel tips'])
    scores = category_results['scores']
    max_score = max(scores)
    max_index = scores.index(max_score)
    max_category = category_results['labels'][max_index]

    post_data.append({'caption':caption , 'date_time': date_time, 'timestamp': timestamp,
                           'username':username,'fullname':full_name ,'sentiment_analysis': sentiment_analysis_data,
                           'category': max_category})
    return render_template('result2.html', post_data=post_data)
@app.route('/twitter', methods=['POST'])
def searchtwitter():
    keyword = request.form['keyword']
    #twitter api calling 
    url = "https://twitter32.p.rapidapi.com/getSearch"
    querystring = {"hashtag":keyword,"lang":"en"}
    headers = {
        "X-RapidAPI-Key": "2171691dbbmsh1b969628c76c2d5p164aafjsnc482730e096c",
        "X-RapidAPI-Host": "twitter32.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    tweeter_data=response.json()
    tweet_data = []
    for data in tweeter_data:
        tweet_text=tweeter_data['data']['tweets'][0]['text']
        tweet_datetime=tweeter_data['data']['tweets'][0]['created_at']
        date_string = tweet_datetime
        date_format = "%a %b %d %H:%M:%S %z %Y"
        date_obj = datetime.strptime(date_string, date_format)
        timestamp = date_obj.timestamp()
        tweet_name=tweeter_data['data']['tweets'][0]['user']['name']
        tweet_screenname=tweeter_data['data']['tweets'][0]['user']['screen_name']
        text=(tweet_text)
        text=preprocess(text)
        # Sentiment analysis
        sentiment_results = sentiment_analysis(text)
        sentiment_analysis_data = []
        for result in sentiment_results:
            if result['label'] == 'LABEL_2':
                result['label'] = 'Positive'
            elif result['label'] == 'LABEL_1':
                result['label'] = 'Neutral'
            elif result['label'] == 'LABEL_0':
                result['label'] = 'Negative'
            result['score'] = round(result['score'], 2)
            sentiment_analysis_data.append({'label': result['label'], 'score': result['score']})

        # Category classification
        category_results = category_classification(text, ['travel', 'cooking', 'dancing', 'politics','music','programming'])
        scores = category_results['scores']
        max_score = max(scores)
        max_index = scores.index(max_score)
        max_category = category_results['labels'][max_index]

        tweet_data.append({'text': tweet_text, 'date_time': date_obj, 'timestamp': timestamp,
                           'screenname':tweet_screenname,'fullname':tweet_name ,'sentiment_analysis': sentiment_analysis_data,
                           'category': max_category})
    return render_template('result3.html', tweet_data=tweet_data)
if __name__ == '__main__':
    app.run(debug=True)