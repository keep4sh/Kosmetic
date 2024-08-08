import requests
from bs4 import BeautifulSoup
import pandas as pd
from IPython.display import display

# 각 카테고리별: category_id=4nnn
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

data = pd.DataFrame(columns=['type','id','brand','name','rating','volume','price','tag_good','tag_bad','ingredient_count','caution','allergy','efficacy','skin_type'])

# 유저에게 카테고리 선택하게 한 후 카테고리 아이디를 인풋으로
class CrawlTopN():
    def __init__(self, category_name:str, categoryid:int):
        self.categoryid = categoryid
        self.category_name = category_name

    def call_topn_products(self, num_of_items:int):
        #url 에서 데이터 로딩
        category_url = f'https://www.hwahae.co.kr/rankings?english_name=category&theme_id={self.categoryid}'
        resp = requests.get(category_url)
        print("Status Code:", resp.status_code)
        skincare_html_content = resp.text
        skincare_soup = BeautifulSoup(skincare_html_content, 'html.parser')
        a_class = skincare_soup.find_all('a', class_="w-full flex items-center")

        # top3 제품정보 가져오기
        topn_summary = {}
        for i in range(num_of_items):
            product_id = int(a_class[i]['href'].strip('/products/'))
            type_ = self.category_name
            brand = a_class[i].find('span', class_="hds-text-body-medium hds-text-gray-tertiary").get_text()
            name =  a_class[i].find('span', class_="hds-text-body-medium hds-text-gray-primary").get_text()
            rating =  a_class[i].find('span', class_="hds-text-body-small hds-text-gray-secondary hds").get_text()
            try:
                ml =  a_class[i].find('span', variant="capacity").get_text()
                price =  a_class[i].find('span', class_="hds-text-body-large hds-text-gray-secondary").get_text()
            except AttributeError:
                ml = 'N/A'
                price = 'N/A'
            topn_summary[i+1] = [type_, product_id, brand, name, rating, ml, price]
        
        top100_summary = pd.DataFrame.from_dict(topn_summary, orient='index', columns=['type','id','brand','name','rating','volume','price'])
        print(f'Top3 products for {self.category_name} is:')
        display(top100_summary)
        return top100_summary
    
# 유저가 더 알고싶은 제품을 선택한 후 인자로 받아 제품 크롤링 진행
class CallProductDetail():
    def __init__(self, product_id_list:list):
        self.product_id_list = product_id_list
        
    #url 크롤링 & 데이터 로딩
    def crawl_website(self, product_id:int):
        product_url = f"https://www.hwahae.co.kr/products/{product_id}"
        resp = requests.get(product_url)
        print(f"Status Code for {product_id}:", resp.status_code)
        product_html_content = resp.text
        product_soup = BeautifulSoup(product_html_content, 'html.parser')
        if resp.status_code == 200:
            return product_soup
        else:
            return 'error'

    # 제품 리뷰 키워드 정보 출력
    def call_product_detail(self, product_soup, product_id:int):
        good_class = product_soup.find('div',class_="grow mr-24 w-1/2")
        bad_class = product_soup.find('div',class_="grow ml-24 w-1/2")
        gli_class = good_class.find_all('li',class_="flex justify-between gap-x-8")
        bli_class = bad_class.find_all('li',class_="flex justify-between gap-x-8")
        # 좋아요
        good = []
        for i in range(len(gli_class)):
            gtag = gli_class[i].find('span', class_="hds-text-caption-large text-gray-primary line-clamp-1").get_text()
            greview_count = gli_class[i].find('span',class_="hds-text-body-medium text-gray-tertiary").get_text()
            good.append(f'{gtag}({greview_count})')
        # 아쉬워요
        bad = []
        for j in range(len(bli_class)):
            btag = bli_class[j].find('span', class_="hds-text-caption-large text-gray-primary line-clamp-1").get_text()
            breview_count = bli_class[j].find('span',class_="hds-text-body-medium text-gray-tertiary").get_text()
            bad.append(f'{btag}({breview_count})')
        good_tag = ', '.join(good)
        bad_tag = ', '.join(bad)
        product_review_tags = [product_id, good_tag, bad_tag]
    
    # 유저가 해당 제품의 전성분을 알고자 할때
        # 전체 성분 갯수
        for parent_div in product_soup.find_all('div', class_='px-20'):
            try:
                total_ingredients = int(parent_div.find('span', class_='text-mint-primary').get_text())
            except:
                pass
        # 주의성분
        harm_parent_div = product_soup.find_all('div', class_="flex justify-between items-center py-8")
        caution = int(harm_parent_div[0].find('span', class_="hds-text-subtitle-medium text-gray-primary").get_text())
        allergy = int(harm_parent_div[1].find('span', class_="hds-text-subtitle-medium text-gray-primary").get_text())
        ingredient_info = [total_ingredients, caution, allergy]
        # 목적별 성분
        purpose_parent_div = product_soup.find_all('div', class_="flex flex-col items-center gap-y-10 w-[60px] h-[139px]")
        purpose_list = []
        for p in purpose_parent_div:
            try:
                count = int(p.find('span', class_='hds-text-subtitle-medium text-gray-primary').get_text())
                if count == 0:
                    pass
                else:
                    purpose = p.find('span', class_='hds-text-body-small text-gray-secondary text-center').get_text()
                    purpose_list.append(f'{purpose}({count})')
            except AttributeError:
                pass
        ingredient_info.append(', '.join(purpose_list))
        # 피부 타입별
        type_parent_div = product_soup.find_all('div', class_="flex items-center gap-x-24 py-8")
        for t in type_parent_div:
            t_name = t.find('span',class_="hds-text-body-medium w-[72px] text-gray-secondary").get_text()
            t_good = int(t.find('span', class_="hds-text-caption-large text-mint-primary").get_text())
            t_bad = int(t.find('span', class_="hds-text-caption-large text-red-primary").get_text())
            type_ = {'Good':t_good, 'Bad':t_bad}
            ingredient_info.append(f'Good({t_good}), Bad({t_bad})')
        print(f"Ingredients summary for {product_id}")

        # review_tag & ingredient_info 합침
        product_review_tags.extend(ingredient_info)
        return product_review_tags
    
    def crawl_all(self):
        detail_dict = {}
        for i in self.product_id_list:
            soup = self.crawl_website(i)
            if soup == 'error':
                detail_dict[i] = []
            else:
                detail_list = self.call_product_detail(soup, i)
                detail_dict[i] = detail_list

        detail_dataframe = pd.DataFrame.from_dict(detail_dict, orient='index', columns=['id','tag_good','tag_bad','ingredient_count','caution','allergy','efficacy','oily_skin','dry_skin','sensitive_skin'])
        # display(detail_dataframe)
        return detail_dataframe
            





