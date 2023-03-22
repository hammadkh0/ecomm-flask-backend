import pandas as pd
from pytrends.request import TrendReq
from fake_useragent import UserAgent


def initial_config():
    ua = UserAgent()
    user_agent = ua.random
    request_args = {
        "headers": {
            "authority": "trends.google.com",
            "method": "GET",
            "path": "/trends/explore?q=pizza&date=now%201-d&geo=PK&hl=en",
            "scheme": "https",
            "accept":
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/"signed-exchange;v=b3;q=0.7',
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "cookie":
            "__utmc=10102256; __utma=10102256.2125122689.1679127282.1679127289.1679140763.2; __utmz=10102256.1679140763.2.2.utmcsr=trends.google.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmt=1; __utmb=10102256.18.9.1679140864703; HSID=AMax7lZXPUFV-crkR; SSID=AKLJIL8dw2AOn9OlO; APISID=9nFoJQ6wPBCmMFB1/As9HJo6hpGVvDiqrN; SAPISID=MTWFg6wW0CTFbKjl/AwTFToQ-Z1-GAHkE8; __Secure-1PAPISID=MTWFg6wW0CTFbKjl/AwTFToQ-Z1-GAHkE8; __Secure-3PAPISID=MTWFg6wW0CTFbKjl/AwTFToQ-Z1-GAHkE8; S=billing-ui-v3=CXHfGFFK0cX-D2-a4Mmt6CgXzr_HNyhn:billing-ui-v3-efe=CXHfGFFK0cX-D2-a4Mmt6CgXzr_HNyhn; AEC=ARSKqsLNpmn6KENzMdHyoxlF3DzsAk4mIoTOQ_MP-sChjpfehOFd33BrZO8; 1P_JAR=2023-03-17-12; SID=UgjwcaYRJrnwUdfdFR3dSjtG6CzolK3tfm5QaxmwbbZaEF3dHgbSHfTxQ-ppN_Hcwi5CIw.; __Secure-1PSID=UgjwcaYRJrnwUdfdFR3dSjtG6CzolK3tfm5QaxmwbbZaEF3dhNQE-hbQpUgTrNJ49IfQoA.; __Secure-3PSID=UgjwcaYRJrnwUdfdFR3dSjtG6CzolK3tfm5QaxmwbbZaEF3dvlHvnSHsqXwFjd5FSCxxjA.; OGPC=19026797-5:19010599-1:19026792-1:; OGP=-19010599:-19026792:; _gid=GA1.3.884020012.1679127282; OTZ=6947055_36_36__36_; NID=511=IV4_EvZk5te82aSb29DndrGx2yuMNEbQFP8LDwY8jbKCn56x3vQozjAfPmtPmDYGfUxhplpn39iAxIvky-fSLVj61N9I5hi7taDltr8PPOAFDTSJla1WpwW8dya3yuUOghJkDj8E0IDWpBr3f75rr3k9g4gSDfbS7REhRuUWaAhRgN98vcRam4V3Tc007JW_NDi1KsIdrTktLH4Y0DK1sr-9M6LEgZL6Wn_hkUOGX_NjCTCMYu4S7jbjfP2VqoprUjFxbn1QItkBTMQ; _ga=GA1.3.2125122689.1679127282; _gat_gtag_UA_4401283=1; SIDCC=AFvIBn8w-YS1mL64s8_HSjp3M_MO9OR4JkvIlLRIn4dwHUWanCXY-Ubpx3i4pKKf7idLyG-6TB0; __Secure-1PSIDCC=AFvIBn9JwrE4QLzyeo_sxe94KgnEbKNNlDpDvzqohauMNwPaxlGkoqQfqhX3iPADmav3CUJgrXg; __Secure-3PSIDCC=AFvIBn8CdqVAQY3ks-xUUAM8LiYhaILjEGiVG5aah7qZrnW6H3OghVsbu0VBRo0UgZY_EtwmRWc; _ga_VWZPXDNJJB=GS1.1.1679139471.2.1.1679140881.0.0.0",
            "referer": "https://trends.google.com/",
            "sec-ch-ua":
            'Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99',
            "sec-ch-ua-arch": "x86",
            "sec-ch-ua-bitness": "64",
            "sec-ch-ua-full-version": "112.0.1722.11",
            "sec-ch-ua-full-version-list":
            'Chromium";v="112.0.5615.20", "Microsoft Edge";v="112.0.1722.11',
            "Not": 'A-Brand";v="99.0.0.0',
            "sec-ch-ua-mobile": '?0',
            "sec-ch-ua-model": "",
            "sec-ch-ua-platform": "Windows",
            "sec-ch-ua-platform-version": "10.0.0",
            "sec-ch-ua-wow64": '?0',
            "sec-fetch-dest": 'document',
            "sec-fetch-mode": 'navigate',
            "sec-fetch-site": 'same-origin',
            "sec-fetch-user": '?1',
            "upgrade-insecure-requests": '1',
            "user-agent": user_agent
        }
    }
    print(user_agent)

    pytrend = TrendReq(requests_args=request_args,
                       retries=10,
                       backoff_factor=0.1)
    return pytrend


