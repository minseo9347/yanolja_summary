import datetime
from dateutil import parser
import json
import pickle
import os
from openai import OpenAI
from dotenv import load_dotenv

# prompt 로딩
def load_prompt(promt_file):
    try:
        with open(promt_file, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        print("프롬프트 파일이 없습니다.")


# 파일데이터 로딩 및 전처리하기
def preprocess_reviews(path):
    with open(path, 'r', encoding='utf-8') as f:
        review_list = json.load(f)

    reviews_good, reviews_bad = [], []

    current_date = datetime.datetime.now()
    date_boundary = current_date - datetime.timedelta(days=6*30)

    filtered_cnt = 0
    for r in review_list:
        review_date_str = r['date']
        try:
            review_date = parser.parse(review_date_str)
        except (ValueError, TypeError):
            review_date = current_date

        if review_date < date_boundary:
            continue

        # 고품질 리뷰만 남김
        if len(r['review']) < 30:
            filtered_cnt += 1
            # print(r['review'])
            continue

        if r['stars'] == 5:
            reviews_good.append('[REVIEW_START]' + r['review'] + '[REVIEW_END]')
        else:
            reviews_bad.append('[REVIEW_START]' + r['review'] + '[REVIEW_END]')

    # good, bad 각각의 리스트의 요소 최대 길이가 50까지 되도록 자름 
    # print("min(len(reviews_good), 50) : ", min(len(reviews_good), 50))
    # print("len(reviews_good): ", len(reviews_good))
    reviews_good = reviews_good[:min(len(reviews_good), 50)]
    reviews_bad = reviews_bad[:min(len(reviews_bad), 50)]
    # print(len(reviews_good))
    # print(reviews_good)

    reviews_good_text = '\n'.join(reviews_good)
    reviews_bad_text = '\n'.join(reviews_bad)

    return reviews_good_text, reviews_bad_text


# LLM을 통한 요약
def summarize(reviews, prompt, temperature=0.0, model='gpt-3.5-turbo-0125'):

    # 환경변수 로딩
    load_dotenv('../.env', override=True)

    # 메모리에 로딩된 값을 api_key 변수에 대입
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = prompt + '\n\n' + reviews

    completion = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        temperature=temperature
    )

    return completion.choices[0].message.content

# DB에 저장하기