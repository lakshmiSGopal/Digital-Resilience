import pandas as pd
import re
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

#code to preprocess content csv data
def preprocess_dataframe(df_texts, text_col='text'):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    for index, row in df_texts.iterrows():
        text = row[text_col]
        
        # Handle missing or non-string data
        if not isinstance(text, str):
            text = '' if pd.isna(text) else str(text)

        text = re.sub(r'http\S+', '', text)  # Remove URLs
        text = re.sub(r'#\S+', '', text)  # Remove hashtags
        text = re.sub(r' 0 ', ' zero ', text)  # Replace 0 with zero
        text = re.sub(r'[^A-Za-z]', ' ', text)  # Remove non-alphabetic characters
        text = text.lower()  # Convert to lowercase

        words = word_tokenize(text)  # Tokenize the words
        words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]  # Lemmatize and remove stop words

        df_texts.at[index, 'preprocessed_content'] = ' '.join(words)  # Store cleaned text

    return df_texts
#main filtration function to sort disaster articles from data set
def Emer(json_data, df_news, disaster_categories, output):
    #Extract exclusion keywords from Json file
    exclusion_keywords = json_data['Exclusion']
    #Set to keep track of unique article IDs
    unique_article_ids = set()
    #list to store filtered results 
    filtered_results = []
    #code block to filter the dataframe using the disaster keywords
    for category in disaster_categories:
        disaster_keywords = json_data[category]

        for disaster_keyword in disaster_keywords:
            matching_rows = df_news[df_news['preprocessed_content'].str.contains(disaster_keyword)]
            for index, row in matching_rows.iterrows():
                if row['id'] not in unique_article_ids:
                    filtered_results.append({
                        #data extracted with apropiate column names
                        'keyword': disaster_keyword,
                        'id': row['id'],
                        'title': row['title'], 
                        'content': row['preprocessed_content']
                    })                    
                    unique_article_ids.add(row['id'])
       #code block to remove text with the exclusion keywords
        filtered_results_excluded = []
        for result in filtered_results:
            exclude = False
            for exclusion_keyword in exclusion_keywords:
                if exclusion_keyword in result['content']:
                    exclude = True
                    break
            if not exclude:
                filtered_results_excluded.append(result)
    
    # code block to remove duplicates from the filtered results
    uniqueids = set()
    finalresult = []
    for article in filtered_results_excluded:
        if article['id'] not in uniqueids:
            finalresult.append(article)
            uniqueids.add(article['id'])

    # Create a DataFrame and save to CSV
    df_output = pd.DataFrame(finalresult)
    df_output.to_csv(output, index=False)

    # Print the total number of disaster-related content found
    f = len(finalresult)
    print("total disaster related-content found: ", f)
#code to convert file to csv and give it an index

df = pd.read_excel('/home/adarsh_js/Downloads/wayanad(5th).xlsx')#requres user input

df.to_csv('input.csv', index= False)#input csv filname

print("CSV file generated successfully")

df = pd.read_csv('input.csv')#csv filename

df.insert(0,'id',range(5000,5000+len(df)))

df.to_csv('ninput.csv', index=False)#new csv filename

df_texts = pd.read_csv('ninput.csv')#input csv name

#preprocess text
df_texts = preprocess_dataframe(df_texts)

#load disaster keywords
json_data = pd.read_json('disaster3.json')

#define disaster categories
disaster_categories = ["Tsunami", "Earthquake", "Hurricane", "Tornado", "Flood", "Wildfire", "Drought", "Landslide", "Monsoon", "Epidemics"]


output = "output.csv" #set output file

#run main function
Emer(json_data,df_texts,disaster_categories,output)

#print total texts
total = len(df_texts)
print("total tweets available: ",total)




#function to convert final csv file to an excel sheet
def csv_to_excel(input_csv, output_excel):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_csv)

    # Write the DataFrame to an Excel file
    df.to_excel(output_excel, index=False, sheet_name='Sheet1')

# Example usage
input_csv = 'output.csv'  # Replace with your CSV file path
output_excel = 'output.xlsx'  # Replace with your desired Excel file path

csv_to_excel(input_csv, output_excel)

