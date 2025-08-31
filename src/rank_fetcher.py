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
            level = ''

            # Fetch level information
            level = ''
            
            # Try multiple selectors for level information
            level_selectors = [
                'div.summonerLevel',
                'span.summonerLevel',
                '.summonerLevel',
                'div[class*="level"]',
                'span[class*="level"]',
                '.profile-level',
                '.summoner-level'
            ]
            
            for selector in level_selectors:
                level_element = soup.select_one(selector)
                if level_element:
                    level_text = level_element.get_text().strip()
                    # Try different patterns to extract level number
                    level_patterns = [
                        r'Level (\d+)',
                        r'(\d+)',
                        r'Lvl (\d+)',
                        r'Lv (\d+)'
                    ]
                    for pattern in level_patterns:
                        level_match = re.search(pattern, level_text)
                        if level_match:
                            level = level_match.group(1)
                            break
                    if level:
                        break
            
            # If still no level found, try looking in meta tags or other elements
            if not level:
                # Look for level in any text containing "Level" or "Lvl"
                for element in soup.find_all(text=re.compile(r'[Ll]evel|[Ll]vl')):
                    level_match = re.search(r'[Ll]evel\s*(\d+)|[Ll]vl\s*(\d+)', element)
                    if level_match:
                        level = level_match.group(1) or level_match.group(2)
                        break

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
                'level': level,
                'reached_last_season': reached_last_season,
                'finished_last_season': finished_last_season
            }
        except Exception as e:
            return {
                'tier': 'Error',
                'division': '',
                'lp': '',
                'level': '',
                'reached_last_season': '...',
                'finished_last_season': '...'
            } 