# MariaDB2LDAP
MariaDB2LDAP is a simple python program which replicates all MariaDB contacts entries in LDAP.

The problem: We had a Zimbra mail server and a FreePBX as VoIP PBX, the voip phones are able to read contacts from LDAP, but Zimbra saves the user's contact's into MariaDB.
The problem is that we want to save those contacts made from an account for example "contacts@example.com" into an LDAP tree. 
How we do it?

The solution: A script made in Python may be a good solution (but not the best). 
I made this script, it works as a normal script, started by the cron daemon every 4 hours.
It will replicate all edits made into contact@example.com's contacts list on LDAP, making VoIP phones able to read it.

The code may seem rude, it has been made very fastly. 

For any help, check our wiki.
