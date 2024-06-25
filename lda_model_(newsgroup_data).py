# -*- coding: utf-8 -*-
"""LDA model (newsgroup data).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Nhsb3OUK6uaC5T86kXmU92clY9vfpTOR

### Importing 20 newsgroups data
"""

from sklearn.datasets import fetch_20newsgroups

newsgroups_train = fetch_20newsgroups(subset='train')
newsgroups_train.target_names

"""#### 분석 대상 주제 선택
20개의 주제 중 각자 5개의 주제를 선택하여 "categories" 리스트를 작성하고 이 리스트를 이용하여 "newsgroups_train" 데이터의 일부만 불러와서 와서 "newsgroups_train"라는 이름으로 저장합니다.
 `comp.sys.ibm.pc.hardware`, `misc.forsale`, `rec.sport.baseball`, `sci.space`, `talk.politics.guns`를 선택하여 다음과 같은 명령문을 작성하겠습니다
"""

categories = ["comp.sys.ibm.pc.hardware", "misc.forsale", "rec.sport.baseball", "sci.space", "talk.politics.guns"]
newsgroups_train = fetch_20newsgroups(subset='train', categories=categories)

dir(newsgroups_train)

newsgroups_train.data[0]

newsgroups_train.filenames[0]

newsgroups_train.target[0]

"""### Preprocessing
다음과 같이 기본적인 전처리 과정을 진행합니다.
"""

import re
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('omw-1.4')
from nltk.stem import WordNetLemmatizer
wnl = WordNetLemmatizer()
from nltk.corpus import stopwords
stopwordslist = stopwords.words("english")

# POS fetching
def get_wnpos(tag):
    if tag.startswith('J'):
        return 'a'
    elif tag.startswith('V'):
        return 'v'
    elif tag.startswith('N'):
        return 'n'
    elif tag.startswith('R'):
        return 'r'
    else:
        return None

# tokenization
from nltk.stem import WordNetLemmatizer
wnl = WordNetLemmatizer()
stop_words = stopwords.words("english")
def my_tokenizer(text):
    words = nltk.word_tokenize(text)
    tokens = [word.lower() for word in words]
    tokens = nltk.pos_tag(tokens)
    tokens = [wnl.lemmatize(word, get_wnpos(tag)) if get_wnpos(tag) is not None else word for word, tag in tokens]
    tokens = [re.sub("\d+", "", w) for w in tokens]
    tokens = [re.sub(r"[^\w\-\']","",w) for w in tokens]
    tokens = [w for w in tokens if w not in stop_words]
    tokens = list(filter(None, tokens))
    return tokens
news_data = newsgroups_train.data
news_docs = [my_tokenizer(news_data[i]) for i in range(len(news_data))]
news_docs

print(news_docs[0])

len(news_docs)

"""# DTM

CountVectorizer() 함수를 이용하여 문서-단어행렬을 작성할 것이며

* 단, 지나치게 빈번하게 또는 지나치게 드물게 등장하는 단어들을 제거하기 위해 문서빈도가 0.02 이상 0.95 이하인 단어들만으로 문서-단어행렬을 생성하겠습니다.

* 문서-단어행렬은 pandas 데이터프레임 형태로 표현하고 열 인덱스는 각 단어가 되도록 할 것입니다.

* 생성된 문서-단어행렬의 행과 열의 개수를 확인해보겠습니다.
"""

from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

# CountVectorizer 설정: 문서빈도가 0.02 이상 0.95 이하인 단어들만 포함
vectorizer = CountVectorizer(tokenizer=my_tokenizer, min_df=0.02, max_df=0.95)

# 문서-단어 행렬 생성
X = vectorizer.fit_transform(newsgroups_train.data)

# Pandas 데이터프레임으로 변환
df = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())

# 행과 열의 개수 확인
print(f"Number of rows: {df.shape[0]}")
print(f"Number of columns: {df.shape[1]}")

df.head()

"""**table을 보면 열 인덱스가 각각의 단어가 되었음을 알 수 있습니다.**

두 개의 서로 다른 문서를 선택하여 코사인 유사도를 평가 할 것입니다.
"""

from sklearn.metrics.pairwise import cosine_similarity

def cos(matrix):
    # 코사인 유사도 계산
    cosine_sim = cosine_similarity(matrix)
    return cosine_sim

