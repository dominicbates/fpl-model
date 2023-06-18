# fpl-model

Code built to predict likely Fantasy Premier League (FPL) points for 
all players in future weeks.

Will consist of:
- Code to load historical and current data and clean this
- Code to transform this in to a training dataset of the right format
- Modelling code (e.g. random forest) to fit over this dataset
- Code to apply this model to future gameweeks
- Perhaps automated running and deployment

#### To do:
- Code to append "opponent_avg_gc_last_n_weeks" to every row using already created function
- Add this to feature generation code (can just add as additional feature to average
- Add all of this code in to python script "data.py"
- Create random forest model code "model.py"
- Test fitting model with simple set of features
- Hyperparameter fitting (remember to tune bins + n week history) using crossvalidation of time periods