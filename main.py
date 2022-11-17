import random
import os
import time
import math
from colorama import Fore, Style


class Player:
  def __init__(self, card1, card2, money, points, isAllIn, choice=""):
    self.card1 = card1
    self.card2 = card2
    self.money = money
    self.points = points
    self.isAllIn = isAllIn
    self.choice = choice


class Card:
  def __init__(self, suit, val):
    self.suit = suit
    self.val = val

  # resets the values of the card
  def restart(self):
    self.suit = "?"
    self.val = "?"

  # returns a printable string value the card
  def display(self, isRevealed=False):
    if isRevealed:
      return f"{self.suit}{self.val}"
    return "?"


clearL = lambda: os.system('clear')
potMoney = 0
suits = ["\u2663", "\u2666", "\u2660", "\u2665"]
numbers = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
usedCards = []
moveChoices = ["r", "ch", "ca", "f"]

player = Player(Card("?", "?"), Card("?", "?"), 0, 0, False)
computer = Player(Card("?", "?"), Card("?", "?"), 0, 0, False)

roundNumber = 0
cardCount = 0
computer.money = 0
communityCards = [Card("?", "?"),
                  Card("?", "?"),
                  Card("?", "?"),
                  Card("?", "?"),
                  Card("?", "?")]
notEnough = 0
notCompEnough = 0
isBluff = False


def printInstructions():
  print(
    "Warning: Entering a wrong option will automatically be a fold!\nAndy's Poker Game is not liable for any losses!\n"
  )

# checks if a card is in a list
def isCardInList(card, list):
  for c in list:
    if doCardsMatch(card, c):
      return True
  return False

# checks if two cards are exactly the same
def doCardsMatch(card1, card2):
  return (card1.val == card2.val and card1.suit == card2.suit)

# converts the string value of a card to the appropriate integer value
def convert(card, isA1=False):
  if card.val == "K":
    return 13
  elif card.val == "Q":
    return 12
  elif card.val == "J":
    return 11
  elif card.val == "A":
    if isA1:
      return 1
    else:
      return 14
  else:
    return int(card.val)


# adds points to the ranking of a hand based on the cards value
def highNumber(points, cardOne, cardTwo, isSecondHigh):
  rankPoints1 = convert(cardOne) * 0.001
  rankPoints2 = convert(cardTwo) * 0.001
  
  if isSecondHigh == False:
    if rankPoints1 > rankPoints2:
      return (points + rankPoints1)
    elif rankPoints2 > rankPoints1:
      return (points + rankPoints2)
    else:
      return (points)
  else:
    return (points + rankPoints1 + rankPoints2)


