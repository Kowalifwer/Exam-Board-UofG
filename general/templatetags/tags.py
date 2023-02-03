import imp
from django import template
register = template.Library()

clean_url = lambda x: x.replace('_', ' ')

@register.simple_tag(name='is_selected')
def generate_urls(request, ):
    url_to_return = '/'
    final_string = f'<a href="{url_to_return}">Home</a> >'
    ##get the current url
    current_url = request.path
    ##split the url into a list
    url_list = current_url.split('/')[1:-1]
    print(url_list)
    if 'all' in url_list:
        final_string += f'<a href="{current_url}">all {clean_url(url_list[0])}</a> >'
    elif len(url_list) == 2:
        final_string += f'<a href="/{url_list[0]}/all/">{clean_url(url_list[0])}</a> >'
        final_string += f'<a href="{current_url}">{clean_url(url_list[1])}</a> >'

    return final_string
    # for url in url_list:
        
    #     if url == 'all':
    #         url_to_return += f'{url}/'
    #         final_string += f'<a href="{url_to_return}">All</a> >'
    #     else:
    #         url_to_return += f'{url}/'
    # print(final_string)
    # return final_string
    
    # return str(url_list)