# 두 문서의 인덱스 선택
index1 = 0
index2 = 1

# 코사인 유사도 계산
cosine_sim = cos(X)

# 선택한 두 문서의 코사인 유사도 출력
print(cosine_sim[index1, index2])

"""**0번 문서와 1번문서의 유사도를 계산하였습니다**

# TF-IDF DTM

NumPy의 기본함수들만 이용하여 TF-IDF 방식의 문서-단어행렬을 작성하 겠습니다.

* 위에서 생성한 문서-단어행렬을 이용하여 각 단어의 문서빈도(df)를 확인해 보겠습니다.

* 단어빈도는 단어의 출현빈도를 이용하고 log(N/df)를 곱하여 TF-IDF 방식 DTM을 생성할 것입니다.(단, N은 전체 문서의 수)
"""

import numpy as np

# 문서-단어 행렬 생성
X = vectorizer.fit_transform(newsgroups_train.data).toarray()

# 전체 문서의 수
N = X.shape[0]

# 각 단어의 문서 빈도 계산
df = np.sum(X > 0, axis=0)

# TF 계산
tf = X

# IDF 계산
idf = np.log(N / df)

# IDF의 차원을 맞추기 위해 reshape
idf = idf.reshape(1, -1)

# TF-IDF 계산
tfidf = tf * idf

# 결과 확인
print("TF-IDF 행렬 SHAPE:", tfidf.shape)
print("TF-IDF 행렬의 첫번째 문서:", tfidf[0])

"""**기존행렬과 비교하기**"""

# 첫 번째 문서의 기존 문서-단어 행렬 값을 출력

print("기존 문서 단어행렬의 첫번째 문서:", X[0])

"""**기존의 문서단어행렬과 비교 해봤을때 가중치를 곱하여 잘 처리가 되었음을 알 수 있습니다.**

# LDA

gensim 딕셔너리를 생성합니다.



* filter_extremes() 메서드를 이용하여 문서빈도가 0.02 미만인 단어들은 제거할 것
"""

# 텍스트 데이터를 딕셔너리로 전환
from gensim import corpora
dictionary = corpora.Dictionary(news_docs)
print(dictionary)

# 딕셔너리에 적용할 수 있는 메서드와 애트리뷰트 확인
dir(dictionary)

# 딕셔너리의 키
dictionary.keys()

"""**키값을 이용하여 단어를 선택하는 예시**"""

dictionary.get(2)

# 토큰:단어 인덱스 딕셔너리
dictionary.token2id

# 문서의 도수분포표를 단어 인덱스-단어 출현 빈도의 튜플로 표현
dictionary.doc2bow(news_docs[0])

"""**filtering**"""

# 총 문서 수
total_docs = len(news_docs)

# 문서 빈도가 0.02 미만인 단어를 제거하기 위한 no_below 값 계산
no_below = max(1, int(total_docs * 0.02))

# 딕셔너리 객체 생성
dictionary = corpora.Dictionary(news_docs)

# 빈도 필터링 적용
dictionary.filter_extremes(no_below=no_below, keep_n=100000, keep_tokens=None)

# 필터링 후 딕셔너리 출력
print(dictionary)

# 모든 문서에 대해 BoW 도수분포표를 생성
corpus = [dictionary.doc2bow(text) for text in news_docs]

# 생성된 corpus 출력
for doc in corpus:
    print(doc)

"""다음과 같은 파라미터 값을 이용하여 "20 newsgropu data"에 대한 LDA 모형을 생성하겠습니다.

생성된 모형의 모수 alpha와 beta 값을 확인하고 beta 행렬의 의미를 파악해보겠습니다.
"""

from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer
from gensim import corpora
import gensim

# 파라미터 값 지정
num_topics = 10
chunksize = 200
passes = 20
iterations = 400
eval_every = 10

# LDA 모델 생성 및 학습
lda_model = gensim.models.LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=num_topics,
    chunksize=chunksize,
    passes=passes,
    iterations=iterations,
    eval_every=eval_every
)

# 각 주제 출력
for idx, topic in lda_model.print_topics(-1):
    print(f"Topic: {idx} \nWords: {topic}\n")

"""**beta는 각 주제에 대한 확률분포를 말하며 예시로 첫번째 주제에 대해 각 단어가 나타날 확률을 출력해보겠습니다.**"""

