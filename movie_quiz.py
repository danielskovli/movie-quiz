#!/usr/bin/python3
'''
Simple standalone console-based movie quiz game

Requires Python 3.10 or later.
'''

import random
import platform
from enum import Enum, auto
from os import system
from os.path import dirname, join
from dataclasses import dataclass, field


class ConsoleUtils:
    class Format:
        HEADER = '\033[34m'
        KEYWORD = '\033[96m'
        CORRECT = '\033[92m'
        INCORRECT = '\033[91m'
        WARNING = '\033[93m'
        HIDDEN = '\033[8m'
        BOLD = '\033[1m'
        RESET = '\033[0m'

    @staticmethod
    def is_win():
        return platform.system() == 'Windows'

    @staticmethod
    def clear():
        system('cls' if ConsoleUtils.is_win() else 'clear')

    @staticmethod
    def get_input(prompt: str) -> str:
        try:
            answer = input(prompt)
            return answer.strip()
        except KeyboardInterrupt:
            print('\n\nGiving up are we? Okay, bye 👋')
            exit()


class GuessResult(Enum):
    '''All possible results from a user's guess.'''

    DEFAULT = auto()
    CORRECT = auto()
    INCORRECT = auto()
    PASS = auto()


@dataclass
class Movie:
    '''Stores movie title and anagrams of the title, along with mechanisms for fetching
    random anagrams (while keeping track of ones already used). Also stores whether the
    title has been correctly guessed or not.'''

    title: str
    anagrams: list[str]
    correct_guess: bool = False
    _spent: list[str] = field(default_factory=list)

    @property
    def title_lower(self) -> str:
        return self.title.lower()

    def random_anagram(self) -> str:
        anagram = random.choice([x for x in self.anagrams if x not in self._spent])
        self._spent.append(anagram)
        return anagram


class MovieQuiz:
    '''Generates a quiz from a list of movie titles. Proceedings are executed manually via the `start()` method.
    
    Args:
        filename (str, optional): The name of the file containing the list of movie titles.
            Relative to the current directory. Default is 'movies.txt'.
        max_guesses (int, optional): The maximum number of guesses allowed for each movie title. Default is 3.
    '''

    def __init__(self, filename: str = 'movies.txt', max_guesses: int = 3):
        self._movie_titles = self._load_movie_titles(filename)
        self._questions = self._generate_quiz(self._movie_titles)
        self._max_guesses = max_guesses

    @property
    def questions(self):
        return self._questions

    # Alias for questions
    movies = questions

    @property
    def max_guesses(self):
        return self._max_guesses

    def _load_movie_titles(self, filename: str) -> list[str]:
        dir = dirname(__file__)
        file = join(dir, filename)
        with open(file) as f:
            return f.read().splitlines()

    def _generate_quiz(self, movie_titles: list[str]):
        questions: list[Movie] = []

        for title in movie_titles:
            movie = Movie(title, [])

            for _ in range(50):
                anagram = [self._scramble_word(word) for word in title.split()]
                movie.anagrams.append(' '.join(anagram).upper())

            questions.append(movie)

        random.shuffle(questions) # in-place edit
        return questions

    def _scramble_word(self, word: str) -> str:
        i = 0
        while i < 10:
            anagram = ''.join(random.sample(word, len(word)))
            if anagram != word:
                return anagram

        return word

    def start(self):
        '''Starts the quiz and iterates through the questions.

        The user follows the prompts along the way, and the process
        can be aborted at any time by pressing Ctrl+C.
        '''

        quiz_progress = lambda i: f'{i+1}/{len(self.questions)}'
        guess_progress = lambda i: f'{i+1} of {self.max_guesses}'

        for i, question in enumerate(self.questions):
            ConsoleUtils.clear()
            print(f'[{quiz_progress(i)}] Which movie is this?')
            print(f'Type {ConsoleUtils.Format.KEYWORD}next{ConsoleUtils.Format.RESET} to shuffle or {ConsoleUtils.Format.KEYWORD}pass{ConsoleUtils.Format.RESET} to skip')

            result = GuessResult.DEFAULT
            for x in range(self.max_guesses):
                if result == GuessResult.DEFAULT:
                    print(f'\n{ConsoleUtils.Format.HEADER}{ConsoleUtils.Format.BOLD}{question.random_anagram()}{ConsoleUtils.Format.RESET}\n')

                answer = ConsoleUtils.get_input(f'Guess {guess_progress(x)}: ')

                match answer.lower():
                    case 'next':
                        result = GuessResult.DEFAULT
                    case 'pass':
                        result = GuessResult.PASS
                    case question.title_lower:
                        question.correct_guess = True
                        result = GuessResult.CORRECT
                        print(f'{ConsoleUtils.Format.CORRECT}🎉 Correct! Nicely done 🎉{ConsoleUtils.Format.RESET}')
                    case _:
                        result = GuessResult.INCORRECT
                        print(f'{ConsoleUtils.Format.INCORRECT}👎 Incorrect, try again 👎{ConsoleUtils.Format.RESET}')

                if result in [GuessResult.CORRECT, GuessResult.PASS]:
                    break

            if result != GuessResult.CORRECT:
                intro = 'The answer was'
                if result != GuessResult.PASS:
                    intro = f'No more attempts left, {intro.lower()}'

                print(f'\n{intro}:\n{ConsoleUtils.Format.WARNING}{ConsoleUtils.Format.BOLD}{question.title.upper()}{ConsoleUtils.Format.RESET}')

            ConsoleUtils.get_input('\nPress enter to continue...')

        ConsoleUtils.clear()

        print('All done! Here are the results:\n')
        num_questions = len(self.questions)
        correct = len([question for question in self.questions if question.correct_guess])
        incorrect = num_questions - correct

        if correct == num_questions:
            print(f'{ConsoleUtils.Format.CORRECT}🎉 You got them all right! 🎉{ConsoleUtils.Format.RESET}')
        elif correct == 0:
            print(f'{ConsoleUtils.Format.INCORRECT}👎 You got them all wrong! 👎{ConsoleUtils.Format.RESET}')
        else:
            print('Not bad... but some room for improvement')
            print(f'You got {ConsoleUtils.Format.CORRECT}{correct}{ConsoleUtils.Format.RESET} right and {ConsoleUtils.Format.INCORRECT}{incorrect}{ConsoleUtils.Format.RESET} wrong')

        print('\n')



if __name__ == '__main__':
    quiz = MovieQuiz()
    quiz.start()