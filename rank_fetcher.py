import requests
from bs4 import BeautifulSoup
import re
import bs4

class RankFetcher:
    def fetch_rank(self, account):
        try:
            region = account.region
            formatted_name = account.name.replace('#', '-').replace(' ', '+').replace("--", "-")
            url = f'https://www.leagueofgraphs.com/summoner/{region}/{formatted_name}'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            tier = 'Unranked'
            division = ''
            lp = ''

            lp_div = soup.select_one('div.league-points')
            if lp_div:
                lp_span = lp_div.select_one('span.leaguePoints')
                if lp_span:
                    lp = lp_span.get_text().strip()

            meta_desc = soup.find('meta', attrs={'name': 'twitter:description'})
            if isinstance(meta_desc, bs4.element.Tag) and meta_desc.has_attr('content'):
                desc = meta_desc['content']
                if isinstance(desc, str) and ' - ' in desc:
                    rank_part = desc.split(' - ')[0]
                    match = re.search(r'([A-Za-z]+)\s+([IV]+)', rank_part)
                    if match:
                        tier = match.group(1)
                        division = match.group(2)
                    else:
                        match = re.search(r'([A-Za-z]+)', rank_part)
                        if match:
                            tier = match.group(1)
                            division = ''

            reached_last_season = '...'
            finished_last_season = '...'
            tooltip_divs = soup.find_all('div', attrs={'tooltip': True})
            matching_tooltips = []
            for div in tooltip_divs:
                tooltip_content = div.get('tooltip', '')
                if 'This player reached' in tooltip_content:
                    matching_tooltips.append(tooltip_content)
            if matching_tooltips:
                latest_tooltip = matching_tooltips[-1]
                reached_match = re.search(r'This player reached ([A-Za-z]+(?:\s+[IV]+)?) during Season \d+ \(Split \d+\). At the end of the season, this player was ([A-Za-z]+(?:\s+[IV]+)?)', latest_tooltip)
                if reached_match:
                    reached_last_season = reached_match.group(1)
                    finished_last_season = reached_match.group(2)
            return {
                'tier': tier,
                'division': division,
                'lp': lp,
                'reached_last_season': reached_last_season,
                'finished_last_season': finished_last_season
            }
        except Exception as e:
            return {
                'tier': 'Error',
                'division': '',
                'lp': '',
                'reached_last_season': '...',
                'finished_last_season': '...'
            } 