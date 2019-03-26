import bs4
import requests
import re
import smtplib
from email.mime.text import MIMEText
import sys


def main(mail):
    previousCardList = buildList(open("previousCard.txt", "r"))
    previousCostList = buildList(open("previousCost.txt", "r"))
    cardList = buildList(open("cardList.txt", "r"))

    open('previousCard.txt', 'w').close()
    open('previousCost.txt', 'w').close() # clear the lists
    while "\n" in cardList: cardList.remove("\n") # just to be sure, had some issues with this.

    cardList.extend(extendCardList("https://www.svenskamagic.com/cardcollection/index.php?action=search&s_name=&s_rules=1*sacrifice*search*your*library*for&s_not_rules=&s_type=&s_not_type=&s_exp=&s_not_exp=&s_artist=&s_flavour=&order=name&view=normal&x=9&y=14&ctype%5B1%5D=1&rarity_r=1&selected_block=Ixalan-block&lager=1&cc_left=0&cc_right=16&cost_choice=is&cost=&power_left=-1&power_right=13&toughness_left=-1&toughness_right=13&red=0&black=0&white=0&blue=0&green=0&multi=0&land=0&hybrid=0&tokens=1&special=1&basicland=1&reprints=0&clan=&guild=&faction=")
) # adds fetches
    cardList.extend(extendCardList("https://www.svenskamagic.com/cardcollection/index.php?action=search&s_name=&s_rules=bb%7Cuu%7Cww%7Crr%7Cgg&s_not_rules=&s_type=&s_not_type=&s_exp=future+sight%7Cshadowmoor%7Ciconic+masters%7Cmasters+25%7Ceventide&s_not_exp=&s_artist=&s_flavour=&order=name&view=normal&x=0&y=0&ctype%5B1%5D=1&rarity_mr=1&rarity_r=1&selected_block=Ixalan-block&lager=1&cc_left=0&cc_right=16&cost_choice=is&cost=&power_left=-1&power_right=13&toughness_left=-1&toughness_right=13&red=0&black=0&white=0&blue=0&green=0&multi=0&land=0&hybrid=0&tokens=1&special=1&basicland=1&reprints=0&clan=&guild=&faction=")
) # adds filterlands
    cardList.extend(extendCardList("https://www.svenskamagic.com/cardcollection/index.php?action=search&s_name=&s_rules=&s_not_rules=&s_type=&s_not_type=&s_exp=battlebond&s_not_exp=&s_artist=&s_flavour=&order=name&view=bildspoiler&x=17&y=15&ctype%5B1%5D=1&rarity_r=1&selected_block=Ixalan-block&cc_left=0&cc_right=16&cost_choice=is&cost=&power_left=-1&power_right=13&toughness_left=-1&toughness_right=13&red=0&black=0&white=0&blue=0&green=0&multi=0&land=0&hybrid=0&tokens=1&special=1&basicland=1&reprints=0&clan=&guild=&faction=")
) # adds battlelands

    searchForCards(cardList, previousCardList, previousCostList,  mail)


