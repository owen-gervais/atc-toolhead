# Basic Card class with the ability to add a name
from types import NoneType
from typing import List
import random


class Game: 

    def __init__(self, numPlayers) -> None:
        "Player name: Owen, Deck Choice:"
        "Use the player name to authenticate the device joining the game"
        self.numPlayers = numPlayers
        player1 = Player("Owen", "/Users/owengervais/Downloads/Deck - Jund Control.txt")
        player2 = Player("Scott", "/Users/owengervais/Downloads/Deck - Boros Aggro.txt")
        self.players = [player1, player2]
        self.starting = True

    def isStarting(self): 
        return self.starting



class Player:

    def __init__(self, name, deckPath, life=20) -> None:
        self.STARTING_HAND_SIZE = 7
        self.discardCnt = 0
        self.name = name
        self.life = life
        self.deck = Deck(deckPath)
        self.hand = []
        self.graveyard = []

    def draw(self, numCards=1):
        # Take nCards top card off the deck
        for i in range(numCards):
            self.hand.append(self.deck.mainDeck[i])
            self.deck.mainDeck.pop(0)

    def discard(self, index=1, random=False) -> None:
        '''
        discard():
            discard the card at the current
            index: card in the hand list
            By default discards the first card in hand, leftmost
        '''
        if random: 
            index = random.randrange(len(self.hand))
        self.graveyard.append(self.hand[index-1])
        self.hand.pop(index-1)
        return None
    
    def setLife(self, amount: int) -> None: 
        self.life += amount

    def getHand(self) -> None:
        '''
        printHand():

            Output current hand of the player
        '''
        for index, card in enumerate(self.hand):
            print("  {}. {}".format(index+1,card))
        return None

    def getGraveyard(self) -> None:
        for index, card in enumerate(self.graveyard):
            print("  {}. {}".format(index+1,card))
        return None


class Hand:

    def __init


class Deck:
    '''
    Deck:

        This class takes in a plain text representation of a deck and sideboard 
        in MTG and creates main deck and sideboard with the corresponding card 
        names and quantities. 
    '''
    def __init__(self, filename) -> None:
        self.name = filename.split(" - ",maxsplit=1)[1].strip(".txt")
        self.mainDeck, self.sideboard = self.parseDeckFile(filename)

    def parseDeckFile(self,filename) -> List:
        '''
        parseDeckFile(): Takes in a filename and parses into main deck 
        and sideboard lists
        '''
        newMainDeck, newSideboard = ([] for i in range(2))
        with open(filename) as fp:
            line = fp.readline()
            populatingMainDeck = True # set the 
            while line:
                try: 
                    quantity, cardName = line.strip().split(" ",maxsplit=1) 
                    quantity = int(quantity)
                    while quantity:
                        if populatingMainDeck:
                            newMainDeck.append(cardName)
                        else: 
                            newSideboard.append(cardName)
                        quantity-=1
                except:
                    populatingMainDeck = False
                    pass
                line = fp.readline()
            return newMainDeck, newSideboard

    def shuffle(self):
        random.shuffle(self.mainDeck)

    def revealTopCard(self):
        '''
        Return the name of the top card on the deck
        '''
        return self.mainDeck[0]

if __name__ == "__main__":

    game = Game(numPlayers=2)
    print("New MTG Game started with {} players".format(game.numPlayers))
    for player in game.players:
        print(" {} is playing {} ".format(player.name, player.deck.name))
        player.deck.shuffle()
        while True:
            choice = input("Draw a card?? ..... \n")
            if choice is not "n":
                player.draw()
            else:
                break
            player.displayHand()
            choice = input("Discard a card? .... \n")
            if choice is not "n":
                player.discard(index = int(choice))
            else:
                break
            player.displayGraveyard()
            
                
            

            
        

        
