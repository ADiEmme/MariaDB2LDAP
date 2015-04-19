#!/usr/bin/python2.7
import MySQLdb, ldap, sys, re, ldap.modlist as modlist, time, datetime
from string import digits
from validate_email import validate_email

#http://www.grotan.com/ldap/python-ldap-samples.html
#apt-get install python-ldap python-mysqldb python-pip
#pip install validate-email

#Global vars
uid = [""];
email = [""];

#LDAP config
server_ldap = "127.0.0.1";
user_dn = "cn=test";
user_pw = "password";
baseDN = "ou=contacts, dc=example, dc=com"
searchScope = ldap.SCOPE_SUBTREE
retrieveAttributes = None

#MariaDB config
server_mariadb = "127.0.0.1";
port_mariadb = "7306";
user_mdb = "zimbra";
passwd_mdb = "zimbrapassword";
db = "zimbra";


def print_wdate(string):
    date = datetime.datetime.now().strftime( "%d/%m/%Y %H:%M:%S" );
    print "["+str(date)+"] "+str(string);


#Initializing connections to MariaDB & LDAP

#LDAP
try:
    l = ldap.open(server_ldap);
    l.protocol_version = ldap.VERSION3;
    try:
        l.bind_s(user_dn, user_pw)
    except ldap.INVALID_CREDENTIALS:
        print_wdate("Your username or password is incorrect.");
        sys.exit();

except ldap.LDAPError, e:
    print_wdate(e);
##########################################

#MariaDB
db = MySQLdb.connect(host=server_mariadb, port=int(port_mariadb), user=user_mdb, passwd=passwd_mdb, db=db)
cur = db.cursor()
###########################################


def get_id():
    cur.execute("select * from mailbox where comment like 'contacts@example.com';")
    row = cur.fetchall();
    return row[0][0];


def find_email(email):
    searchFilter = "mail="+str(email);
    try:
        ldap_result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
	result_set = []
	index = 0;
	while 1:
            result_type, result_data = l.result(ldap_result_id, 0)
            if (result_data == []):
                break;
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    index += 1;
		    #uid_ldap = result_data[0][1]['uid'][0];
		    #print "UID LDAP:"+str(uid_ldap);
                    break;
        return index;
    except ldap.LDAPError, e:
        print_wdate(e);


def get_ldap_num():
    searchFilter = "uid=*";
    try:
        ldap_result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
        result_set = []
        index = 0;
        while 1:
            result_type, result_data = l.result(ldap_result_id, 0)
            if (result_data == []):
                break;
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    index += 1;
        return index;
    except ldap.LDAPError, e:
        print_wdate(e);


def get_mariadb_num(id_account):
    cur.execute("USE mboxgroup"+str(id_account)+";");
    cur.execute("select * from mail_item WHERE type = 6 and mailbox_id = 6 and folder_id = 7;");

    for row in cur.fetchall():
        index = 0;  
        uid_mysql = row[1];
        mysql_data = row[20];
        data_array = mysql_data.split(":");
        email1 = "";
	email1_pos = 0;
	email_array = "";
        email2 = "";
        index = 0;
        while index < len(data_array):
            if data_array[index].translate(None, digits) == "email" and email1 == "":
                l_email1 = re.sub("\D", "", data_array[index])
                email1 = data_array[index+1][0:int(l_email1)];
		email1_pos = index;
                if validate_email(email1) == False:
                    email1 = "";
	    if email1_pos != 0:
		email_array = data_array[int(email1_pos)+2:len(data_array)];
            index += 1;
        
        
	if email_array != "":
            index = 0;
            while index < len(email_array):
                if email_array[index].translate(None, digits) == "email":
		    email2_pos = index;
                    l_email2 = re.sub("\D", "", email_array[index])
                    l_email2 = l_email2[1:len(l_email2)];
                    email2 = email_array[index+1][0:int(l_email2)];

                    if validate_email(email2) == False:
                        email2 = "";
                index += 1;
		
        index2 = 0;
        found1 = 0;
        while index2 < len(email):
            if email1.lower() == email[index2].lower():
                found1 = 1;
		index2 = len(email);
	    else:
                index2 += 1;
 
        index2 = 0;
        found2 = 0;
        while index2 < len(email):
            if email2.lower() == email[index2].lower():
                found = 1;
                index2 = len(email);
	    else:
                index2 += 1;
        
        if found1 == 0 and found2 == 0 or email1 == "" and email2 == "":
            email.append(email1);
            uid.append(int(uid_mysql));
    
    return len(uid)-1;


