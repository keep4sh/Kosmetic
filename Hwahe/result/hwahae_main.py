from hwahae_crawler import CrawlTopN, CallProductDetail
import pandas as pd

def hwahae_main(number:int):
    category_id = {'스킨/토너': 4156,
    '로션/에멀젼': 4165,
    '에센스/엠플/세럼': 4174,
    '페이스오일': 4183,
    '크림': 4184,
    '아이케어': 4193,
    '미스트': 4194,
    '젤': 4199,
    '스킨/토너 패드': 4498,
    '밤/멀티밤': 4518}

    frames = []
    for category in category_id:
        id = category_id[category]
        type_ = CrawlTopN(category, id)
        top100 = type_.call_topn_products(number)
        crawl_list = [x for x in top100['id']]
        crawler = CallProductDetail(crawl_list)
        reviews = crawler.crawl_all()
        final = top100.join(reviews.set_index('id'), on='id')
        frames.append(final)

    result = pd.concat(frames, ignore_index=True, sort=False)
    result.to_csv('hwahae_data.csv')
    print('File successfully saved!')

if __name__ =='__main__':
    number = input('How many?:')
    hwahae_main(int(number))