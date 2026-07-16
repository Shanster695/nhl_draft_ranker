import requests
import json
import time


# Config

API_KEY = "pmx_097eb4b7d3702bd4861d94bfcaad1b4b"

YEAR = 2027    #Default is 2027, but can take input when you run it manually.

OUTPUT_FILE = (
    f"data/draft_{YEAR}.json"
)

GRAPHQL_URL = (
    "https://gql.eliteprospects.com/"
)


# Parse API.
# EliteProspects has core stats from the most recent team/season the draft center page, but biographical info and stats like +/- and PIM are kept on each
# respective player's profile page, so there are actually two scrapes.


def get_draft_class(year):

    url = (
        "https://api.parse.bot/scraper/"
        "46f9055c-a50d-4f31-9773-8755924ff8bd/"
        "get_draft_eligible"
    )

    r = requests.get(
        url,
        headers={
            "X-API-Key": API_KEY
        },
        params={
            "year": str(year)
        },
        timeout=30
    )

    r.encoding = "utf-8" 

    data = r.json()


    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        # old format
        if "data" in data and isinstance(data["data"], dict):
            if "prospects" in data["data"]:
                return data["data"]["prospects"]

        # alternative format
        if "prospects" in data:
            return data["prospects"]

    print("Unexpected API format:")
    print(json.dumps(data, indent=2)[:1000])

    return []




# GraphQL

HEADERS = {

    "User-Agent":
    "Mozilla/5.0",

    "Origin":
    "https://www.eliteprospects.com",

    "Referer":
    "https://www.eliteprospects.com",

    "apollo-require-preflight":
    "true",

    "Content-Type":
    "application/json"

}




def get_stats(player_id):
    params = {

        "operationName":
        "PlayerStatisticsDefault",

        "variables":

        json.dumps({

            "player": str(player_id),

            "statsType":
            "default,projected",

            "leagueType":
            "league",

            "sort":
            "season"

        }),

        "extensions":

        json.dumps({

            "persistedQuery": {

                "version": 1,

                "sha256Hash":
                "2b19f87ae83e7cd9ee833de6abb875f88a7d641dfbea9aaba532493e6407536e"

            }

        })

    }


    try:

        r = requests.get(
            GRAPHQL_URL,
            headers=HEADERS,
            params=params,
            timeout=20
        )

        if r.status_code != 200:
            return None
        r.encoding = "utf-8" 

        return r.json()

    except Exception as e:

        print("GraphQL error:", e)

        return None



def parse_stats(data):

    if not data:
        return {}


    edges = (
        data
        .get("data", {})
        .get("playerStats", {})
        .get("edges", [])
    )


    if not edges:
        return {}



    rows = []



    for edge in edges:

        season = edge.get("season")

        if not season:
            continue


        stats = edge.get("regularStats") or {}


        if not stats.get("GP"):
            continue



        # Goalie stats are on a different page than the draft center, so this requires a separate section entirely.
        # Goalies are weirdd, man

        is_goalie = (
            stats.get("SVP") is not None
            or stats.get("GAA") is not None
            or stats.get("SO") is not None
        )



        if is_goalie:

            rows.append({

                "season":
                f"{season.get('startYear')}-{str(season.get('endYear'))[-2:]}",


                "team":
                edge.get("teamName"),


                "league":
                edge.get("leagueName"),


                "gp":
                stats.get("GP") or 0,


                "goalsAgainstAverage":
                stats.get("GAA"),


                "savePercentage":
                stats.get("SV%"),


                "shutouts":
                stats.get("SO") or 0,


                "wins":
                stats.get("W") or 0,


                "losses":
                stats.get("L") or 0,


                "pim":
                stats.get("PIM") or 0,


                "plusMinus":
                None

            })


        else:

            rows.append({

                "season":
                f"{season.get('startYear')}-{str(season.get('endYear'))[-2:]}",


                "team":
                edge.get("teamName"),


                "league":
                edge.get("leagueName"),


                "gp":
                stats.get("GP") or 0,


                "goals":
                stats.get("G") or 0,


                "assists":
                stats.get("A") or 0,


                "points":
                stats.get("PTS") or 0,


                "pim":
                stats.get("PIM") or 0,


                "plusMinus":
                stats.get("PM")

            })




    if not rows:
        return {}





    # Keeps the stats of all teams in the most recent two seasons.

    seasons = sorted(
        list(
            set(
                r["season"]
                for r in rows
            )
        ),
        reverse=True
    )


    recent_seasons = seasons[:2]


    rows = [

        r for r in rows

        if r["season"] in recent_seasons

    ]



    return {

        "season":
        rows[0]["season"],


        "teams":
        rows,

        "plusMinus":
        sum(
            r.get("plusMinus", 0)
            for r in rows
            if r.get("plusMinus") is not None
        )

    }


# Run!


players = get_draft_class(YEAR)

print(json.dumps(players[0], indent=4))

print("Players:", len(players))

for i, player in enumerate(players):

    print(
        i + 1,
        "/",
        len(players),
        player["name"]
    )


    stats = get_stats(player["id"])

    if stats is None:
        print("No stats found for", player["name"])
        parsed = {}
    else:
        parsed = parse_stats(stats)



    if "performanceStats" not in player:
        player["performanceStats"] = {}


    player["performanceStats"].update(parsed)


    print(
        player["name"],
        parsed
    )


    time.sleep(1)





#Save output


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        players,
        f,
        indent=4,
        ensure_ascii=False
    )

print()
print("Saved:", OUTPUT_FILE)
