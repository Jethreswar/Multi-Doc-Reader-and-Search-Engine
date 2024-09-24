import re
from nltk.stem import PorterStemmer
from collections import defaultdict
import fitz 
stemmer = PorterStemmer()
# Preprocessing  the query
def preprocess(query):
    query = re.sub(r'[^a-zA-Z\s]', '', query).lower()
    terms = query.split()
    terms = [stemmer.stem(term) for term in terms]
    return terms

def tokenize(text):
    tokens = preprocess(text)
    index = defaultdict(list)
    for position, term in enumerate(tokens):
        index[term].append(position)
    obj = {
            "terms": [{"term": term, "positions": positions} for term, positions in index.items()]
        }
    return obj

def highlight_query_in_text(input_string, word, tag_name="span", **kwargs):
    word = word.lower()
    word = re.sub(r'[^a-zA-Z\s]', '', word)
    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
    highlighted_string = pattern.sub("<{} {}>{}</{}>".format(tag_name, ' '.join([f'{key}="{value}"' for key, value in kwargs.items()]), word, tag_name), input_string)
    return highlighted_string

import re
# import random

def highlight_query_in_text(input_string, word_list, color_array, tag_name="span", **kwargs):
    """
    Highlights words from the word_list in the input_string using colors from the color_array.

    Args:
    - input_string (str): The input string to be highlighted.
    - word_list (list): A list of words to highlight.
    - color_array (list): An array of colors to use for highlighting.
    - tag_name (str): The HTML tag name to use for highlighting (default is 'span').
    - **kwargs: Additional keyword arguments for styling.

    Returns:
    - str: The input string with highlighted words.
    """
    # Iterate over each word and its corresponding color
    highlighted_string = input_string
    for word, color in zip(word_list ,color_array):
        word = word.lower()
        word = re.sub(r'[^a-zA-Z\s]', '', word)
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        
        # Create the opening tag with specified attributes (including color)
        opening_tag = "<{} style='background-color:{}' {}>".format(tag_name, color, ' '.join([f'{key}="{value}"' for key, value in kwargs.items()]))
        
        # Create the closing tag
        closing_tag = "</{}>".format(tag_name)
        
        # Modify the substitution pattern to include background color styling
        highlighted_string = pattern.sub("{}{}{}".format(opening_tag, word, closing_tag), highlighted_string)
    return highlighted_string

# Example usage
# input_string = "I have an Apple, a banana, and an orange."
# word_list = ["apple", "banana", "orange"]
# color_array = ["lightblue", "lightgreen", "lightpink"]
# highlighted_text = highlight_query_in_text(input_string, word_list, color_array)
# print(highlighted_text)

def get_positions(docs, query):
    data = []
    query_terms = preprocess(query)
    for document in docs:
        document_terms = [term['term'] for term in document['terms']]
        # print("Document terms:", document_terms)
        
        if all(term in document_terms for term in query_terms):
            # print("Match found in document:", document['filename']) 
            first_query_term = query_terms[0]
            first_term_positions = [term['positions'] for term in document['terms'] if term['term'] == first_query_term][0]
            
            start_positions = []
            for start_pos in first_term_positions:
                position_matched = True
                for i in range(1, len(query_terms)):
                    term_positions = [term['positions'] for term in document['terms'] if term['term'] == query_terms[i]][0]
                    if start_pos + i not in term_positions:
                        position_matched = False
                        break
                if position_matched:
                    start_positions.append(start_pos)
            
            if start_positions:
                doc = {
                    "file_name": document['filename'],
                    "start_positions": start_positions,
                    "query": query,
                    "type": document['type'],
                    "total_occurances": len(start_positions),
                    "id" : document['id'],
                    "extension": document['filename'].split('/')[-1].split('.')[-1] if document['type'] == 'file' else None,
                }
                data.append(doc)
                print("Match found in document:", document['filename'])
                print("Start positions:", start_positions)
            else:
                print("No consecutive matches found.")
        else:
            print("No match found in document:", document['filename'])
    return data

def stringMod(sentence,position,length):
    li = list(sentence.split())
    flag =False
    correctingFactor = 0
    temp=-1
    print(position)
    for element in position:
        print(correctingFactor)
        element +=correctingFactor
        if(element<=temp):
            element -=1
            flag =True
        li.insert(element,"<span style='color:red;background-color:yellow;'>")
        print(element)
        after = element+length+1
        if(flag):
            after +=1
        temp=after
        li.insert(after,"</span>")
        correctingFactor += 2
        print(after)
    return ' '.join(li)




def highlight_text_in_pdf(pdf_path, queries, colors, output_path):
    # Open the PDF
    doc = fitz.open(pdf_path)
    
    # Iterate over queries and colors
    for query, color in zip(queries, colors):
        # Search for the text to highlight
        for page in doc:
            # Split text into words
            # Highlight exact matches
            text_instances = page.search_for(query)
            for inst in text_instances:
                # Highlight the text with the specified color
                highlight = page.add_highlight_annot(inst)
                highlight.set_colors(stroke=fitz.pdfcolor[color])
                highlight.update() 
                # highlight = page.add_highlight_annot(inst)
                # highlight.set_colors(stroke=color)
                # highlight.update() 
    # Save the modified PDF
    doc.save(output_path)
    doc.close()

# # Example usage
# pdf_path = "paper.pdf"
# queries = ["The Content of PC is ABC", "combinational", " assembly language program to multiply"]
# colors = [fitz.pdfcolor["pink"], fitz.pdfcolor["green"], fitz.pdfcolor['blue']]  # Specify colors in hexadecimal format (e.g., yellow, cyan)
# output_path = "highlighted.pdf"

# highlight_text(pdf_path, queries, colors, output_path)

def merge_lists(lists):
    data = []
    file_dict = {}
    
    for input_list in lists:
        for item in input_list:
            file_id = item["id"]
            if file_id not in file_dict:
                file_dict[file_id] = {
                    "id": file_id,
                    "file_name": item["file_name"],
                    "extension": item["extension"],
                    "type": item["type"],
                    "query": []
                }
            file_dict[file_id]["query"].append({
                "query": item["query"],
                "start_positions": item["start_positions"],
                "total_occurances": item["total_occurances"]
            })
    
    for file_id, file_data in file_dict.items():
        data.append(file_data)
    
    return data