# alpha와 beta 계산
alpha = lda_model.alpha
beta = lda_model.get_topics()

# alpha 출력
print("Alpha values: ", alpha)

# beta 출력 (첫번째 주제에서의 분포)
print("Beta (첫번째 주제): ", beta[0])

# beta 행렬의 shape
print("Beta matrix shape: ", beta.shape)

""">  여기서 beta 행렬값은 첫번째 문서안에서 각각의 단어가 나타날 확률값이 계산되어있음을 알 수 있습니다.

토픽의 수 num_topics 값을 2,3,4,5,6,...,19,20으로 변화시켜가면서 UMass Coherence와 코사인 유사도 값을 구한 후

이들 지표를 이용하여 적절한 토픽의 수를 선택하겠습니다.

* UMass Coherence 값은 LDA 모형에서 출력되는 값을 사용

* 코사인 유사도 값은 문제3에서 작성한 함수를 이용하여 생성
"""

import re
import nltk
from sklearn.datasets import fetch_20newsgroups
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from gensim.models import CoherenceModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 순회할 토픽 번호 저장
num_topics_list = list(range(2, 21))

# coherence와 코사인 유사도 저장 위치
coherence_values = []
cosine_similarity_values = []

for num_topics in num_topics_list:
    # LDA model
    lda_model = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        chunksize=200,
        passes=20,
        iterations=400,
        eval_every=10
    )

    # UMass Coherence 계산
    coherence_model_lda = CoherenceModel(model=lda_model, corpus=corpus, dictionary=dictionary, coherence='u_mass')
    coherence_lda = coherence_model_lda.get_coherence()
    coherence_values.append(coherence_lda)

    # 주제-단어 분포 행렬을 가져오기
    topics_matrix = lda_model.get_topics()

    # 코사인 유사도 계산
    cosine_sim = cos(topics_matrix)

    # 주제 간의 평균 코사인 유사도
    upper_triangle_indices = np.triu_indices_from(cosine_sim, k=1)
    mean_cosine_similarity = cosine_sim[upper_triangle_indices].mean()
    cosine_similarity_values.append(mean_cosine_similarity)

    print(f'Num Topics: {num_topics}, Coherence: {coherence_lda}, Cosine Similarity: {mean_cosine_similarity}')

"""**위에 결과를 해석하여 각 문서의 유사도가 적당히 낮으면서 문서내에 일관성이 높은 토픽수인 5로 잡습니다**
> coherence가 -1.4919로 주변의 값보다 상대적으로 크면서 cosine유사도는 0.3으로 상대적으로 낮습니다 정확히 말하면 분할되는 문서수가 많아질수록 유사도는 당연히
감소하기에 coherence가 큰 값중에서 cosine 유사도가 적당히 낮은값을 택해야합니다.
"""

# LDA 모델 생성
num_topics = 5
lda_model = LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=num_topics,
    chunksize=200,
    passes=20,
    iterations=400,
    eval_every=10
)

# 각 토픽의 상위 단어 출력
for idx, topic in lda_model.print_topics(num_words=10):
    print(f"Topic {idx + 1}:")
    print(topic)
    print()

# 토픽의 의미 해석
topics = lda_model.show_topics(formatted=False, num_words=10)

topic_words = [[word for word, _ in topic[1]] for topic in topics]

# 토픽 해석
for i, words in enumerate(topic_words):
    print(f"Topic {i + 1} interpretation:")
    print(words)
    print()

"""**각 토픽의 상위 단어를 통해 주제를 추정하기**

- 1번 토픽은 `game`과 `win` `run` 을보아 토픽은 스포츠와 관련된 주제인 것으로 추정 해 볼 수 있습니다.
- 2번 토픽은  `gun`, `people`, `use` 등의 단어들이 포함되어 있어 총기 사용과 관련된 토론이나 논의가 포함된 것으로 볼 수 있습니다.
- 3번 토픽은  `sale` `new` 을 보아 판매와 관련한 주제인 것으로 추정 해 볼 수 있습니다.
- 4번 토픽은 `space` `launch` `nasa` `orbit` 등을보아 우주의 관한 주제임을 추정해 볼 수 있습니다.
- 5번 토픽은 `controller`, `card`, `system` 등을 통해 컴퓨터 하드웨어와 관련한 내용임을 추론 해 볼 수 있습니다.
"""