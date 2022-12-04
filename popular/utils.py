from nrclex import NRCLex
from wordcloud import WordCloud
import heapq
from nltk.corpus import stopwords

def get_bubble(df):
    weekdays = ['Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday', 'Sunday']
    temp_df = df.groupby('date', as_index=False)['ratio'].mean()
    temp_df1 = df.groupby('date', as_index=False)['comment'].mean()
    bubbles = []
    for day in weekdays:
        ratio = temp_df[temp_df['date'] == day].get('ratio')
        if len(ratio) != 0:
            bubbles.append(dict(x=day, y=round(ratio.iloc[0], 2),
                            r=int(temp_df1[temp_df1['date'] == day]['comment'].iloc[0])))
    return bubbles


def get_emotions(text_object):
    
    
    data=text_object.raw_emotion_scores
    highest=max(list(data.values()))
    highest=min([highest, 10000])
    lowest=min(list(data.values()))
    lowest=min(lowest, highest-1)


    emotion_json=[]
    order_emotion=['anticipation', 'disgust', 'joy', 'surprise','positive',
         'negative', 'fear', 'trust', 'anger', 'sadness']
    for emo in order_emotion:
        if(data.get(emo) == None):
            adj_score=0
        else:
            adj_score=min(1 + (4/(highest-lowest))*(data[emo]-lowest), 5)
        emotion_json.append(dict(
            name=emo.title(),
            radius=adj_score,
            values=[dict(label=emo.title(), value=adj_score)]
        ))
    return emotion_json

def get_words(text_object):
    wordcloud = WordCloud()
    freq = wordcloud.process_text(' '.join(text_object.words))
    foodict = {k: v for k, v in freq.items() if len(k)>=3}
    sorted_freq = heapq.nlargest(10, foodict, key=foodict.get)
    frequent_json = []
    for word in sorted_freq:
        frequent_json.append(dict(x=word.title(), y=foodict[word]))
    return frequent_json

def preprocess(dp):
    dp["cleaned"] = (
            dp["title"]+dp["description"]
            # remove whitespace
            .str.strip()
            # replace newlines with space
            .str.replace("\n", " ")
            # remove mentions and links
            .str.replace(r"(?:\@|http?\://|https?\://|www)\S+", "", regex=True)
            # remove punctuations, emojis, special characters
            .str.replace(r"[^\w\s]+", "", regex=True)
            # turn into lowercase
            .str.lower()
            # remove numbers
            .str.replace(r"\d+", "", regex=True)
            # remove hashtags
            .str.replace(r"#\S+", " ", regex=True)
        )
    stop_words=stopwords.words("english")
    dp["cleaned"]=dp["cleaned"].apply(
        lambda comment: " ".join(
            [word for word in comment.split() if word not in stop_words])
    )

    str_title = ','.join(dp['cleaned'])
    text_object=NRCLex(str_title)

    return text_object

#Channel
