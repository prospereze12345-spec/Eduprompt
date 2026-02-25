"""
Academic Text Improver Module
Transforms casual/conversational text into academic/professional writing
"""

import re
from typing import Dict, List, Tuple, Optional
import json

class AcademicToneImprover:
    """
    Main class for improving text to academic/professional tone
    """
    
    def __init__(self):
        # Initialize all phrase libraries
        self.weak_phrases = self._load_weak_phrases()
        self.academic_replacements = self._load_academic_replacements()
        self.grammar_fixes = self._load_grammar_fixes()
        self.transition_phrases = self._load_transition_phrases()
        self.hedging_language = self._load_hedging_language()
        self.strong_verbs = self._load_strong_verbs()
        
    def _load_weak_phrases(self) -> Dict[str, List[str]]:
        """
        Comprehensive dictionary of weak phrases and their academic alternatives
        """
        return {
            # Opening phrases
            "i think": [
                "it is arguable that",
                "it can be argued that",
                "one might contend that",
                "it is reasonable to assume that",
                "the evidence suggests that",
                "it could be hypothesized that",
                "one may postulate that",
                "it is plausible that"
            ],
            "i believe": [
                "it is evident that",
                "it appears that",
            "the research indicates that",
                "scholars have noted that",
                "it is widely accepted that",
                "the literature suggests that",
                "academic consensus holds that",
                "prevailing theories suggest that"
            ],
            "in my opinion": [
                "from an analytical perspective",
                "based on the available evidence",
                "considering the theoretical framework",
                "within the context of this analysis",
                "according to the research findings",
                "from a scholarly viewpoint",
                "in light of the evidence",
                "the data suggests that"
            ],
            "i feel": [
                "it is apparent that",
                "one can observe that",
                "the evidence points to",
                "analysis reveals that",
                "research demonstrates that",
                "findings indicate that",
                "studies show that",
                "data confirms that"
            ],
            
            # Vague quantifiers
            "a lot of": [
                "a significant number of",
                "a substantial portion of",
                "numerous",
                "countless",
                "a considerable amount of",
                "an extensive range of",
                "a plethora of",
                "a multitude of"
            ],
            "lots of": [
                "a considerable quantity of",
                "a vast array of",
                "a diverse range of",
                "an abundance of",
                "a profusion of",
                "a wealth of",
                "extensive",
                "comprehensive"
            ],
            "many": [
                "a multitude of",
                "a plethora of",
                "numerous",
                "countless",
                "a variety of",
                "diverse",
                "multiple",
                "various"
            ],
            "some": [
                "several",
                "a number of",
                "certain",
                "specific",
                "particular",
                "selected",
                "a portion of",
                "a subset of"
            ],
            "a few": [
                "several",
                "a limited number of",
                "a select few",
                "a minority of",
                "a handful of",
                "a small proportion of",
                "a modest number of",
                "an insignificant number of"
            ],
            
            # Weak adjectives
            "good": [
                "beneficial",
                "advantageous",
                "favorable",
                "positive",
                "constructive",
                "productive",
                "effective",
                "efficacious"
            ],
            "bad": [
                "detrimental",
                "adverse",
                "negative",
                "unfavorable",
                "problematic",
                "deleterious",
                "pernicious",
                "counterproductive"
            ],
            "big": [
                "substantial",
                "considerable",
                "significant",
                "extensive",
                "comprehensive",
                "large-scale",
                "major",
                "immense"
            ],
            "small": [
                "minor",
                "insignificant",
                "marginal",
                "negligible",
                "minimal",
                "limited",
                "modest",
                "incremental"
            ],
            "important": [
                "significant",
                "crucial",
                "critical",
                "essential",
                "paramount",
                "fundamental",
                "pivotal",
                "integral"
            ],
            "interesting": [
                "noteworthy",
                "significant",
                "compelling",
                "intriguing",
                "remarkable",
                "striking",
                "salient",
                "pertinent"
            ],
            
            # Weak verbs
            "get": [
                "obtain",
                "acquire",
                "attain",
                "secure",
                "procure",
                "achieve",
                "garner",
                "receive"
            ],
            "got": [
                "obtained",
                "acquired",
                "attained",
                "secured",
                "procured",
                "achieved",
                "garnered",
                "received"
            ],
            "use": [
                "utilize",
                "employ",
                "implement",
                "apply",
                "leverage",
                "deploy",
                "exercise",
                "adopt"
            ],
            "used": [
                "utilized",
                "employed",
                "implemented",
                "applied",
                "leveraged",
                "deployed",
                "exercised",
                "adopted"
            ],
            "make": [
                "create",
                "develop",
                "construct",
                "formulate",
                "establish",
                "generate",
                "produce",
                "compose"
            ],
            "made": [
                "created",
                "developed",
                "constructed",
                "formulated",
                "established",
                "generated",
                "produced",
                "composed"
            ],
            "do": [
                "perform",
                "conduct",
                "execute",
                "undertake",
                "accomplish",
                "achieve",
                "implement",
                "complete"
            ],
            "did": [
                "performed",
                "conducted",
                "executed",
                "undertook",
                "accomplished",
                "achieved",
                "implemented",
                "completed"
            ],
            "show": [
                "demonstrate",
                "illustrate",
                "indicate",
                "reveal",
                "exhibit",
                "display",
                "present",
                "manifest"
            ],
            "showed": [
                "demonstrated",
                "illustrated",
                "indicated",
                "revealed",
                "exhibited",
                "displayed",
                "presented",
                "manifested"
            ],
            "help": [
                "facilitate",
                "assist",
                "aid",
                "support",
                "contribute to",
                "enable",
                "promote",
                "foster"
            ],
            "helped": [
                "facilitated",
                "assisted",
                "aided",
                "supported",
                "contributed to",
                "enabled",
                "promoted",
                "fostered"
            ],
            "change": [
                "modify",
                "alter",
                "adjust",
                "transform",
                "revise",
                "amend",
                "adapt",
                "refine"
            ],
            "changed": [
                "modified",
                "altered",
                "adjusted",
                "transformed",
                "revised",
                "amended",
                "adapted",
                "refined"
            ],
            
            # Conversational phrases
            "sort of": [
                "to some extent",
                "in some ways",
                "partially",
                "somewhat",
                "moderately",
                "to a certain degree",
                "in part",
                "relatively"
            ],
            "kind of": [
                "somewhat",
                "rather",
                "quite",
                "moderately",
                "to some degree",
                "in a sense",
                "effectively",
                "essentially"
            ],
            "a bit": [
                "somewhat",
                "slightly",
                "marginally",
                "modestly",
                "to a limited extent",
                "minimally",
                "incrementally",
                "perceptibly"
            ],
            "really": [
                "genuinely",
                "truly",
                "fundamentally",
                "essentially",
                "substantially",
                "considerably",
                "significantly",
                "markedly"
            ],
            "very": [
                "extremely",
                "exceedingly",
                "particularly",
                "notably",
                "considerably",
                "remarkably",
                "exceptionally",
                "profoundly"
            ],
            
            # Time-related weak phrases
            "now": [
                "currently",
                "presently",
                "at present",
                "in the current context",
                "contemporarily",
                "at this juncture",
                "in the present study",
                "within the current framework"
            ],
            "then": [
                "subsequently",
                "thereafter",
                "following that",
                "at that time",
                "during that period",
                "historically",
                "in that context",
                "at that juncture"
            ],
            "soon": [
                "in the near future",
                "proximately",
                "in due course",
                "subsequently",
                "thereafter",
                "in a timely manner",
                "expediently",
                "promptly"
            ],
            "later": [
                "subsequently",
                "thereafter",
                "at a later stage",
                "in subsequent phases",
                "following this",
                "eventually",
                "ultimately",
                "in due course"
            ],
            
            # Cause and effect
            "so": [
                "therefore",
                "thus",
                "hence",
                "consequently",
                "accordingly",
                "as a result",
                "for this reason",
                "subsequently"
            ],
            "because": [
                "due to",
                "owing to",
                "as a consequence of",
                "on account of",
                "in light of",
                "given that",
                "considering that",
                "since"
            ],
            "that's why": [
                "for this reason",
                "consequently",
                "thus",
                "therefore",
                "hence",
                "accordingly",
                "as such",
                "this explains why"
            ],
            
            # Adding information
            "also": [
                "furthermore",
                "moreover",
                "additionally",
                "in addition",
                "likewise",
                "similarly",
                "further",
                "besides"
            ],
            "plus": [
                "furthermore",
                "moreover",
                "additionally",
                "in addition to",
                "coupled with",
                "along with",
                "together with",
                "as well as"
            ],
            
            # Contrast
            "but": [
                "however",
                "nevertheless",
                "nonetheless",
                "conversely",
                "on the contrary",
                "in contrast",
                "yet",
                "although"
            ],
            "though": [
                "although",
                "however",
                "nevertheless",
                "nonetheless",
                "despite this",
                "notwithstanding",
                "even though",
                "albeit"
            ],
            "anyway": [
                "nevertheless",
                "nonetheless",
                "in any case",
                "regardless",
                "irrespective",
                "despite this",
                "be that as it may",
                "in any event"
            ],
            
            # Emphasis
            "of course": [
                "undoubtedly",
                "certainly",
                "indeed",
                "to be sure",
                "naturally",
                "evidently",
                "manifestly",
                "unquestionably"
            ],
            "obviously": [
                "clearly",
                "evidently",
                "apparently",
                "manifestly",
                "patently",
                "undeniably",
                "indisputably",
                "unquestionably"
            ],
            
            # Conclusions
            "in the end": [
                "ultimately",
                "finally",
                "in conclusion",
                "to conclude",
                "in summary",
                "overall",
                "in the final analysis",
                "when all is considered"
            ],
            "to sum up": [
                "in summary",
                "to summarize",
                "in conclusion",
                "to conclude",
                "ultimately",
                "in essence",
                "in brief",
                "to recapitulate"
            ]
        }
    
    def _load_academic_replacements(self) -> Dict[str, str]:
        """
        Simple one-to-one replacements for common words
        """
        return {
            # Basic replacements
            "a lot": "substantially",
            "lots": "numerous",
            "thing": "aspect",
            "things": "elements",
            "stuff": "material",
            "way": "method",
            "ways": "methods",
            "idea": "concept",
            "ideas": "concepts",
            "guess": "hypothesize",
            "maybe": "perhaps",
            "maybe": "possibly",
            "like": "such as",
            "etc": "et cetera",
            "ok": "acceptable",
            "okay": "satisfactory",
            "cool": "notable",
            "awesome": "remarkable",
            "amazing": "extraordinary",
            "terrible": "problematic",
            "awful": "unfavorable",
            "funny": "peculiar",
            "weird": "anomalous",
            "strange": "unusual",
            "normal": "typical",
            "usual": "customary",
            "always": "consistently",
            "never": "rarely if ever",
            "everyone": "all individuals",
            "nobody": "no individuals",
            "people": "individuals",
            "guys": "individuals",
            "kids": "children",
            "grown-ups": "adults",
            "boss": "supervisor",
            "worker": "employee",
            "job": "position",
            "work": "employment",
            "company": "organization",
            "school": "educational institution",
            "college": "higher education institution",
            "teacher": "educator",
            "student": "learner",
            "book": "text",
            "paper": "document",
            "article": "publication",
            "study": "research",
            "find": "discover",
            "look": "examine",
            "see": "observe",
            "hear": "perceive",
            "talk": "discuss",
            "speak": "articulate",
            "tell": "relate",
            "ask": "inquire",
            "answer": "respond",
            "question": "interrogate",
            "problem": "issue",
            "solution": "resolution",
            "answer": "solution",
            "fix": "rectify",
            "break": "compromise",
            "stop": "cease",
            "start": "commence",
            "begin": "initiate",
            "end": "conclude",
            "finish": "complete",
            "keep": "maintain",
            "hold": "retain",
            "give": "provide",
            "take": "acquire",
            "bring": "transport",
            "send": "transmit",
            "get": "receive",
            "put": "position",
            "set": "establish",
            "place": "situate",
            "move": "relocate",
            "come": "approach",
            "go": "proceed",
            "leave": "depart",
            "stay": "remain",
            "wait": "anticipate",
            "meet": "encounter",
            "see": "witness",
            "watch": "observe",
            "look": "examine",
            "show": "demonstrate",
            "tell": "inform",
            "say": "state",
            "speak": "verbalize",
            "talk": "converse",
            "listen": "attend",
            "hear": "perceive",
            "feel": "experience",
            "touch": "contact",
            "smell": "odor",
            "taste": "flavor",
            "eat": "consume",
            "drink": "imbibe",
            "sleep": "rest",
            "wake": "arise",
            "dream": "aspire",
            "think": "cogitate",
            "believe": "hold",
            "know": "comprehend",
            "understand": "grasp",
            "learn": "acquire knowledge",
            "teach": "instruct",
            "study": "examine",
            "read": "peruse",
            "write": "compose",
            "draw": "illustrate",
            "paint": "depict",
            "sing": "vocalize",
            "dance": "move rhythmically",
            "play": "engage",
            "work": "labor",
            "rest": "repose",
            "run": "sprint",
            "walk": "ambulate",
            "jump": "leap",
            "sit": "be seated",
            "stand": "be upright",
            "lie": "recline",
            "fall": "descend",
            "rise": "ascend",
            "grow": "expand",
            "shrink": "contract",
            "increase": "augment",
            "decrease": "diminish",
            "add": "append",
            "remove": "eliminate",
            "include": "incorporate",
            "exclude": "omit",
            "open": "commence",
            "close": "conclude",
            "enter": "access",
            "exit": "egress",
            "build": "construct",
            "destroy": "demolish",
            "create": "generate",
            "make": "fabricate",
            "do": "perform",
            "undo": "reverse",
            "redo": "repeat",
            "use": "utilize",
            "need": "require",
            "want": "desire",
            "like": "prefer",
            "love": "cherish",
            "hate": "detest",
            "enjoy": "appreciate",
            "dislike": "disapprove",
            "care": "attend",
            "ignore": "disregard",
            "help": "assist",
            "hinder": "impede",
            "support": "uphold",
            "oppose": "resist",
            "agree": "concur",
            "disagree": "dissent",
            "argue": "contend",
            "discuss": "deliberate",
            "debate": "dispute",
            "decide": "determine",
            "choose": "select",
            "pick": "opt",
            "prefer": "favor",
            "want": "desire",
            "need": "require",
            "must": "must necessarily",
            "should": "ought to",
            "can": "is capable of",
            "could": "might be able to",
            "would": "might",
            "will": "shall",
            "may": "might",
            "might": "could potentially",
            "maybe": "perhaps",
            "perhaps": "possibly",
            "probably": "likely",
            "certainly": "undoubtedly",
            "definitely": "indisputably",
            "absolutely": "unquestionably",
            "totally": "completely",
            "completely": "entirely",
            "entirely": "wholly",
            "fully": "thoroughly",
            "partly": "partially",
            "mostly": "predominantly",
            "mainly": "primarily",
            "largely": "substantially",
            "generally": "typically",
            "usually": "commonly",
            "often": "frequently",
            "sometimes": "occasionally",
            "rarely": "infrequently",
            "never": "never",
            "always": "invariably",
            "constantly": "perpetually",
            "continuously": "incessantly"
        }
    
    def _load_grammar_fixes(self) -> Dict[str, str]:
        """
        Common grammar mistakes and their corrections
        """
        return {
            # Subject-verb agreement
            "they was": "they were",
            "he were": "he was",
            "she were": "she was",
            "we was": "we were",
            "you was": "you were",
            "there is many": "there are many",
            "there is several": "there are several",
            "there is numerous": "there are numerous",
            "there's many": "there are many",
            "there's several": "there are several",
            
            # Double negatives
            "didn't do nothing": "did nothing",
            "couldn't find nothing": "could find nothing",
            "wouldn't say nothing": "would say nothing",
            "shouldn't do nothing": "should do nothing",
            "haven't got none": "have none",
            "don't know nothing": "know nothing",
            "can't get no": "cannot get any",
            "won't do nothing": "will do nothing",
            "isn't nothing": "is nothing",
            "aren't any": "are no",
            
            # Preposition errors
            "different than": "different from",
            "different to": "different from",
            "similar with": "similar to",
            "compare to" : "compare with" ,  # For detailed comparison
            "contrast to": "contrast with",
            "based off": "based on",
            "based upon": "based on",
            "in regards to": "in regard to",
            "with regards to": "with regard to",
            "irregardless": "regardless",
            "towards": "toward",
            "forwards": "forward",
            "backwards": "backward",
            "afterwards": "afterward",
            "upwards": "upward",
            "downwards": "downward",
            
            # Article errors
            "a unique": "a unique",  # Correct - 'unique' starts with consonant sound
            "an unique": "a unique",  # Incorrect
            "a hour": "an hour",  # 'hour' starts with vowel sound
            "an hour": "an hour",  # Correct
            "a historical": "a historical",  # Both acceptable, but 'a' more common
            "an historical": "a historical",  # Less common in modern usage
            "a university": "a university",  # Correct - 'university' starts with consonant sound
            "an university": "a university",  # Incorrect
            "a one": "a one",  # Correct - 'one' starts with 'w' sound
            "an one": "a one",  # Incorrect
            
            # Pronoun errors
            "me and him": "he and I",
            "me and her": "she and I",
            "him and me": "he and I",
            "her and me": "she and I",
            "me and them": "they and I",
            "myself and": "I and",
            "yourself and": "you and",
            "hisself": "himself",
            "theirselves": "themselves",
            "theirself": "themselves",
            "ourself": "ourselves",
            "yourselfs": "yourselves",
            
            # Comparative/superlative errors
            "more better": "better",
            "more worse": "worse",
            "more faster": "faster",
            "more slower": "slower",
            "most best": "best",
            "most worst": "worst",
            "most fastest": "fastest",
            "most slowest": "slowest",
            "more unique": "unique",  # 'Unique' is absolute
            "most unique": "unique",
            "more perfect": "perfect",  # 'Perfect' is absolute
            "most perfect": "perfect",
            "more complete": "more complete",  # Can be acceptable
            "most complete": "most complete",  # Can be acceptable
            
            # Verb tense errors
            "have went": "have gone",
            "has went": "has gone",
            "had went": "had gone",
            "have saw": "have seen",
            "has saw": "has seen",
            "had saw": "had seen",
            "have did": "have done",
            "has did": "has done",
            "had did": "had done",
            "have came": "have come",
            "has came": "has come",
            "had came": "had come",
            "have ran": "have run",
            "has ran": "has run",
            "had ran": "had run",
            "have wrote": "have written",
            "has wrote": "has written",
            "had wrote": "had written",
            "have broke": "have broken",
            "has broke": "has broken",
            "had broke": "had broken",
            "have spoke": "have spoken",
            "has spoke": "has spoken",
            "had spoke": "had spoken",
            "have drove": "have driven",
            "has drove": "has driven",
            "had drove": "had driven",
            "have rode": "have ridden",
            "has rode": "has ridden",
            "had rode": "had ridden",
            "have chose": "have chosen",
            "has chose": "has chosen",
            "had chose": "had chosen",
            "have froze": "have frozen",
            "has froze": "has frozen",
            "had froze": "had frozen",
            
            # Conditional errors
            "if I was": "if I were",  # Subjunctive mood
            "if he was": "if he were",
            "if she was": "if she were",
            "if it was": "if it were",
            "if they was": "if they were",
            "I wish I was": "I wish I were",
            "I wish he was": "I wish he were",
            "I wish she was": "I wish she were",
            "I wish it was": "I wish it were",
            
            # Commonly confused words
            "there": "there",  # Location
            "their": "their",  # Possession
            "they're": "they are",  # Contraction
            "your": "your",  # Possession
            "you're": "you are",  # Contraction
            "its": "its",  # Possession
            "it's": "it is",  # Contraction
            "whose": "whose",  # Possession
            "who's": "who is",  # Contraction
            "then": "then",  # Time
            "than": "than",  # Comparison
            "affect": "affect",  # Verb: to influence
            "effect": "effect",  # Noun: result
            "accept": "accept",  # To receive
            "except": "except",  # To exclude
            "advice": "advice",  # Noun: recommendation
            "advise": "advise",  # Verb: to recommend
            "loose": "loose",  # Not tight
            "lose": "lose",  # To misplace
            "lead": "lead",  # Present tense
            "led": "led",  # Past tense
            "breath": "breath",  # Noun
            "breathe": "breathe",  # Verb
            
            # Redundancies
            "ATM machine": "ATM",  # ATM = Automated Teller Machine
            "PIN number": "PIN",  # PIN = Personal Identification Number
            "HIV virus": "HIV",  # HIV = Human Immunodeficiency Virus
            "LCD display": "LCD",  # LCD = Liquid Crystal Display
            "ISBN number": "ISBN",  # ISBN = International Standard Book Number
            "UPC code": "UPC",  # UPC = Universal Product Code
            "GPS system": "GPS",  # GPS = Global Positioning System
            "ABS system": "ABS",  # ABS = Anti-lock Braking System
            "DC current": "DC",  # DC = Direct Current
            "AC current": "AC",  # AC = Alternating Current
            "CAD design": "CAD",  # CAD = Computer-Aided Design
            "CMS system": "CMS",  # CMS = Content Management System
            "ERP system": "ERP",  # ERP = Enterprise Resource Planning
            "CRM system": "CRM",  # CRM = Customer Relationship Management
            "PDF format": "PDF",  # PDF = Portable Document Format
            "HTML format": "HTML",  # HTML = Hypertext Markup Language
            "CSS styling": "CSS",  # CSS = Cascading Style Sheets
            "JS JavaScript": "JavaScript",  # JS = JavaScript
            "IP address": "IP address",  # IP = Internet Protocol (keep 'address')
            "URL address": "URL",  # URL = Uniform Resource Locator
            "SMS message": "SMS",  # SMS = Short Message Service
            "MMS message": "MMS",  # MMS = Multimedia Messaging Service
            "RSS feed": "RSS",  # RSS = Really Simple Syndication
            "same exact": "exactly the same",
            "exact same": "exactly the same",
            "free gift": "gift",
            "past history": "history",
            "past experience": "experience",
            "future plans": "plans",
            "advance planning": "planning",
            "advance warning": "warning",
            "added bonus": "bonus",
            "unexpected surprise": "surprise",
            "end result": "result",
            "final outcome": "outcome",
            "general public": "public",
            "usual custom": "custom",
            "each and every": "each",
            "first and foremost": "first",
            "last and final": "final",
            "one and the same": "the same",
            "sum total": "total",
            "completely full": "full",
            "completely empty": "empty",
            "totally unique": "unique",
            "absolutely essential": "essential",
            "very unique": "unique",
            "very excellent": "excellent",
            "very perfect": "perfect",
            "more preferable": "preferable",
            "more optimal": "optimal",
            "most optimal": "optimal",
            "more superior": "superior",
            "most superior": "superior",
            "more inferior": "inferior",
            "most inferior": "inferior",
            
            # Split infinitives (can be fixed based on style)
            "to boldly go": "to go boldly",  # Classic example
            "to quickly run": "to run quickly",
            "to easily understand": "to understand easily",
            "to carefully consider": "to consider carefully",
            "to thoroughly examine": "to examine thoroughly",
            
            # Dangling modifiers
            "Walking to school, the bus passed me": "While I was walking to school, the bus passed me",
            "Running quickly, the finish line approached": "As I ran quickly, the finish line approached",
            "After reading the book, the movie was disappointing": "After I read the book, I found the movie disappointing",
            "Being late, the meeting started without me": "Because I was late, the meeting started without me",
            "Tired and hungry, dinner was welcome": "Tired and hungry, I welcomed dinner",
            
            # Sentence fragments
            "Because I said so.": "This is because I said so.",
            "When we arrived.": "When we arrived, the situation became clear.",
            "If that happens.": "If that happens, consequences will follow.",
            "Although it's true.": "Although it's true, other factors exist.",
            "Especially when.": "Especially when conditions are favorable.",
            
            # Run-on sentences
            "I went to the store I bought milk.": "I went to the store and bought milk.",
            "He ran fast he won the race.": "He ran fast and won the race.",
            "She studied hard she passed the exam.": "She studied hard, so she passed the exam.",
            "They arrived late the show had started.": "They arrived late; the show had already started.",
            "It was raining we stayed inside.": "Because it was raining, we stayed inside."
        }
    
    def _load_transition_phrases(self) -> Dict[str, List[str]]:
        """
        Academic transition phrases for different purposes
        """
        return {
            # Adding information
            "addition": [
                "furthermore",
                "moreover",
                "additionally",
                "in addition",
                "further",
                "also",
                "besides",
                "not to mention",
                "what is more",
                "equally important"
            ],
            
            # Showing contrast
            "contrast": [
                "however",
                "nevertheless",
                "nonetheless",
                "on the other hand",
                "conversely",
                "in contrast",
                "yet",
                "still",
                "although",
                "despite this",
                "notwithstanding",
                "alternatively",
                "on the contrary",
                "rather"
            ],
            
            # Showing cause and effect
            "cause_effect": [
                "therefore",
                "thus",
                "hence",
                "consequently",
                "accordingly",
                "as a result",
                "for this reason",
                "due to this",
                "because of this",
                "as a consequence",
                "in consequence",
                "thereby",
                "resulting in",
                "leading to"
            ],
            
            # Showing similarity
            "similarity": [
                "similarly",
                "likewise",
                "in the same way",
                "equally",
                "by the same token",
                "correspondingly",
                "in similar fashion",
                "analogously"
            ],
            
            # Emphasizing a point
            "emphasis": [
                "indeed",
                "in fact",
                "significantly",
                "notably",
                "importantly",
                "of course",
                "to emphasize",
                "as a matter of fact",
                "in particular",
                "particularly",
                "especially",
                "above all"
            ],
            
            # Giving examples
            "example": [
                "for example",
                "for instance",
                "as an illustration",
                "to illustrate",
                "such as",
                "including",
                "particularly",
                "specifically",
                "to demonstrate",
                "as evidenced by",
                "in the case of"
            ],
            
            # Showing sequence
            "sequence": [
                "first",
                "firstly",
                "second",
                "secondly",
                "third",
                "thirdly",
                "next",
                "then",
                "subsequently",
                "afterward",
                "later",
                "following this",
                "previously",
                "prior to",
                "simultaneously",
                "concurrently",
                "meanwhile"
            ],
            
            # Summarizing or concluding
            "conclusion": [
                "in conclusion",
                "to conclude",
                "in summary",
                "to summarize",
                "in sum",
                "overall",
                "ultimately",
                "finally",
                "all things considered",
                "taking everything into account",
                "in the final analysis",
                "in essence",
                "in brief",
                "to recapitulate"
            ],
            
            # Showing concession
            "concession": [
                "admittedly",
                "certainly",
                "granted",
                "of course",
                "to be sure",
                "it is true that",
                "while it may be true that",
                "although",
                "even though",
                "despite the fact that"
            ],
            
            # Clarifying or rephrasing
            "clarification": [
                "in other words",
                "that is",
                "to put it differently",
                "to clarify",
                "more simply",
                "to explain",
                "specifically",
                "namely",
                "i.e.",
                "e.g.",
                "viz."
            ]
        }
    
    def _load_hedging_language(self) -> Dict[str, List[str]]:
        """
        Hedging language for academic writing (to express uncertainty appropriately)
        """
        return {
            # Strong hedging (very uncertain)
            "strong_hedge": [
                "it is possible that",
                "it may be that",
                "it could be that",
                "perhaps",
                "possibly",
                "maybe",
                "might",
                "could",
                "potentially",
                "conceivably"
            ],
            
            # Moderate hedging
            "moderate_hedge": [
                "it appears that",
                "it seems that",
                "it suggests that",
                "tentatively",
                "apparently",
                "seemingly",
                "presumably",
                "arguably",
                "one might argue that"
            ],
            
            # Weak hedging (more confident)
            "weak_hedge": [
                "it is likely that",
                "it is probable that",
                "generally",
                "typically",
                "usually",
                "often",
                "frequently",
                "in most cases",
                "tends to",
                "indicates that"
            ],
            
            # Hedging verbs
            "hedging_verbs": [
                "suggests",
                "indicates",
                "implies",
                "appears",
                "seems",
                "tends",
                "may",
                "might",
                "could",
                "would",
                "can"
            ],
            
            # Hedging nouns
            "hedging_nouns": [
                "possibility",
                "probability",
                "likelihood",
                "tendency",
                "indication",
                "suggestion",
                "implication"
            ],
            
            # Hedging adverbs
            "hedging_adverbs": [
                "possibly",
                "probably",
                "likely",
                "unlikely",
                "perhaps",
                "maybe",
                "arguably",
                "presumably",
                "tentatively",
                "approximately",
                "roughly",
                "about",
                "around",
                "almost",
                "nearly"
            ]
        }
    
    def _load_strong_verbs(self) -> Dict[str, List[str]]:
        """
        Strong academic verbs categorized by purpose
        """
        return {
            # Verbs for showing agreement
            "agreement": [
                "confirms",
                "corroborates",
                "substantiates",
                "validates",
                "verifies",
                "supports",
                "endorses",
                "reinforces",
                "strengthens",
                "bolsters"
            ],
            
            # Verbs for showing disagreement
            "disagreement": [
                "contradicts",
                "refutes",
                "challenges",
                "disputes",
                "counters",
                "opposes",
                "rebuts",
                "denies",
                "repudiates",
                "negates"
            ],
            
            # Verbs for analysis
            "analysis": [
                "analyzes",
                "examines",
                "investigates",
                "explores",
                "evaluates",
                "assesses",
                "appraises",
                "scrutinizes",
                "dissects",
                "deconstructs"
            ],
            
            # Verbs for showing evidence
            "evidence": [
                "demonstrates",
                "illustrates",
                "exemplifies",
                "shows",
                "reveals",
                "displays",
                "exhibits",
                "manifests",
                "evidences",
                "attests"
            ],
            
            # Verbs for argumentation
            "argument": [
                "argues",
                "contends",
                "asserts",
                "maintains",
                "posits",
                "postulates",
                "theorizes",
                "hypothesizes",
                "proposes",
                "suggests"
            ],
            
            # Verbs for description
            "description": [
                "describes",
                "depicts",
                "portrays",
                "characterizes",
                "represents",
                "illustrates",
                "outlines",
                "sketches",
                "traces",
                "chronicles"
            ],
            
            # Verbs for comparison
            "comparison": [
                "compares",
                "contrasts",
                "differentiates",
                "distinguishes",
                "juxtaposes",
                "likens",
                "equates",
                "parallels",
                "correlates",
                "relates"
            ],
            
            # Verbs for causation
            "causation": [
                "causes",
                "produces",
                "generates",
                "leads to",
                "results in",
                "contributes to",
                "influences",
                "affects",
                "impacts",
                "shapes"
            ]
        }
    
    def improve_text(self, text: str) -> Dict:
        """
        Main method to improve text to academic tone
        """
        # Track changes for reporting
        changes = []
        original = text
        
        # Apply grammar fixes first
        text, grammar_changes = self._fix_grammar(text)
        changes.extend(grammar_changes)
        
        # Replace weak phrases
        text, phrase_changes = self._replace_weak_phrases(text)
        changes.extend(phrase_changes)
        
        # Apply vocabulary upgrades
        text, vocab_changes = self._upgrade_vocabulary(text)
        changes.extend(vocab_changes)
        
        # Improve sentence structure
        text, structure_changes = self._improve_structure(text)
        changes.extend(structure_changes)
        
        # Add appropriate transitions
        text, transition_changes = self._add_transitions(text)
        changes.extend(transition_changes)
        
        # Apply hedging where appropriate
        text, hedging_changes = self._apply_hedging(text)
        changes.extend(hedging_changes)
        
        # Final formatting
        text = self._final_formatting(text)
        
        # Generate metrics
        metrics = self._calculate_metrics(original, text)
        
        return {
            'original': original,
            'improved': text,
            'changes': changes,
            'metrics': metrics,
            'suggestions': self._generate_suggestions(metrics)
        }
    
    def _fix_grammar(self, text: str) -> Tuple[str, List[str]]:
        """
        Fix common grammar mistakes
        """
        changes = []
        
        # Apply grammar fixes from dictionary
        for wrong, correct in self.grammar_fixes.items():
            if wrong in text.lower():
                pattern = r'\b' + re.escape(wrong) + r'\b'
                if re.search(pattern, text.lower()):
                    text = re.sub(pattern, correct, text, flags=re.IGNORECASE)
                    changes.append(f"Grammar: '{wrong}' → '{correct}'")
        
        return text, changes
    
    def _replace_weak_phrases(self, text: str) -> Tuple[str, List[str]]:
        """
        Replace weak phrases with academic alternatives
        """
        changes = []
        
        for weak_phrase, alternatives in self.weak_phrases.items():
            pattern = r'\b' + re.escape(weak_phrase) + r'\b'
            if re.search(pattern, text.lower()):
                # Choose appropriate alternative (can be randomized or context-based)
                alternative = alternatives[0]  # Simple approach - use first
                
                # Preserve case
                if weak_phrase[0].isupper():
                    alternative = alternative.capitalize()
                
                text = re.sub(pattern, alternative, text, flags=re.IGNORECASE)
                changes.append(f"Phrase: '{weak_phrase}' → '{alternative}'")
        
        return text, changes
    
    def _upgrade_vocabulary(self, text: str) -> Tuple[str, List[str]]:
        """
        Upgrade common words to academic alternatives
        """
        changes = []
        words = text.split()
        upgraded_words = []
        
        for word in words:
            word_lower = word.lower().strip('.,!?;:()[]{}"\'')
            punctuation = word[len(word_lower):] if len(word) > len(word_lower) else ''
            
            if word_lower in self.academic_replacements:
                replacement = self.academic_replacements[word_lower]
                # Preserve capitalization
                if word[0].isupper():
                    replacement = replacement.capitalize()
                
                upgraded_words.append(replacement + punctuation)
                changes.append(f"Vocab: '{word_lower}' → '{replacement}'")
            else:
                upgraded_words.append(word)
        
        return ' '.join(upgraded_words), changes
    
    def _improve_structure(self, text: str) -> Tuple[str, List[str]]:
        """
        Improve sentence structure and flow
        """
        changes = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        improved_sentences = []
        
        for sentence in sentences:
            original = sentence
            
            # Fix sentence length (combine short sentences or break long ones)
            word_count = len(sentence.split())
            
            if word_count < 5:
                # Too short - mark for review
                changes.append(f"Structure: Short sentence detected - consider expanding")
            
            if word_count > 30:
                # Too long - suggest breaking
                changes.append(f"Structure: Long sentence detected - consider breaking into multiple sentences")
            
            # Fix passive voice (basic implementation)
            if re.search(r'\b(am|is|are|was|were|be|been|being)\s+\w+ed\b', sentence):
                changes.append(f"Structure: Passive voice detected - consider active voice")
            
            improved_sentences.append(sentence)
        
        return ' '.join(improved_sentences), changes
    
    def _add_transitions(self, text: str) -> Tuple[str, List[str]]:
        """
        Add appropriate transition phrases
        """
        changes = []
        paragraphs = text.split('\n\n')
        
        if len(paragraphs) > 1:
            for i in range(1, len(paragraphs)):
                # Add transition to start of paragraph if it doesn't already have one
                if paragraphs[i] and not any(paragraphs[i].startswith(t) for t in self.transition_phrases['addition']):
                    transition = self.transition_phrases['addition'][0].capitalize() + ', '
                    paragraphs[i] = transition + paragraphs[i]
                    changes.append(f"Transition: Added '{transition}'")
        
        return '\n\n'.join(paragraphs), changes
    
    def _apply_hedging(self, text: str) -> Tuple[str, List[str]]:
        """
        Apply appropriate hedging language
        """
        changes = []
        
        # Look for statements that might need hedging
        strong_statements = re.finditer(r'\b(is|are|was|were|will|shall|must|always|never)\b', text)
        
        for match in strong_statements:
            # Simple approach - add hedging suggestion
            changes.append(f"Hedging: Consider softening absolute statement near '{match.group()}'")
        
        return text, changes
    
    def _final_formatting(self, text: str) -> str:
        """
        Apply final formatting rules
        """
        # Ensure proper spacing after punctuation
        text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure proper capitalization at sentence starts
        sentences = re.split(r'([.!?]\s+)', text)
        for i in range(0, len(sentences), 2):
            if sentences[i]:
                sentences[i] = sentences[i][0].upper() + sentences[i][1:]
        
        return ''.join(sentences)
    
    def _calculate_metrics(self, original: str, improved: str) -> Dict:
        """
        Calculate improvement metrics
        """
        original_words = len(original.split())
        improved_words = len(improved.split())
        
        # Count changes
        original_weak_count = sum(
            1 for phrase in self.weak_phrases 
            if phrase in original.lower()
        )
        improved_weak_count = sum(
            1 for phrase in self.weak_phrases 
            if phrase in improved.lower()
        )
        
        # Calculate average word length (academic texts tend to have longer words)
        original_avg_word_length = sum(len(word) for word in original.split()) / original_words if original_words > 0 else 0
        improved_avg_word_length = sum(len(word) for word in improved.split()) / improved_words if improved_words > 0 else 0
        
        return {
            'word_count_change': improved_words - original_words,
            'weak_phrases_reduced': original_weak_count - improved_weak_count,
            'avg_word_length_change': round(improved_avg_word_length - original_avg_word_length, 2),
            'academic_score': self._calculate_academic_score(improved),
            'readability_level': self._estimate_readability_level(improved)
        }
    
    def _calculate_academic_score(self, text: str) -> int:
        """
        Calculate academic tone score (0-100)
        """
        score = 50  # Start at neutral
        
        words = text.split()
        
        # Check for academic vocabulary
        academic_word_count = sum(
            1 for word in words 
            if word.lower() in self.academic_replacements.values()
        )
        score += min(academic_word_count * 2, 25)
        
        # Check for hedging (appropriate for academic writing)
        hedge_count = sum(
            1 for hedge_list in self.hedging_language.values()
            for hedge in hedge_list
            if hedge in text.lower()
        )
        score += min(hedge_count * 2, 15)
        
        # Penalize remaining weak phrases
        weak_phrase_count = sum(
            1 for phrase in self.weak_phrases
            if phrase in text.lower()
        )
        score -= weak_phrase_count * 5
        
        return max(0, min(100, score))
    
    def _estimate_readability_level(self, text: str) -> str:
        """
        Estimate the readability/academic level
        """
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        if avg_word_length < 4:
            return "Basic/Conversational"
        elif avg_word_length < 5:
            return "Intermediate"
        elif avg_word_length < 6:
            return "Advanced Undergraduate"
        elif avg_word_length < 7:
            return "Graduate Level"
        else:
            return "Expert/Scholarly"
    
    def _generate_suggestions(self, metrics: Dict) -> List[str]:
        """
        Generate improvement suggestions based on metrics
        """
        suggestions = []
        
        if metrics['weak_phrases_reduced'] < 0:
            suggestions.append("Consider replacing more weak phrases with academic alternatives")
        
        if metrics['avg_word_length_change'] < 0.5:
            suggestions.append("Use more sophisticated vocabulary for stronger academic tone")
        
        if metrics['academic_score'] < 60:
            suggestions.append("Add more academic vocabulary and complex sentence structures")
        elif metrics['academic_score'] < 80:
            suggestions.append("Good academic tone - consider adding more hedging language for nuance")
        else:
            suggestions.append("Excellent academic tone - text is ready for scholarly publication")
        
        suggestions.append("Review any remaining passive voice constructions")
        suggestions.append("Ensure all claims are properly supported with evidence")
        suggestions.append("Check for consistent use of academic terminology throughout")
        
        return suggestions