# calculates the ranking of a hand
def whoWins(points, cardOne, cardTwo):
  global communityCards
  global cardCount
  
  points = 0
  isFullHouse = False
  isStraight = False
  isBigStraight = False
  isFourKind = False
  isFlush = False
  isRoyalFlush = False
  isStraightFlush = False
  isThreeKind = False
  isPair = False
  isTwoPair = False
  straightHigh = 0
  flushHigh = 0
  threeHigh = 0
  pairHigh = 0
  fullHigh = 0
  fourHigh = 0
  pairSecondHigh = 0
  availCards = [cardOne, cardTwo]
  numsInStraight = []
  cardsInStraight = []
  numsInFlush = []
  cardsInFlush = []
  cardPairs = {}
  pairs = {}
  threePairs = {}
  fourPairs = {}

  # creates a list of cards that have been revealed and can be used to calculate the ranking of a hand
  locCardCount = cardCount
  if locCardCount > 5:
    locCardCount = 5
  unrankedCards = {
    convert(cardOne, True): cardOne,
    convert(cardTwo, True): cardTwo
  }
  for i in range(locCardCount):
    unrankedCards[convert(communityCards[i], True)] = communityCards[i]
    availCards.append(communityCards[i])

  # puts the cards available in order from least to highest value
  keyList = unrankedCards.keys()
  sortedKeys = sorted(keyList)
  
  # calculates a 10, J, Q, K, A straight
  if 1 in sortedKeys and 13 in sortedKeys and 12 in sortedKeys and 11 in sortedKeys and 10 in sortedKeys:
    isStraight = True
    isBigStraight = True
    straightHigh = 14

    # keeps track of cards that are in the straight
    cardsInStraight.append(unrankedCards[1])
    cardsInStraight.append(unrankedCards[13])
    cardsInStraight.append(unrankedCards[12])
    cardsInStraight.append(unrankedCards[11])
    cardsInStraight.append(unrankedCards[10])
  else:
    # calculates a normal straight
    for i in range(len(sortedKeys) - 1):
      # since sortedKeys is already in ascending order the difference of the current element and next element must equal -1 in order for them to be sequential
      if sortedKeys[i] - sortedKeys[i + 1] in [0,-1]:
        # keeps track of the number values and the cards in the straight
        if i == 0:
          numsInStraight.append(sortedKeys[i])
          numsInStraight.append(sortedKeys[i + 1])
          cardsInStraight.append(unrankedCards[sortedKeys[i + 1]])
          cardsInStraight.append(unrankedCards[sortedKeys[i]])
        else:
          numsInStraight.append(sortedKeys[i + 1])
          cardsInStraight.append(unrankedCards[sortedKeys[i + 1]])
      else:
        # clears the two lists if sortedKeys[i] and sortedKeys[i+1] are not sequential and if a straight has not been found. If a straight has been found, ends the loop
        if len(list(dict.fromkeys(numsInStraight))) < 5:
          numsInStraight.clear()
          cardsInStraight.clear()
        else:
          break
          
  # checks if a straight has been found and calculates the ranking of that straight if there is one
  if len(list(dict.fromkeys(numsInStraight))) >= 5:
    isStraight = True
    if max(numsInStraight) > straightHigh:
      straightHigh = max(numsInStraight)
      
  # calculates if there is a flush
  flushCounter = 1
  # used range(len(availCards)-4) because if i is at the end of the range and a flush has not been found yet, then a flush does not exist
  for i in range(len(availCards)-4):
      cardsInFlush.append(availCards[i])
      for j in range(i+1,len(availCards)):
        if availCards[i].suit == availCards[j].suit:
          cardsInFlush.append(availCards[j])
          flushCounter += 1
      if flushCounter >= 5:
        isFlush = True
        break
      else:
        flushCounter = 1
        cardsInFlush.clear()

  # finds the highest card value in the flush
  if isFlush:
    for card in cardsInFlush:
      numsInFlush.append(convert(card))
    flushHigh = max(numsInFlush)

  # sorts matching cards into a dictionary called cardPairs {cardValue: [Card]}

  for i in availCards:
    for j in range(availCards.index(i), len(availCards)):
      if not (doCardsMatch(i, availCards[j])) and i.val == availCards[j].val:
        if not (convert(i) in cardPairs.keys()):
          cardPairs[convert(i)] = [i, availCards[j]]
        else:
          if not (availCards[j] in cardPairs[convert(i)]):
            cardPairs[convert(i)].append(availCards[j])
  
  # determines whether there is a three of a kind, four of a kind, or a two pair
  for pairNumber in cardPairs:
    if len(cardPairs[pairNumber]) == 3:
      isThreeKind = True
      if pairNumber > threeHigh:
        threeHigh = pairNumber
      threePairs[pairNumber] = cardPairs.get(pairNumber)
    elif len(cardPairs[pairNumber]) == 4:
      isFourKind = True
      if pairNumber > fourHigh:
        fourHigh = pairNumber
      fourPairs[pairNumber] = cardPairs.get(pairNumber)
    elif len(cardPairs[pairNumber]) == 2:
      isPair = True
      if pairNumber > pairHigh:
        pairHigh = pairNumber
      pairs[pairNumber] = cardPairs.get(pairNumber)

  # calculates the high card for each type of hand
  if isThreeKind and isPair:
    isFullHouse = True
    fullHigh = threeHigh
  elif isPair:
    for i in pairs:
      if i > pairSecondHigh and i < pairHigh:
        pairSecondHigh = i
  if len(pairs) >= 2:
    isTwoPair = True

  #calculates if there is a straight flush or royal flush
  flushCounter = 1
  if isStraight:
    for i in range(len(cardsInStraight)-4):
      for j in range(i+1,len(cardsInStraight)):
        if cardsInStraight[i].suit == cardsInStraight[j].suit:
          flushCounter += 1
      if flushCounter >= 5:
        if isBigStraight:
          isRoyalFlush = True
        isStraightFlush = True
        break
      else:
        flushCounter = 1

  # calculates the number of points based on the hand
  if isRoyalFlush:
    points = 24
  elif isStraightFlush:
    points = 21 + straightHigh * 0.01
  elif isFourKind:
    points = 18 + fourHigh * 0.01
    if isPair:
      points += 1 + pairHigh * 0.01
  elif isFullHouse:
    points = 15 + fullHigh * 0.01 + pairHigh * 0.001
  elif isFlush:
    points = 12 + flushHigh * 0.01
    if isThreeKind:
      points += 2 + threeHigh * 0.001
    elif isTwoPair:
      points += 1 + pairHigh * 0.01 + pairSecondHigh * 0.001
    elif isPair:
      points += pairHigh * 0.01
  elif isStraight:
    points = 9 + straightHigh * 0.01
    if isThreeKind:
      points += 2 + threeHigh * 0.001
    elif isTwoPair:
      points += 1 + pairHigh * 0.01 + pairSecondHigh * 0.001
    elif isPair:
      points += pairHigh * 0.01
  elif isThreeKind:
    points = 6 + threeHigh * 0.01
  elif isTwoPair:
    points = 3 + pairHigh * 0.01 + pairSecondHigh * 0.001
  elif isPair:
    points = 1 + pairHigh * 0.01

  return points


