import math
import random
from colorama import init as colorama_init
from colorama import Fore, Style


class Wordle:
    def __init__(self):
        self.green_letters = []
        self.green_idx = []
        self.word_freq = {}
        with open('word_frequency.txt') as f:
            # Derived from the google ngram dataset using the api.
            x = f.read().split('\n')
            for line in x:
                temp = line.split(' ')
                self.word_freq[temp[0]] = float(temp[1])
                # Word frequencies for the likelihood that the word is correct

        self.words = list(self.word_freq.keys())  # Gets the words from the word_frequency file
        self.valid_guesses = self.words  # self.valid_guesses is constant
        self.guesses = 0  # Number of guesses made so far

        with open('possible_words.txt', 'r') as f:
            x = f.read().split('\n')
        self.word = random.choice(x)
        # The word for if you are just playing wordle.

        self.colours = [Fore.GREEN, Fore.YELLOW, Fore.WHITE]
        # Initialises a list of colours for the printing

        self.best_word = None
        self.running_high_score = None

    def pretty_print(self, guess, colour_idx=[0] * 5):
        print(f'{self.colours[colour_idx[0]]}{guess[0]}'
              f'{self.colours[colour_idx[1]]}{guess[1]}'
              f'{self.colours[colour_idx[2]]}{guess[2]}'
              f'{self.colours[colour_idx[3]]}{guess[3]}'
              f'{self.colours[colour_idx[4]]}{guess[4]}'
              f'{Style.RESET_ALL}')
        # Prints the colours for wordle

    def guess(self, guess=None):
        self.guesses += 1
        valid_guess = False
        if guess:
            if guess in self.valid_guesses:
                valid_guess = True
        # Removes the unecessary input if you put in a guess.

        while valid_guess is False:
            guess = input()
            if guess in self.valid_guesses:
                valid_guess = True
            # Loops until a valid input is put in.

        if guess == self.word:
            self.pretty_print(guess)  # Prints the word in colour. Defaults to green without the colour_idx parameter.
            print(f'You solved it in {self.guesses} guesses!')
            return True  # True ends the game

        colour_idx = [0,0,0,0,0]
        orange_letters = []
        for u, (g_letter, w_letter) in enumerate(zip(guess, self.word)):
            if g_letter == w_letter:
                orange_letters.append(g_letter)
        for u, (g_letter, w_letter) in enumerate(zip(guess, self.word)):
            if g_letter == w_letter:
                pass
            elif g_letter in self.word:
                word_list = [x for x in self.word]
                for letter in orange_letters:
                    if letter == g_letter:
                        word_list.remove(letter)
                if g_letter in word_list:
                    orange_letters.append(g_letter)
                    colour_idx[u] = 1
                else:
                    colour_idx[u] = 2
            else:
                colour_idx[u] = 2
        # Makes a list of the colours for the use of the pretty_print part.

        self.pretty_print(guess, colour_idx)

        self.poss_words(guess, colour_idx, True)
        # Generates the possible words given the guess, and generates the next guess you should ideally make

    def apply_sigmoid(self, x, x_offset: float = 0, x_stretch: float = 1):
        # Sigmoid function. x_stretch is the compression along the x plane. x_offset is the distance right offset
        return 1 / (1 + math.e ** (-x_stretch * (x - x_offset)))

    def poss_words(self, guess=None, colour_idx=None, saved=False, external=False):  # Saved is whether you want the words list updated.
        if external:
            guess = input('What did you guess?: ')
            green = input('What are the green indexes?: ')
            yellow = input('What are the yellow indexes?: ')
            green = green.split(', ')
            yellow = yellow.split(', ')

            if green == ['']:
                green = []
            if yellow == ['']:
                yellow = []

            for i, g in enumerate(green):
                green[i] = int(g) - 1
            for i, y in enumerate(yellow):
                yellow[i] = int(y) - 1

            black = [0, 1, 2, 3, 4]
            temp = green[:]
            temp.extend(yellow)
            for x in temp:
                black.remove(x)

        else:
            green, yellow, black = [], [], []
            temp_ls = [green, yellow, black]
            for i, idx in enumerate(colour_idx):
                temp_ls[idx].append(i)  # Separates the colour_idx into green, yellow and black indexes

        guess_letters = {}
        for letter in guess:
            try:
                guess_letters[letter] += 1
            except KeyError:
                guess_letters[letter] = 1
        multi_letter = []
        for x, y in guess_letters.items():
            if y > 1:
                multi_letter.append([x, y])
        blk_dict_letters = {}
        for x in black:
            try:
                blk_dict_letters[guess[x]] += 1
            except KeyError:
                blk_dict_letters[guess[x]] = 1

        #for i in green:
        #    self.green_idx.append(i)
        #    self.green_letters.append(guess[i])
            # Will have repeats, but is quicker than iterating through to remove them
        new_list = []
        for word in self.words:
            valid_word = True
            # Need to check for duplicate letters in word, and if there are more in word than guess, and it is
            for idx in green:
                if word[idx] != guess[idx]:
                    valid_word = False
                    break

            if valid_word:
                for idx in yellow:
                    if word[idx] == guess[idx]:
                        valid_word = False
                        break
                    elif guess[idx] not in word:
                        valid_word = False
                        break
                        # If the orange is in the right space it would have been green.

            if valid_word:
                duplicate = len(set(list(guess))) < 5
                for idx in black:
                    ####### need to check for the duplicate case
                    if guess[idx] in word:
                        if duplicate:
                            x = list(guess)
                            guess_count = 1
                            x.remove(guess[idx])
                            while guess[idx] in x:
                                guess_count += 1
                                x.remove(guess[idx])
                            if guess_count == 1:
                                valid_word = False
                                break
                            x = list(word)
                            word_count = 1
                            x.remove(guess[idx])
                            while guess[idx] in x:
                                word_count += 1
                                x.remove(guess[idx])
                            if word_count >= guess_count:
                                valid_word = False
                                break
                            # print(guess_count, word_count)
                            # print(guess[idx], guess, word)
                        else:
                            valid_word = False
                            break

            if valid_word:
                new_list.append(word)

        if saved:
            self.words = new_list
        # else:
        #     for _ in range(len(green)):
        #         self.green_letters.pop()
        #         self.green_idx.pop()

        return len(new_list)

    def get_information(self):
        all_guesses = [[a, b, c, d, e] for a in range(3) for b in range(3)
                       for c in range(3) for d in range(3) for e in range(3)]
        # Sets up a list of all the outcomes of a guess. 

        word_list_length = len(self.words)
        self.running_high_score = -1  # Keeps track of the current high score
        self.best_word = ''  # Keeps track of the current best word

        for i, word in enumerate(self.words):
            total = 0
            for g in all_guesses:  # Iterates through all words and all guesses for those words.
                new_word_list_length = self.poss_words(word, g)  # Gets the number of words left for that outcome
                if new_word_list_length > 0:
                    prob = new_word_list_length / word_list_length  # Probability of it being the right guess
                    s_value = self.apply_sigmoid(self.word_freq[word], x_offset=0.00005, x_stretch=100000)
                    prob *= s_value  # Probability is changed to take into account word frequency
                    information = -math.log2(prob)  # Calculates how many bits of information the guess makes.
                    # Formula for information is -log2 probability
                    total += prob * information

            if total > self.running_high_score:
                self.running_high_score = total
                self.best_word = word
                with open('current_best_word.txt', "w") as f:
                    f.write(word)
                    # Writes the best word so far to file.

            print(f'{round((i + 1) / len(self.words) * 100, 2)}%')

        print(f'Guess: {self.best_word}')
        return self.best_word

    # def blk_exception(self, word, guess, black, green, yellow, idx):
    #     # You already know that the word has a black letter that is also in another place
    #     # There are two possibilities: A yellow or a green.
    #     # If it's yellow, it means that there are only the number of yellows of that character
    #     # If it's green, it means the same.
    #     if word[idx] == guess[idx]:
    #         return False
    #     else:
    #         green_ls = []
    #         for i, x in enumerate(self.green_letters):
    #             if x == word[idx]:
    #                 green_ls.append(self.green_idx[i])
    #         temp = word
    #         temp.pop()
    #         print(word, guess, green_ls)







if __name__ == '__main__':
    colorama_init()
    wordle = Wordle()
    external = input('Do you want to play on this device? Type y for yes: ') != 'y'
    if external:
        wordle.poss_words(saved=True, external=True)
        for i in range(5):
            wordle.get_information()
            wordle.poss_words(saved=True, external=True)

    else:
        solved = wordle.guess()
        while solved is not True:
            wordle.get_information()
            solved = wordle.guess()
