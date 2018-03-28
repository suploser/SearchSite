from django.shortcuts import render_to_response
from search.models import  client
from django.http import HttpResponse
import json
# Create your views here.

def index(request):
    return render_to_response('index.html')

def suggest(request):
    key_word = request.GET.get('s', '')
    datas = []
    if key_word:
        response = client.search(
            index='article',
            body={
                "suggest": {
                    "my-suggest" : {
                        "text" : key_word,
                        "completion" : {
                            "field" : "suggest",
                            "fuzzy" : {
                                "fuzziness" : 1
                            },
                            "size": 10
                        }
                    }
                }
            }
            )
        for match in response['suggest']['my-suggest'][0]['options']:
            source = match['_source']
            datas.append(source['title'])
    return HttpResponse(json.dumps(datas), content_type='application/json')


def search(request):
    key_word = request.GET.get('q', '')
    page = request.GET.get('p', 1)
    try:
        page = int(page)
    except:
        page = 1
    if key_word:
        response = client.search(
                index= "article",
                body={
                    "query":{
                        "multi_match":{
                            "query":key_word,
                            "fields":["tags", "title", "content"]
                        }
                    },
                    "from": (page-1)*10,
                    "size":10,
                    "highlight": {
                        "pre_tags": ['<span class="keyWord">'],
                        "post_tags": ['</span>'],
                        "fields": {
                            "title": {},
                            "content": {},
                        }
                    }
                }
            )
        total_nums = response['hits']['total']
        if total_nums%10 > 0:
            page_nums = int(total_nums/10)+1
        else:
            page_nums = int(total_nums/10)
        page_range = list(range(max(1, page-2), page))+\
        list(range(page, min(page_nums, page+2)+1))
        if page_range[0]-1>=2:
            page_range.insert(0, '...')
        if page_nums-page_range[-1]>=2:
            page_range.append('...')
        if page_range[0] != 1:
            page_range.insert(0, 1)
        if page_range[-1] != page_nums:
            page_range.append(page_nums)
        hit_list = []
        for hit in response['hits']['hits']:
            hit_dict = {}
            if 'title' in hit['highlight']:
                hit_dict['title'] = ''.join(hit['highlight']['title'])
            else:
                hit_dict['title'] = hit['_source']['title']
            if 'content' in hit['highlight']:
                hit_dict['content'] = ''.join(hit['highlight']['content'])
            else:
                hit_dict['content'] = hit['_source']['content']
            hit_dict['created_at'] = hit['_source']['created_at']
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]
            hit_list.append(hit_dict)

    return render_to_response('result.html', 
                            {'hit_list':hit_list, 
                            "total_nums":total_nums, 
                            'page_nums':page_nums, 
                            'page_range':page_range,
                            'keyWord':key_word,
                            'has_pre':page-1>0,
                            'has_next':page+1<=page_nums,
                            'page':page
                            }
                            )