def printCommCards():
  global potMoney
  global cardCount
  global player
  global computer
  global communityCards

  print("Pot: $" + str(potMoney))

  print("\nCommunity cards: \n")

  for i in range(5):
    if i >= cardCount:
      print(communityCards[i].display() + "   ", end='')
    else:
      if communityCards[i].suit == suits[1] or communityCards[i].suit == suits[
          3]:
        print(Fore.RED + communityCards[i].display(True) + "   ", end='')
        print(Style.RESET_ALL, end='')
      else:
        print(communityCards[i].display(True) + "   ", end='')

  print("\n")
  print("-----------------------------------------------\n")


def printComputerInfo():
  global computer
  global cardCount
  print("Computer's cash: $", int(round(computer.money)), "\n", sep='')
  if cardCount == 6:
    print("Computer's cards: ")
    if computer.card1.suit == suits[1] or computer.card1.suit == suits[3]:
      print(Fore.RED + computer.card1.display(True) + ", ", end='')
      print(Style.RESET_ALL, end='')
    else:
      print(computer.card1.display(True) + ", ", end='')
    if computer.card2.suit == suits[1] or computer.card2.suit == suits[3]:
      print(Fore.RED + computer.card2.display(True) + "\n\n", end='')
      print(Style.RESET_ALL, end='')
    else:
      print(computer.card2.display(True) + "\n\n", end='')
  else:
    print("Computer's cards: \n" + "?, " + "?\n")
  print("-----------------------------------------------\n")


def printUserInfo():
  global player

  print("Your cash: $" + str(int(round(player.money))) + "\n")
  print("Your cards: ")
  if player.card1.suit == suits[1] or player.card1.suit == suits[3]:
    print(Fore.RED + player.card1.display(True) + ", ", end='')
    print(Style.RESET_ALL, end='')
  else:
    print(player.card1.display(True) + ", ", end='')
  if player.card2.suit == suits[1] or player.card2.suit == suits[3]:
    print(Fore.RED + player.card2.display(True) + "\n\n", end='')
    print(Style.RESET_ALL, end='')
  else:
    print(player.card2.display(True) + "\n\n", end='')


