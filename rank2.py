import json
import unicodedata
import urllib.request
from bs4 import BeautifulSoup

def preformat_cjk(string, width, align='<', fill=' '):
    count = (width - sum(1 + (unicodedata.east_asian_width(c) in "WF") for c in string))
    return {
        '>': lambda s: fill * count + s,
        '<': lambda s: s + fill * count,
        '^': lambda s: fill * (count // 2) + s + fill * (count // 2 + count % 2)
    }[align](string)

# 데이터 가져오기
url = 'https://sports.news.naver.com/kbaseball/record/index.nhn?category=kbo&year=2024'  # 실제 데이터 소스 URL로 수정 필요
baseballData = urllib.request.urlopen(url)
source = baseballData.read()
baseballData.close()

# HTML 파싱
soup = BeautifulSoup(source, 'html.parser')
scripts = soup.find_all('script')

# JSON 데이터 찾기
recordJsonData = None
for script in scripts:
    line = str(script)
    if 'var ' in line and 'jsonTeamRecord' in line:
        recordList = line.split('jsonTeamRecord = ')
        if len(recordList) > 1:
            record = recordList[1].split('};')[0] + '}'
            recordJsonData = record.strip()

# JSON 파싱
if recordJsonData:
    r = json.loads(recordJsonData)
    regularTeamRecordList = r['regularTeamRecordList']

    # 두산 팀 데이터 추출
    doosan_data = None
    for team in regularTeamRecordList:
        if '두산' in team['teamName']:
            doosan_data = {
                'rank': team['rank'],
                'games': team['gameCount'],
                'wins': team['won'],
                'losses': team['lost'],
                'draws': team['drawn']
            }
            break

    # HTML 구조에 두산 팀 데이터 삽입
    if doosan_data:
        html_output = f'''
        <div class="inner">
            <section>
                <h2 class="page_hide__zAl1t hide">현재 랭킹</h2>
                <ul class="page_ranking-box__3IxlH ranking-box" role="presentation">
                    <li class="page_total__e0MMI total">
                        <h1>순위</h1>
                        <h2 class="page_rank__ZyQCt rank">{doosan_data['rank']}</h2>
                    </li>
                    <li>
                        <h1>경기</h1>
                        <h2 class="page_rank__ZyQCt rank">{doosan_data['games']}</h2>
                    </li>
                    <li>
                        <h1>승</h1>
                        <h2 class="page_rank__ZyQCt rank">{doosan_data['wins']}</h2>
                    </li>
                    <li>
                        <h1>패</h1>
                        <h2 class="page_rank__ZyQCt rank">{doosan_data['losses']}</h2>
                    </li>
                    <li>
                        <h1>무</h1>
                        <h2 class="page_rank__ZyQCt rank">{doosan_data['draws']}</h2>
                    </li>
                </ul>
            </section>
        </div>
        '''

        # HTML 파일로 저장
        with open('-template-scss-basic/doosan_baseball_record.html', 'w', encoding='utf-8') as f:
            f.write(f'''
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8" />
        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        />
        <title>두산베어스</title>
        <meta
            property="og:type"
            content="website"
        />
        <meta
            property="og:title"
            content="페이지 제목"
        />
        <meta
            property="og:description"
            content="페이지 설명"
        />
        <meta
            property="og:image"
            content="http://www.mysite.com/article/article1_featured_image.jpg"
        />
        <meta
            property="og:url"
            content="http://www.mysite.com/article/article1.html"
        />
        <meta
            name="twitter:card"
            content="summary"
        />
        <meta
            name="twitter:title"
            content="페이지 제목"
        />
        <meta
            name="twitter:description"
            content="페이지 설명"
        />
        <meta
            name="twitter:image"
            content="http://www.mysite.com/article/article1.html"
        />
        <meta
            name="twitter:domain"
            content="사이트 명"
        />
        <link
            rel="stylesheet"
            as="style"
            crossorigin
            href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard-gov.min.css"
        />
        <!-- icons -->
        <link
            href="https://fonts.googleapis.com/css?family=Material+Icons|Material+Icons+Outlined|Material+Icons+Round"
            rel="stylesheet"
        />

        <!-- symbols -->
        <link
            rel="stylesheet"
            href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@NaN,0,0,0"
        />
        <link
            rel="stylesheet"
            href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0"
        />
        <link
            rel="stylesheet"
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"
        />
        <link
            rel="stylesheet"
            href="https://maxst.icons8.com/vue-static/landings/line-awesome/line-awesome/1.3.0/css/line-awesome.min.css"
        />
        <link
            rel="stylesheet"
            href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css"
        />
        <link
            rel="stylesheet"
            href="./resources/css/styles.css"
        />
            </head>
            <body>
                {html_output}
            </body>
            </html>
            ''')
    else:
        print('두산 팀 데이터를 찾을 수 없습니다.')
else:
    print('데이터를 찾을 수 없습니다.')
