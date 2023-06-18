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
- Create random forest model code in "model.py"
- Test fitting model with simple set of features
- Hyperparameter fitting (remember to tune bins + n week history) using crossvalidation of time periods