def mariadb2ldap(id_account):
    cur.execute("USE mboxgroup"+str(id_account)+";");
    ul = len(uid);
    index = 1;	
    index_adding = 0;
    index_updating = 0;
    while index < ul:	
        cur.execute("select * from mail_item where id = "+str(uid[index])+";");
        row = cur.fetchall();
        uid_mysql = row[0][1];
        cdata_mysql = row[0][8];
        mysql_data = row[0][20];
        searchFilter = "uid="+str(uid_mysql);
        try:
            ldap_result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes);
            result_type, result_data = l.result(ldap_result_id, 0)
            if (result_data == []):
                dn = "uid="+str(uid_mysql)+", "+baseDN;
                data_array = mysql_data.split(":");
                company = "";
                firstName = "";
                lastName = "";
                fullName = "";
                homeStreet = "";
                homeCity = "";
                homeCountry = "";
                homePostalCode = "";
                homeState = "";
                email1 = "";
                email2 = "";
                homePhone = "";
                mobilePhone = "";
                workPhone = "";
                index_int = 0;
                email1_pos = 0;
                email_array = "";
                while index_int < len(data_array):
                    if data_array[index_int].translate(None, digits) == "firstName":
                        l_firstName = re.sub("\D", "", data_array[index_int])
                        firstName = data_array[index_int+1][0:int(l_firstName)];

                    if data_array[index_int].translate(None, digits) == "lastName":
                        l_lastName = re.sub("\D", "", data_array[index_int])
                        lastName = data_array[index_int+1][0:int(l_lastName)];

                    if data_array[index_int].translate(None, digits) == "fullName":
                        l_fullName = re.sub("\D", "", data_array[index_int])
                        fullName = data_array[index_int+1][0:int(l_fullName)];

                    if data_array[index_int].translate(None, digits) == "homeStreet":
                        l_homeStreet = re.sub("\D", "", data_array[index_int])
                        homeStreet = data_array[index_int+1][0:int(l_homeStreet)];

                    if data_array[index_int].translate(None, digits) == "company":
                        l_company = re.sub("\D", "", data_array[index_int])
                        company = data_array[index_int+1][0:int(l_company)];

                    if data_array[index_int].translate(None, digits) == "workPhone":
                        l_workPhone = re.sub("\D", "", data_array[index_int])
                        workPhone = data_array[index_int+1][0:int(l_workPhone)];

                    if data_array[index_int].translate(None, digits) == "homeCity":
                        l_homeCity = re.sub("\D", "", data_array[index_int])
                        homeCity = data_array[index_int+1][0:int(l_homeCity)];

                    if data_array[index_int].translate(None, digits) == "homeCountry":
                        l_homeCountry = re.sub("\D", "", data_array[index_int])
                        homeCountry = data_array[index_int+1][0:int(l_homeCountry)];

                    if data_array[index_int].translate(None, digits) == "homePostalCode":
                        l_homePostalCode = re.sub("\D", "", data_array[index_int])
                        homePostalCode = data_array[index_int+1][0:int(l_homePostalCode)];

                    if data_array[index_int].translate(None, digits) == "homeState":
                        l_homeState = re.sub("\D", "", data_array[index_int])
                        homeState = data_array[index_int+1][0:int(l_homeState)];

                    if data_array[index_int].translate(None, digits) == "homePhone":
                        l_homePhone = re.sub("\D", "", data_array[index_int])
                        homePhone = data_array[index_int+1][0:int(l_homePhone)];

                    if data_array[index_int].translate(None, digits) == "mobilePhone":
                        l_mobilePhone = re.sub("\D", "", data_array[index_int])
                        mobilePhone = data_array[index_int+1][0:int(l_mobilePhone)];

                    if data_array[index_int].translate(None, digits) == "workPhone":
                        l_workPhone = re.sub("\D", "", data_array[index_int])
                        workPhone = data_array[index_int+1][0:int(l_workPhone)];

                    if data_array[index_int].translate(None, digits) == "email" and email1 == "":
                        l_email1 = re.sub("\D", "", data_array[index_int])
                        email1 = data_array[index_int+1][0:int(l_email1)];
		        email1_pos = index_int;
                        if validate_email(email1) == False:
                            email1 = "";
	                if email1_pos != 0:
		            email_array = data_array[int(email1_pos)+2:len(data_array)];

                    index_int += 1;

                if email_array != "":
                    index_int2 = 0;
                    while index_int2 < len(email_array):
                        if email_array[index_int2].translate(None, digits) == "email":
		            email2_pos = index_int2;
                            l_email2 = re.sub("\D", "", email_array[index_int2])
                            l_email2 = l_email2[1:len(l_email2)];
                            email2 = email_array[index_int2+1][0:int(l_email2)];

                        if validate_email(email2) == False:
                            email2 = "";
                        index_int2 += 1;

              	attrs = {}
              	attrs['objectClass'] = "inetOrgPerson";
              	attrs['uid'] = str(uid_mysql);
              	if firstName != "" and lastName != "":
              	    attrs['cn'] = str(fullName);
              	    attrs['givenName'] = str(firstName);
              	    attrs['sn'] = str(lastName);
                else:
              	    if str(company) == "":
              	        attrs['cn'] = "No Name - "+str(uid_mysql);
              	        attrs['sn'] = "No Name - "+str(uid_mysql);
              	    else:
              	        attrs['cn'] = str(company);
              	        attrs['sn'] = str(company);

              	if str(email1) == "" and str(email2) == "":
              	    attrs['mail'] = "";
              	elif str(email1) != "" and str(email2) == "":
              	    attrs['mail'] = str(email1).lower();
              	elif str(email2) != "" and str(email1) == "":
              	    attrs['mail'] = str(email2).lower();
              	else:
              	    attrs['mail'] = [str(email1).lower(), str(email2).lower()];

              	attrs['roomNumber'] = str(cdata_mysql); #Uso il campo roomNumber come campo data della tupla
              	if str(mobilePhone) != "":
              	    attrs['mobile'] = str(mobilePhone);
              	if str(workPhone) != "":
              	    attrs['telephoneNumber'] = str(workPhone);
              	if str(homePhone) != "":
              	    attrs['homePhone'] = str(homePhone);
              	if str(homeStreet):
              	    attrs['street'] = str(homeStreet);
              	if str(homePostalCode) != "":
              	    attrs['postalCode'] = str(homePostalCode);
              	if str(homeCity) != "" and str(homeState) != "":
              	    attrs['l'] = str(homeCity+" ("+homeState+")");
              	if str(company) != "":
              	    attrs['o'] = str(company);
              	if (int(find_email(email1)) == 0 and int(find_email(email2)) == 0):
                    print_wdate("Adding "+str(dn));
              	    ldif = modlist.addModlist(attrs)
              	    l.add_s(dn,ldif)
                    index_adding += 1;
            else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        uid_ldap = result_data[0][1]['uid'][0];
                        cdata_ldap = result_data[0][1]['roomNumber'][0];
                        if str(cdata_ldap) != str(cdata_mysql):
                            deleteDN = "uid="+str(uid_ldap)+", "+baseDN;
                            try:
                                l.delete_s(deleteDN)
                            except ldap.LDAPError, e:
                                print_wdate(e);

                            dn = "uid="+str(uid_mysql)+", "+baseDN;
                            print_wdate("Updating "+str(dn));
                            data_array = mysql_data.split(":");
                            company = "";
                            firstName = "";
                            lastName = "";
                            fullName = "";
                            homeStreet = "";
                            homeCity = "";
                            homeCountry = "";
                            homePostalCode = "";
                            homeState = "";
                            email1 = "";
                            email2 = "";
                            homePhone = "";
                            mobilePhone = "";
                            workPhone = "";
                            index_int = 0;
                            email1_pos = 0;
                            email_array = "";
                            while index_int < len(data_array):
                                if data_array[index_int].translate(None, digits) == "firstName":
                                    l_firstName = re.sub("\D", "", data_array[index_int])
                                    firstName = data_array[index_int+1][0:int(l_firstName)];

                                if data_array[index_int].translate(None, digits) == "lastName":
                                    l_lastName = re.sub("\D", "", data_array[index_int])
                                    lastName = data_array[index_int+1][0:int(l_lastName)];

                                if data_array[index_int].translate(None, digits) == "fullName":
                                    l_fullName = re.sub("\D", "", data_array[index_int])
                                    fullName = data_array[index_int+1][0:int(l_fullName)];

                                if data_array[index_int].translate(None, digits) == "homeStreet":
                                    l_homeStreet = re.sub("\D", "", data_array[index_int])
                                    homeStreet = data_array[index_int+1][0:int(l_homeStreet)];

                                if data_array[index_int].translate(None, digits) == "company":
                                    l_company = re.sub("\D", "", data_array[index_int])
                                    company = data_array[index_int+1][0:int(l_company)];

                                if data_array[index_int].translate(None, digits) == "workPhone":
                                    l_workPhone = re.sub("\D", "", data_array[index_int])
                                    workPhone = data_array[index_int+1][0:int(l_workPhone)];

                                if data_array[index_int].translate(None, digits) == "homeCity":
                                    l_homeCity = re.sub("\D", "", data_array[index_int])
                                    homeCity = data_array[index_int+1][0:int(l_homeCity)];

                                if data_array[index_int].translate(None, digits) == "homeCountry":
                                    l_homeCountry = re.sub("\D", "", data_array[index_int])
                                    homeCountry = data_array[index_int+1][0:int(l_homeCountry)];

                                if data_array[index_int].translate(None, digits) == "homePostalCode":
                                    l_homePostalCode = re.sub("\D", "", data_array[index_int])
                                    homePostalCode = data_array[index_int+1][0:int(l_homePostalCode)];

                                if data_array[index_int].translate(None, digits) == "homeState":
                                    l_homeState = re.sub("\D", "", data_array[index_int])
                                    homeState = data_array[index_int+1][0:int(l_homeState)];

                                if data_array[index_int].translate(None, digits) == "homePhone":
                                    l_homePhone = re.sub("\D", "", data_array[index_int])
                                    homePhone = data_array[index_int+1][0:int(l_homePhone)];

                                if data_array[index_int].translate(None, digits) == "mobilePhone":
                                    l_mobilePhone = re.sub("\D", "", data_array[index_int])
                                    mobilePhone = data_array[index_int+1][0:int(l_mobilePhone)];

                                if data_array[index_int].translate(None, digits) == "workPhone":
                                    l_workPhone = re.sub("\D", "", data_array[index_int])
                                    workPhone = data_array[index_int+1][0:int(l_workPhone)];

                                if data_array[index_int].translate(None, digits) == "email" and email1 == "":
                                    l_email1 = re.sub("\D", "", data_array[index_int])
                                    email1 = data_array[index_int+1][0:int(l_email1)];
		                    email1_pos = index_int;
                                    if validate_email(email1) == False:
                                        email1 = "";
	                            if email1_pos != 0:
		                        email_array = data_array[int(email1_pos)+2:len(data_array)];

                                index_int += 1;

                            if email_array != "":
                                index_int2 = 0;
                                while index_int2 < len(email_array):
                                    if email_array[index_int2].translate(None, digits) == "email":
		                        email2_pos = index_int2;
                                        l_email2 = re.sub("\D", "", email_array[index_int2])
                                        l_email2 = l_email2[1:len(l_email2)];
                                        email2 = email_array[index_int2+1][0:int(l_email2)];

                                        if validate_email(email2) == False:
                                            email2 = "";
                                    index_int2 += 1;

                            attrs = {}
                            attrs['objectClass'] = "inetOrgPerson";
                            attrs['uid'] = str(uid_mysql);
                            if firstName != "" and lastName != "":
                                attrs['cn'] = str(fullName);
                                attrs['givenName'] = str(firstName);
                                attrs['sn'] = str(lastName);
                            else:
                                if str(company) == "":
                                    attrs['cn'] = "No Name - "+str(uid_mysql);
              	                    attrs['sn'] = "No Name - "+str(uid_mysql);
                                else:
                                    attrs['cn'] = str(company);
                                    attrs['sn'] = str(company);

                            if str(email1) == "" and str(email2) == "":
                                attrs['mail'] = "";
                            elif str(email1) != "" and str(email2) == "":
                                attrs['mail'] = str(email1).lower();
                            elif str(email2) != "" and str(email1) == "":
                                attrs['mail'] = str(email2).lower();
                            else:
                                attrs['mail'] = [str(email1).lower(), str(email2).lower()];

                            attrs['roomNumber'] = str(cdata_mysql); #Uso il campo roomNumber come campo data della tupla
                            if str(mobilePhone) != "":
                                attrs['mobile'] = str(mobilePhone);
                            if str(workPhone) != "":
                                attrs['telephoneNumber'] = str(workPhone);
                            if str(homePhone) != "":
                                attrs['homePhone'] = str(homePhone);
                            if str(homeStreet):
                                attrs['street'] = str(homeStreet);
                            if str(homePostalCode) != "":
                                attrs['postalCode'] = str(homePostalCode);
                            if str(homeCity) != "" and str(homeState) != "":
                                attrs['l'] = str(homeCity+" ("+homeState+")");
                            if str(company) != "":
                                attrs['o'] = str(company);

                            ldif = modlist.addModlist(attrs);
                            l.add_s(dn,ldif);
                            index_updating += 1;

        except ldap.LDAPError, e:
            print_wdate(e);
        index += 1;
    print_wdate("Contacts added: "+str(index_adding));
    print_wdate("Contacts updated: "+str(index_updating));
    l.unbind_s();
		

