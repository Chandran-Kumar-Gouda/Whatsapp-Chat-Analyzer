from urlextract import URLExtract
from wordcloud import WordCloud

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
    media_message = df['message'].value_counts()["<Media omitted>\n"]

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
    
    wc = WordCloud(width=500 ,height=500 ,min_font_size=10 ,background_color='white')
    df_wc =wc.generate(df['message'].str.cat(sep=" "))
    return df_wc