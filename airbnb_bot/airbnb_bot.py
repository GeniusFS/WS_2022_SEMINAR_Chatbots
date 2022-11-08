import re
import sqlite3 as sql
from os.path import isfile


location_regex = [
    # first entry in every tuple is a regex for matching user inputs
    # second entry in every tuple is a possible value
    #   for the key neighbourhood_group in our sql file
    (r'(charlottenburg)|(wilmersdorf)','Charlottenburg-Wilm.'),
    (r'(friedrichshain)|(kreuzberg)', 'Friedrichshain-Kreuzberg'),
    (r'lichtenberg', 'Lichtenberg'),
    (r'(marzahn)|(Hellersdorf)', 'Marzahn - Hellersdorf'),
    (r'mitte', 'Mitte'),
    (r'neukölln', 'Neukölln'),
    (r'pankow', 'Pankow'),
    (r'reinickendorf', 'Reinickendorf'),
    (r'spandau', 'Spandau'),
    (r'(steglitz)|(zehlendorf)', 'Steglitz - Zehlendorf'),
    (r'(tempelhof)|(schöneberg)', 'Tempelhof - Schöneberg'),
    (r'(treptow)|(köpenick)', 'Treptow - Köpenick')
]


#Listen für Inputüberprüfungen (Felix)
stop_words = ['stop', 'cancel', 'tschüss', 'abbruch']
positive_answers = ['ja', 'klar', 'natürlich']
pricing_words = ['preis', 'kosten']
nights_words = ['nächte', 'min nächte', 'minimum nächte']
available_words = ['verfügbarkeit', 'verfügbar']
overall_slots = ['preis', 'kosten', 'nächte', 'min nächte', 'minimum nächte', 'verfügbarkeit', 'verfügbar']

#Regex function to get the wanted input extracted(Felix)
def get_specific_from_input(sentence, regex_list):
    for regex in regex_list:
        match = re.search(regex, sentence)
        if match:
            # if a regex matches the input: return the regex
            return regex
    # return None if no regular expression matches the input
    return None


def get_location_from_input(sentence, regex_list=location_regex):
    """
    get valid location names from user input using RegEx
    """
    # iterate through regular expressions and associated values in regex_list
    for regex, value in regex_list:
        match = re.search(regex, sentence)
        if match:
            # if a regex matches the input: return the corresponding value
            return value
    # return None if no regular expression matches the input
    return None


def query_sql(key, value, columns, sql_file):
    """
    Query a sqlite file for entries where "key" has the value "value".
    Return the values corresponding to columns as a list.
    """

    # set up sqlite connection
    conn = sql.connect(sql_file)
    c = conn.cursor()


    # prepare query string
    query_template = 'SELECT {columns} FROM listings WHERE {key} = "{value}"'
    columns_string = ', '.join(columns)  # e.g. [location, price] -> 'location, price'
    # replace the curly brackets in query_template with the corresponding info
    query = query_template.format(columns=columns_string, key=key, value=value)

    # execute query
    r = c.execute(query)
    # get results as list
    results = r.fetchall()

    # close connection
    conn.close()

    return results

def take_third(elem):
    return elem[2]

def take_fourth(elem):
    return elem[3]

def take_fifth(elem):
    return elem[4]