#procedure when someone folds
def foldProcedure():
  global potMoney
  global cardCount
  global player
  global computer
  global notEnough
  global notCompEnough
  global communityCards
  
  player.card1.restart()
  player.card2.restart()
  computer.card1.restart()
  computer.card2.restart()
  for card in communityCards:
    card.restart()
  notEnough = 0
  notCompEnough = 0
  cardCount = 0
  player.isAllIn = False
  computer.isAllIn = False

  choice = input("Would you like to play another round (y/n)? ")
  potMoney = 0

  if choice == 'y':
    initialProcedure()
  else:
    clearL()
    print("Thanks for playing!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("You had: $", player.money, sep='')


#procedure for a normal round of poker
def procedure():
  global roundNumber
  global potMoney
  global communityCards
  global cardCount
  global notEnough
  global notCompEnough
  global isBluff
  global player
  global computer

  if player.isAllIn or computer.isAllIn:
    cardCount = 6
  
  printInstructions()
  printComputerInfo()
  printCommCards()
  printUserInfo()

  if cardCount <= 5:
    player.choice = input(
      "Would you like to check(ch), raise(r), or fold(f)? ")
    # computer makes decisions based on user's decision and based on the computer's hand
    if player.choice == "ch":
      print("The computer is thinking...")
      time.sleep(1.5)
      computer.points = whoWins(computer.points, computer.card1,
                                computer.card2)
      if computer.points >= 1:
        computer.choice = moveChoices[0]
      else:
        if random.randint(0, 9) == 1:
          isBluff = True
          computer.choice = moveChoices[0]
        else:
          computer.choice = moveChoices[1]
      if computer.choice == "ch":
        print("The computer chose to check!")
        time.sleep(1.5)
        clearL()
        cardCount += 1
        procedure()
      else:
        if isBluff:
          if computer.money > 500:
            computer.choice = random.randint(math.floor(0.05 * computer.money),
                                             math.floor(0.35 * computer.money))
            while int(computer.choice) > computer.money:
              computer.choice = random.randint(
                math.floor(0.05 * computer.money),
                math.floor(0.35 * computer.money))
          else:
            computer.choice = random.randint(math.ceil(0.05 * computer.money),
                                             math.ceil(0.45 * computer.money))
            while int(computer.choice) > computer.money:
              computer.choice = random.randint(
                math.ceil(0.05 * computer.money),
                math.ceil(0.45 * computer.money))
        else:
          if computer.points >= 2:
            if computer.money > 500:
              computer.choice = random.randint(
                math.floor(0.05 * computer.money),
                math.floor(0.35 * computer.money))
              while int(computer.choice) > computer.money:
                computer.choice = random.randint(
                  math.floor(0.05 * computer.money),
                  math.floor(0.35 * computer.money))
            else:
              computer.choice = random.randint(math.ceil(0.1 * computer.money),
                                               math.ceil(0.5 * computer.money))
              while int(computer.choice) > computer.money:
                computer.choice = random.randint(
                  math.ceil(0.1 * computer.money),
                  math.ceil(0.5 * computer.money))
          else:
            computer.choice = random.randint(1,
                                             math.ceil(0.1 * computer.money))
            while int(computer.choice) > computer.money:
              computer.choice = random.randint(
                1, math.ceil(0.01 * computer.money))

        potMoney += computer.choice
        computer.money -= computer.choice
        print("The computer chose to raise the bet to $",
              computer.choice,
              sep='')
        player.choice = input("Would you like to call(ca) or fold(f)? ")
        if player.choice == "ca":
          if player.money <= computer.choice:
            print("You went all in!")
            player.isAllIn = True
            potMoney += player.money
            notEnough = computer.choice - player.money
            player.money = 0
            cardCount = 6
          else:
            player.money -= computer.choice
            potMoney += computer.choice
            cardCount += 1
          time.sleep(1)
          clearL()
          procedure()
        else:
          print("You folded! :(")
          computer.money += potMoney
          potMoney = 0
          cardCount = 0
          foldProcedure()
    elif player.choice == "r":
      try:
        player.choice = int(input("How much money would you like to put in? "))
      except:
        print("You folded!")
        foldProcedure()
      while player.choice > player.money:
        print("You don't have enough money!")
        try:
          player.choice = int(
            input("How much money would you like to put in? "))
        except:
          print("You folded!")
          foldProcedure()

      player.money -= player.choice
      potMoney += player.choice
      print("The computer is thinking...")
      time.sleep(1.5)
      computer.points = whoWins(computer.points, computer.card1,
                                computer.card2)

      if computer.money >= 100:
        if player.choice >= math.floor(
            0.1 * computer.money) and player.choice <= math.floor(
              0.2 * computer.money) and computer.points >= 2:
          computer.choice = moveChoices[2]
        elif player.choice >= math.floor(
            0.2 * computer.money) and computer.points < 3:
          computer.choice = moveChoices[3]
        elif player.choice >= math.floor(
            0.2 * computer.money) and computer.points >= 3:
          computer.choice = moveChoices[2]
        elif player.choice < math.floor(0.1 * computer.money):
          computer.choice = moveChoices[2]
        else:
          computer.choice = moveChoices[random.randint(2, 3)]
      else:
        if player.choice >= math.floor(
            0.2 * computer.money) and player.choice <= math.floor(
              0.5 * computer.money) and computer.points >= 2:
          computer.choice = moveChoices[2]
        elif player.choice >= math.floor(
            0.5 * computer.money) and computer.points < 3:
          computer.choice = moveChoices[3]
        elif player.choice >= math.floor(
            0.5 * computer.money) and computer.points >= 3:
          computer.choice = moveChoices[2]
        elif player.choice < math.floor(
            0.2 * computer.money) and computer.points >= 1:
          computer.choice = moveChoices[2]
        else:
          computer.choice = moveChoices[random.randint(2, 3)]
      if computer.choice == 'ca':
        if computer.money <= player.choice:
          print("The computer chose to go all in!")
          computer.isAllIn = True
          potMoney += computer.money
          notCompEnough = player.choice - computer.money
          computer.money = 0
          cardCount = 6
        else:
          print("The computer chose to call!")
          computer.money -= player.choice
          potMoney += player.choice
          cardCount += 1
        time.sleep(1.5)
        clearL()
        procedure()
      elif computer.choice == 'f':
        print("The computer chose to fold! :(")
        player.money += potMoney
        potMoney = 0
        cardCount = 0
        foldProcedure()
    else:
      print("You folded! :(")
      computer.money += potMoney
      cardCount = 0
      foldProcedure()
  else:
    player.points = 0
    computer.points = 0
    player.points = whoWins(player.points, player.card1, player.card2)
    computer.points = whoWins(computer.points, computer.card1, computer.card2)
    
    if player.points == computer.points:
      player.points = highNumber(player.points, player.card1, player.card2,
                                False)
      computer.points = highNumber(computer.points, computer.card1,
                                   computer.card2, False)
      if player.points == computer.points:
        player.points = highNumber(player.points, player.card1, player.card2,
                                  True)
        computer.points = highNumber(computer.points, computer.card1,
                                     computer.card2, True)
    
    if player.points == computer.points:
      print("It's a tie")
      player.money += math.floor(potMoney / 2)
      computer.money += math.floor(potMoney / 2)
      foldProcedure()
    elif player.points > computer.points:
      if computer.money == 0:
        print("The computer is bankrupt! You win! :D")
      else:
        print("You win! :)")
        if player.isAllIn == True:
          potMoney -= notEnough
          computer.money += notEnough
        player.money += potMoney
        foldProcedure()
    else:
      if player.money == 0:
        print("You're bankrupt! :(")
      else:
        print("You lost! :(")
        if computer.isAllIn == True:
          potMoney -= notCompEnough
          player.money += notCompEnough
        computer.money += potMoney
        foldProcedure()


def deal():
  global usedCards
  
  while True:
    card = Card(random.choice(suits), random.choice(numbers))
    if not isCardInList(card, usedCards):
      usedCards.append(card)
      return card


#procedure for the poker game pre-flop



def initialProcedure():
  global potMoney
  global roundNumber
  global cardCount
  global player
  global computer
  global usedCards
  global communityCards

  clearL()

  printInstructions()
  printComputerInfo()
  printCommCards()

  # deals cards to the computer and the player

  player.card1 = deal()
  player.card2 = deal()
  computer.card1 = deal()
  computer.card2 = deal()

  printUserInfo()

  print("You are small blind so you must put in $1")
  potMoney += 1
  player.money -= 1
  if computer.money <= 2:
    print("The computer is going all in!")
    potMoney += computer.money
    computer.money = 0
    computer.isAllIn = True
  else:
    print("The computer is big blind and puts in $2")
    computer.money -= 2
    potMoney += 2
  if player.money <= 1:
    print("You're going all in!")
    potMoney += player.money
    player.money = 0
    player.isAllIn = True
    time.sleep(1.5)
  else:
    player.choice = input(
      "Would you like to put in another $1 (p) or fold (f)? ")
    if player.choice == "p":
      clearL()
      player.money -= 1
      potMoney += 1
      roundNumber += 1
      cardCount = 3
    else:
      computer.money += potMoney
      potMoney = 0
      print("You folded!")
      foldProcedure()
      
  for i in range(len(communityCards)):
    communityCards[i] = deal()
  
  procedure()


def checkNumber():
  global player
  global computer
  try:
    player.money = int(input("How much money would you like to have: "))
    while player.money < 5:
      print("You need at least $5!")
      player.money = int(input("How much money would you like to have: "))
  except:
    print("That's not a number!")
    checkNumber()


started = input("Type 's' to begin the game: ")
clearL()
print("Welcome to Andy's Poker Game!!!!! It's you vs. the computer.\n")
printInstructions()
checkNumber()
computer.money = player.money
initialProcedure()
