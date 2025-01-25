"""Modules required for tagger widget in the Orange Story Navigator add-on.
"""

import os
import string
import pandas as pd
import math
import numpy as np
import storynavigation.modules.constants as constants
import storynavigation.modules.util as util
from nltk.tokenize import RegexpTokenizer
from Orange.data.pandas_compat import table_to_frames
import spacy


class Tagger:
    """Class to perform NLP tagging of relevant actors and actions in textual stories
    For the storynavigator Orange3 add-on:
    https://pypi.org/project/storynavigator/0.0.11/

    Args:
        n_segments (int): Number of segments to split each story into.
        use_infinitives (bool): Whether to use infinitives for verbs.
    """
    def __init__(self, lang, n_segments, remove_stopwords, text_tuples, custom_tags_and_word_column=None, callback=None,use_infinitives=False):
        self.text_tuples = text_tuples
        self.lang = lang
        self.n_segments = n_segments
        self.remove_stopwords = remove_stopwords
        self.custom_tags = None
        self.word_column = None
        self.use_infinitives = use_infinitives
        self.complete_data_columns = constants.TAGGING_DATAFRAME_COLUMNNAMES_BASE

        if custom_tags_and_word_column is not None:
            self.word_column = custom_tags_and_word_column[1]
            self.custom_tags = custom_tags_and_word_column[0]
        
        self.stopwords = None
        self.pronouns = None
        self.model = None
        self.past_tense_verbs = None
        self.present_tense_verbs = None
        self.false_positive_verbs = None
        self.__setup_required_nlp_resources(self.lang)

        self.nlp = util.load_spacy_pipeline(self.model)
        self.n = 20 # top n scoring tokens for all metrics

        self.complete_data = self.__process_stories(self.nlp, self.text_tuples, callback)

    def __calculate_story_wordcounts(self, collection_df):
        story_sentence_column = collection_df['sentence'].tolist()
        tokenizer = RegexpTokenizer(r"\w+|\$[\d\.]+|\S+") # word tokenizer
        num_words_in_sentence_column = []
        for sentence in story_sentence_column:
            spans = list(tokenizer.span_tokenize(sentence))
            num_words_in_sentence_column.append(len(spans))
        return num_words_in_sentence_column

    def __process_stories(self, nlp, text_tuples, callback):
        """This function runs the nlp tagging process on a list of input stories and stores the resulting tagging information in a dataframe.

        Args:
            nlp (list): list of (spacy.tokens.doc.Doc) objects - one for each element of 'sentences'
            text_tuples (list): each element of the list is a binary tuple. The first component is the text of the story (string) and the second component is a number (int) uniquely identifying that story in the given list

        Returns:
            pandas.DataFrame: a dataframe containing all tagging data for all stories in the given list
        """

        collection_df = pd.DataFrame()
        c = 1
        for story_tuple in text_tuples:
            story_df = self.__process_story(story_tuple[1], story_tuple[0], nlp)
            collection_df = pd.concat([collection_df, story_df], axis=0)
            c+=1
            if callback:
                callback((c / len(text_tuples) * 100))

        # Process custom tags and word column if provided
        if self.custom_tags is not None and self.word_column is not None:
            if self.use_infinitives:
                collection_df['custom_' + self.word_column] = collection_df['spacy_lemma'].str.lower()
            else:
                collection_df['custom_' + self.word_column] = collection_df['token_text'].str.lower()
                collection_df['custom_' + self.word_column] = collection_df['custom_' + self.word_column].str.lstrip('0123456789@#$!“"-')
                            
            # Merge the custom tags
            collection_df = pd.merge(collection_df, self.custom_tags, left_on='custom_' + self.word_column, right_on=self.word_column, how='left')
            collection_df = collection_df.drop(columns=[self.word_column])
        
        else:
            collection_df['token_text_lowercase'] = collection_df['token_text'].str.lower()

        # Clean up associated action columns
        collection_df['associated_action'] = collection_df['associated_action'].str.lstrip('0123456789@#$!“"-')
        collection_df['associated_action_lowercase'] = collection_df['associated_action'].str.lower()
        
        # Add language column and word count
        lang_col_values = [self.lang] * len(collection_df)
        collection_df['lang'] = lang_col_values
        story_wordcount_values = self.__calculate_story_wordcounts(collection_df)
        collection_df['num_words_in_sentence'] = story_wordcount_values
        
        return collection_df
    
    def __process_story(self, storyid, story_text, nlp):
        """Given a story text, this function preprocesses the text, then runs and stores the tagging information for each sentence in the story in memory. It then uses this information to generate a dataframe synthesising all the tagging information for downstream analysis.

        Args:
            storyid (int): a number uniquely identifying a specific story
            story_text (string): the text of the story referred to by storyid
            nlp (spacy.language.Language): a spacy language model object to use on the input stories

        Returns:
            pandas.DataFrame: a dataframe containing all tagging data for the given story, and a column with the segment.
            The segment is the segment number of the corresponding sentence in a given story.
        """
        story_df = pd.DataFrame()
        sentences = util.preprocess_text(story_text)

        # generate and store nlp tagged models for each sentence
        tagged_sentences = []
        for sentence in sentences:
            if (len(sentence.split()) > 0): # sentence has at least one word in it
                tagged_sentence = nlp(sentence)
                tagged_sentences.append(tagged_sentence)

        story_df = self.__parse_tagged_story(storyid, sentences, tagged_sentences)

        # Append the segment id by sentence 
        # NOTE: join on storyid x sentence id may be better, but for this we'd need to store the sentence id also in story_df
        sentences_df = []
        sentence_id = 0
        for segment_id, group in enumerate(np.array_split(sentences, self.n_segments)):
            for s in group:
                sentences_df.append([storyid, s, sentence_id, segment_id])
                sentence_id += 1

        sentences_df = pd.DataFrame(sentences_df, columns=["storyid", "sentence", "sentence_id", "segment_id"])

        idx_cols = ["storyid", "sentence"]
        story_df = (story_df.
                    set_index(idx_cols).
                    join(sentences_df.loc[:, idx_cols + ["sentence_id", "segment_id"]].
                         set_index(idx_cols)
                         ).
                    reset_index()
                    )

        return story_df
        
    def __parse_tagged_story(self, storyid, sentences, tagged_sentences):
        """Given a list of sentences in a given story and a list of nlp tagging information for each sentence,
        this function processes and appends nlp tagging data about these sentences to the master output dataframe

        Args:
            storyid (int): a number uniquely identifying a specific story
            sentences (list): a list of strings (each string is a sentence within the story referred to by storyid
            tagged_sentences (list): list of (spacy.tokens.doc.Doc) objects - one for each element of 'sentences'

        Returns:
            pandas.DataFrame: a dataframe containing all tagging data for the given story
        """
        story_df = pd.DataFrame()
        story_df_rows = []
        
        for sentence, tagged_sentence in zip(sentences, tagged_sentences):
            first_word_in_sent = sentence.split()[0].lower().strip()
            tags = []            
                       
            # store all spacy nlp tags and dependency info for each token in the sentence in a tuple
            for token in tagged_sentence:
                token_ne = "O" if token.ent_iob_ == "O" else token.ent_iob_ + "-" + token.ent_type_
                # (text, part of speech (POS) tag, fine-grained POS tag, linguistic dependency, named entity tag, the spacy token object itself)                
                tags.append((token.text, token.pos_, token.tag_, token.dep_, token_ne, token)) 

            tokenizer = RegexpTokenizer(r"\w+|\$[\d\.]+|\S+") # word tokenizer
            spans = list(tokenizer.span_tokenize(sentence)) # generate token spans in sentence (start and end indices)

            # Determine the voice (passive or active) for the current sentence
            voice = self.__process_dutch_voice(tags)
            
            # Process each token
            for tag, span in zip(tags, spans):
                story_df_row = self.__process_tag(storyid, sentence, tag, span)
                if story_df_row is not None:
                    story_df_row.append(voice)
                    story_df_rows.append(story_df_row)            
            
            # Append the voice to each row corresponding to this sentence
            #for row in tags:
            #    row.append(voice)  # Add the voice classification to the row of the df                      
            
        for index, row in enumerate(story_df_rows):           
            future_verb = self.__process_dutch_future_verbs(story_df_rows, row)
            row.append(future_verb)           
            
            # overwrite the verb value if it's a future verb
            if future_verb == "FUTURE_VB":
                row[5] = "FUTURE_VB"
                            
        story_df = pd.DataFrame(story_df_rows, columns=self.complete_data_columns)
        
        return story_df
        
    def __process_tag(self, storyid, sentence, tag, span):
        """Given a tagged token in a sentence within a specific story, this function processes and appends data about this token to the master output dataframe

        Args:
            storyid (int): a number uniquely identifying a specific story
            sentence (string): a sentence within this story
            tag (tuple): a tuple with 6 components:
                        1) text: the text of the given token
                        2) pos_: the coarse-grained POS tag of token (string)
                        3) tag_: the fine-grained POS tag of token (string)
                        4) dep_: the syntactic linguistic dependency relation of the token (string)
                        5) the named entity tag of the token
                        6) the complete spacy analysis of the token

            span (tuple): 2-component tuple. First component is the matching start index in the sentence of the given tag.text. Second component is the matching end index.

        Returns:
            list: list representing a row of the master story elements dataframe
        """
        row = None
        if self.__is_valid_token(tag):
            vb = util.find_verb_ancestor(tag)
            vb_text = '-' if vb is None else vb.text
            if self.__is_subject(tag):
                story_navigator_tag = "SP" if self.__is_pronoun(tag) else "SNP"
            elif self.__is_pronoun(tag):
                story_navigator_tag = "NSP"
            elif self.__is_noun_but_not_pronoun(tag):
                story_navigator_tag = "NSNP"
            else:
                story_navigator_tag = "-"
            if story_navigator_tag == "-":
                row = self.__process_non_noun_tag(storyid, sentence, tag)
            else:
                row = [storyid, sentence, tag[0], tag[-1].idx, tag[-1].idx + len(tag[0]), story_navigator_tag,
                       tag[1], tag[2], tag[3], tag[4], tag[-1].lemma_, tag[-1].head.text, tag[-1].head.idx, 
                       True, True, self.__is_active_voice_subject(tag), vb_text]
        return row
    
    def __process_english_potential_action(self, tag):
        if (tag[-1].pos_ in ["VERB","AUX"]):
            # VB  --  verb, base form
            # VBD  --  verb, past tense
            # VBG  --  verb, gerund or present participle
            # VBN  --  verb, past participle
            # VBP  --  verb, non-3rd person singular present
            # VBZ  --  verb, 3rd person singular present
            
            # Classify verb as either past or present tense
            if tag[-1].tag_ in ['VB', 'VBG', 'VBP', 'VBZ']:
                return "PRES_VB"
            elif tag[-1].tag_ in ['VBD', 'VBN']:
                return "PAST_VB"
            else:                                                                                                                                       
                return "-"
        else:   # Not Verb
            return "-"

    def __process_dutch_potential_action(self, tag):
    
        token = tag[-1]
        
        if token and token.pos_ in ["VERB", "AUX"] and token.tag_.split('|')[0] == "WW":
                        
            # Classify the verb as either past or present tense
            if token.tag_.startswith('WW|pv|tgw|') or token.tag_.startswith('WW|pv|conj|') or token.tag_.startswith('WW|inf|'):
                return "PRES_VB"
            elif token.tag_.startswith('WW|pv|verl|') or token.tag_.startswith('WW|vd|'):
                return "PAST_VB"
            else:                
                return "-"
        else: # Not a verb            
            return "-"

    def __process_dutch_future_verbs(self, tags, tag):
        """Determine if a specific token is in the future tense.
    
        Args:
            sentence (spacy.tokens.doc.Doc): A spaCy Doc object representing a sentence.
            token (spacy.tokens.token.Token): The token being classified.

        Returns:
            str: "FUTURE_VB" if the token is part of a future tense construction, otherwise "-".
        """
        
        # Check if the token itself is a conjugation of "zullen" or "gaan" (indicating future tense)
        lemma_value = tag[10]
        pos_value = tag[6]
        tag_value = tag[7]
        
        # Auxiliary verbs in Dutch indicating future tense
        #future_auxiliary_verbs = ["zal", "zult", "zullen","ga", "gaat", "gaan"]
        if lemma_value in ["zullen", "gaan"] and pos_value == "AUX":
            return "FUTURE_VB"
    
        # Variable to track if we've encountered a conjugation of 'zullen' in the sentence
        future_verb_triggered = False

        # Loop through each token in the sentence
        for tok in tags:
            lemma_value = tok[10]
            text_value = tok[2]
            pos_value = tok[6]
            tag_value = tok[7]
            dep_value = tok[8]
            
            # Check if the token is an auxiliary 'zullen' or 'gaan' or a conjugation of it
            if lemma_value in ["zullen", "gaan"] and pos_value == "AUX":
                future_verb_triggered = True
                continue

            # Check if the specific token is an infinitive verb that follows 'zullen' or 'gaan'
            if future_verb_triggered and tag_value.startswith("WW|inf|"):
            # Classify the infinitive as FUTURE_VB if it's the target token
                if tok == tag:
                    return "FUTURE_VB"
                continue  # Keep marking subsequent infinitives as FUTURE_VB
                                 
            # reset the future_verb_triggered flag whenever a clause boundary is detected
            if dep_value == "punct" and text_value in [";", ",", ".", ":", "?", "!"]:
                future_verb_triggered = False
            
            # if a finite verb (that isn't part of a future tense construction) appears in the
            # sentence after a conjugation of "zullen" or "gaan", it signals the end of the
            # future verb construction. In this case, you don't want to continue marking 
            # subsequent verbs or infinitives as part of a future tense construction, 
            # so the flag is reset to False.
            elif pos_value == "VERB" and not tag_value.startswith("WW|inf|"):
                future_verb_triggered = False

        return "-"  # if no future tense verb is detected
    
    
    def __process_dutch_voice(self, tags):
        """
        Determine if a Dutch sentence is in the passive or active voice.

        Args:
            tags (list): A list of tags representing tokens in the sentence or clause.

        Returns:
            str: "PASSIVE" if the sentence/clause is in the passive voice, otherwise "ACTIVE".
        """
        # Lemmas of auxiliary verbs indicating passive voice
        #passive_auxiliaries = {"worden", "zijn"}
        passive_auxiliaries = {"worden"}
        past_participle_tag_prefix = "WW|vd"  # past participles
        auxiliary_pos_tag = "AUX"

        # Flags to track detection of relevant elements
        auxiliary_found = False
        passive_auxiliary_found = False
        past_participle_found = False
        prepositional_agent_found = False  # Tracks presence of a "door" or similar preposition

        # Keep track of auxiliary heads for context
        auxiliary_heads = set()

        # Iterate through the tags
        for tok in tags:
            lemma_value = tok[5].lemma_
            pos_value = tok[1]  
            tag_value = tok[2]  
            dep_value = tok[3]  # Dependency relation
            head_value = tok[5].head.lemma_  # Syntactic head (index of the parent token)

            # Check for auxiliary verbs (e.g., "moeten", "kunnen") that might chain with "worden" or "zijn"
            if pos_value == auxiliary_pos_tag and lemma_value not in passive_auxiliaries:
                auxiliary_found = True
                auxiliary_heads.add(head_value)

            # Check for the passive auxiliary "worden" or "zijn"
            if lemma_value in passive_auxiliaries and pos_value == auxiliary_pos_tag:
                passive_auxiliary_found = True
                auxiliary_heads.add(head_value)

            # Check for a past participle
            if tag_value.startswith(past_participle_tag_prefix):
                past_participle_found = True

            # Check for a prepositional agent introduced by "door" or similar
            if lemma_value == "door" and dep_value == "case" and head_value in auxiliary_heads:
                # Look for a connection between "door" and auxiliary heads via the head token              
                prepositional_agent_found = True

            # If a passive auxiliary is found with a past participle, it's passive
            # e.g., "De deur werd gesloten"
            if passive_auxiliary_found and past_participle_found:
                return "PASSIVE"

        # If "zijn" + past participle is found but no prepositional agent, classify as a state (active)
        # e.g., "Het boek is gelezen": IS THIS THEOREICALLY ACTIVE OR PASSIVE?
        if passive_auxiliary_found and lemma_value == "zijn" and past_participle_found and not prepositional_agent_found:
            return "ACTIVE"

        # If auxiliary verbs chain with "worden" or "zijn" and a past participle is found, it's also passive
        # e.g., "De deur moest worden gesloten"
        if auxiliary_found and passive_auxiliary_found and past_participle_found:
            return "PASSIVE"

        # Default to active if no passive construction is detected
        return "ACTIVE"





    # def __process_dutch_voice(self, tags):
    #     """
    #     Determine if a Dutch sentence or clause is in the passive or active voice.

    #     Args:
    #         tags (list): A list of tags representing tokens in the sentence or clause.

    #     Returns:
    #         str: "PASSIVE" if the sentence/clause is in the passive voice, otherwise "ACTIVE".
    #     """
    #     # Auxiliary verb indicating passive voice
    #     passive_auxiliary_lemma = "worden"
        
    #     # Track whether "worden" and a past participle are found
    #     passive_triggered = False

    #     # Loop through tokens in the sentence
    #     for tok in tags:
    #         lemma_value = tok[5].lemma_
    
    #         # Access the POS tag (index 1)
    #         pos_value = tok[1] # token.pos_
            
    #         # Access the fine-grained tag (index 2)
    #         tag_value = tok[2]  # token.tag_

    #         # Check if the token is an auxiliary "worden"
    #         if lemma_value == passive_auxiliary_lemma and pos_value == "AUX":
    #             passive_triggered = True
    #             continue

    #         # Check for a past participle if "worden" was triggered
    #         if passive_triggered and tag_value.startswith('WW|vd'):
    #             return "PASSIVE"

    #     # If no passive construction is found, return ACTIVE
    #     return "ACTIVE"

     
    def __process_potential_action(self, tag):
        if self.lang == constants.NL:
            return self.__process_dutch_potential_action(tag)
        elif self.lang == constants.EN:
            return self.__process_english_potential_action(tag)
        else: 
            return "-"        
    
    def __process_non_noun_tag(self, storyid, sentence, tag):
        """Given a tagged token in a sentence within a specific story known to not be a noun (potentially a verb), this function processes and appends data about this action to the master output dataframe

        Args:
            storyid (int): a number uniquely identifying a specific story
            sentence (string): a sentence within this story
            tag (tuple): a tuple with 6 components:
                        1) text: the text of the given token
                        2) pos_: the coarse-grained POS tag of token (string)
                        3) tag_: the fine-grained POS tag of token (string)
                        4) dep_: the syntactic linguistic dependency relation of the token (string)
                        5) the named entity tag of the token
                        6) the complete spacy analysis of the token

            span (tuple): 2-component tuple. First component is the matching start index in the sentence of the given tag.text. Second component is the matching end index.

        Returns:
            list: list representing a row of the master story elements dataframe with the tense of the input action / verb word
        """
        row = None
        if self.__is_valid_token(tag):
            tense_value = self.__process_potential_action(tag)            
            row = [storyid, sentence, tag[0], tag[-1].idx, tag[-1].idx + len(tag[0]), tense_value, 
                   tag[1], tag[2], tag[3], tag[4], tag[-1].lemma_, tag[-1].head.text, tag[-1].head.idx,
                   False, False, False, '-']            
            
        return row
    
    def __is_valid_token(self, token):
        """Verifies if token is valid word

        Args:
            token (spacy.tokens.token.Token): tagged Token | tuple : 5 components - (text, tag, fine-grained tag, dependency)

        Returns:
            string, boolean : cleaned token text, True if the input token is a valid word, False otherwise
        """
        word = util.get_normalized_token(token)

        return (word not in self.stopwords) and len(word) > 0 and util.is_only_punctuation(word) != '-'

    def __is_subject(self, tag):
        """Checks whether a given pos-tagged token is a subject of its sentence or not

        Args:
            tag (tuple): a tuple with 6 components:
                        1) text: the text of the given token
                        2) pos_: the coarse-grained POS tag of token (string)
                        3) tag_: the fine-grained POS tag of token (string)
                        4) dep_: the syntactic linguistic dependency relation of the token (string)
                        5) the named entity tag of the token
                        6) the complete spacy analysis of the token

        Returns:
            boolean: True if the given token is a subject of its sentence - False otherwise
        """
        if ((tag[3].lower() in ["nsubj", "nsubj:pass", "nsubjpass", "csubj"]) and (tag[1] in ["PRON", "NOUN", "PROPN"])):
            return True
        
        return False
    
    def __is_active_voice_subject(self, tag):
        """Checks whether a given pos-tagged token is involved in an active voice subject role in the sentence

        Args:
            tag (tuple): a tuple with 6 components:
                        1) text: the text of the given token
                        2) pos_: the coarse-grained POS tag of token (string)
                        3) tag_: the fine-grained POS tag of token (string)
                        4) dep_: the syntactic linguistic dependency relation of the token (string)
                        5) the named entity tag of the token
                        6) the complete spacy analysis of the token

        Returns:
            boolean: True if the given token is an active voice subject of its sentence - False otherwise
        """
        if (tag[3].lower() in ["nsubj"] and (tag[1] in ["PRON", "NOUN", "PROPN"])):
            return True
        return False

    def __is_pronoun(self, tag):
        """Checks whether a given pos-tagged token is a pronoun or not

        Args:
            tag (tuple): a tuple with 6 components:
                        1) text: the text of the given token
                        2) pos_: the coarse-grained POS tag of token (string)
                        3) tag_: the fine-grained POS tag of token (string)
                        4) dep_: the syntactic linguistic dependency relation of the token (string)
                        5) the named entity tag of the token
                        6) the complete spacy analysis of the token

        Returns:
            boolean: True if the given token is a pronoun - False otherwise
        """
        if tag[0].lower().strip() == "ik":
            return True
        if tag[0].lower().strip() not in self.stopwords:
            if tag[1] == "PRON":
                if "|" in tag[2]:
                    tmp_tags = tag[2].split("|")
                    if (tmp_tags[1] == "pers" and tmp_tags[2] == "pron") or (
                        tag[0].lower().strip() == "ik"
                    ):
                        return True
        return False

    def __is_noun_but_not_pronoun(self, tag):
        """Checks whether a given pos-tagged token is a non-pronoun noun (or not)

        Args:
            tag (tuple): a tuple with 6 components:
                        1) text: the text of the given token
                        2) pos_: the coarse-grained POS tag of token (string)
                        3) tag_: the fine-grained POS tag of token (string)
                        4) dep_: the syntactic linguistic dependency relation of the token (string)
                        5) the named entity tag of the token
                        6) the complete spacy analysis of the token

        Returns:
            boolean: True if the given token is a non-pronoun noun - False otherwise
        """
        if (not self.__is_pronoun(tag)) and (tag[1] in ["NOUN", "PROPN"]):
            return True
        else:
            return False
        
    def __generate_customtag_column_names(self):
        """Creates a Python list of column names for the boolean columns for each custom tag and classification-scheme

        Returns:
            list: list of strings where each string is the name of a boolean column e.g. "is_realm-scheme_doing" or "is_realm-scheme_being" or "is_realm-scheme_sensing"
                    e.g. ["is_realm-scheme_doing", "is_realm-scheme_being", "is_realm-scheme_sensing", ...]
        """
        column_names = []

        for col in self.custom_tags.columns:    # make sure to only look from Column 2 onwards (Column 1 is a list of words, Column 2 onwards are the tag labels)
            if col != self.word_column:
                for col_value in list(set(self.custom_tags[col].tolist())): # get unique values in column
                    column_names.append('is_' + str(col) + '-scheme_' + str(col_value).lower())
        
        return list(set(column_names))
    
    def __flatten_custom_tag_dictionary(self):
        """Creates a Python dictionary where the keys are each column name generated by `__generate_customtag_column_names()` and the values are a list of strings which belong to the category / tag / label represented by the key

        Returns:
            dict: dict where the keys are strings representing a word category / tag / label, and the values are lists (where each element of the list is a string representing a word belong to the specific category / label / tag)
                    e.g. {
                        "is_realm-scheme_doing" : ['voetballen', 'speel', 'spreek', ...],
                        "is_realm-scheme_being" : ['ben', 'weet', 'vertrouw', ...],
                        "is_realm-scheme_sensing" : ['voel', 'denk', 'overwoog', ...],
                        ...
                    }
        """
        flattened_dict = {}
        if self.customtag_column_names is None:
            self.customtag_column_names = self.__generate_customtag_column_names()

        for col_name in self.customtag_column_names:
            orig_col_name = col_name.split('-scheme_')[0].replace('is_', '')
            orig_tag_name = col_name.split('-scheme_')[1]
            matched_df = self.custom_tags[self.custom_tags[orig_col_name] == orig_tag_name]
            matched_words = list(set(matched_df.iloc[:, 0].tolist()))
            flattened_dict[col_name] = matched_words

        return flattened_dict        
    
    def __lookup_custom_tags(self, tag):
        """Creates a Python dictionary where the keys are each column name generated by `__generate_customtag_column_names()` and the values are a list of strings which belong to the category / tag / label represented by the key

        Args:
            tag (tuple): a tuple with 6 components:
                        1) text: the text of the given token
                        2) pos_: the coarse-grained POS tag of token (string)
                        3) tag_: the fine-grained POS tag of token (string)
                        4) dep_: the syntactic linguistic dependency relation of the token (string)
                        5) the named entity tag of the token
                        6) the complete spacy analysis of the token

        Returns:
            list: a list where the nth element is a boolean value (either True or False) indicating whether tag.text belongs to the category represented by the nth custom tag column in self.customtag_column_names
                    e.g. [True, False, True, ...]
        """
        if self.custom_tags is None:
            return []

        results = []

        if self.flattened_custom_tags_dictionary is None:
            self.flattened_custom_tags_dictionary = self.__flatten_custom_tag_dictionary()
            
        for entry in self.flattened_custom_tags_dictionary:
            if isinstance(tag, str):
                if tag.lower().strip() in self.flattened_custom_tags_dictionary[entry]:
                    results.append(True)
                else:
                    results.append(False)
            else:
                if tag[0].lower().strip() in self.flattened_custom_tags_dictionary[entry]:
                    results.append(True)
                else:
                    results.append(False)

        return results
    
    def __lookup_existing_association(self, word, sentence, story_elements_frame):
        matching_rows_sent = story_elements_frame[story_elements_frame['sentence'] == sentence]
        matching_rows_word = matching_rows_sent[matching_rows_sent['token_text'].str.lower() == word.lower()]
        possible_actions = list(set(matching_rows_word['associated_action'].tolist()))
        if len(possible_actions) == 0:
            return '-'
        if len(possible_actions) == 1:
            return util.is_only_punctuation(possible_actions[0])
        
        result = '-'
        for action in possible_actions:
            result = util.is_only_punctuation(action)
            if  result != '-':
                continue

        return result

    def __setup_required_nlp_resources(self, lang):
        """Loads and initialises all language and nlp resources required by the tagger based on the given language

        Args:
            lang (string): the ISO code for the language of the input stories (e.g. 'nl' or 'en'). Currently only 'nl' and 'en' are supported
        """
        self.stopwords = []
        if lang == constants.NL:
            if self.remove_stopwords == constants.YES:
                self.stopwords = constants.NL_STOPWORDS_FILE.read_text(encoding="utf-8").split("\n")
            self.pronouns = constants.NL_PRONOUNS_FILE.read_text(encoding="utf-8").split("\n")
            self.model = constants.NL_SPACY_MODEL
            self.past_tense_verbs = constants.NL_PAST_TENSE_FILE.read_text(encoding="utf-8").split("\n")
            self.present_tense_verbs = constants.NL_PRESENT_TENSE_FILE.read_text(encoding="utf-8").split("\n")
            self.false_positive_verbs = constants.NL_FALSE_POSITIVE_VERB_FILE.read_text(encoding="utf-8").split("\n")
        else:
            if self.remove_stopwords == constants.YES:
                self.stopwords = constants.EN_STOPWORDS_FILE.read_text(encoding="utf-8").split("\n")
            self.pronouns = constants.EN_PRONOUNS_FILE.read_text(encoding="utf-8").split("\n")
            self.model = constants.EN_SPACY_MODEL
            self.past_tense_verbs = constants.EN_PAST_TENSE_FILE.read_text(encoding="utf-8").split("\n")
            self.present_tense_verbs = constants.EN_PRESENT_TENSE_FILE.read_text(encoding="utf-8").split("\n")
            self.false_positive_verbs = constants.EN_FALSE_POSITIVE_VERB_FILE.read_text(encoding="utf-8").split("\n")

        self.stopwords = [item for item in self.stopwords if len(item) > 0]
        self.pronouns = [item for item in self.pronouns if len(item) > 0]
        self.past_tense_verbs = [item for item in self.past_tense_verbs if len(item) > 0]
        self.present_tense_verbs = [item for item in self.present_tense_verbs if len(item) > 0]
        self.false_positive_verbs = [item for item in self.false_positive_verbs if len(item) > 0]