def airbnb_bot(sql_file, top_n):
    """
    find flats in a given location.
    main steps:
    1) get input sentence from the user; normalize upper/lowercase
    2) extract the location name from the user input
    3) query sql_file for flats in the given location
    4) print the top_n results
    """

    # (Step 0: make sure sql_file exists)
    if not isfile(sql_file):
        # raise an error if the file is not found
        raise FileNotFoundError(
            'Die Datei {} konnte nicht gefunden werden!'.format(sql_file)
            )

    #########################################
    # STEP 1: say hi and ask for user input #
    #########################################

    print('Hallöchen!\n')

    # print available neighbourhoods
    neighbourhoods = [
        'Charlottenburg-Wilm.', 'Friedrichshain-Kreuzberg',
        'Lichtenberg', 'Marzahn - Hellersdorf', 'Mitte', 'Neukölln', 'Pankow',
        'Reinickendorf', 'Spandau', 'Steglitz - Zehlendorf',
        'Tempelhof - Schöneberg', 'Treptow - Köpenick']
    print('Wir haben Appartements in folgenden Stadtteilen:')
    print(', '.join(neighbourhoods))
    # Information für den User, welche Wörter den bot beenden (Lilith)
    print('Um das Gespräch zu beenden, schreibe "stop", "cancel" oder "tschüss".')
    
    
    #Loop für mehrfachen Input (Felix)
    while(True):
        # get query from user
        sentence = input('\nWo möchtest du denn übernachten?\n')
        # normalize to lowercase
        sentence = sentence.lower()
        #stop the Chatbot if a Word in stop_words is written (Felix)
        if sentence in stop_words:
            print('Ich hoffe ich konnte helfen. Einen schönen Tag noch!')
            break;

        # NLU -SPRACHVERSTEHEN

        # extract location from user input
        location = get_location_from_input(sentence)
        

        if location is None:
            # if the user input doesn't contain valid location information:
                # apologize & quit
            print('\nEntschuldigung, das habe ich leider nicht verstanden...')
        # if there are no results: apologize & quit
        else:
             # get matches from csv file
            columns = ['name', 'neighbourhood', 'price', 'minimum_nights', 'availability_365']
            results = query_sql(
                key='neighbourhood_group', value=location,
                columns=columns, sql_file=sql_file
                )
            if len(results) == 0:
                 print('Tut mir Leid, ich konnte leider nichts finden!')
 
            else: 
                #Abfrage zu Spezifikationen der Anzeige (Felix)
                specifics = input('Möchtest du deine Suche weiter eingrenzen?\n') #änderung nele
                specifics = specifics.lower()
                
                specifics = get_specific_from_input(specifics, positive_answers)
                if specifics in positive_answers:
                    print('Welche Spezifikation möchtest du angeben?')
                    slots = input('Wir haben: Preis, Minimum Nächte, Verfügbarkeit\n')
                    slots = slots.lower()
                    
                    slots = get_specific_from_input(slots, overall_slots)
                    
                    if slots in pricing_words:
                        # Sorted by best result OR lowest price (Lilith)
                        # return results sorted by lowest price
                        pricing = input('\nSuchst du ein Zimmer für wenig Geld?\n')
                        pricing = pricing.lower()
                        if pricing in positive_answers:
                            print('Ich habe {} passende Wohnungen in {} gefunden.\n'.format(
                                len(results), location))
                            print('Hier sind die {} günstigsten Ergebnisse:\n'.format(top_n))
                            
                            resultprice = sorted(results, key=take_third)
                            
                            # print the first top_n entries from the results list
                            for r in resultprice[:top_n]:
                                
                                answer = '"{}", {}. Das Apartment kostet {}€.'.format(
                                    # look at the columns list to see what r[0], r[1], r[2] are referring to!
                                    r[0], r[1], r[2]
                                    )
                                
                                print(answer)
                        else:
                             # print the first top_n entries from the results list ignoring the price
                             # return results
                            print('Ich habe ohne Spezifikationen {} passende Wohnungen in {} gefunden.\n'.format(
                                len(results), location))
                            print('Hier sind die {} besten Ergebnisse:\n'.format(top_n))
                            
                            # print the first top_n entries from the results list
                            for r in results[:top_n]:
                                answer = '"{}", {}. Das Apartment kostet {}€.'.format(
                                    # look at the columns list to see what r[0], r[1], r[2] are referring to!
                                    r[0], r[1], r[2]
                                    )
                                print(answer)
                                
                    #Spezifische Ausgabe für Minimum Nights (Felix)
                    elif slots in nights_words:
                        nights = input('\nWie viele Nächte soll die Wohnung als Mindestzahl anbieten?\n')
                        
                        if nights.isdigit():
                            resultnights = sorted(results, key=take_fourth)
                            minimum_nights_result = []
                            for i in resultnights:
                                min_night = i[3]
                                if min_night >= int(nights):
                                    minimum_nights_result.append(i)
                            if len(minimum_nights_result) == 0:
                                print('Es gibt kein Angebot mit der Mindestanzahl an Nächten.\n')
                            else:
                                print('Ich habe {} passende Wohnungen in {} gefunden.\n'.format(
                                    len(minimum_nights_result), location))
                                print('Hier sind die {} besten Ergebnisse:\n'.format(top_n))
                                
                                for r in minimum_nights_result[:top_n]:
                                    answer = '"{}", {}. Das Apartment kostet {}€. Die Mindestanzahl an Nächten ist {}.'.format(
                                    r[0], r[1], r[2], r[3]
                                    )
                                    print(answer)
                        else:
                            print('Tut mir leid, Sie müssen eine Zahl angeben.')
                            
                    #Spezifische Ausgabe für Availability (Felix)    
                    elif slots in available_words:
                        days = input('\nWie viele Tage im Jahr soll die Wohnung zur Verfügung stehen?\n')
                        
                        if days.isdigit() and int(days) < 366:
                            resultdays = sorted(results, key=take_fifth)
                            days_result = []
                            for i in resultdays:
                                d = i[4]
                                if d >= int(days):
                                    days_result.append(i)
                            if len(days_result) == 0:
                                print('Es gibt kein Angebot mit dieser Anzahl an verfügbaren Tagen im Jahr\n')
                            else:
                                print('Ich habe {} passende Wohnungen in {} gefunden.\n'.format(
                                    len(days_result), location))
                                print('Hier sind die {} besten Ergebnisse:\n'.format(top_n))
                                
                                for r in days_result[:top_n]:
                                    answer = '"{}", {}. Das Apartment kostet {}€. Die verfügbaren Tage im Jahr sind {}.'.format(
                                    r[0], r[1], r[2], r[4]
                                    )
                                    print(answer)
                        else:
                            print('Tut mir leid, Sie müssen eine Zahl angeben zwischen 1 und 365.')
                    else:
                        print('Tut mir leid, mit dieser Spezifikation kann ich nicht dienen.\n')
       
                    
               
                                
                else:
                
                
                    print('Ich habe ohne Spezifikationen {} passende Wohnungen in {} gefunden.\n'.format(
                        len(results), location))
                    print('Hier sind die {} besten Ergebnisse:\n'.format(top_n))
                    
                    # print the first top_n entries from the results list
                    for r in results[:top_n]:
                        answer = '"{}", {}. Das Apartment kostet {}€.'.format(
                            # look at the columns list to see what r[0], r[1], r[2] are referring to!
                            r[0], r[1], r[2]
                            )
                        print(answer)
                
            
                    
                    
            # Grounding (Lilith)
                    
            print('\nBist du mit den Ergebnissen deiner Suche zufrieden?')
        
            ground_words = ['ja', 'klar', 'danke']
            ground = input('\n Falls etwas für dich dabei ist, antworte mit "ja".\n')
            # normalize to lowercase
            ground = ground.lower()
            # stop the Chatbot if a word in ground_words is written
            if ground in ground_words:
                print('Schön, dass du etwas gefunden hast!')
                break;

            # nachfrage, ob der nutzer eine neue suche starten will, sonst verabschiedung (nele)
            else:
                restart = input("Schade, dass du nichts gefunden hast. Wenn du eine neue Anfrage starten willst, antworte mit 'ja'.\n")
                restart = restart.lower()
                if restart != 'ja':
                    print("Ok, schade. Ich wünsche dir noch einen schönen Tag!")
                    break



        
                    
                    
                    
                    


if __name__ == '__main__':
    #  the airbnb_bot() function is called if the script is executed!
    airbnb_bot(sql_file='listings.db', top_n=10)
