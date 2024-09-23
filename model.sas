/* Importing the data */
proc import datafile='/path/to/your/datafile.csv' 
    out=work.data 
    dbms=csv 
    replace;
    getnames=yes;
run;

/* Viewing the first few rows of the dataset */
proc print data=work.data (obs=10); 
run;

/* Checking for missing values */
proc means data=work.data n nmiss;
run;

/* Removing observations with missing values */
data work.cleaned_data;
    set work.data;
    if cmiss(of _all_) then delete;
run;
/* Descriptive statistics */
proc means data=work.cleaned_data mean median std min max;
    var _numeric_;
run;

/* Frequency distribution of categorical variables */
proc freq data=work.cleaned_data;
    tables _character_;
run;

/* Correlation analysis */
proc corr data=work.cleaned_data;
    var _numeric_;
run;
/* Creating new variables or transforming existing ones */
data work.transformed_data;
    set work.cleaned_data;
    /* Example: Creating a new binary variable */
    if some_numeric_variable > threshold then new_binary_var = 1;
    else new_binary_var = 0;
run;
/* Splitting the data into training and test sets */
proc surveyselect data=work.transformed_data out=work.train_sample 
    samprate=0.7 outall method=srs seed=12345;
run;

data work.train work.test;
    set work.train_sample;
    if selected then output work.train;
    else output work.test;
run;

/* Logistic regression model */
proc logistic data=work.train;
    model target_variable(event='1') = predictor1 predictor2 predictor3;
    output out=work.predicted p=prob;
run;

/* Evaluating the model on the test set */
proc logistic inmodel=work.train;
    score data=work.test out=work.test_scored;
run;

proc print data=work.test_scored (obs=10);
run;
/* Creating ROC curve and calculating AUC */
proc logistic data=work.test_scored plots(only)=roc;
    model target_variable(event='1') = predictor1 predictor2 predictor3;
    roc 'ROC Curve' pred=prob;
run;

/* Confusion matrix */
proc freq data=work.test_scored;
    tables target_variable*pred / norow nocol nopercent;
    format pred prob.;
run;
