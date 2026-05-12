import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
import torch

# Download VADER lexicon
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

class SentimentAnalyzer:
    def __init__(self, model_type='vader'):
        self.model_type = model_type
        if self.model_type == 'vader':
            self.analyzer = SentimentIntensityAnalyzer()
            financial_lexicon = {
                'bullish': 2.0,
                'bearish': -2.0,
                'moon': 2.5, 
                'calls': 1.0, 
                'puts': -1.0,
                'long': 1.0,
                'short': -1.0,
                'buy': 1.5,
                'sell': -1.5,
                'hold': 0.5,
                'diamond hands': 2.5,
                'paper hands': -2.0,
                'tendies': 2.0,
                'bagholder': -2.5,
                'rally': 1.5,
                'dip': -1.0,
                'squeeze': 2.0
            }
            self.analyzer.lexicon.update(financial_lexicon)
        elif self.model_type == 'finbert':
            model_name = "ProsusAI/finbert"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            if torch.cuda.is_available():
                device = 0  # NVIDIA GPU
                print("FinBERT: Using NVIDIA GPU (CUDA)")
            else:
                device = -1
                print("FinBERT: No GPU found. Falling back to CPU.")

            self.pipeline = pipeline(
                "sentiment-analysis", 
                model=self.model, 
                tokenizer=self.tokenizer,
                truncation=True,
                max_length=512,
                device=device
            )

    def analyze_text(self, text):
        if not isinstance(text, str) or not text.strip():
            return {'label': 'neutral', 'score': 0.0}
            
        if self.model_type == 'vader':
            scores = self.analyzer.polarity_scores(text)
            compound = scores['compound']
            
            if compound >= 0.05:
                label = 'positive'
            elif compound <= -0.05:
                label = 'negative'
            else:
                label = 'neutral'
                
            return {
                'label': label,
                'score': compound
            }
        
        elif self.model_type == 'finbert':
            try:
                result = self.pipeline(text)
                label = result[0]['label'].lower()
                score = result[0]['score']
                
                if label == 'negative':
                    score = -score
                elif label == 'neutral':
                    score = 0.0
                
                return {
                    'label': label,
                    'score': score
                }
            except Exception as e:
                print(f"Error in FinBERT analysis: {e}")
                return {'label': 'neutral', 'score': 0.0}

    def process_dataframe(self, df, text_column='text'):
        if df is None or df.empty or text_column not in df.columns:
            return df
            
        df = df.copy()
        
        if self.model_type == 'finbert':
            # 1. Convert the whole column to a list of strings
            text_list = df[text_column].fillna('').tolist()
            
            # 2. Feed the entire list to the pipeline at once (batch_size=16 is safe for 4GB VRAM)
            results = self.pipeline(text_list, batch_size=16, truncation=True, max_length=512)
            
            # 3. Extract labels and scores and put them back in the dataframe
            df['sentiment_label'] = [res['label'].lower() for res in results]
            
            # Map negative scores to actual negative numbers
            scores = []
            for res in results:
                score = res['score']
                if res['label'].lower() == 'negative':
                    score = -score
                elif res['label'].lower() == 'neutral':
                    score = 0.0
                scores.append(score)
                
            df['sentiment_score'] = scores
            
        elif self.model_type == 'vader':
            # VADER stays the same (it runs on CPU anyway)
            sentiment_results = df[text_column].apply(self.analyze_text)
            df['sentiment_label'] = sentiment_results.apply(lambda x: x['label'])
            df['sentiment_score'] = sentiment_results.apply(lambda x: x['score'])
            
        return df