def delete_from_ldap():
    searchFilter = "uid=*";
    uid_univ = uid[1:len(uid)]
    index_removed = 0;
    try:
        ldap_result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
        result_set = []
        while 1:
            result_type, result_data = l.result(ldap_result_id, 0)
            if (result_data == []):
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    index = 0;
                    flag = 0;
                    uid_ldap = result_data[0][1]['uid'][0];
                    while index < len(uid_univ):
                        if int(uid_univ[index]) == int(uid_ldap):
                            flag = 1;
                        index += 1;

                    if flag == 0:
                        deleteDN = "uid="+str(uid_ldap)+", "+baseDN;
                        index_removed += 1;
                        try:
                            l.delete_s(deleteDN)
                            print_wdate(str(deleteDN)+" has been deleted");
                        except ldap.LDAPError, e:
                            print_wdate(e);
    except ldap.LDAPError, e:
        print_wdate(e);
    
    print_wdate("Contacts deleted: "+str(index_removed));


def main():
    start = time.time();
    res = get_id();
    if res == 0:
        print_wdate("Error while trying to get Account ID");
        sys.exit();

    print_wdate("Account ID: "+str(res));

    contacts_num_mysql = get_mariadb_num(res);
	
    print_wdate("Contacts in zimbra: "+str(contacts_num_mysql));

    contacts_num_ldap = get_ldap_num();

    print_wdate("Contacts in LDAP: "+str(contacts_num_ldap));

    print_wdate("Updating...");
    delete_from_ldap();
    mariadb2ldap(res);
    end = time.time();	
    print_wdate("Elapsed time: "+str(round(end-start,1)));	
    cur.close();

#Launch the main programm
main();
