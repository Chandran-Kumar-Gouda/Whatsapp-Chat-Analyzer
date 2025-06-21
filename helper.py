from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd

extractor = URLExtract()
def fetch_stats(selected_user , df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    # fetch the number of messages

    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())
    
    

    # fetch number of media messages
    media_message = df[df['message'] == "<Media omitted>\n"].shape[0]

    # fetch the number of linked shared
    
    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(message)) 

    return num_messages ,len(words) ,media_message ,len(links)

def most_busiest_users(df):
    x = df['user'].value_counts().head()
    
    # how much percentage each user contibuted to whole group message
    new_df = round((df['user'].value_counts() / df['user'].shape[0])*100 ,2).reset_index().rename(columns={'user':'Name' ,'count':'Percent'}) 
    return x ,new_df

def create_wordCloud(selected_user ,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # remove all group notification
    temp = df[df['user'] != 'group_notification']
    # remove all <Media omitted>
    temp = temp[temp['message'] != '<Media omitted>\n'] 
    
    wc = WordCloud(width=500 ,height=500 ,min_font_size=10 ,background_color='white')
    df_wc =wc.generate(df['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user , df):
    f = open('stopwords_hinglish_odia.txt','r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.DataFrame(columns=['Word', 'Frequency']) 

    # remove all group notification
    temp = df[df['user'] != 'group_notification']
    # remove all <Media omitted>
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []
    # usernames = set(df['user'].unique())
    # username_list = list(usernames)
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                    words.append(word)

    from collections import Counter
    most_common_df = pd.DataFrame(Counter(words).most_common(2), columns=['Word', 'Frequency'])

    return most_common_df
