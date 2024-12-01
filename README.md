"사용한 데이터와 학습된 모델 데이터는 업로드 한계 때문에 업로드하지 못함."

사용 데이터

https://drive.google.com/file/d/1BIW9LpoDetqOzN8FbWHgle--Wugsyk0d/view?usp=drive_link

최종 모델 학습 시 사용된 데이터

https://docs.google.com/spreadsheets/d/1DP0UjuVIT6Oz5pCiL45Gqf1WB2Zbzdjl/edit?usp=drive_link&ouid=115590581604226607749&rtpof=true&sd=true

사용 모델
1. 임시 버전 https://drive.google.com/file/d/1uqzVT1Zze4EE5M2uADnQ3IbYnVUr39mf/view?usp=drive_link
2. 최종 버전 https://drive.google.com/file/d/1DYUuhoribR-8II855xvYnaLLn5a5nWPC/view?usp=drive_link

데이터 수집은 https://open.law.go.kr/LSO/openApi/guideResult.do 에서 신청하여 얻은 API를 통해 데이터를 크롤링하여 수집.

데이터 전처리는 일차적으로 공백값과 특수문자, 특수기호 등 기본적인 전처리와 법의 쟁점이 다른 '일반행정'과 같은 값이 반복되는 '특허' 값을 제외하여 42,204개의 데이터를 획득하는 중간 전처리 과정을 통해 "df_semi_final.xlsx" 데이터를 획득, 이후 해당 데이터 내부에 있는 판결유형 값을 일일히 변경하여, "데이터_전처리" 코드에서 사용된 데이터를 획득.

이후, 원본 판례 데이터인 "판례_본문.xlsx"와 "df_semi_final.xlsx" 데이터를 호출하여, 학습된 모델을 사용하기 위한 데이터 획득을 위한 전처리 과정을 통해, "df_final_real.xlsx" 데이터 획득 후, 토큰화 및 임베딩 작업 실행 및 공백 대신 쉼표(,)로 변경하여, 실행 코드를 위한 데이터 "df_real_token_with_embeddings_with_commas.xlsx" 획득.


데이터 학습 과정 시 transformers 라이브러리를 통해 BERT 토크나이저, 모델을 호출하여 토큰화 및 모델 학습을 진행.
모델 학습 진행 시 모델의 사건종류별 갯수 차이가 크기 때문에, 클래스 불균형 문제를 해결하기 위해 사건 유형별 가중치를 (전체 샘플 수 / 클래스 샘플 수) 로 하여 부여하고, 어드바이스를 적용하여 최대 에포크 수로 학습을 진행해 정확도를 최대한 상승시킴.

학습된 모델의 평가 방식을 정확도, 정밀도, 재현율, F1 Score의 지표를 저장하여, CSV 파일로 저장.

이후, 사건 종류별 모델의 정확도를 확인하기 위하여 사건 종류별로 모델의 정확도 검증, 어드바이스 적용 전 모델과의 성능 비교까지 하여 해당 값들을 데이터프레임으로 저장 후, csv 파일로 변환하여 저장.

코드 "비교_모델_데이터_준비_및_임시_모델_학습" 에서 transformers 라이브러리를 통해 호출한 BERT 토크나이저와 모델을 통해 조기 종료 조건을 설정한 임시 모델의 학습을 진행하고, 
transformers 라이브러리를 통해 비교 모델인 'klue/bert-base', 'monologg/koelectra-base-v3-discriminator', 'beomi/KcBERT-base'를 호출하고, 각 모델에 적합한 토크나이저를 호출하여 토큰화 작업을 실행 후 "각 모델명.csv" 파일로 저장

이후, "비교모델_학습" 코드에서 각 모델에 최적화된 데이터를 호출하여, 7:3 비율로 데이터를 학습용, 검증용 데이터로 분리하고, 각 모델 별로 알맞은 형태로 토큰 데이터를 패딩하여 학습을 진행 및 평가 지표를 저장.


실행은 "실행_XAI기법_적용"에서 실행. 실행용 데이터인 "df_real_token_with_embeddings_with_commas.xlsx", 어드바이스를 적용한 모델인 "model_weight_5.pth'를 호출하여 실행하고, 이때 SHAP 함수를 사용하여 모델의 설명성과 이해성, 설득력을 향상시키고, 결과가 어째서 저런 값으로 나왔는 지 표현하였습니다.

참고 논문

https://arxiv.org/abs/2206.05224


참고 블로그 (크롤링)

https://velog.io/@suba0113/%EB%B2%95%EB%A0%B9-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EA%B5%AC%EC%B6%95-2.-OPEN-API-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EC%88%98%EC%A7%91