def searchForCards(cardList, previousCardList, previousCostList, mail):
    """
    Given a list of cardnames and the results from the last run, querys svm for availability and costs of cards and
    either  prints all of them or sends an email with the relevant differences from the last run.
    :param cardList: a list of strings representing cardnames to search for.
    :param previousCardList: a list of strings representing the found cardnames during the last run
    :param previousCostList: a list of strings representing the found costs of cards during the last run, will have same
    order as previousCostList
    :param mail: a boolean, True if mail should be sent, False if all results should be printed.
    """
    for card in cardList:
        newCards = []
        cardsIWant = requests.get("https://www.svenskamagic.com/cardcollection/index.php?action=search&s_name="+card+"&s_rules=&s_not_rules=&s_type=&s_not_type=&s_exp=&s_not_exp=&s_artist=&s_flavour=&order=name&view=normal&x=19&y=12&selected_block=Ixalan-block&lager=1&cc_left=0&cc_right=16&cost_choice=is&cost=&power_left=-1&power_right=13&toughness_left=-1&toughness_right=13&red=0&black=0&white=0&blue=0&green=0&multi=0&land=0&hybrid=0&tokens=1&special=1&basicland=1&reprints=0&clan=&guild=&faction=")
        soup1 = bs4.BeautifulSoup(cardsIWant.text, 'html.parser')
        noneLeft = soup1.find_all("b", string="0")
        if noneLeft == []:
            cardNames = soup1.find_all("span", attrs={"class" : "text_svart"})
            prices = soup1.find_all("span", attrs={"class" : "text_bla"} )
            inStore = len(cardNames)
            cleanedNames=[]
            cleanedPrices=[]
            for card in cardNames:
                cleanedNames.append(re.sub(r"<.+?>", "", str(card)))
            for price in prices:
                cleanedPrices.append(re.sub(r"<.+?>", "", str(price)))
            for i in range(0,inStore):
                cardstr = ""
                for char in str(cleanedPrices[i]):
                    if char == ":": #only want the integer representing the price for the saved data
                        break
                    else:
                        cardstr = cardstr+char
                if (cleanedNames[i] not in previousCardList):
                    newCards.append("is new: " + cleanedNames[i].strip("\t") + " " + cleanedPrices[i]) # if new card add
                    # it to the list
                else:
                    pricesFound = []
                    indexFound = []
                    cheaper = True
                    for index,item in enumerate(previousCardList):
                        if item == cleanedNames[i]:
                            pricesFound.append(cardstr)
                            indexFound.append(index)
                            for price in pricesFound:
                                if not int(price)*1.2 < int(previousCostList[index]):
                                    cheaper = False
                    if cheaper:
                        newCards.append("is cheaper: " + cleanedNames[i].strip("\t") + " " + cleanedPrices[i]) # if cost has dropped
                        # with more than 20 % add it to the list
                with open("previousCard.txt", "a") as myfile:
                    myfile.write(cleanedNames[i] + ".")
                with open("previousCost.txt", "a") as myfile:
                    myfile.write(cardstr + ". ") # update the saved data
                if not mail:
                    printCardAndCost(cleanedNames[i], cleanedPrices[i])

    
    if not len(newCards) ==0 and mail:
        sendMail(newCards)

def sendMail(newCards):
    """
    Sends an email with the new cards and costs found.  TODO make the email look nice.
    :param newCards: a list of strings to be sent.
    """
    sender_email = "    " # specify sender email
    receiver_email = "" # specify reciever email
    password = "" # specify password

    msg = MIMEText(newCards.__str__())
    msg['Subject'] = "svms results"
    msg['From'] = sender_email
    msg['To'] = receiver_email


    s = smtplib.SMTP_SSL('smtp.gmail.com')
    s.login(sender_email, password)
    s.sendmail(sender_email,receiver_email, msg.as_string())
    s.quit()

def printCardAndCost(card, cost):
    """
    prints all the found cards and costs. TODO make the printout look nicer.
    :param card: a string representing the card to be printed
    :param cost: a string representing the cost to be printed
    """
    card = card.strip()
    width = 30
    difference = width - len(card)
    for i in range(difference):
        card = card + " "
    print card, cost


def buildList(f):
    """
    reads the results from the last run and saves them as lists of strings.
    :param f: the file to be read
    :return: a list of strings.
    """
    cardString = f.read()
    cardString.replace("\n", "")
    return cardString.split(".")


def extendCardList(query):
    """
    adds cards of a specific type to the search, e.g. all lands of a specific type.
    :param query: The string to search for on svm
    :return: a list of cardnames to be added to the search.
    """
    type = requests.get(query)
    soup = bs4.BeautifulSoup(type.text, "html.parser")
    names = soup.find_all("span", attrs={"class" : "text_svart"})
    cleanedNames = []
    for item in names:
       cleanedString = re.sub(r"<.+?>", "", str(item))
       cleanedNames.append(cleanedString)
    return list(set(cleanedNames))



if __name__ == '__main__':
    mail = False
    if len(sys.argv)>1:
        if sys.argv[1] == "mail":
            mail = True
    main(mail)
