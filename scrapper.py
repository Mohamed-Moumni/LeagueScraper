import asyncio
import zendriver as zd
import re
import json
import requests

# URL = "https://www.sofascore.com/football/match/olympic-safi-wydad-casablanca/tAosMax"
URL = "https://www.sofascore.com/football/match/oceano-club-de-kerkennah-cs-sfaxien/tAosMax"
PLAYER_STATS_URL = "https://www.sofascore.com/api/v1/event/14981977/player/919699/statistics"
BASE_URL = "https://www.sofascore.com"

# def get_lineups(id, cookies):
#     lineup_url = BASE_URL + f"/api/v1/event/{id}/lineups"
#     print(lineup_url)

#     response = requests.get(lineup_url)
#     if response.status_code == 200:
#         json_data = response.json()
#         print("Data Fetched Successfully.", json_data)
#     else:
#         print(response.content)

# get_lineups(14981977)


# async def get_lineup(browser_instance, id:int):
#     lineup_url = BASE_URL + f"/api/v1/event/{id}/lineups"
#     response = requests.get(lineup_url)

#     if response.status_code == 200:
#         json_data = response.json()
#         print("Data Fetched Successfully.")
#     else:
#         print(response.content)

async def get_lineup(browser_instance, id:int, cookies):
    lineup_url = BASE_URL + f"/api/v1/event/{id}/lineups"
    
    print(lineup_url)

    zd_cookies = [zd.cdp.network.CookieParam(name=cookie.name, value=cookie.value, domain=cookie.domain, path=cookie.path) for cookie in cookies]
    await browser_instance.cookies.set_all(zd_cookies)

    tab = await browser_instance.get(lineup_url)
    json_content = await tab.evaluate("JSON.parse(document.body.innerText)")
    # content = await response.get_content()
    with open("lineup.json", "w") as file:
        json.dump(json_content, file, indent=2)

async def main():
    config = zd.Config()
    config.browser_connection_timeout = 30
    config.browser_connection_max_tries = 3  
  
    browser = await zd.start(headless=True,  
    expert=True,  
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",  
    browser_args=[  
        "--disable-blink-features=AutomationControlled",  
        "--no-sandbox",   
        "--disable-dev-shm-usage",  
        "--disable-web-security",  
        "--disable-features=VizDisplayCompositor",  
        "--disable-site-isolation-trials",  
        "--disable-ipc-flooding-protection",  
        "--disable-backgrounding-occluded-windows",  
        "--disable-renderer-backgrounding"  
    ])

    tab = await browser.get(BASE_URL)
    await tab.wait_for_ready_state("complete")
    cookies = await browser.cookies.get_all()

    # print("COOKIES", cookies)
    # for cookie in cookies:
        # print("COOKIE ", cookie)
    sofa_score_domain = [cookie for cookie in cookies if cookie.domain == "www.sofascore.com"]
    # print("SOFA COOKIES", sofa_score_domain)
    # for cookie in cookies:  
    #     print(f"{cookie.name}: {cookie.value}")
    # match_script_elem = await tab.select("#__NEXT_DATA__")

    # html_content = await match_script_elem.get_html()
    # match_league_json = re.search(r'>(.*)</script>', html_content, re.DOTALL)
    # if match_league_json:
    #     league_team_data_json = match_league_json.group(1)
    #     league_team_data = json.loads(league_team_data_json)
    #     league_match_data = league_team_data["props"]["pageProps"]["initialProps"]
    #     match_event_id = int(league_match_data["event"]['id'])
    #     print("EVENT", match_event_id)
    #     await get_lineup(browser, match_event_id)

    await get_lineup(browser, 15295862, sofa_score_domain)
    await browser.stop()
if __name__ == "__main__":
    asyncio.run(main())