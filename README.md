# NHL Draft Ranking Tool
A tool to calculate draft rankings for the next three NHL drafts. The tool ranks players by combining production, league strength, positional value, player attributes and games played/reliability. The system spits out a "Draft Score", player type, a scouting profile based on the calculations, and a rough NHL projection.
You can also run the tool for 2028 and 2029 drafts at the current time, but it is not quite as accurate. The default year is 2027.

# How It Works
The tool uses (not very well written) Python scripts to collect and process NHL draft prospect data from [Elite Prospects](https://www.eliteprospects.com). This would not be possible without the help of [ParseBot](https://parse.bot/marketplace/3ba08450-29f5-4688-9c03-6662454abb2f/eliteprospects-com-api)
The initial data collection retrieves draft-eligible players, including basic profile information such as name, position, nationality, height and weight.
Because complete player information is distributed across multiple sources, additional data collection is required for each prospect. This includes profile information such as height, weight, shooting side, date of birth, and historical statistics.
The collected data is then normalized into a consistent JSON format and passed into the ranking system, which evaluates each player using league strength, production, position, physical profile, and other contextual factors.

# Ranking Methodology
The tool evaluates players using a weighted scoring system designed to account for both statistical production and contextual factors.
The system does not compare raw statistics equally across all players. Instead, production is adjusted based on league strength, season recency, position, physical profile, and sample reliability.

# Scoring Overview
A player's score is generated through several stages:

1. Statistical weighting
2. Production scoring
3. Contextual adjustments
4. Player profile modifiers
5. Reliability adjustments
6. Final ranking

Weighted Production =
Raw Production × League Multiplier × Season Weight × Context Adjustments

## Production Score
Skater production is calculated using:

√(Points + Goals + Assists) × 10

The square root prevents extremely high point totals from overwhelming all other evaluation factors while still rewarding offensive production. Goals are valued slightly higher than assists.

## League Strength
A player producing against older professional competition receives more value than identical production in a lower-level junior league (KHL vs MHL vs VHL, for example.)

League multipliers are stored externally in:
data/league_weights.json

## Position Adjustments
The system applies different evaluation criteria depending on position.

Defensemen receive adjustments for:

- Offensive production
- Being right-handed (parents: teach your kids to play righty!)
- Defensive value

Goalies are evaluated separately using:

- Goals Against Average
- Save Percentage
- Shutouts
- Games Played

Forwards are evaluated primarily through:

- Point production
- Goal scoring
- Points per game

## Age and Development Factors
Players are slightly adjusted based on draft-year age.

Younger players producing at comparable levels may receive additional value because they have more development runway.

## Size Profile
Physical attributes are used as modifiers rather than ranking factors.

The system recognizes profiles such as:

- Elite Size (6'3", 195 lbs and up)
- Large Frame (6'1", 175 lbs and up)
- Undersized Skill (5'10" or shorter, but a PPG > 0.9)

Size alone does not increase a player's ranking, but is used as a bonus. This also helps determine player type.

## Discipline Adjustment
Penalty rates are evaluated using PIM per game. It's hard to separate minor penalties from major penalties/fighting majors/misconducts, so all penalty minutes are treated equally.

Players may receive:

- Discipline bonus
- Nothing
- Penalty rate reduction

## Sample Size Reliability
The model reduces confidence in production during small seasons, such as 1 or 2 games played in a different league (common in Europe), or production during a tournament.
Larger samples receive a small boost adjustment.

## Plus/Minus Adjustment
Plus/minus is included as a contextual performance indicator. I know it's not the most reliable stat ever, but junior leagues don't track (or at least don't provide) Corsi.
The system calculates plus/minus per game and can apply it as a configurable scoring modifier.
Because plus/minus is heavily influenced by team environment and usage, it is not treated as a primary evaluation metric. Its influence can be adjusted through the ranking configuration file.

# Player Evaluation Output
Each prospect receives:

# Draft Score
The final numerical ranking value.

# Projection
- Star rating
- Expected NHL role
- Confidence level (how much statistical evidence supports the projection)
    - High Confidence: Player has a significant statistical sample (50+ games for skaters, 30+ games for goalies)
    - Medium Confidence: Player has a smaller or developing statistical sample

# Player Type
Automatically generated archetype:

Examples:

- Offensive Forward
- Power Forward
- Two-Way Forward
- Offensive Defenseman
- Shutdown Defenseman

# Scouting Report
A summary of player traits generated from the evaluation system.

# Score Breakdown
A detailed breakdown of the bonuses, penalties, and multipliers applied to the player's final Draft Score.

## Model Configuration
The ranking model is intentionally transparent. All scoring weights and league adjustments are stored in external JSON configuration files.
Users can fork the project and create their own ranking model by adjusting these values.

When you download it, you will have to run scraper.py, which will generate a "draft_(YEAR).json" file. Then run ranker.py which will apply the ranking tool and output "ranked_(YEAR).json." The website itself grabs data from the ranked.json file.

## Data Updates
The ranking system uses Actions to periodically refresh prospect data.

1. Collects updated prospect information and statistics
2. Processes the data through the ranking system
3. Generates updated ranking JSON files
4. Commits the refreshed data for the website to display

Because prospect evaluations change throughout the season, rankings may shift as new information becomes available. At the time of writing, there are only 87 ranked 2027 prospects, 29 2028 prospects, and 3 2029 prospects (two of which are on the same team...).
