# svms

A script which querys svm for magic cards specified in cardList.txt and either prints the found cards and costs, or sends an email 
with any new cards not available during the last run of the script, or with any cards which have dropped significantly in price since the last run.

I have the script running on a Rasberry PI and it is scheduled using cron.
