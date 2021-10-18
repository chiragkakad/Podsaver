import requests
import json


def search(keyword, limit=20):
    """
        Search is the iTunes podcast directory for the given keywords.
        Parameter:
            keyword = A string containing the keyword to search.
            limit: the maximum results to return,
            The default is 20 results.
        returns:
            A JSON object.
    """
    keyword = keyword.replace(' ', '+')  # Replace white space with +.
    # Set user agent.
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    headers = {'User-Agent': user_agent}
    # ITunes podcast search URL.
    itunesurl = 'https://itunes.apple.com/search?term=%s&country=us&limit=%d&entity=podcast' % (keyword, limit)
    req = requests.get(itunesurl, headers=headers)
    return json.loads(req.text)


def build():
    """
        Function to build the url file.
    """
    filename = input('''
    Enter the file name to write the feed url to.
    If the file does not exist it will be created.
    If the file exists the feeds will be appended to it.
    File:''')
    with open(filename, 'a') as fp:
        keyword = ''
        while True:
            print('Enter q to quit.')
            keyword = input('Search for a podcast: ').lower()
            if keyword == 'q':
                break
            results = search(keyword)
            for index, r in enumerate(results['results']):
                print('%d: %s by %s' % (index+1, r['collectionName'], r['artistName']))
            if len(results['results']) != 0:
                print('0: to search again')
                print('q: to quit.')
                choice = input('Enter a corresponding value to make your selection: ')
                if choice.lower() == 'q':
                    break
                elif choice.isdigit():
                    choice = int(choice)
                    if int(choice) == 0:
                        continue
                    if choice-1 < len(results['results']):
                        pod_name = results['results'][choice-1]['collectionName']
                        pod_url = results['results'][choice-1]['feedUrl']
                        fp.write('#%s\n' % (pod_name))
                        fp.write('%s\n' % (pod_url))
                        fp.flush()
                        print('Successfully added %s.' % (pod_name))
                    else:
                        print('Invalid selection!')
                else:
                    print('Invalid selection!')
            else:
                print('No results found!')


if __name__ == '__main__':
    build()
