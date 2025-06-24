from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import emoji
from collections import Counter

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
    
    #  Average messages per day
    avg_msgs_per_day = round(df.shape[0] / df['only_date'].nunique(), 2)
    
    #Average Words Per Message
    avg_words_per_msg  = round(len(words) / num_messages, 2) if num_messages else 0

    #Most active date
    most_active_date = df['only_date'].mode()[0]
    
    
    
    # emoji df
    emoji_df = emoji_helper(selected_user, df)
    total_emojis = emoji_df['Count'].sum()

    return num_messages ,len(words) ,media_message ,len(links) ,avg_msgs_per_day ,avg_words_per_msg,most_active_date ,total_emojis

def most_busiest_users(df):
    x = df['user'].value_counts().head()
    
    # how much percentage each user contibuted to whole group message
    new_df = round((df['user'].value_counts() / df['user'].shape[0])*100 ,2).reset_index().rename(columns={'user':'Name' ,'count':'Percent'}) 
    return x ,new_df


def create_wordCloud(selected_user ,df):
    f = open('stopwords_hinglish_odia.txt','r')
    stop_words = f.read()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)
    
    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
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
    most_common_df = pd.DataFrame(Counter(words).most_common(20), columns=['Word', 'Frequency']) # takes out 20 most common words

    return most_common_df

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        for c in message:
            if emoji.is_emoji(c):  # valid for emoji<2.0
                emojis.append(c)

    emoji_count = Counter(emojis)
    emoji_df = pd.DataFrame(emoji_count.most_common(), columns=['Emoji', 'Count'])
    return emoji_df

def monthly_timeline(selected_user ,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    monthly_timeline = df.groupby(['Year' ,'month_num' ,'month']).count()['message'].reset_index()
    time = []
    for i in range(monthly_timeline.shape[0]):
        time.append(monthly_timeline['month'][i] + "-" + str(monthly_timeline['Year'][i]))
    
    monthly_timeline['time'] = time
    return monthly_timeline        

def daily_timeline(selected_user , df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline

def weekely_activity_map(selected_user , df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    weekly_active_user= df['dayname'].value_counts()
    return weekly_active_user

def monthly_activity_map(selected_user , df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    monthly_active_user= df['month'].value_counts()
    return monthly_active_user

def weekly_heatmap(selected_user ,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    activity_heatmap = df.pivot_table(index='dayname' , columns ='peroids',values ='message',aggfunc='count').fillna(0)

    return activity_heatmap