# Example usage function
def improve_to_academic(text: str) -> Dict:
    """
    Convenience function to improve text to academic tone
    """
    improver = AcademicToneImprover()
    return improver.improve_text(text)


# Test the improver
if __name__ == "__main__":
    # Example usage
    sample_text = """
    I think this is a good idea. There's a lot of things to consider. 
    The project was really important and we got good results. 
    But we need to think about some problems that came up.
    """
    
    result = improve_to_academic(sample_text)
    
    print("ORIGINAL TEXT:")
    print(result['original'])
    print("\n" + "="*50)
    print("IMPROVED TEXT:")
    print(result['improved'])
    print("\n" + "="*50)
    print("CHANGES MADE:")
    for change in result['changes'][:10]:  # Show first 10 changes
        print(f"  • {change}")
    print("\n" + "="*50)
    print("METRICS:")
    for key, value in result['metrics'].items():
        print(f"  • {key}: {value}")
    print("\n" + "="*50)
    print("SUGGESTIONS:")
    for suggestion in result['suggestions']:
        print(f"  • {suggestion}")
















class CVImprover(AcademicToneImprover):
    """
    Specialized CV/Resume text improver
    Fixes common resume mistakes that cost people job opportunities
    """
    
    def __init__(self):
        super().__init__()
        self.cv_weak_phrases = self._load_cv_weak_phrases()
        self.action_verbs = self._load_action_verbs()
        self.accomplishment_templates = self._load_accomplishment_templates()
        self.cv_grammar_fixes = self._load_cv_grammar_fixes()
        self.bullet_point_starters = self._load_bullet_point_starters()
        self.industry_keywords = self._load_industry_keywords()
        
    def _load_cv_weak_phrases(self) -> Dict[str, List[str]]:
        """
        Weak CV phrases that kill resumes and their powerful alternatives
        """
        return {
            # Weak job descriptions
            "responsible for": [
                "Spearheaded",
                "Led",
                "Directed",
                "Managed",
                "Oversaw",
                "Championed",
                "Orchestrated",
                "Pioneered"
            ],
            "duties included": [
                "Key accomplishments included",
                "Notable achievements",
                "Significant contributions",
                "Major wins included"
            ],
            "worked on": [
                "Executed",
                "Implemented",
                "Developed",
                "Engineered",
                "Architected",
                "Delivered"
            ],
            "helped with": [
                "Facilitated",
                "Contributed to",
                "Assisted in",
                "Supported",
                "Collaborated on"
            ],
            "in charge of": [
                "Directed",
                "Headed",
                "Managed",
                "Supervised",
                "Oversaw",
                "Led"
            ],
            "dealt with": [
                "Resolved",
                "Addressed",
                "Handled",
                "Managed",
                "Navigated",
                "Mitigated"
            ],
            "tasked with": [
                "Charged with",
                "Accountable for",
                "Responsible for delivering",
                "Entrusted with"
            ],
            
            # Weak personal qualities
            "team player": [
                "Collaborative professional",
                "Cross-functional partner",
                "Team facilitator",
                "Relationship builder"
            ],
            "people person": [
                "Relationship builder",
                "Stakeholder manager",
                "Client liaison",
                "Interpersonal specialist"
            ],
            "hard worker": [
                "Diligent professional",
                "Dedicated achiever",
                "Committed performer",
                "Consistent overachiever"
            ],
            "fast learner": [
                "Rapidly adapts to new technologies",
                "Quickly masters complex concepts",
                "Accelerated learning curve",
                "Adept at acquiring new skills"
            ],
            "motivated": [
                "Self-motivated",
                "Driven",
                "Ambitious",
                "Goal-oriented",
                "Results-driven"
            ],
            "detail-oriented": [
                "Meticulous attention to detail",
                "Precision-focused",
                "Thorough and accurate",
                "Exacting standards"
            ],
            "organized": [
                "Systematic approach",
                "Methodical planner",
                "Strategic organizer",
                "Efficient coordinator"
            ],
            
            # Weak communication
            "good communication skills": [
                "Articulate presenter",
                "Persuasive communicator",
                "Effective negotiator",
                "Clear concise writer"
            ],
            "excellent communication": [
                "Exceptional interpersonal skills",
                "Masterful communicator",
                "Skilled facilitator",
                "Proficient negotiator"
            ],
            "verbal and written skills": [
                "Bilingual communicator",
                "Multilingual proficiency",
                "Cross-cultural communicator"
            ],
            
            # Weak leadership
            "led team": [
                "Directed high-performance team",
                "Spearheaded cross-functional initiative",
                "Orchestrated collaborative effort",
                "Guided strategic initiatives"
            ],
            "managed people": [
                "Mentored junior staff",
                "Developed team capabilities",
                "Cultivated talent",
                "Coached team members"
            ],
            "leadership skills": [
                "Strategic vision",
                "Executive presence",
                "Organizational leadership",
                "Team development"
            ],
            
            # Weak achievements
            "did well": [
                "Exceeded expectations",
                "Surpassed targets",
                "Outperformed benchmarks",
                "Achieved excellence"
            ],
            "successful": [
                "High-impact",
                "Results-driven",
                "Proven track record",
                "Demonstrated success"
            ],
            "accomplished": [
                "Executed successfully",
                "Delivered results",
                "Achieved milestones",
                "Realized objectives"
            ],
            "helped company": [
                "Drove organizational growth",
                "Enhanced operational efficiency",
                "Optimized business processes",
                "Accelerated company objectives"
            ],
            "made better": [
                "Optimized",
                "Enhanced",
                "Improved",
                "Refined",
                "Elevated",
                "Upgraded"
            ],
            "saved money": [
                "Reduced costs",
                "Decreased expenditures",
                "Minimized overhead",
                "Optimized budget allocation"
            ],
            
            # Weak technical skills
            "know": [
                "Proficient in",
                "Experienced with",
                "Skilled in",
                "Expertise in",
                "Mastery of",
                "Advanced knowledge of"
            ],
            "familiar with": [
                "Working knowledge of",
                "Hands-on experience with",
                "Practical expertise in",
                "Proficient in"
            ],
            "basic knowledge": [
                "Foundational understanding",
                "Working familiarity",
                "Introductory proficiency"
            ],
            
            # Weak time phrases
            "worked for": [
                "Contributed to",
                "Served at",
                "Affiliated with",
                "Employed by"
            ],
            "currently working": [
                "Presently employed",
                "Currently serving",
                "Now contributing"
            ],
            
            # Weak problem-solving
            "problem solver": [
                "Strategic problem-solver",
                "Analytical thinker",
                "Solution architect",
                "Critical thinker"
            ],
            "solved problems": [
                "Resolved complex issues",
                "Mitigated risks",
                "Navigated challenges",
                "Overcame obstacles"
            ],
            "fix issues": [
                "Troubleshot effectively",
                "Resolved technical debt",
                "Eliminated bottlenecks",
                "Streamlined processes"
            ],
            
            # Filler phrases
            "trying to": [
                "Aiming to",
                "Seeking to",
                "Striving to",
                "Committed to"
            ],
            "hoping to": [
                "Aspire to",
                "Goal-oriented toward",
                "Focused on achieving"
            ],
            "looking for": [
                "Seeking opportunity in",
                "Pursuing position as",
                "Targeting role in"
            ],
            
            # Overused buzzwords to replace
            "synergy": [
                "Collaborative efficiency",
                "Integrated approach",
                "Unified effort"
            ],
            "think outside the box": [
                "Innovative approach",
                "Creative problem-solving",
                "Novel methodology"
            ],
            "go-getter": [
                "Proactive achiever",
                "Self-starting professional",
                "Initiative-driven"
            ],
            "rockstar": [
                "Top performer",
                "Exceptional talent",
                "High achiever"
            ],
            "ninja": [
                "Expert",
                "Specialist",
                "Master"
            ],
            "guru": [
                "Authority",
                "Expert",
                "Specialist"
            ]
        }
    
    def _load_action_verbs(self) -> Dict[str, List[str]]:
        """
        Powerful action verbs categorized for CVs
        """
        return {
            "leadership": [
                "Spearheaded", "Orchestrated", "Pioneered", "Championed",
                "Directed", "Guided", "Mentored", "Supervised", "Headed",
                "Governed", "Steered", "Commanded", "Presided", "Moderated"
            ],
            
            "achievement": [
                "Accelerated", "Achieved", "Attained", "Completed", "Conquered",
                "Delivered", "Demonstrated", "Earned", "Exceeded", "Excelled",
                "Generated", "Mastered", "Outperformed", "Reached", "Secured",
                "Surpassed", "Won", "Outpaced", "Outdistanced"
            ],
            
            "management": [
                "Administered", "Allocated", "Assigned", "Chaired", "Controlled",
                "Coordinated", "Delegated", "Executed", "Managed", "Organized",
                "Oversaw", "Planned", "Prioritized", "Produced", "Scheduled",
                "Supervised", "Tasked", "Triaged"
            ],
            
            "communication": [
                "Addressed", "Articulated", "Authored", "Briefed", "Collaborated",
                "Communicated", "Composed", "Conveyed", "Convinced", "Corresponded",
                "Counseled", "Demonstrated", "Edited", "Educated", "Explained",
                "Expressed", "Facilitated", "Influenced", "Interpreted", "Interviewed",
                "Lectured", "Mediated", "Moderated", "Negotiated", "Persuaded",
                "Presented", "Promoted", "Publicized", "Published", "Reported",
                "Resolved", "Spoke", "Suggested", "Synthesized", "Wrote"
            ],
            
            "creative": [
                "Conceptualized", "Created", "Customized", "Designed", "Developed",
                "Devised", "Discovered", "Drafted", "Established", "Fashioned",
                "Founded", "Generated", "Illustrated", "Imagined", "Improved",
                "Incorporated", "Initiated", "Innovated", "Instituted", "Integrated",
                "Introduced", "Invented", "Launched", "Modeled", "Modified",
                "Originated", "Performed", "Redesigned", "Revitalized", "Shaped"
            ],
            
            "technical": [
                "Architected", "Assembled", "Built", "Calculated", "Coded",
                "Computed", "Debugged", "Designed", "Detected", "Diagnosed",
                "Engineered", "Fortified", "Implemented", "Installed", "Integrated",
                "Maintained", "Operated", "Optimized", "Overhauled", "Programmed",
                "Re-engineered", "Repaired", "Replaced", "Restored", "Solved",
                "Specified", "Streamlined", "Tested", "Troubleshot", "Upgraded"
            ],
            
            "research": [
                "Analyzed", "Assessed", "Clarified", "Collected", "Compared",
                "Conducted", "Critiqued", "Derived", "Discovered", "Evaluated",
                "Examined", "Experimented", "Explored", "Extracted", "Formulated",
                "Gathered", "Hypothesized", "Identified", "Inspected", "Interpreted",
                "Investigated", "Measured", "Observed", "Qualified", "Quantified",
                "Researched", "Reviewed", "Studied", "Surveyed", "Tested", "Uncovered"
            ],
            
            "financial": [
                "Allocated", "Analyzed", "Appraised", "Approved", "Audited",
                "Balanced", "Budgeted", "Calculated", "Controlled", "Cut",
                "Decreased", "Earned", "Economized", "Eliminated", "Estimated",
                "Evaluated", "Forecasted", "Funded", "Generated", "Improved",
                "Increased", "Invested", "Itemized", "Justified", "Minimized",
                "Monitored", "Negotiated", "Obtained", "Planned", "Prepared",
                "Projected", "Purchased", "Reconciled", "Reduced", "Researched",
                "Restructured", "Retained", "Reviewed", "Saved", "Secured", "Sold"
            ],
            
            "teaching": [
                "Adapted", "Advised", "Coached", "Conducted", "Coordinated",
                "Counseled", "Demonstrated", "Developed", "Educated", "Enabled",
                "Encouraged", "Evaluated", "Explained", "Facilitated", "Fostered",
                "Guided", "Informed", "Instructed", "Mentored", "Modeled",
                "Motivated", "Persuaded", "Presented", "Taught", "Trained", "Tutored"
            ],
            
            "improvement": [
                "Boosted", "Enhanced", "Expanded", "Expedited", "Improved",
                "Increased", "Maximized", "Optimized", "Reinforced", "Revitalized",
                "Sharpened", "Streamlined", "Strengthened", "Transformed", "Upgraded"
            ],
            
            "reduction": [
                "Compressed", "Condensed", "Consolidated", "Decreased", "Diminished",
                "Drove down", "Lowered", "Minimized", "Reduced", "Shrank", "Slashed",
                "Streamlined", "Trimmed"
            ]
        }
    
    def _load_accomplishment_templates(self) -> Dict[str, List[str]]:
        """
        Templates for turning duties into accomplishments
        """
        return {
            "saved_money": [
                "Reduced costs by implementing [strategy]",
                "Decreased expenses through [initiative]",
                "Optimized budget allocation resulting in savings",
                "Minimized overhead by [method]",
                "Cut unnecessary expenditures by [amount]"
            ],
            
            "increased_revenue": [
                "Boosted revenue through [initiative]",
                "Generated additional income via [strategy]",
                "Drove sales growth by expanding [area]",
                "Expanded market share by targeting [segment]",
                "Increased profitability through [method]"
            ],
            
            "improved_efficiency": [
                "Streamlined operations resulting in faster delivery",
                "Reduced processing time by automating [task]",
                "Automated manual processes saving time",
                "Optimized workflow for better throughput",
                "Eliminated bottlenecks in [process]"
            ],
            
            "managed_team": [
                "Led team to achieve [goal]",
                "Mentored junior staff resulting in promotions",
                "Managed cross-functional team delivering [project]",
                "Supervised department achieving [result]",
                "Built high-performing team from scratch"
            ],
            
            "improved_quality": [
                "Reduced error rate through training",
                "Improved customer satisfaction by addressing feedback",
                "Enhanced product quality via testing",
                "Decreased defect rate with new processes",
                "Implemented quality control measures"
            ],
            
            "increased_productivity": [
                "Boosted team productivity with new tools",
                "Increased output through process improvement",
                "Enhanced efficiency by reorganizing workflow",
                "Optimized schedules improving throughput",
                "Implemented productivity tracking system"
            ],
            
            "solved_problems": [
                "Resolved critical issues preventing downtime",
                "Troubleshot complex problems affecting operations",
                "Eliminated bottlenecks slowing production",
                "Mitigated risks before they became issues",
                "Debugged complex system failures"
            ],
            
            "implemented_systems": [
                "Implemented new system improving operations",
                "Deployed technology enhancing productivity",
                "Launched initiative achieving positive results",
                "Rolled out program adopted by entire department",
                "Introduced tool saving time and resources"
            ],
            
            "trained_others": [
                "Trained colleagues on new processes",
                "Developed training program for new hires",
                "Mentored team members improving performance",
                "Certified staff in critical skills",
                "Created documentation adopted company-wide"
            ],
            
            "exceeded_goals": [
                "Surpassed quarterly targets consistently",
                "Exceeded annual goals ahead of schedule",
                "Outperformed benchmarks by significant margin",
                "Achieved above projected results",
                "Delivered beyond expectations"
            ],
            
            "created_new": [
                "Developed innovative solution addressing [problem]",
                "Launched new service adopted by clients",
                "Designed product solving customer pain points",
                "Pioneered approach adopted by team",
                "Built tool from scratch used by [number] users"
            ],
            
            "improved_customer": [
                "Increased customer satisfaction scores",
                "Reduced complaints through better service",
                "Improved retention with follow-up program",
                "Enhanced customer experience via feedback",
                "Resolved issues faster than before"
            ],
            
            "expanded_business": [
                "Entered new markets successfully",
                "Acquired new clients through outreach",
                "Expanded into new region achieving growth",
                "Grew customer base through referrals",
                "Developed partnerships increasing reach"
            ],
            
            "managed_projects": [
                "Delivered project on time and under budget",
                "Managed complex project with multiple stakeholders",
                "Coordinated teams delivering successful outcome",
                "Executed project achieving all milestones",
                "Led project from concept to completion"
            ]
        }
    
    def _load_cv_grammar_fixes(self) -> Dict[str, str]:
        """
        CV-specific grammar and formatting fixes
        """
        return {
            # Common CV typos
            "manger": "manager",
            "managment": "management",
            "developement": "development",
            "acheived": "achieved",
            "recieved": "received",
            "seperate": "separate",
            "responsibile": "responsible",
            "succesful": "successful",
            "succesfully": "successfully",
            "untill": "until",
            "begining": "beginning",
            "ocurred": "occurred",
            "ocurrence": "occurrence",
            "priviledge": "privilege",
            "pubically": "publicly",
            "quantitiy": "quantity",
            "reccomend": "recommend",
            "refered": "referred",
            "responsability": "responsibility",
            "similiar": "similar",
            "speach": "speech",
            "strenght": "strength",
            "sucess": "success",
            "targetted": "targeted",
            "thier": "their",
            "tommorow": "tomorrow",
            "truely": "truly",
            "unforetunately": "unfortunately",
            "unfortunatly": "unfortunately",
            "vacumn": "vacuum",
            "wirting": "writing",
            "writting": "writing",
            "wierd": "weird",
            "wich": "which",
            "withold": "withhold",
            "writen": "written",
            "abberation": "aberration",
            "abreviation": "abbreviation",
            "absense": "absence",
            "abysmal": "abysmal",
            "academc": "academic",
            "accomadate": "accommodate",
            "accomodate": "accommodate",
            "accomodated": "accommodated",
            "accomodates": "accommodates",
            "accomodating": "accommodating",
            "accomodation": "accommodation",
            "accross": "across",
            "acheive": "achieve",
            "acheived": "achieved",
            "acheivement": "achievement",
            "acheivements": "achievements",
            "acknowlegement": "acknowledgment",
            "acknowlegment": "acknowledgment",
            "acommodate": "accommodate",
            "acomplish": "accomplish",
            "acomplished": "accomplished",
            "acomplishment": "accomplishment",
            "acomplishments": "accomplishments",
            "acording": "according",
            "acordingly": "accordingly",
            "acquaintence": "acquaintance",
            "acquiantence": "acquaintance",
            "acquited": "acquitted",
            "addional": "additional",
            "additon": "addition",
            "additonal": "additional",
            "additinally": "additionally",
            "adecuate": "adequate",
            "adhearing": "adhering",
            "adherance": "adherence",
            "adminstrate": "administer",
            "adminstration": "administration",
            "adminstrative": "administrative",
            "adminstrator": "administrator",
            "admissability": "admissibility",
            "admissable": "admissible",
            "adquately": "adequately",
            
            # Tense consistency (for past jobs)
            r'lead\s': 'led ',
            r'manage\s': 'managed ',
            r'create\s': 'created ',
            r'develop\s': 'developed ',
            r'implement\s': 'implemented ',
            r'design\s': 'designed ',
            r'build\s': 'built ',
            r'coordinate\s': 'coordinated ',
            r'organize\s': 'organized ',
            r'oversee\s': 'oversaw ',
            
            # Formatting fixes
            r'^([a-z])': lambda m: m.group(1).upper(),  # Capitalize first letter
            r'\.([A-Z])': r'. \1',  # Space after periods
            r'\s+\.': '.',  # Remove space before period
            r'\s+,': ',',  # Remove space before comma
        }
    
    def _load_bullet_point_starters(self) -> List[str]:
        """
        Strong ways to start bullet points
        """
        return [
            "Spearheaded", "Orchestrated", "Pioneered", "Championed",
            "Directed", "Led", "Managed", "Executed", "Delivered",
            "Achieved", "Exceeded", "Surpassed", "Outperformed",
            "Increased", "Decreased", "Reduced", "Improved", "Optimized",
            "Developed", "Created", "Designed", "Built", "Launched",
            "Implemented", "Integrated", "Streamlined", "Transformed",
            "Negotiated", "Secured", "Generated", "Saved", "Resolved"
        ]
    
    def _load_industry_keywords(self) -> Dict[str, List[str]]:
        """
        Industry-specific keywords for different fields
        """
        return {
            "tech": [
                "Python", "Java", "JavaScript", "React", "Node.js", "AWS",
                "Cloud Computing", "DevOps", "Agile", "Scrum", "API",
                "Database", "SQL", "NoSQL", "Machine Learning", "AI",
                "Full-stack", "Frontend", "Backend", "Mobile Development",
                "iOS", "Android", "Docker", "Kubernetes", "CI/CD"
            ],
            
            "business": [
                "Strategic Planning", "Business Development", "Market Analysis",
                "Competitive Intelligence", "ROI", "KPI", "Stakeholder Management",
                "Change Management", "Risk Mitigation", "Process Optimization",
                "Quality Assurance", "Compliance", "Governance", "Scalability"
            ],
            
            "sales": [
                "Revenue Growth", "Client Acquisition", "Account Management",
                "Sales Pipeline", "Lead Generation", "Conversion Rate",
                "Customer Retention", "Upselling", "Cross-selling", "CRM",
                "Salesforce", "Territory Management", "Quota Attainment"
            ],
            
            "marketing": [
                "Digital Marketing", "Content Strategy", "SEO", "SEM", "PPC",
                "Social Media", "Email Marketing", "Marketing Automation",
                "Brand Management", "Market Research", "Campaign Analysis",
                "ROI Tracking", "Conversion Optimization", "A/B Testing"
            ],
            
            "finance": [
                "Financial Analysis", "Budgeting", "Forecasting", "Variance Analysis",
                "Profit & Loss", "Balance Sheet", "Cash Flow", "Audit",
                "Compliance", "Risk Management", "Investment Analysis",
                "Mergers & Acquisitions", "Due Diligence", "Financial Reporting"
            ],
            
            "healthcare": [
                "Patient Care", "Clinical Research", "Healthcare Management",
                "HIPAA Compliance", "Electronic Health Records", "Medical Terminology",
                "Patient Advocacy", "Treatment Planning", "Diagnosis", "Therapy"
            ],
            
            "education": [
                "Curriculum Development", "Instructional Design", "Student Assessment",
                "Classroom Management", "Lesson Planning", "Educational Technology",
                "Student Engagement", "Learning Outcomes", "Academic Advising"
            ],
            
            "hr": [
                "Talent Acquisition", "Recruiting", "Onboarding", "Employee Relations",
                "Performance Management", "Training & Development", "Compensation",
                "Benefits Administration", "HRIS", "Succession Planning"
            ]
        }
    
    def improve_cv(self, text: str, industry: str = "general") -> Dict:
        """
        Main method to improve CV text
        
        Args:
            text: The CV text to improve
            industry: Optional industry for keyword optimization
        """
        changes = []
        original = text
        
        # Step 1: Fix CV-specific grammar and typos
        text, grammar_changes = self._fix_cv_grammar(text)
        changes.extend(grammar_changes)
        
        # Step 2: Replace weak CV phrases
        text, phrase_changes = self._replace_cv_weak_phrases(text)
        changes.extend(phrase_changes)
        
        # Step 3: Add powerful action verbs to bullet points
        text, verb_changes = self._add_action_verbs_to_bullets(text)
        changes.extend(verb_changes)
        
        # Step 4: Identify duties that should be accomplishments
        text, accomplishment_notes = self._flag_duties_for_conversion(text)
        
        # Step 5: Format CV properly
        text = self._format_cv_text(text)
        
        # Step 6: Add industry keywords if specified
        if industry != "general":
            text, keyword_changes = self._add_industry_keywords(text, industry)
            changes.extend(keyword_changes)
        
        # Calculate CV metrics
        metrics = self._calculate_cv_metrics(original, text)
        
        # Generate CV-specific suggestions
        suggestions = self._generate_cv_suggestions(text, metrics)
        
        return {
            'original': original,
            'improved': text,
            'changes': changes,
            'metrics': metrics,
            'suggestions': suggestions,
            'accomplishment_notes': accomplishment_notes
        }
    
    def _fix_cv_grammar(self, text: str) -> Tuple[str, List[str]]:
        """
        Fix CV-specific grammar issues and typos
        """
        changes = []
        
        # Apply grammar fixes from dictionary
        for wrong, correct in self.cv_grammar_fixes.items():
            if isinstance(wrong, str) and wrong in text.lower():
                # Case-insensitive replacement
                pattern = r'\b' + re.escape(wrong) + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    # Preserve case of replacement
                    text = re.sub(pattern, correct, text, flags=re.IGNORECASE)
                    changes.append(f"Fixed: '{wrong}' → '{correct}'")
        
        # Fix tense for past jobs (simplified - looks for past date ranges)
        lines = text.split('\n')
        fixed_lines = []
        in_past_job = False
        
        for line in lines:
            # Check if this line contains a date range suggesting past job
            if re.search(r'20\d{2}\s*[-—]\s*20\d{2}', line) and not re.search(r'present|current|now', line.lower()):
                in_past_job = True
            elif re.search(r'20\d{2}\s*[-—]\s*(present|current|now)', line.lower()):
                in_past_job = False
            
            # If in past job and line is a bullet point, ensure past tense
            if in_past_job and line.strip().startswith(('•', '-', '*')):
                words = line.split()
                if len(words) > 1:
                    first_word = words[1].lower()
                    # Common present to past tense conversions
                    tense_map = {
                        'lead': 'led', 'manage': 'managed', 'create': 'created',
                        'develop': 'developed', 'implement': 'implemented',
                        'design': 'designed', 'build': 'built', 'coordinate': 'coordinated',
                        'organize': 'organized', 'oversee': 'oversaw', 'lead': 'led',
                        'run': 'ran', 'spearhead': 'spearheaded', 'pioneer': 'pioneered'
                    }
                    if first_word in tense_map:
                        words[1] = tense_map[first_word]
                        line = ' '.join(words)
                        changes.append(f"Tense: '{first_word}' → '{tense_map[first_word]}'")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines), changes
    
    def _replace_cv_weak_phrases(self, text: str) -> Tuple[str, List[str]]:
        """
        Replace weak CV phrases with powerful alternatives
        """
        changes = []
        
        for weak_phrase, alternatives in self.cv_weak_phrases.items():
            if weak_phrase in text.lower():
                # Choose appropriate alternative (first one for simplicity)
                alternative = alternatives[0]
                
                # Case-insensitive replacement
                pattern = r'\b' + re.escape(weak_phrase) + r'\b'
                text = re.sub(pattern, alternative, text, flags=re.IGNORECASE)
                changes.append(f"Improved: '{weak_phrase}' → '{alternative}'")
        
        return text, changes
    
    def _add_action_verbs_to_bullets(self, text: str) -> Tuple[str, List[str]]:
        """
        Add powerful action verbs to bullet points that start weakly
        """
        changes = []
        lines = text.split('\n')
        fixed_lines = []
        
        weak_starts = ['was', 'were', 'had', 'did', 'got', 'made', 'worked', 
                      'responsible', 'duties', 'tasked', 'helped', 'assisted']
        
        for line in lines:
            if line.strip().startswith(('•', '-', '*')):
                words = line.split()
                if len(words) > 1 and words[1].lower() in weak_starts:
                    # Replace with strong action verb
                    import random
                    all_verbs = []
                    for category in self.action_verbs.values():
                        all_verbs.extend(category)
                    
                    strong_verb = random.choice(all_verbs)
                    old_word = words[1]
                    words[1] = strong_verb
                    new_line = ' '.join(words)
                    fixed_lines.append(new_line)
                    changes.append(f"Action verb: '{old_word}' → '{strong_verb}'")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines), changes
    
    def _flag_duties_for_conversion(self, text: str) -> Tuple[str, List[str]]:
        """
        Identify duty-oriented phrases that should be accomplishments
        """
        notes = []
        
        duty_indicators = [
            'responsible for', 'duties included', 'tasked with',
            'job required', 'had to', 'needed to', 'worked on'
        ]
        
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if any(indicator in line.lower() for indicator in duty_indicators):
                notes.append(f"Line {i+1}: '{line[:50]}...' - Consider converting to accomplishment with results")
        
        return text, notes
    
    def _add_industry_keywords(self, text: str, industry: str) -> Tuple[str, List[str]]:
        """
        Add relevant industry keywords to skills section
        """
        changes = []
        
        if industry in self.industry_keywords:
            keywords = self.industry_keywords[industry]
            
            # Check if keywords are already present
            missing_keywords = []
            for keyword in keywords:
                if keyword.lower() not in text.lower():
                    missing_keywords.append(keyword)
            
            if missing_keywords and len(missing_keywords) > 0:
                # Add to skills section or create one
                if "skills" in text.lower() or "technologies" in text.lower():
                    # Add to existing skills section (simplified)
                    changes.append(f"Consider adding these industry keywords: {', '.join(missing_keywords[:5])}...")
                else:
                    # Create skills section
                    text += f"\n\n**Technical Skills:** {', '.join(missing_keywords[:8])}"
                    changes.append(f"Added skills section with industry keywords")
        
        return text, changes
    
    def _format_cv_text(self, text: str) -> str:
        """
        Apply CV-specific formatting
        """
        # Ensure consistent bullet points
        text = re.sub(r'^[-*]\s*', '• ', text, flags=re.MULTILINE)
        
        # Ensure each bullet ends with period
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip().startswith('•') and line.strip() and not line.strip().endswith('.'):
                line += '.'
            formatted_lines.append(line)
        
        text = '\n'.join(formatted_lines)
        
        # Fix spacing
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Max two newlines
        
        return text
    
    def _calculate_cv_metrics(self, original: str, improved: str) -> Dict:
        """
        Calculate CV improvement metrics
        """
        original_lines = original.split('\n')
        improved_lines = improved.split('\n')
        
        # Count bullet points
        original_bullets = sum(1 for line in original_lines if line.strip().startswith(('•', '-', '*')))
        improved_bullets = sum(1 for line in improved_lines if line.strip().startswith('•'))
        
        # Count action verbs used
        action_verb_count = 0
        all_verbs = []
        for category in self.action_verbs.values():
            all_verbs.extend([v.lower() for v in category])
        
        for verb in all_verbs:
            if verb in improved.lower():
                action_verb_count += 1
        
        # Count weak phrases remaining
        weak_phrases_remaining = 0
        for weak_phrase in self.cv_weak_phrases.keys():
            if weak_phrase in improved.lower():
                weak_phrases_remaining += 1
        
        # Count quantifiable achievements (with numbers)
        quantifiable_count = len(re.findall(r'\d+%|\$\d+|\d+\s+(people|employees|customers|clients|users|years|months)', improved.lower()))
        
        return {
            'bullet_points': improved_bullets,
            'action_verbs_used': action_verb_count,
            'weak_phrases_remaining': weak_phrases_remaining,
            'quantifiable_achievements': quantifiable_count,
            'improvements_made': improved_bullets - original_bullets
        }
    
    def _generate_cv_suggestions(self, text: str, metrics: Dict) -> List[str]:
        """
        Generate practical CV improvement suggestions
        """
        suggestions = []
        
        # Bullet point suggestions
        if metrics['bullet_points'] < 5:
            suggestions.append("📝 Add more bullet points under each role (aim for 4-6 per position)")
        elif metrics['bullet_points'] > 10:
            suggestions.append("📝 Consider trimming to 5-7 strongest bullet points per role")
        
        # Action verb suggestions
        if metrics['action_verbs_used'] < 5:
            suggestions.append("⚡ Start bullet points with powerful action verbs (led, created, improved, etc.)")
        
        # Quantifiable achievement suggestions
        if metrics['quantifiable_achievements'] < 2:
            suggestions.append("📊 Add numbers to your achievements (%, $, time saved, people managed)")
        
        # Weak phrase suggestions
        if metrics['weak_phrases_remaining'] > 0:
            suggestions.append("🔧 Replace remaining weak phrases with stronger alternatives")
        
        # Length suggestions
        if len(text) < 300:
            suggestions.append("📄 CV seems brief - consider adding more detail about your achievements")
        elif len(text) > 2000:
            suggestions.append("📄 CV is quite long - aim for 1-2 pages maximum")
        
        # Common CV mistakes
        if 'references available' in text.lower():
            suggestions.append("✅ Remove 'references available upon request' - it's assumed")
        
        if 'objective' in text.lower():
            suggestions.append("🎯 Consider replacing 'Objective' with 'Professional Summary' or 'Profile'")
        
        if 'hobbies' in text.lower() or 'interests' in text.lower():
            suggestions.append("🎨 Only include hobbies if they're relevant to the job or show valuable skills")
        
        # Check for email
        if not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text):
            suggestions.append("📧 Ensure your email is included and clearly visible")
        
        # Check for phone
        if not re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text):
            suggestions.append("📱 Include a professional voicemail-enabled phone number")
        
        # Check for LinkedIn
        if 'linkedin' not in text.lower():
            suggestions.append("🔗 Add your LinkedIn profile URL (make sure it's updated)")
        
        # Actionable improvement suggestions
        suggestions.append("💪 Turn duties into achievements: 'Responsible for X' → 'Achieved Y by doing X'")
        suggestions.append("🎯 Tailor your CV to each job by matching keywords from the job description")
        suggestions.append("📏 Keep formatting clean and consistent - no tables or columns for ATS")
        
        return suggestions


