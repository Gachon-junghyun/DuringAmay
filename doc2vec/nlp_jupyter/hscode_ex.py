import re
import pandas as pd
from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec
from tqdm import tqdm
import os

df_train = pd.read_csv("C:/Users/onepe/PycharmProjects/DuringAmay/doc2vec/nlp_jupyter/data/train_data.csv", sep="\t", dtype='str')
df_train = df_train.drop_duplicates()
#print(df_train)

df_test = pd.read_csv("C:/Users/onepe/PycharmProjects/DuringAmay/doc2vec/nlp_jupyter/data/test_data.csv", sep="\t", dtype='str')
df_test = df_test.drop_duplicates()
#df_test


# Setting up stopwords
org_stop_words = {'of', 'or', 'and', 'for', 'than', 'the', 'in', 'with', 'to', 'but', 'by', 'whether',
                  'on', 'its', 'an', 'their', 'at', 'this', 'which', 'from', 'as', 'be', 'is', 'other'}


# regular expression pattern
space_pattern = re.compile(r'\s\s+') # Process whitespace
remove_pattern = re.compile(r'[\;\,\)\(\[\]]') # select only ; , ) ( ] [

# Process white space
df_train["DESC"] = df_train["DESC"].apply(lambda x : re.sub(space_pattern, " ", x))

# Create a list where the preprocessing data is stored.
refined_text_list = []

# For each dataframe row, iterate and perform data preprocessing.
for idx, row in tqdm(df_train.iterrows(), total=df_train.shape[0]):
    # Convert to lowercase
    text = row['DESC'].lower()
    # Remove some special characters
    text = re.sub(remove_pattern, " ", text)
    # split
    text_split = text.split()

    # Create an array only selecting words with more than 1 character, and is not part of stopwords.
    org_contents_split = [w for w in text_split if len(w.strip()) > 1 and w.strip() not in org_stop_words]
    org_contents = " ".join(w for w in org_contents_split)

    # Convert multiple whitespace into one whitespace.
    final_sentence = re.sub(space_pattern, " ", org_contents)

    # Add the preprocessed data to the list.
    refined_text_list.append(final_sentence)


# Add the preprocessed data to the dataframe.
df_train['REFINED_TEXT'] = refined_text_list
df_train = df_train.sort_values(by=['HSCODE', 'REFINED_TEXT']).drop_duplicates(subset=['HSCODE', 'REFINED_TEXT']).reset_index(drop=True)
#print(df_train)


# Remove whitespace
df_test["DESC"] = df_test["DESC"].apply(lambda x : re.sub(space_pattern, " ", x))

# Array where the preprocessing data will be stored
refined_text_list = []

# Perform data proprocessing, iterating through data frame rows.
for idx, row in tqdm(df_test.iterrows(), total=df_test.shape[0]):
    # Covert to lowercase
    text = row['DESC'].lower()
    # Remove some special characters
    text = re.sub(remove_pattern, " ", text)
    # split
    text_split = text.split()

    # Create an array only selecting words with more than 1 character, and is not part of stopwords.
    org_contents_split = [w for w in text_split if len(w.strip()) > 1 and w.strip() not in org_stop_words]
    org_contents = " ".join(w for w in org_contents_split)

    # Convert multiple whitespaces to one whitespace
    final_sentence = re.sub(space_pattern, " ", org_contents)

    refined_text_list.append(final_sentence)


# Add the preprocessing data to the dataframe.
df_test['REFINED_TEXT'] = refined_text_list
df_test = df_test.sort_values(by=['HSCODE', 'REFINED_TEXT']).drop_duplicates(subset=['HSCODE', 'REFINED_TEXT']).reset_index(drop=True)
#print(df_test)



model = Doc2Vec(
    vector_size=200,
    min_count=0,
    window=5,
    sample=1e-4,
    negative=5,
    workers=os.cpu_count(),
    hs=1,
    alpha=0.025,
    min_alpha=0.001,
    seed=1,
    dm=0,
    dbow_words=0,
    dm_mean=0,
    dm_concat=0,
    dm_tag_count=1
)


# paragraph id = HSCODE
sentence = []
for idx, row in tqdm(df_train.iterrows(), total=df_train.shape[0]):
    sentence.append(TaggedDocument(row['REFINED_TEXT'].split(), [row['HSCODE']]))

# vocab creation
model.build_vocab(sentence)

# model training
model.train(sentence, total_examples=model.corpus_count, epochs=10)


# Evaluate similarity
df_sim = pd.DataFrame(columns = ['HSCODE', 'TOP_1_HS', 'TOP_1_SCORE', 'TOP_2_HS', 'TOP_2_SCORE', 'TOP_3_HS', 'TOP_3_SCORE'])
for idx, row in tqdm(df_test.iterrows(), total=df_test.shape[0]):
    # Method for data prediction(return result for top 3)
    input_vector = model.infer_vector(row['REFINED_TEXT'].split(), epochs=20)
    similarities = model.dv.most_similar([input_vector], topn=3)
    simil_result = [(simil[0], round(simil[1], 4)) for simil in similarities]
    new_row = pd.DataFrame({
        'HSCODE': [row['HSCODE']],
        'TOP_1_HS': [simil_result[0][0]], 
        'TOP_1_SCORE': [simil_result[0][1]],
        'TOP_2_HS': [simil_result[1][0]], 
        'TOP_2_SCORE': [simil_result[1][1]],
        'TOP_3_HS': [simil_result[2][0]], 
        'TOP_3_SCORE': [simil_result[2][1]]
    })
    df_sim = pd.concat([df_sim, new_row], ignore_index=True)

#print(df_sim)


# Check whether included or not

correct_result = []
for idx, row in tqdm(df_sim.iterrows(), total=df_sim.shape[0]):
    simil_hs_list = [row['TOP_1_HS'], row['TOP_2_HS'], row['TOP_3_HS']]
    if row['HSCODE'] in simil_hs_list:
        correct_result.append(True)
    else:
        correct_result.append(False)
df_sim['INCLUDED'] = correct_result

print(df_sim)


# Function that returns the sample test result

def simil_test_input(model, input_text):
    # Preprocessing
    input_text = re.sub(space_pattern, " ", input_text)
    input_text = input_text.lower()
    input_text = re.sub(remove_pattern, " ", input_text)
    text_split = input_text.split()
    org_contents_split = [w for w in text_split if len(w.strip()) > 1 and w.strip() not in org_stop_words]
    org_contents = " ".join(w for w in org_contents_split)
    final_sentence = re.sub(space_pattern, " ", org_contents)
    refined_text_list = final_sentence.split()
    
    # Model input
    input_vector = model.infer_vector(refined_text_list, epochs=20)
    similarities = model.dv.most_similar([input_vector], topn=3)
    simil_result = [(simil[0], round(simil[1], 4)) for simil in similarities]
    return simil_result


input_text = "Lamborghini" #"VEGETABLE VENUSTARS CABBICHOKE GOLD CABBAGE SOUP POWDER HEAT VENUSTARS CABBICHOKE GOLD CABBAGE SOUP POWDER HEATED 250G" #input("DESC input:")
result = simil_test_input(model, input_text)

for idx, data in enumerate(result):
    print("\n{}순위:\n\tHS코드: {}\n\t유사도 점수: {}".format(idx + 1, data[0], data[1]))