def get_trends_by_region(keywords: str):
    pytrend = initial_config()

    pytrend.build_payload(kw_list=[keywords])
    df = pytrend.interest_by_region()
    df = df.sort_values(by=keywords, ascending=True)
    # remove rows with value 0

    df = df[df[keywords] != 0]

    # rename column name keywords to values
    column_name = "kw-" + "_".join(keywords.split(" "))
    df.rename(columns={keywords: column_name}, inplace=True)

    # convert df to a dictionary with {region: value}
    df = df.to_dict()
    df = df[column_name]

    return df


def get_related_results(keywords):

    pytrend = initial_config()

    suggestions = pytrend.suggestions(keyword=keywords)
    # df = pd.DataFrame(keywords, columns=['title', 'type'])

    pytrend.build_payload(kw_list=[keywords])
    related_topics = pytrend.related_topics()

    formatted_topics = get_formatted_data(related_topics, "rt").to_dict()

    # related queries
    related_queries = pytrend.related_queries()
    formatted_queries = get_formatted_data(related_queries, "rq").to_dict()

    dict = {}
    dict["related_topics"] = formatted_topics
    dict["related_queries"] = formatted_queries
    dict["suggestions"] = suggestions

    return dict


def get_formatted_data(data, type):
    top = list(data.values())[0]['top']
    rising = list(data.values())[0]['rising']

    # convert lists to dataframes
    if (type == "rt"):
        dftop = pd.DataFrame(top,
                             columns=['value', 'topic_title', 'topic_type'])
        dfrising = pd.DataFrame(rising,
                                columns=['value', 'topic_title', 'topic_type'])
    else:
        dftop = pd.DataFrame(top)
        dfrising = pd.DataFrame(rising)

    # join two data frames
    joindfs = [dftop, dfrising]
    allqueries = pd.concat(joindfs, axis=1)

    # function to change duplicates
    cols = pd.Series(allqueries.columns)
    for dup in allqueries.columns[allqueries.columns.duplicated(keep=False)]:
        cols[allqueries.columns.get_loc(dup)] = ([
            dup + '.' + str(d_idx) if d_idx != 0 else dup
            for d_idx in range(allqueries.columns.get_loc(dup).sum())
        ])
    allqueries.columns = cols

    # rename to proper names
    allqueries.rename(
        {
            'query': 'top_query',
            'value': 'top_query_value',
            'query.1': 'rising_query',
            'value.1': 'rising_query_value',
            'topic_title': 'top_topic_title',
            'topic_type': 'top_topic_type',
            'topic_title.1': 'rising_topic_title',
            'topic_type.1': 'rising_topic_type'
        },
        axis=1,
        inplace=True)

    return allqueries
