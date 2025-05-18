
#debugging
#import pdb

class TrieNode:
    # Trie node class
    def __init__(self):
        #27th node is a dummy node 
        self.children = [None] * 27
        self.terminalNode = False

class Trie:

    def __init__(self,words):
        self.root = TrieNode()
        for word in words:
            self.insert_key(word)
    
    def insert_key(self, word):
    # Initialize the currentNode pointer
    # with the root node
        currentNode = self.root

    # Iterate across the length of the string
        for c in word:
        # Check if the node exist for the current
        # character in the Trie.
            if currentNode.children[ord(c) - ord('a')] == None:
            # If node for current character does not exist
            # then make a new node
                newNode = TrieNode()

            # Keep the reference for the newly created
            # node.
                currentNode.children[ord(c) - ord('a')] = newNode

        # Now, move the current node pointer to the newly
        # created node.
            currentNode = currentNode.children[ord(c) - ord('a')]
        currentNode.terminalNode = True

    def start_search_possible_matches(self,word,typoTolerance):
        return self.__search_for_possible_matches(self.root,word,typoTolerance,0,0,0)
    
    #recursive function for typo check
    def __search_for_possible_matches(self,currentNode,word,typoTolerance,typoEncountered,depth,wordindex):
        
        #used mostly if the node is a terminal one and the word is still not finished
        verdictTerminalNode = False

        char = '{'#27th caracter for bogus path
        if len(word)-1 >= wordindex:#this is to not take characters outside of bounderies
            char = word[wordindex]

        if typoTolerance < typoEncountered:
            return False

        if currentNode.terminalNode == True:
            OverAllTypos = typoEncountered + max(0,(len(word) - wordindex))#the typos if the word is not finished are all the remaining to check which are considered errors
            verdictTerminalNode = typoEncountered + OverAllTypos <= typoTolerance#if all the typos got are good to go

        if currentNode.children[ord(char) - ord('a')] is None:
            for i in range(26):#take every path
                if currentNode.children[i] is not None:
                    #case in which the word has incorect letter on the current position
                    verdict1 = self.__search_for_possible_matches(currentNode.children[i],word,typoTolerance,typoEncountered+1,depth+1,wordindex+1)
                    #case in which the word is missing a letter in the current position
                    verdict2 = self.__search_for_possible_matches(currentNode.children[i],word,typoTolerance,typoEncountered+1,depth+1,wordindex)
                    if verdict1 | verdict2 == True:
                        return True
            verdict3 = False
            if wordindex - 1 >= 0:
                #case in which the word has an extra letter in the current position
                verdict3 = self.__search_for_possible_matches(currentNode,word,typoTolerance,typoEncountered+1,depth,wordindex+1)
                if verdict3 == True:
                    return True
        else:
            #best case scenario we have a match so we take that path
            return verdictTerminalNode or self.__search_for_possible_matches(currentNode.children[ord(char) - ord('a')],word,typoTolerance,typoEncountered,depth+1,wordindex+1)
        
        return verdictTerminalNode or False#the worst case scenario comes here if everything is wrong
    


#word = "cu"
#words = ['calciu']
#trie = Trie(words)
#pdb.set_trace()

#print(trie.start_search_possible_matches(word,1))
