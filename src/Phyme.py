import util
import rhymeUtils as ru
from IOUtil import load_word_phone_dict, load_phone_type_dicts, load_rhyme_trie


class Phyme(object):
    '''Phyme: a rhyming dictionary for songwriting'''

    def __init__(self):
        self.rhyme_trie = load_rhyme_trie()

    def search(self, phones):
        '''Search the rhyme trie for sub words given a listen of phones
        Returns a set of strings'''
        result = self.rhyme_trie.search(phones)
        if result:
            return set(result.get_sub_words())
        else:
            return None

    def get_perfect_rhymes(self, word, num_syllables=None):
        """Get perfect rhymes of a word, defaults to last stressed vowel

        Arguments:
            word {str} -- word to rhyme

        Keyword Arguments:
            num_syllables {int | None} -- Number of syllables to check
                subtractive rhymes for (default: {None}) for last stressed and
                unstressed

        Returns:
            [set] -- set of rhymes
        """

        phones = ru.get_last_syllables(word, num_syllables)
        results = self.search(list(util.flatten(phones)))
        if results:
            results.remove(word.upper())
            return results
        else:
            return set()

    def get_family_rhymes(self, word, num_syllables=None):
        """Get consonant family rhymes of a word

        Arguments:
            word {str} -- word to rhyme

        Keyword Arguments:
            num_syllables {int | None} -- Number of syllables to check
                family rhymes for (default: {None}) for last stressed and
                unstressed

        Returns:
            [set] -- set of rhymes
        """
        phones = ru.get_last_syllables(word, num_syllables)
        # todo: this rhymes on first stressed syllable. possibly implement
        # multiple stressed syllable rhymes
        if not ru.is_consonant(phones[0][-1]):
            return set()
        results = set()
        permutations = self._recursive_permute_words(phones, family=True)
        for result in self._search_permutations(permutations):
            results.update(result)
        return results

    def get_partner_rhymes(self, word, num_syllables=None):
        """Get consonant partner rhymes of a word

        Arguments:
            word {str} -- word to rhyme

        Keyword Arguments:
            num_syllables {int | None} -- Number of syllables to check
                partner rhymes for (default: {None}) for last stressed and
                unstressed

        Returns:
            [set] -- set of rhymes
        """
        phones = ru.get_last_syllables(word, num_syllables)
        if not ru.is_consonant(phones[0][-1]):
            return set()
        results = set()
        permutations = self._recursive_permute_words(phones, family=False)
        for result in self._search_permutations(permutations):
            results.update(result)
        return results

    def get_additive_rhymes(self, word, num_syllables=None):
        """Get additive rhymes of a word, eg DO -> DUDE

        Arguments:
            word {str} -- word to rhyme

        Keyword Arguments:
            num_syllables {int | None} -- Number of syllables to check
                additive rhymes for (default: {None}) for last stressed and
                unstressed

        Returns:
            [set] -- set of rhymes
        """
        phones = ru.get_last_syllables(word, num_syllables)
        results = set()
        permutations = self._recursive_permute_words(phones, add_sub='ADD')
        for result in self._search_permutations(permutations):
            results.update(result)
        return results

    def get_subtractive_rhymes(self, word, num_syllables=None):
        """Get subtractive rhymes of a word, eg DUDE -> DO

        Arguments:
            word {str} -- word to rhyme

        Keyword Arguments:
            num_syllables {int | None} -- Number of syllables to check
                subtractive rhymes for (default: {None}) for last stressed and
                unstressed

        Returns:
            [set] -- set of rhymes
        """

        phones = ru.get_last_syllables(word, num_syllables)
        results = set()
        permutations = self._recursive_permute_words(phones, add_sub='SUB')
        for result in self._search_permutations(permutations):
            results.update(result)
        return results

    def get_consonant_rhymes(self, word, num_syllables=None):
        """Get consonant rhymes of a word, eg COG -> BAG

        Arguments:
            word {str} -- word to rhyme

        Keyword Arguments:
            num_syllables {int | None} -- Number of syllables to check
                consonant rhymes for (default: {None}) for last stressed and
                unstressed

        Returns:
            [set] -- set of rhymes
        """
        phones = ru.get_last_syllables(word, num_syllables)
        results = set()
        permutations = self._recursive_permute_vowels(phones)
        for result in self._search_permutations(permutations):
            results.update(result)
        return results

    def get_assonance_rhymes(self, word, num_syllables=None):
        """Get assonance rhymes of a word, eg DOG -> JAUNT

        Arguments:
            word {str} -- word to rhyme

        Keyword Arguments:
            num_syllables {int | None} -- Number of syllables to check
                assonance rhymes for (default: {None}) for last stressed and
                unstressed

        Returns:
            [set] -- set of rhymes
        """
        phones = ru.get_last_syllables(word, num_syllables)
        phones = list(map(lambda syll: [phone for phone in syll if
                                        ru.is_vowel(phone)], phones))
        results = set()
        permutations = self._recursive_permute_words(phones, add_sub='ADD')
        for result in self._search_permutations(permutations):
            results.update(result)
        return results

    def _permute_vowels(self, syll):
        '''Get all permutations on the vowel of a syllable'''
        for vowel in ru.VOWELS:
            yield [vowel] + syll[1:]

    def _recursive_permute_vowels(self, sylls):
        '''Get all (existing) permutations of a set of syllables on vowels'''
        if len(sylls) == 1:
            yield from ([syll] for syll in self._permute_vowels(sylls[0]))
        else:
            permutations = self._permute_vowels(sylls[0])
            for syll in permutations:
                yield from ([syll] + rest for rest in
                            self._recursive_permute_vowels(self, sylls)
                            if self.rhyme_trie.contains(
                                list(util.flatten(rest))))

    def _recursive_permute_additive(self, syll):
        '''Get all valid permutations of additive '''
        # TODO: check this is an appropriate cutoff for # of consonants
        if len(syll) == 4:
            return syll
        yield syll
        for consonant in ru.CONSONANTS:
            # TODO: check there are no doubled consonants
            if consonant == syll[-1]:
                continue
            result = self._recursive_permute_additive(syll + [consonant])
            if result:
                yield from result

    def _recursive_permute_subtractive(self, syll):
        '''Get all subtractive permutations of a syllable'''
        yield syll
        if ru.is_consonant(syll[-1]):
            yield syll
            yield from self._recursive_permute_subtractive(syll[:-1])

    def _recursive_permute_words(self, sylls, family=True, add_sub=None):
        '''Recursively permute a list of syllables based either on their
        consonant companions or on additive/subtractive rules'''
        if len(sylls) == 1:
            if add_sub is None:
                permutations = self._recursive_permute_syllable(sylls[0],
                                                                family)
            elif add_sub == 'ADD':
                permutations = self._recursive_permute_additive(sylls[0])
            elif add_sub == 'SUB':
                permutations = self._recursive_permute_subtractive(sylls[0])
            yield from ([syll] for syll in permutations)
        else:

            for syll in self._recursive_permute_syllable(sylls[0], family):
                yield from ([syll] + rest for rest in
                            self._recursive_permute_words(sylls[1:], family)
                            if self.rhyme_trie.contains(
                                list(util.flatten(rest))))

    def _recursive_permute_syllable(self, syll, family=True):
        '''Recursively permute a syllable based on its consonant companions'''
        if len(syll) == 1:
            yield from ([companion] for companion in
                        self._permute_consonant(syll[0], family))
        else:
            if ru.is_vowel(syll[0]):
                yield from ([syll[0]] + list(rest) for rest in
                            self._recursive_permute_syllable(syll[1:],
                                                             family))
            else:
                for companion in self._permute_consonant(syll[0], family):
                    yield from ([companion] + list(rest) for rest in
                                self._recursive_permute_syllable(syll[1:],
                                                                 family))

    def _permute_consonant(self, consonant, family=True):
        '''Given a consonant, yield its family members or partners'''
        if family:
            companions = ru.get_consonant_family(consonant)
        else:
            companions = ru.get_consonant_partners(consonant)
        yield from companions

    def _search_permutations(self, permutations):
        '''Given a collection of permutations of syllables, yield the sets of
        their search results'''
        for permutation in permutations:
            permutation = list(util.flatten(permutation))
            result = self.search(permutation)
            if result:
                yield result
