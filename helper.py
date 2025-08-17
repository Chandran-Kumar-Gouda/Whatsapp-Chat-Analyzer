from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import emoji
from collections import Counter
from gensim import corpora, models
import pdfkit
import tempfile
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from bertopic import BERTopic
from prophet import Prophet




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
    inactive_days = df.attrs['num_inactive_days']

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
    total_emojis = emoji_df['count'].sum()


    return num_messages ,len(words) ,inactive_days ,len(links) ,avg_msgs_per_day ,avg_words_per_msg,most_active_date ,total_emojis

def most_busiest_users(df):
    x = df['user'].value_counts().head()
    
    # how much percentage each user contibuted to whole group message
    new_df = round((df['user'].value_counts() / df['user'].shape[0])*100 ,2).reset_index().rename(columns={'user':'Name' ,'count':'Percent'}) 
    return x ,new_df


def create_wordCloud(selected_user ,df):
    f = open('stopwords_hinglish_odia2.txt','r')
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
    f = open('stopwords_hinglish_odia2.txt','r')
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
            if emoji.EMOJI_DATA.get(c):  # Correct emoji detection
                emojis.append(c)

    emoji_count = Counter(emojis)
    emoji_df = pd.DataFrame(emoji_count.most_common(), columns=['emoji', 'count'])
    return emoji_df


def emoji_pie_chart(df, selected_user="Overall"):
    # Get emoji counts for the selected user or overall
    emoji_df = emoji_helper(selected_user, df)
    if emoji_df.empty:
        return None

    # Take top 10 most used emojis
    top_emojis = emoji_df.head(10)

    # Create pie chart
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        top_emojis['count'],      # emoji usage counts
        labels=top_emojis['emoji'], # emoji symbols as labels
        autopct="%1.1f%%",        # show percentages on chart
        textprops={'fontsize': 14},
        startangle=90
    )

    # Increase font size for emoji labels
    for t in texts:
        t.set_fontsize(18)

    # Adjust percentage text
    for at in autotexts:
        at.set_fontsize(12)
        at.set_color("white")

    ax.set_title("Top Emojis Distribution", fontsize=16)
    return fig



def generate_summary(df, selected_user="Overall"):
    """
    Generate a chatbot-style summary of the chat.
    - If selected_user == "Overall": group summary
    - Else: individual user summary
    """

    if df.empty:
        return "No data available to generate summary."

    # OVERALL SUMMARY
    if selected_user == "Overall":
        total_msgs = df.shape[0]
        top_user = df['user'].value_counts().idxmax()
        sentiment = df['Sentiment'].value_counts().idxmax()
        
        # Most used emoji
        emoji_df = emoji_helper(selected_user, df)
        top_emoji = emoji_df.iloc[0, 0] if not emoji_df.empty else "🙂"

        summary = (
            f"In this group chat, {top_user} was the most active member. "
            f"The overall mood was {sentiment}. "
            f"The group exchanged {total_msgs} messages, "
            f"and the most popular emoji was {top_emoji}."
        )
        return summary

    # INDIVIDUAL SUMMARY
    else:
        user_df = df[df['user'] == selected_user]

        if user_df.empty:
            return f"No messages found for {selected_user}."

        total_msgs = user_df.shape[0]
        avg_words = round(user_df['message'].str.split().str.len().mean(), 2)
        sentiment = user_df['Sentiment'].value_counts().idxmax()
        
        # Most used emoji
        emoji_df = emoji_helper(selected_user, df)
        top_emoji = emoji_df.iloc[0, 0] if not emoji_df.empty else "🙂"

        summary = (
            f"{selected_user} has sent {total_msgs} messages. "
            f"On average, their messages contain {avg_words} words. "
            f"Their overall mood was {sentiment}, "
            f"and their most frequently used emoji was {top_emoji}."
        )
        return summary



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


def forecast_activity(df, periods=7):
    """
    Forecast future message activity using Facebook Prophet.
    df: chat DataFrame with 'only_date' and 'message'
    periods: number of days to forecast
    """

    daily_msgs = df.groupby('only_date').count()['message'].reset_index()
    daily_msgs.rename(columns={'only_date': 'ds', 'message': 'y'}, inplace=True)

    model = Prophet()
    model.fit(daily_msgs)

    # Forecast for the next 'periods' days
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]


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

def user_profiling(df):
    """
    Categorize users into roles (Leader, Responder, Silent) 
    based on chat activity features.
    """

    profiles = pd.DataFrame()

    # Messages per day per user
    messages_per_day = df.groupby(['user', 'only_date']).size().reset_index(name='msgs_per_day')
    avg_msgs_per_day = messages_per_day.groupby('user')['msgs_per_day'].mean()

    # Avg words per message
    avg_words = df.groupby('user')['message'].apply(lambda x: x.str.split().str.len().mean())

    # Emoji usage rate
    emoji_counts = {}
    for user in df['user'].unique():
        user_msgs = df[df['user'] == user]['message']
        emojis = []
        for msg in user_msgs:
            for c in msg:
                if c in emoji.EMOJI_DATA:  # emoji library
                    emojis.append(c)
        emoji_counts[user] = len(emojis)
    emoji_rate = pd.Series(emoji_counts) / df['user'].value_counts()

    # Combine features
    profiles['AvgMsgsPerDay'] = avg_msgs_per_day
    profiles['AvgWordsPerMsg'] = avg_words
    profiles['EmojiRate'] = emoji_rate

    # Categorize roles (simple thresholds)
    def role(row):
        if row['AvgMsgsPerDay'] > 10:
            return 'Leader'
        elif row['AvgMsgsPerDay'] > 2:
            return 'Responder'
        else:
            return 'Silent'

    profiles['Role'] = profiles.apply(role, axis=1)

    return profiles


def get_Sentiment(selected_user , df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    sentiment_count = df['Sentiment'].value_counts()

    return sentiment_count
    

def save_plot(fig):
    """
    Save a Matplotlib figure to a temporary PNG file and return the path.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(temp_file.name, bbox_inches='tight', dpi=150)
    plt.close(fig)
    return temp_file.name

def generate_report(html_content):
    """
    Generate PDF from HTML string using pdfkit.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        pdfkit.from_string(html_content, f.name, options={"encoding": "UTF-8"})
        return f.name