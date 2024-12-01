import xml.etree.ElementTree as ET
from urllib.request import urlopen
from tqdm import trange
from datetime import datetime
import re
import ssl
import pandas as pd
import logging

# SSL 인증서 문제 해결
ssl._create_default_https_context = ssl._create_unverified_context

def remove_tag(content):
    """HTML 태그를 제거하는 함수"""
    cleaned_text = re.sub('<.*?>', '', content)
    return cleaned_text

# API URL 설정
API_KEY = "본인 ID"
BASE_URL = f"https://www.law.go.kr/DRF/lawSearch.do?OC={API_KEY}&target=prec&type=XML"

# 전책매 항목
lawService = ['판시사항', '판결요지', '참조조문', '참조판례', '판례내용']

# 페이지 URL 생성
def get_page_url(base_url, page):
    return f"{base_url}&page={page}"

# API 호출 및 처리
try:
    response = urlopen(BASE_URL).read()
    xml_data = ET.fromstring(response)
except Exception as e:
    print(f"Failed to retrieve data from API: {e}")
    exit()

# 전체 판례 수 확인
try:
    totalCnt = int(xml_data.find('totalCnt').text)
    print(f"Total cases: {totalCnt}")
except AttributeError:
    print("Failed to parse totalCnt from API response")
    exit()

# 페이지별 데이터 수집
all_data = []
for page in trange(1, totalCnt // 20 + 1):
    try:
        prec_info = xml_data.findall('prec')
    except Exception as e:
        print(f"Failed to parse page {page}: {e}")
        break

    for info in prec_info:
        try:
            judicPrecNum = info.find('판례일료번호').text
            case = info.find('사건명').text
            caseNum = info.find('사건번호').text
            sentence_date = datetime.strptime(info.find('선고일자').text, '%Y.%m.%d')
            court = info.find('법원명').text
            caseInfo = info.find('사건종류명').text
            caseCode = info.find('사건종류코드').text
            judgment = info.find('판결유형').text
            sentence = info.find('선고').text
            judicPrecLink = info.find('판례상세링크').text

            detail_link = "https://www.law.go.kr/" + judicPrecLink.replace('HTML', 'XML')
            detail = urlopen(detail_link).read()
            detail_data = ET.fromstring(detail)

            content_list = []
            for content in lawService:
                if detail_data.find(content) is None:
                    text = '내용없음'
                else:
                    text = remove_tag(str(detail_data.find(content).text))
                content_list.append(text)
            
            prec_content = content_list[4].split("【")[1:]
            pattern = "[^【]*】"
            prec_dic = {}

            for content in prec_content:
                match = re.match(pattern, content)
                if match:
                    key = match.group(0).replace("】", "").strip()
                    value = content.replace(match.group(0), "").strip()
                    if key in prec_dic:
                        prec_dic[key] += f" 【{key}" + value
                    else:
                        prec_dic[key] = value

            result = {
                '판례일료번호': judicPrecNum,
                '사건명': case,
                '사건번호': caseNum,
                '선고일자': sentence_date.strftime("%Y-%m-%d"),
                '법원명': court,
                '사건종류명': caseInfo,
                '사건종류코드': caseCode,
                '판결유형': judgment,
                '선고': sentence,
                '판시사항': content_list[0].strip(),
                '판결요지': content_list[1].strip(),
                '참조조문': content_list[2].strip(),
                '참조판례': content_list[3].strip(),
                '판례내용': prec_dic
            }

            all_data.append(result)

        except Exception as e:
            print(f"Error processing case {caseNum}: {e}")
    
    page += 1
    response = urlopen(get_page_url(BASE_URL, page)).read()
    xml_data = ET.fromstring(response)

judicPrecList = pd.DataFrame(all_data)

# .xlsx 파일로 저장
judicPrecList.to_excel('./판례_본문.xlsx', index=False)

print("데이터 수집 및 저장 완료!")