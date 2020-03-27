import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from nltk.stem import PorterStemmer
from string import punctuation
from nltk.stem import WordNetLemmatizer

from P5VoiceToText import db
from P5VoiceToText.models import Imist_ambo_template, Voice_files, Voice_text_conversion, Text_categorization

class ClassifyText:

	def __init__(self): 
		self.voice_file = None
		self.text = ""
		self.sentences = []
		self.category_keyword = { "identification" : [],
								  "mechanism" : [],
								  "injury": [],
								  "signs": [],
								  "treatment": [],
								  "allergy": [],
								  "medication": [],
								  "background": [],
								  "other": [] }

	def if_voice_file_exists(self, filename):
		self.voice_file = Voice_files.objects.filter(filename=filename)
		return len(self.voice_file) > 0

	def if_converted_text_exists(self, filename):
		self.voice_file = Voice_files.objects.filter(filename=filename)[0]
		voice_text_conversion = Voice_text_conversion.objects.filter(voiceFile=self.voice_file)
		if len(voice_text_conversion)>0:
			self.text = voice_text_conversion[0].converted_text
		return len(voice_text_conversion) > 0

	def if_categorized_text_exists(self, filename):
		self.voice_file = Voice_files.objects.filter(filename=filename)[0]
		text_categorization = Text_categorization.objects.filter(voiceFile=self.voice_file)
		return len(text_categorization) > 0 

	# Removing Stop Words ....
	def remove_stopwords(self, sentence):
		sentence = sentence.lower()
		stop_words = set(stopwords.words('english') + list(punctuation)) 		
		word_tokens = word_tokenize(sentence) 
		filtered_sentence = [w for w in word_tokens if not w in stop_words] 
		filtered_sentence = [] 
		for w in word_tokens: 
			if w not in stop_words: 
				filtered_sentence.append(w) 

		return filtered_sentence 



	# Get the root of words using Stemming and Lemmatization ....
	def stemming_and_lemmatization_text(self, words):
		ps = PorterStemmer() 
		wordnet_lemmatizer = WordNetLemmatizer()
		words = [wordnet_lemmatizer.lemmatize(ps.stem(word)) for word in words]
		return words
		

	# Cleaning of Text	
	def clean_text(self, sentence):
		words = self.remove_stopwords(sentence)
		words = self.stemming_and_lemmatization_text(words)
		return words


	# Classify the specific words into IMIST_AMBO categories ....
	def classify_text_into_categories(self, sentence, words):
		idx = 0
		age_word = ""
		for i in range(0, len(words)):
			if words[i]=='age' or words[i]=='old':
				age_word = words[i]
				idx = i
				break

		if (age_word=='old' or age_word=='age') and words[i-2].isnumeric() and (sentence not in self.category_keyword['identification']): #ex: 23 year old, 23 years of age
			self.category_keyword['identification'].append(sentence)
		elif age_word=='age' and words[i+1].isnumeric() and (sentence not in self.category_keyword['identification']): #ex. age is 23 years
			self.category_keyword['identification'].append(sentence)


		for i in range(0, len(words)):
			#unigrams
			imist_ambos = Imist_ambo_template.objects.filter(keyword=words[i])
			if len(imist_ambos) and (sentence not in self.category_keyword[imist_ambos[0].category]):
				self.category_keyword[imist_ambos[0].category].append(sentence)

			#bigrams
			if i<(len(words)-1):
				search_keyword = words[i]+" "+words[i+1]
				imist_ambos = Imist_ambo_template.objects.filter(keyword=search_keyword)
				if len(imist_ambos) and (sentence not in self.category_keyword[imist_ambos[0].category]):
					self.category_keyword[imist_ambos[0].category].append(sentence)

			#trigrams		
			if i<(len(words)-2):
				search_keyword = words[i]+" "+words[i+1]+" "+words[i+2]
				imist_ambos = Imist_ambo_template.objects.filter(keyword=search_keyword)				
				if len(imist_ambos) and (sentence not in self.category_keyword[imist_ambos[0].category]):
					self.category_keyword[imist_ambos[0].category].append(sentence)



	def clean_and_classify(self):
		self.sentences = self.text.split('.')

		for sentence in self.sentences:
			words = self.clean_text(sentence)
			self.classify_text_into_categories(sentence, words)
		return self.category_keyword


	def save_categorizedText_in_db(self):
		text_categorization = Text_categorization(voiceFile=self.voice_file)
		text_categorization.identification = self.category_keyword['identification']
		text_categorization.mechanism = self.category_keyword['mechanism']
		text_categorization.injury = self.category_keyword['injury']
		text_categorization.signs = self.category_keyword['signs']
		text_categorization.treatment = self.category_keyword['treatment']
		text_categorization.allergy = self.category_keyword['allergy']
		text_categorization.medication = self.category_keyword['medication']
		text_categorization.background = self.category_keyword['background']
		text_categorization.other = self.category_keyword['other']
		text_categorization.save()



	def get_categorizedText_from_db(self, filename):
		self.voice_file = Voice_files.objects.filter(filename=filename)[0]
		text_categorization = Text_categorization.objects.filter(voiceFile=self.voice_file)[0]
		self.category_keyword['identification'] = text_categorization.identification
		self.category_keyword['mechanism'] = text_categorization.mechanism
		self.category_keyword['injury'] = text_categorization.injury
		self.category_keyword['signs'] = text_categorization.signs
		self.category_keyword['treatment'] = text_categorization.treatment
		self.category_keyword['allergy'] = text_categorization.allergy
		self.category_keyword['medication'] = text_categorization.medication
		self.category_keyword['background'] = text_categorization.background
		self.category_keyword['other'] = text_categorization.other
		return self.category_keyword


	def insert_into_imist_ambo_template(self):
		map_keyword_category = [
			{"keyword": "age",
			 "category": "identification"},
			{"keyword": "mal",
			 "category": "identification"},
			{"keyword": "femal",
			 "category": "identification"},
			{"keyword": "mca",
			 "category": "mechanism"},
			{"keyword": "rollov",
			 "category": "mechanism"},
			{"keyword": "eject",
			 "category": "mechanism"},
			{"keyword": "death other occupant",
			 "category": "mechanism"},
			{"keyword": "pedestrian",
			 "category": "mechanism"},
			{"keyword": "motorcyclist",
			 "category": "mechanism"},
			{"keyword": "cyclist",
			 "category": "mechanism"},
			 {"keyword": "motorcycl",
			 "category": "mechanism"},
			{"keyword": "cycl",
			 "category": "mechanism"},
			{"keyword": "fall",
			 "category": "mechanism"},
			{"keyword": "fell",
			 "category": "mechanism"},
			{"keyword": "burn",
			 "category": "mechanism"},
			{"keyword": "hit",
			 "category": "mechanism"},
			{"keyword": "explos",
			 "category": "mechanism"},
			{"keyword": "trap",
			 "category": "mechanism"},
			{"keyword": "time entrap",
			 "category": "mechanism"},
			{"keyword": "mba",
			 "category": "mechanism"},
			{"keyword": "extric",
			 "category": "mechanism"},
			{"keyword": "fatal",
			 "category": "mechanism"},
			{"keyword": "penetr",
			 "category": "injury"},
			{"keyword": "blunt",
			 "category": "injury"},
			{"keyword": "blunt",
			 "category": "trauma"},
			{"keyword": "head",
			 "category": "injury"},
			{"keyword": "neck",
			 "category": "injury"},
			{"keyword": "chest",
			 "category": "injury"},
			{"keyword": "abdomen",
			 "category": "injury"},
			{"keyword": "pelvi",
			 "category": "injury"},
			{"keyword": "axilla",
			 "category": "injury"},
			{"keyword": "groin",
			 "category": "injury"},
			{"keyword": "limb",
			 "category": "injury"},
			{"keyword": "amput",
			 "category": "injury"},
			{"keyword": "crush",
			 "category": "injury"},
			{"keyword": "spinal",
			 "category": "injury"},
			{"keyword": "tension pneumothorax",
			 "category": "injury"},
			{"keyword": "rigid abdomen",
			 "category": "injury"},
			{"keyword": "fractur",
			 "category": "injury"},
			{"keyword": "facial burn",
			 "category": "injury"},
			{"keyword": "disloc",
			 "category": "injury"},
			{"keyword": "eviscer",
			 "category": "injury"},
			{"keyword": "blast",
			 "category": "injury"},    
			{"keyword": "pr",
			 "category": "signs"},
			{"keyword": "bp",
			 "category": "signs"},
			{"keyword": "gcs",
			 "category": "signs"},
			{"keyword": "evm",
			 "category": "signs"},
			{"keyword": "pupil size",
			 "category": "signs"},
			{"keyword": "reactiv",
			 "category": "signs"},
			{"keyword": "rr",
			 "category": "signs"},
			{"keyword": "t degree",
			 "category": "signs"},
			{"keyword": "spo 2",
			 "category": "signs"},
			{"keyword": "sob",
			 "category": "signs"},
			{"keyword": "sbp",
			 "category": "signs"},
			{"keyword": "cervic collar",
			 "category": "treatment"},
			{"keyword": "op airway",
			 "category": "treatment"},
			{"keyword": "np airway",
			 "category": "treatment"},
			{"keyword": "lma",
			 "category": "treatment"},
			{"keyword": "ett",
			 "category": "treatment"},
			{"keyword": "rsi",
			 "category": "treatment"},
			{"keyword": "ventil",
			 "category": "treatment"},
			{"keyword": "chest decompress",
			 "category": "treatment"},
			{"keyword": "iv access",
			 "category": "treatment"},
			{"keyword": "iv hartmann",
			 "category": "treatment"},
			{"keyword": "methoxyfluran",
			 "category": "treatment"},
			{"keyword": "maxolon",
			 "category": "treatment"},
			{"keyword": "morphin",
			 "category": "treatment"},
			{"keyword": "midazolam",
			 "category": "treatment"},
			{"keyword": "fentanyl",
			 "category": "treatment"},
			{"keyword": "suxamethonium",
			 "category": "treatment"},
			{"keyword": "pancuronium",
			 "category": "treatment"},
			{"keyword": "adrenalin",
			 "category": "treatment"},
			{"keyword": "intub",
			 "category": "treatment"},
			{"keyword": "haemost dressing",
			 "category": "treatment"},
			{"keyword": "toumiquet",
			 "category": "treatment"},
			{"keyword": "blood transfus",
			 "category": "treatment"},
			{"keyword": "neuromuscular block",
			 "category": "treatment"},
			{"keyword": "allergi",
			 "category": "other"},
			{"keyword": "mass casualti",
			 "category": "other"},
			{"keyword": "inter-hospit transfer",
			 "category": "other"},
			{"keyword": "pregnanc",
			 "category": "other"},
			{"keyword": "pregnant",
			 "category": "other"},
			{"keyword": "co-morbid",
			 "category": "other"},
			{"keyword": "anticoagul therapi",
			 "category": "other"}
			]
		arr = [Imist_ambo_template(**data) for data in map_keyword_category]
		Imist_ambo_template.objects.insert(arr, load_bulk=True)


	def test_db(self):
		voice_file = Voice_files(filename="mediahandler4.aac", s3link="some s3link of aws 4").save()
		text = "Phoenix soon. Judy, this is Sean. Go ahead. Trauma. I got Ah. I mean you 10 minutes. Okay. 12 year old. Best dream. A history of white. I'm sorry. He was a pedestrian walking. Got hit by a vehicle. Okay, Okay. Multi system trauma. Okay. Thank you."

		'''
		voice_text_conversion = Voice_text_conversion(converted_text=text, voiceFile=voice_file).save()
		print("Connection to db successful")
		
		voice_file = Voice_files.objects.filter(filename="test_file1")
		text_categorization = Text_categorization(voiceFile=voice_file[0])
		text_categorization.identification = self.category_keyword['identification']
		text_categorization.mechanism = self.category_keyword['mechanism']
		text_categorization.injury = self.category_keyword['injury']
		text_categorization.signs = self.category_keyword['signs']
		text_categorization.treatment = self.category_keyword['treatment']
		text_categorization.allergy = self.category_keyword['allergy']
		text_categorization.medication = self.category_keyword['medication']
		text_categorization.background = self.category_keyword['background']
		text_categorization.other = self.category_keyword['other']
		text_categorization.save()
		'''