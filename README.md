Idea: Search for NBA player and receive the 5(?) most similiar players to them.

Commentary:
- First drafts of the similarity search lead to Games played, Possessions etc dominating the cosine similarity.

[ 2025-12-02 13:05:05,950 ] 76 root - INFO - Layer 1 Top 5:
PLAYER_NAME  SIMILARITY      top_1       top_2       top_3       top_4      top_5
Cade Cunningham      0.9538 GP (32.6%) MIN (24.5%) PTS (12.4%) AGE (12.3%) FGA (8.1%)
Brandon Ingram      0.9523 GP (30.1%) MIN (26.2%) AGE (16.0%) PTS (12.6%) FGA (7.9%)
Devin Booker      0.9499 GP (36.4%) MIN (22.6%) AGE (13.6%) PTS (12.2%) FGA (7.0%)
De'Aaron Fox      0.9394 GP (36.1%) MIN (23.4%) AGE (13.7%) PTS (12.0%) FGA (7.3%)
Paolo Banchero      0.9345 GP (35.3%) MIN (24.2%) AGE (12.1%) PTS (11.9%) FGA (7.0%)
[ 2025-12-02 13:05:05,952 ] 77 root - INFO - Layer 2 Top 5:
PLAYER_NAME  SIMILARITY        top_1             top_2             top_3       top_4             top_5
Cade Cunningham      0.9538 POSS (99.3%) OFF_RATING (0.2%) DEF_RATING (0.2%) PACE (0.1%) PACE_PER40 (0.1%)
Brandon Ingram      0.9403 POSS (99.2%) OFF_RATING (0.2%) DEF_RATING (0.2%) PACE (0.2%) PACE_PER40 (0.1%)
Devin Booker      0.9374 POSS (99.5%) OFF_RATING (0.1%) DEF_RATING (0.1%) PACE (0.1%) PACE_PER40 (0.1%)
De'Aaron Fox      0.9309 POSS (99.4%) OFF_RATING (0.2%) DEF_RATING (0.1%) PACE (0.1%) PACE_PER40 (0.1%)
Stephon Castle      0.9276 POSS (99.2%) OFF_RATING (0.2%) DEF_RATING (0.2%) PACE (0.2%) PACE_PER40 (0.1%)

- Tried implementing PCA and removing features to get a more accurate sense of comparison.
- Dataset is made of mostly features indicating playstyles which is good for similarity comparisons, however it creates a nonlinear, multi-modal feature space and players fall into clusters.
- PCA was a bad idea because of this, it preserves variance but doesn't help to preserve similiarity. Rare and noisy features (like off-screen shooting and cut efficiency have large variance and PCA amplifies this.
- PCA produced some pretty non-sensical results:

[ 2025-12-03 13:10:27,366 ] 68 root - INFO - Layer 3 Top 5:
          PLAYER_NAME  SIMILARITY       top_1             top_2             top_3          top_4          top_5
Giannis Antetokounmpo      0.8473 DD2 (20.6%)       PTS (20.4%) AST_RATIO (13.6%)     FGA (9.6%)  FGA_PG (9.6%)
        Pascal Siakam      0.8314 PTS (21.4%) AST_RATIO (17.4%)       FGA (12.2%) FGA_PG (12.2%)    DD2 (10.6%)
         Jaylen Brown      0.8112 PTS (23.7%) AST_RATIO (14.6%)    FGA_PG (13.7%)    FGA (13.7%)     DD2 (4.8%)
          Luka Doncic    0.8084 PTS (20.8%) AST_RATIO (15.7%)       DD2 (14.9%)    FGA (10.8%) FGA_PG (10.8%)
       Paolo Banchero      0.8072 PTS (21.9%) AST_RATIO (16.8%)       FGA (12.2%) FGA_PG (12.2%)     DD2 (8.0%)
[ 2025-12-03 13:10:27,367 ] 69 root - INFO - Layer 3 (PCA) Top 5:
      PLAYER_NAME  SIMILARITY                    top_1                     top_2                            top_3                    top_4                         top_5
    DeJon Jarreau      0.6568    OffScreen_FREQ (2.8%)      OffScreen_FGA (2.6%)            OffScreen_FGMX (2.6%)    OffScreen_POSS (2.5%)          OffScreen_PTS (2.5%)
 Ignas Brazdeikis      0.6359   Cut_FT_POSS_PCT (2.7%)    Cut_SF_POSS_PCT (2.7%)      Cut_PLUSONE_POSS_PCT (2.4%)           Cut_PPP (2.2%)     Cut_SCORE_POSS_PCT (2.2%)
      Buddy Hield      0.5828    Transition_PPP (1.9%) Transition_EFG_PCT (1.9%) Transition_SCORE_POSS_PCT (1.8%) Transition_FG_PCT (1.8%)  Spotup_SCORE_POSS_PCT (1.8%)
      Cory Joseph      0.5813   Cut_FT_POSS_PCT (1.9%)    Cut_SF_POSS_PCT (1.9%)            OffScreen_FREQ (1.8%)         Misc_FREQ (1.7%)   Cut_PLUSONE_POSS_PCT (1.6%)
Mitchell Robinson      0.5794 Transition_FG_PCT (1.9%) Transition_EFG_PCT (1.9%) Transition_SCORE_POSS_PCT (1.9%)    Transition_PPP (1.8%) Transition_FT_POSS_PCT (1.6%)

-The above is player comparison for Lebron James, non-PCA you get players you might expect with Double Doubles and PTS being the key drivers. With PCA you get players you would not expect to be similar to Lebron because of these noisy and rare features. It ends up grouping players by unusual and unique features.
-Next idea was to introduce UMAP instead, which worked pretty well.

-Addded some graphing and "interactive" features to the frontend. 

-Decided to have the frontend and backend running asynchronously, so when the frontend is interacted with there isn't a need to pull all the data from the NBA api every time. A FAISS Index is generated and stored and then the frontend queries that. Plan would be for the backend to run daily to update the stats and the index and then frontend would be called whenever needed.

Current Limitations:
- Runs locally on my machine, no scaling etc.
- Dockerfiles are present to containerise if needed.
- Backend needs to be run manually to update db
- Defensive stats are probably underrepresented

Future Improvements (to move towards production ready):
- Increase defensive features contribution (increase weighting, add more features)]
- Deploy to server, put backend onto GCP cloudrun or something similar to run daily
- Change DB storage to again server location
- Containerise fully, Docker Compose etc