# Convenience function for easy use
def improve_cv_text(text: str, industry: str = "general") -> Dict:
    """
    Quickly improve CV text
    
    Args:
        text: The CV text to improve
        industry: Optional industry for keyword optimization
    """
    improver = CVImprover()
    return improver.improve_cv(text, industry)




class ProfessionalEmailImprover(AcademicToneImprover):
    """
    Specialized Email text improver
    Fixes common email mistakes that cost professional opportunities
    """
    
    def __init__(self):
        super().__init__()
        self.email_openings = self._load_email_openings()
        self.email_closings = self._load_email_closings()
        self.weak_email_phrases = self._load_weak_email_phrases()
        self.email_subjects = self._load_email_subjects()
        self.email_grammar_fixes = self._load_email_grammar_fixes()
        self.professional_tone_guides = self._load_professional_tone_guides()
        self.email_purposes = self._load_email_purposes()
        
    def _load_email_openings(self) -> Dict[str, List[str]]:
        """
        Professional email opening lines for different contexts
        """
        return {
            "formal": [
                "Dear [Name],",
                "Dear Mr./Ms. [Last Name],",
                "To Whom It May Concern,",
                "Dear Hiring Manager,",
                "Dear Recruiting Team,",
                "Dear Search Committee,",
                "Dear Sir or Madam,"
            ],
            
            "semi_formal": [
                "Hello [Name],",
                "Hi [Name],",
                "Good morning [Name],",
                "Good afternoon [Name],",
                "I hope this email finds you well,",
                "I hope you're having a productive week,",
                "I hope your week is going well,"
            ],
            
            "follow_up": [
                "Following up on our conversation,",
                "Per our discussion,",
                "As promised, here is",
                "As we discussed,",
                "Further to our conversation,",
                "In reference to our meeting,",
                "Following up on my previous email,",
                "I'm circling back on"
            ],
            
            "introduction": [
                "My name is [Name] and I'm reaching out because",
                "I'm writing to introduce myself as",
                "Allow me to introduce myself. I'm",
                "I came across your profile and",
                "I was referred to you by",
                "We haven't met, but I'm"
            ],
            
            "grateful": [
                "Thank you for your prompt response,",
                "I appreciate your quick reply,",
                "Thank you for getting back to me,",
                "I'm grateful for your time,",
                "Thank you for the opportunity to",
                "I appreciate you taking the time to"
            ],
            
            "apologetic": [
                "I apologize for the delay in responding,",
                "Please accept my apologies for the late reply,",
                "I'm sorry for the delayed response,",
                "My sincerest apologies for",
                "I apologize for any inconvenience caused,",
                "Please forgive the delay in"
            ]
        }
    
    def _load_email_closings(self) -> Dict[str, List[str]]:
        """
        Professional email closing lines
        """
        return {
            "formal": [
                "Sincerely,",
                "Yours sincerely,",
                "Yours faithfully,",
                "Respectfully,",
                "With gratitude,",
                "Respectfully yours,"
            ],
            
            "semi_formal": [
                "Best regards,",
                "Kind regards,",
                "Warm regards,",
                "Regards,",
                "With appreciation,",
                "Thank you for your consideration,"
            ],
            
            "friendly": [
                "Best,",
                "Cheers,",
                "Thanks,",
                "Talk soon,",
                "Looking forward to hearing from you,",
                "Have a great day,"
            ],
            
            "action_oriented": [
                "I look forward to your response,",
                "Looking forward to discussing this further,",
                "Eager to hear your thoughts,",
                "Hoping to connect soon,",
                "Awaiting your feedback,",
                "Let me know your thoughts,"
            ],
            
            "grateful": [
                "Thank you for your time,",
                "Thanks again for your help,",
                "Appreciate your assistance,",
                "Grateful for your support,",
                "Many thanks for your consideration,"
            ]
        }
    
    def _load_email_subjects(self) -> Dict[str, List[str]]:
        """
        Professional email subject lines
        """
        return {
            "job_application": [
                "Application for [Position] - [Your Name]",
                "Job Application: [Position] - [Your Name]",
                "Interest in [Position] Role",
                "Candidate for [Position] Position",
                "Application: [Position] Opportunity",
                "Seeking [Position] Role - [Your Name]"
            ],
            
            "follow_up": [
                "Following Up on [Topic]",
                "Checking In Regarding [Topic]",
                "Following Up: [Original Subject]",
                "Circling Back on [Topic]",
                "Follow-up on Our Conversation",
                "Checking In: [Topic]"
            ],
            
            "meeting": [
                "Meeting Request: [Topic/Purpose]",
                "Scheduling a Meeting to Discuss [Topic]",
                "Availability for Meeting Re: [Topic]",
                "Request to Schedule a Call",
                "Proposed Meeting Time for [Topic]",
                "Let's Connect Regarding [Topic]"
            ],
            
            "introduction": [
                "Introduction: [Your Name] - [Context]",
                "Connecting Regarding [Topic]",
                "Reaching Out About [Topic]",
                "Introduction from [Referral Name]",
                "Getting on Your Radar: [Topic]"
            ],
            
            "follow_up": [
                "Checking In on [Topic]",
                "Following Up: [Original Subject]",
                "Just Circling Back on This",
                "Bumping This to Your Inbox",
                "Following Up on My Previous Email"
            ],
            
            "thank_you": [
                "Thank You for [Specific Reason]",
                "Appreciation for [Topic]",
                "Grateful for Your Time",
                "Thanks for the Conversation",
                "Thank You: [Topic]"
            ],
            
            "proposal": [
                "Proposal: [Project/Initiative Name]",
                "Recommendation Regarding [Topic]",
                "Suggestion for [Topic]",
                "Ideas for [Project]",
                "Potential Opportunity: [Topic]"
            ],
            
            "urgent": [
                "URGENT: [Time-Sensitive Topic]",
                "Time-Sensitive: [Topic]",
                "Action Required: [Topic]",
                "Important: [Topic]",
                "Attention Needed: [Topic]"
            ]
        }
    
    def _load_weak_email_phrases(self) -> Dict[str, List[str]]:
        """
        Weak email phrases and their professional alternatives
        """
        return {
            # Weak openings
            "just wanted to": [
                "I am writing to",
                "I'm reaching out to",
                "This email serves to",
                "I would like to"
            ],
            "just checking in": [
                "Following up on",
                "Checking in regarding",
                "Circling back on",
                "Reaching out about"
            ],
            "sorry to bother you": [
                "I appreciate your time regarding",
                "Thank you for your attention to",
                "I realize you're busy, but",
                "When you have a moment,"
            ],
            "not sure if you saw": [
                "I wanted to ensure you received",
                "Following up on my previous email about",
                "Bringing this back to your attention",
                "I wanted to reiterate"
            ],
            
            # Weak requests
            "can you": [
                "Would you be able to",
                "Could you please",
                "I would appreciate it if you could",
                "When convenient, could you"
            ],
            "i need you to": [
                "Could you please",
                "Would you mind",
                "I would be grateful if you could",
                "If possible, could you"
            ],
            "i want": [
                "I would like",
                "I am hoping to",
                "My preference would be",
                "I am interested in"
            ],
            
            # Weak apologies
            "sorry i'm late": [
                "My apologies for the delay",
                "Please accept my apologies for the delayed response",
                "I apologize for not responding sooner",
                "Forgive the delayed reply"
            ],
            "my bad": [
                "My apologies",
                "I apologize for the oversight",
                "Please accept my apologies",
                "I take responsibility for"
            ],
            "sorry for the confusion": [
                "I apologize for any confusion",
                "Let me clarify",
                "To clarify,",
                "I hope this clears up any misunderstanding"
            ],
            
            # Weak confirmations
            "got your email": [
                "Thank you for your email",
                "I received your message",
                "Thanks for reaching out",
                "I appreciate your correspondence"
            ],
            "sounds good": [
                "That works well",
                "That sounds agreeable",
                "I'm amenable to that",
                "That would be acceptable"
            ],
            "no problem": [
                "You're welcome",
                "Happy to help",
                "My pleasure",
                "Glad I could assist"
            ],
            
            # Weak closings
            "that's all": [
                "That covers everything for now",
                "Those are the key points",
                "I believe I've covered everything",
                "To summarize"
            ],
            "let me know": [
                "I look forward to your response",
                "Please let me know your thoughts",
                "I await your feedback",
                "Your input would be appreciated"
            ],
            "talk soon": [
                "Looking forward to connecting",
                "I anticipate our conversation",
                "Eager to discuss further",
                "Until we speak again"
            ],
            
            # Weak thank yous
            "thx": [
                "Thank you",
                "Thanks so much",
                "I appreciate it",
                "Many thanks"
            ],
            "thanks in advance": [
                "Thank you for your assistance",
                "I appreciate your help with this",
                "Grateful for your support",
                "Thank you for considering"
            ],
            
            # Weak explanations
            "just so you know": [
                "For your information",
                "I wanted to make you aware",
                "Please note that",
                "For your reference"
            ],
            "the thing is": [
                "The situation is",
                "The challenge is",
                "The issue is",
                "The circumstance is"
            ],
            "basically": [
                "In essence",
                "Essentially",
                "To summarize",
                "The fundamental point is"
            ],
            
            # Weak agreements
            "i guess": [
                "I believe",
                "It seems that",
                "My understanding is",
                "I would assume"
            ],
            "sort of": [
                "In some ways",
                "To an extent",
                "Partially",
                "Somewhat"
            ],
            "kind of": [
                "Somewhat",
                "Rather",
                "Moderately",
                "To some degree"
            ],
            
            # Weak promises
            "i'll try": [
                "I will make every effort to",
                "I will do my best to",
                "I aim to",
                "I will endeavor to"
            ],
            "i'll get back to you": [
                "I will respond by [date]",
                "I will follow up by",
                "You can expect my response by",
                "I will revert by"
            ],
            
            # Weak enthusiasm
            "cool": [
                "Excellent",
                "Wonderful",
                "That's great to hear",
                "Delighted to hear that"
            ],
            "awesome": [
                "That's excellent news",
                "Wonderful to hear",
                "I'm pleased to hear that",
                "That's fantastic"
            ],
            "great": [
                "Excellent",
                "Wonderful",
                "Delighted",
                "Pleased"
            ],
            
            # Weak hedging
            "maybe": [
                "Perhaps",
                "Possibly",
                "It may be that",
                "One option could be"
            ],
            "i think": [
                "I believe",
                "It seems to me",
                "My understanding is",
                "In my assessment"
            ],
            
            # Weak urgency
            "asap": [
                "At your earliest convenience",
                "As soon as possible",
                "Promptly",
                "By [specific date]"
            ],
            "urgent": [
                "Time-sensitive",
                "Requires attention by",
                "Please prioritize",
                "Needs immediate attention"
            ]
        }
    
    def _load_email_grammar_fixes(self) -> Dict[str, str]:
        """
        Email-specific grammar and formatting fixes
        """
        return {
            # Common email typos
            "recieved": "received",
            "seperate": "separate",
            "definately": "definitely",
            "tommorow": "tomorrow",
            "tommorrow": "tomorrow",
            "untill": "until",
            "begining": "beginning",
            "ocurred": "occurred",
            "alot": "a lot",
            "thier": "their",
            "wierd": "weird",
            "acheive": "achieve",
            "acheived": "achieved",
            "succesful": "successful",
            "succesfully": "successfully",
            "accomodate": "accommodate",
            "accomodated": "accommodated",
            "accomodation": "accommodation",
            "embarass": "embarrass",
            "embarassed": "embarrassed",
            "occassion": "occasion",
            "occasional": "occasional",
            "occasionally": "occasionally",
            "prefered": "preferred",
            "refered": "referred",
            "refering": "referring",
            "transfered": "transferred",
            "transfering": "transferring",
            
            # Email formatting
            r'^([a-z])': lambda m: m.group(1).upper(),  # Capitalize first letter
            r'\.([A-Z])': r'. \1',  # Space after periods
            r'\s+\.': '.',  # Remove space before period
            r'\s+,': ',',  # Remove space before comma
            
            # Common email mistakes
            "pls": "please",
            "plz": "please",
            "thx": "thanks",
            "u": "you",
            "ur": "your",
            "btw": "by the way",
            "fyi": "for your information",
            "asap": "as soon as possible",
            "lmk": "let me know",
            "ttyl": "talk to you later",
            "brb": "be right back",
            "omg": "oh my goodness",
            "lol": "ha",
            "smh": "shaking my head",
            
            # Redundancies
            "advance planning": "planning",
            "advance warning": "warning",
            "added bonus": "bonus",
            "end result": "result",
            "final outcome": "outcome",
            "past history": "history",
            "past experience": "experience",
            "future plans": "plans",
            "each and every": "each",
            "first and foremost": "first",
            "one and the same": "the same",
            
            # Email-specific
            "attached please find": "I've attached",
            "please find attached": "I've attached",
            "enclosed please find": "I've enclosed",
            "please see attached": "I've attached",
            "as per": "according to",
            "due to the fact that": "because",
            "in spite of the fact that": "although",
            "in the event that": "if",
            "with regard to": "regarding",
            "with respect to": "regarding",
            "in order to": "to"
        }
    
    def _load_professional_tone_guides(self) -> Dict[str, Dict]:
        """
        Guidelines for different professional tones
        """
        return {
            "formal": {
                "do": [
                    "Use complete sentences",
                    "Avoid contractions (don't → do not)",
                    "Use formal salutations (Dear Mr./Ms.)",
                    "Be concise but thorough",
                    "Use professional vocabulary"
                ],
                "avoid": [
                    "Slang or casual language",
                    "Emojis or emoticons",
                    "Exclamation marks",
                    "Informal abbreviations",
                    "Humor or jokes"
                ]
            },
            
            "semi_formal": {
                "do": [
                    "Be professional but approachable",
                    "Use some contractions",
                    "Show personality within bounds",
                    "Be clear and direct"
                ],
                "avoid": [
                    "Overly casual language",
                    "Slang or text speak",
                    "Unprofessional jokes",
                    "Excessive exclamation"
                ]
            },
            
            "friendly": {
                "do": [
                    "Build rapport",
                    "Show warmth and approachability",
                    "Use positive language",
                    "Acknowledge relationship"
                ],
                "avoid": [
                    "Being overly familiar",
                    "Assuming intimacy",
                    "Unprofessional topics",
                    "Over-sharing"
                ]
            },
            
            "persuasive": {
                "do": [
                    "Lead with value proposition",
                    "Use confident language",
                    "Include clear call to action",
                    "Highlight benefits",
                    "Provide social proof"
                ],
                "avoid": [
                    "Being pushy or aggressive",
                    "Making false promises",
                    "Vague or ambiguous language",
                    "Ignoring potential objections"
                ]
            },
            
            "apologetic": {
                "do": [
                    "Take responsibility",
                    "Be sincere and genuine",
                    "Offer solution if applicable",
                    "Thank them for patience"
                ],
                "avoid": [
                    "Making excuses",
                    "Blaming others",
                    "Being overly dramatic",
                    "Promising what you can't deliver"
                ]
            }
        }
    
    def _load_email_purposes(self) -> Dict[str, Dict]:
        """
        Templates for different email purposes
        """
        return {
            "job_application": {
                "subject": "Application for [Position] - [Your Name]",
                "body": """
Dear [Hiring Manager Name],

I am writing to express my strong interest in the [Position] role at [Company Name]. With my background in [relevant experience] and passion for [industry/field], I am confident I would be a valuable addition to your team.

[Paragraph 2: Highlight 2-3 key achievements or qualifications relevant to the role]

[Paragraph 3: Explain why you're interested in this specific company/role]

Thank you for considering my application. I have attached my resume and would welcome the opportunity to discuss how my skills align with [Company Name]'s needs.

Best regards,
[Your Name]
[Your Phone Number]
[Your LinkedIn Profile]
"""
            },
            
            "follow_up": {
                "subject": "Following Up: [Original Subject]",
                "body": """
Hi [Name],

I hope this email finds you well. I'm writing to follow up on my previous message regarding [topic] sent on [date].

[Brief reminder of what you're following up about]

Would you be available for a brief call this week to discuss further? Let me know what works best for your schedule.

Best regards,
[Your Name]
"""
            },
            
            "meeting_request": {
                "subject": "Meeting Request: [Topic]",
                "body": """
Hi [Name],

I hope you're having a good week. I'd like to schedule a [30-minute] meeting to discuss [purpose of meeting].

I'm available at the following times:
- [Date] at [Time]
- [Date] at [Time]
- [Date] at [Time]

Please let me know if any of these work for you, or suggest an alternative that fits your schedule.

Looking forward to connecting,

[Your Name]
"""
            },
            
            "thank_you": {
                "subject": "Thank You for [Specific Reason]",
                "body": """
Dear [Name],

I wanted to take a moment to express my sincere gratitude for [specific thing you're thanking them for - their time, the interview, their help, etc.].

[Specific detail about what you appreciated or how it helped you]

Thank you again for your [kindness/time/support/consideration]. I truly appreciate it.

Warm regards,
[Your Name]
"""
            },
            
            "introduction": {
                "subject": "Introduction: [Your Name] - [Context/Reasons for Reaching Out]",
                "body": """
Hi [Name],

My name is [Your Name] and I'm [your role/context for reaching out]. I came across your profile/work through [how you found them] and was impressed by [specific detail].

I'm reaching out because [reason for connecting - collaboration, advice, opportunity, etc.].

Would you be open to a brief [call/chat] next week? I'd love to learn more about your work in [their area of expertise].

Best regards,
[Your Name]
"""
            },
            
            "problem_resolution": {
                "subject": "Regarding: [Issue/Topic]",
                "body": """
Hi [Name],

Thank you for bringing [issue] to my attention. I apologize for any inconvenience this may have caused.

I've looked into the matter and [explain what you found/what you're doing to resolve it].

[If resolved: The issue has been resolved and [explain resolution]]
[If still working on it: I'm actively working on this and expect to have it resolved by [date]]

Please let me know if you have any questions in the meantime.

Best regards,
[Your Name]
"""
            },
            
            "networking": {
                "subject": "Connecting Regarding [Shared Interest/Industry]",
                "body": """
Hi [Name],

I hope this message finds you well. My name is [Your Name] and I'm a [your role/background] with a strong interest in [shared interest/industry].

I've been following your work on [specific project/achievement] and was particularly impressed by [specific detail].

I'm reaching out to [request - ask for advice, learn about their career path, explore potential collaboration]. Would you be open to a brief [15-minute] call in the coming weeks?

Thank you for your consideration.

Best regards,
[Your Name]
[Your LinkedIn Profile]
"""
            },
            
            "proposal": {
                "subject": "Proposal: [Project/Idea Name]",
                "body": """
Hi [Name],

I hope you're doing well. I've been thinking about [problem/opportunity] and wanted to share an idea I believe could benefit [company/department/project].

The concept is [brief explanation of proposal]. I believe this could [benefit - save time, increase revenue, improve efficiency, etc.] because [brief reasoning].

Would you be open to discussing this further? I've outlined some initial thoughts below:

[Bullet points or brief outline of proposal]

I'd love to get your feedback and hear your thoughts on whether this aligns with current priorities.

Looking forward to your perspective,

[Your Name]
"""
            }
        }
    
    def improve_email(self, text: str, email_type: str = "general", tone: str = "semi_formal") -> Dict:
        """
        Main method to improve email text
        
        Args:
            text: The email text to improve
            email_type: Type of email (job_application, follow_up, meeting_request, etc.)
            tone: Desired tone (formal, semi_formal, friendly, persuasive, apologetic)
        """
        changes = []
        original = text
        
        # Step 1: Fix email-specific grammar and typos
        text, grammar_changes = self._fix_email_grammar(text)
        changes.extend(grammar_changes)
        
        # Step 2: Replace weak email phrases
        text, phrase_changes = self._replace_weak_email_phrases(text)
        changes.extend(phrase_changes)
        
        # Step 3: Improve subject line if present
        text, subject_changes = self._improve_subject_line(text, email_type)
        changes.extend(subject_changes)
        
        # Step 4: Improve opening line
        text, opening_changes = self._improve_opening(text, tone)
        changes.extend(opening_changes)
        
        # Step 5: Improve closing line
        text, closing_changes = self._improve_closing(text, tone)
        changes.extend(closing_changes)
        
        # Step 6: Apply tone guidelines
        text, tone_changes = self._apply_tone_guidelines(text, tone)
        changes.extend(tone_changes)
        
        # Step 7: Format email properly
        text = self._format_email(text)
        
        # Calculate email metrics
        metrics = self._calculate_email_metrics(original, text)
        
        # Generate email-specific suggestions
        suggestions = self._generate_email_suggestions(text, metrics, tone)
        
        # Check for missing elements
        missing_elements = self._check_missing_elements(text)
        
        return {
            'original': original,
            'improved': text,
            'changes': changes,
            'metrics': metrics,
            'suggestions': suggestions,
            'missing_elements': missing_elements
        }
    
    def _fix_email_grammar(self, text: str) -> Tuple[str, List[str]]:
        """
        Fix email-specific grammar issues and typos
        """
        changes = []
        
        # Apply grammar fixes from dictionary
        for wrong, correct in self.email_grammar_fixes.items():
            if isinstance(wrong, str) and wrong in text.lower():
                # Case-insensitive replacement for words, not patterns
                if ' ' not in wrong and '(' not in wrong:
                    pattern = r'\b' + re.escape(wrong) + r'\b'
                    if re.search(pattern, text, re.IGNORECASE):
                        # Preserve case of replacement
                        text = re.sub(pattern, correct, text, flags=re.IGNORECASE)
                        changes.append(f"Fixed: '{wrong}' → '{correct}'")
                elif isinstance(wrong, str):
                    # Handle patterns
                    try:
                        text = re.sub(wrong, correct, text)
                        changes.append(f"Fixed formatting issue")
                    except:
                        pass
        
        return text, changes
    
    def _replace_weak_email_phrases(self, text: str) -> Tuple[str, List[str]]:
        """
        Replace weak email phrases with professional alternatives
        """
        changes = []
        
        for weak_phrase, alternatives in self.weak_email_phrases.items():
            if weak_phrase in text.lower():
                # Choose appropriate alternative (first one for simplicity)
                alternative = alternatives[0]
                
                # Case-insensitive replacement
                pattern = r'\b' + re.escape(weak_phrase) + r'\b'
                text = re.sub(pattern, alternative, text, flags=re.IGNORECASE)
                changes.append(f"Improved: '{weak_phrase}' → '{alternative}'")
        
        return text, changes
    
    def _improve_subject_line(self, text: str, email_type: str) -> Tuple[str, List[str]]:
        """
        Improve or suggest email subject line
        """
        changes = []
        
        # Check if there's a subject line (looking for common patterns)
        lines = text.split('\n')
        first_line = lines[0] if lines else ""
        
        # If first line looks like a subject (no greeting), treat it as subject
        if first_line and not any(greeting in first_line.lower() for greeting in ['dear', 'hi', 'hello', 'hey', 'good morning', 'good afternoon']):
            # This might be a subject line - check if it's weak
            weak_subjects = ['question', 'help', 'info', 'quick question', 'checking in']
            
            subject_lower = first_line.lower()
            for weak in weak_subjects:
                if weak in subject_lower:
                    if email_type in self.email_subjects:
                        suggestion = self.email_subjects[email_type][0].replace('[Topic]', 'Your Topic').replace('[Position]', 'Position').replace('[Your Name]', 'Your Name')
                        changes.append(f"Consider better subject: '{first_line[:50]}' → '{suggestion}'")
                    break
        
        return text, changes
    
    def _improve_opening(self, text: str, tone: str) -> Tuple[str, List[str]]:
        """
        Improve email opening line
        """
        changes = []
        lines = text.split('\n')
        
        # Find the greeting line
        greeting_line_index = -1
        for i, line in enumerate(lines):
            if any(greeting in line.lower() for greeting in ['dear', 'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'to whom']):
                greeting_line_index = i
                break
        
        if greeting_line_index >= 0:
            greeting = lines[greeting_line_index]
            
            # Check if it's a weak opening (just the greeting with no follow-up)
            if len(greeting.split()) <= 3 and greeting_line_index + 1 < len(lines):
                next_line = lines[greeting_line_index + 1]
                
                # Check if next line starts with weak phrase
                weak_openings = ['just wanted to', 'just checking', 'sorry to', 'i think', 'i was wondering']
                
                for weak in weak_openings:
                    if next_line.lower().startswith(weak):
                        # Suggest improvement based on tone
                        if tone == 'formal':
                            improved_opening = "I am writing to"
                        elif tone == 'semi_formal':
                            improved_opening = "I'm reaching out to"
                        else:
                            improved_opening = "I wanted to"
                        
                        lines[greeting_line_index + 1] = next_line.replace(weak, improved_opening, 1)
                        changes.append(f"Opening: '{weak}' → '{improved_opening}'")
                        break
        
        return '\n'.join(lines), changes
    
    def _improve_closing(self, text: str, tone: str) -> Tuple[str, List[str]]:
        """
        Improve email closing line
        """
        changes = []
        lines = text.split('\n')
        
        # Find closing line (looking for sign-offs)
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            
            # Check if line is a closing
            if line and not line.endswith(('.', '?', '!')) and len(line.split()) <= 3:
                # Potential closing line
                weak_closings = ['thanks', 'thx', 'cheers', 'talk soon', 'let me know']
                
                for weak in weak_closings:
                    if weak in line.lower():
                        # Suggest better closing based on tone
                        if tone == 'formal':
                            improved_closing = "Sincerely,"
                        elif tone == 'semi_formal':
                            improved_closing = "Best regards,"
                        else:
                            improved_closing = "Thanks,"
                        
                        if improved_closing != line:
                            lines[i] = improved_closing
                            changes.append(f"Closing: '{line}' → '{improved_closing}'")
                        break
                break
        
        return '\n'.join(lines), changes
    
    def _apply_tone_guidelines(self, text: str, tone: str) -> Tuple[str, List[str]]:
        """
        Apply tone-specific improvements
        """
        changes = []
        
        if tone == "formal":
            # Remove contractions
            contractions = {
                "don't": "do not",
                "won't": "will not",
                "can't": "cannot",
                "couldn't": "could not",
                "wouldn't": "would not",
                "shouldn't": "should not",
                "isn't": "is not",
                "aren't": "are not",
                "wasn't": "was not",
                "weren't": "were not",
                "haven't": "have not",
                "hasn't": "has not",
                "hadn't": "had not",
                "i'm": "I am",
                "you're": "you are",
                "he's": "he is",
                "she's": "she is",
                "it's": "it is",
                "we're": "we are",
                "they're": "they are",
                "i've": "I have",
                "you've": "you have",
                "we've": "we have",
                "they've": "they have",
                "i'll": "I will",
                "you'll": "you will",
                "he'll": "he will",
                "she'll": "she will",
                "we'll": "we will",
                "they'll": "they will"
            }
            
            for contraction, full in contractions.items():
                if contraction in text.lower():
                    # Preserve case for I'm -> I am
                    if contraction == "i'm":
                        text = re.sub(r'\b' + re.escape(contraction) + r'\b', full, text, flags=re.IGNORECASE)
                    else:
                        text = re.sub(r'\b' + re.escape(contraction) + r'\b', full, text, flags=re.IGNORECASE)
                    changes.append(f"Formal tone: '{contraction}' → '{full}'")
            
            # Remove exclamation marks
            if '!' in text:
                text = text.replace('!', '.')
                changes.append("Formal tone: Replaced '!' with '.'")
        
        elif tone == "persuasive":
            # Add confident language
            confident_phrases = [
                (r'\bI think\b', 'I am confident'),
                (r'\bmaybe\b', 'certainly'),
                (r'\bpossibly\b', 'undoubtedly'),
                (r'\bI hope\b', 'I am confident'),
                (r'\bI believe\b', 'I am certain')
            ]
            
            for weak, strong in confident_phrases:
                if re.search(weak, text, re.IGNORECASE):
                    text = re.sub(weak, strong, text, flags=re.IGNORECASE)
                    changes.append(f"Persuasive tone: '{weak}' → '{strong}'")
        
        elif tone == "apologetic":
            # Add sincere apology language
            if 'sorry' not in text.lower() and 'apologize' not in text.lower():
                # Check if email needs apology (based on context)
                if 'delay' in text.lower() or 'late' in text.lower() or 'mistake' in text.lower():
                    # Add apology at beginning
                    lines = text.split('\n')
                    if len(lines) > 1:
                        lines.insert(1, "\nI sincerely apologize for the delay.")
                        text = '\n'.join(lines)
                        changes.append("Apologetic tone: Added sincere apology")
        
        return text, changes
    
    def _format_email(self, text: str) -> str:
        """
        Apply email-specific formatting
        """
        # Ensure proper spacing after salutation
        lines = text.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            if any(greeting in line.lower() for greeting in ['dear', 'hi', 'hello', 'hey', 'good morning', 'good afternoon']):
                formatted_lines.append(line)
                # Add blank line after greeting if not present
                if i + 1 < len(lines) and lines[i + 1].strip():
                    formatted_lines.append('')
            else:
                formatted_lines.append(line)
        
        text = '\n'.join(formatted_lines)
        
        # Fix spacing
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Max two newlines
        
        # Ensure proper capitalization
        sentences = re.split(r'([.!?]\s+)', text)
        for i in range(0, len(sentences), 2):
            if sentences[i] and sentences[i][0].islower() and len(sentences[i]) > 1:
                sentences[i] = sentences[i][0].upper() + sentences[i][1:]
        
        return ''.join(sentences)
    
    def _calculate_email_metrics(self, original: str, improved: str) -> Dict:
        """
        Calculate email improvement metrics
        """
        original_words = len(original.split())
        improved_words = len(improved.split())
        
        # Count weak phrases
        weak_phrases_original = 0
        weak_phrases_improved = 0
        
        for weak_phrase in self.weak_email_phrases.keys():
            if weak_phrase in original.lower():
                weak_phrases_original += 1
            if weak_phrase in improved.lower():
                weak_phrases_improved += 1
        
        # Count informal language
        informal_terms = ['pls', 'thx', 'u', 'ur', 'btw', 'fyi', 'lmk', 'ttyl', 'lol', 'omg']
        informal_count = sum(1 for term in informal_terms if term in improved.lower())
        
        # Check for key email elements
        has_greeting = any(greeting in improved.lower() for greeting in ['dear', 'hi', 'hello', 'hey'])
        has_closing = any(closing in improved.lower() for closing in ['regards', 'sincerely', 'thanks', 'best', 'cheers'])
        has_signature = '@' in improved or 'phone' in improved.lower() or 'linkedin' in improved.lower()
        
        return {
            'word_count': improved_words,
            'weak_phrases_removed': weak_phrases_original - weak_phrases_improved,
            'informal_terms_remaining': informal_count,
            'has_greeting': has_greeting,
            'has_closing': has_closing,
            'has_signature': has_signature,
            'improvement_score': round(((weak_phrases_original - weak_phrases_improved) / max(weak_phrases_original, 1)) * 100)
        }
    
    def _generate_email_suggestions(self, text: str, metrics: Dict, tone: str) -> List[str]:
        """
        Generate email-specific improvement suggestions
        """
        suggestions = []
        
        # Greeting suggestions
        if not metrics['has_greeting']:
            suggestions.append("👋 Add a professional greeting (Dear, Hi, Hello, etc.)")
        
        # Closing suggestions
        if not metrics['has_closing']:
            suggestions.append("📝 Add a professional closing (Best regards, Sincerely, etc.)")
        
        # Signature suggestions
        if not metrics['has_signature']:
            suggestions.append("📇 Include a signature with your name, title, and contact information")
        
        # Tone-specific suggestions
        if tone == 'formal':
            suggestions.append("🎩 Maintain formal tone - avoid contractions and casual language")
        elif tone == 'persuasive':
            suggestions.append("💪 Use confident, action-oriented language to drive response")
        elif tone == 'apologetic':
            suggestions.append("🙏 Be sincere and specific in your apology, then offer solution")
        
        # Content suggestions
        if len(text.split()) < 30:
            suggestions.append("📄 Email seems brief - ensure you've included all necessary information")
        elif len(text.split()) > 300:
            suggestions.append("📄 Email is quite long - consider breaking into shorter paragraphs")
        
        if metrics['informal_terms_remaining'] > 0:
            suggestions.append("🔤 Replace remaining informal terms with professional language")
        
        # Check for missing elements
        if '@' not in text and 'email' in text.lower():
            suggestions.append("📧 Make sure your email address is clearly visible in signature")
        
        if 'call' in text.lower() and 'phone' not in text.lower():
            suggestions.append("📱 If suggesting a call, include your phone number")
        
        if 'attach' in text.lower() and 'attach' not in text:
            suggestions.append("📎 You mentioned an attachment - make sure it's actually attached")
        
        # Call to action
        if '?' not in text and not any(phrase in text.lower() for phrase in ['let me know', 'looking forward', 'hope to hear']):
            suggestions.append("🎯 Add a clear call to action - what do you want the recipient to do?")
        
        # Tone check
        if '!' in text:
            suggestions.append("⚠️ Limit exclamation marks in professional emails")
        
        if any(word in text.lower() for word in ['literally', 'honestly', 'actually', 'basically']):
            suggestions.append("🔍 Remove filler words that weaken your message")
        
        if any(word in text.lower() for word in ['urgent', 'asap', 'immediately']):
            suggestions.append("⏰ Be careful with urgency language - use only when truly necessary")
        
        # Subject line suggestion
        first_line = text.split('\n')[0] if text.split('\n') else ''
        if len(first_line) < 5 or 'subject' not in first_line.lower():
            suggestions.append("📌 Ensure your subject line is clear and specific")
        
        return suggestions
    
    def _check_missing_elements(self, text: str) -> List[str]:
        """
        Check for missing professional email elements
        """
        missing = []
        
        # Check for name
        lines = text.split('\n')
        last_few_lines = lines[-3:] if len(lines) > 3 else lines
        
        has_name = False
        for line in last_few_lines:
            if len(line.split()) <= 3 and line.strip() and not any(greeting in line.lower() for greeting in ['dear', 'hi', 'hello']):
                # Potential name line
                has_name = True
                break
        
        if not has_name:
            missing.append("Your name in signature")
        
        # Check for date/time if discussing meetings
        if 'meet' in text.lower() or 'call' in text.lower() or 'schedule' in text.lower():
            if not re.search(r'\d{1,2}[:/]\d{2}|\b(mon|tue|wed|thu|fri|monday|tuesday|wednesday|thursday|friday)\b', text.lower()):
                missing.append("Specific date/time for meeting")
        
        # Check for attachment mention
        if 'attach' in text.lower() and 'attach' not in text:
            missing.append("Actual attachment (you mentioned one)")
        
        return missing


# Convenience function for easy use
def improve_email_text(text: str, email_type: str = "general", tone: str = "semi_formal") -> Dict:
    """
    Quickly improve email text
    
    Args:
        text: The email text to improve
        email_type: Type of email (job_application, follow_up, meeting_request, etc.)
        tone: Desired tone (formal, semi_formal, friendly, persuasive, apologetic)
    """
    improver = ProfessionalEmailImprover()
    return improver.improve_email(text, email_type, tone)
