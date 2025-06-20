from urlextract import URLExtract
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