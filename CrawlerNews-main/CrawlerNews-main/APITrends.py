from pytrends.request import TrendReq
import json

def getTrending():
    pytrends = TrendReq(hl='id-ID', tz=360)


    trending_searches_df = pytrends.trending_searches(pn='indonesia')

    trending_searches = trending_searches_df[0].tolist() 
    
    return trending_searches

if __name__ == "__main__":
    getTrending()