import csv
import re
import torch
import json
import torch
import ast
import uuid
import json
import os
from openai import OpenAI
from guidance import models, select, gen
torch.manual_seed(0)


global model
global modelType
global promptModel
global promptModelType
global previous_results
global topics
global selectOptions
global topic_id_counter
global interface


model=""
modelType="Transformers"
promptModel=""
promptModelType="Transformers"


topics = []


interface = False
previous_results = {}
topic_id_counter = 0



def setModel(newModel,newModelType,api_key=""):
    global model
    global modelType
    model=newModel
    modelType=newModelType
    global ModelGuidance 
    global client
    if modelType=="Transformers":
        ModelGuidance = models.Transformers(model, device_map='cuda', torch_dtype=torch.bfloat16, echo=False, trust_remote_code=True)
    if modelType == "LlamaCpp":
        ModelGuidance = models.LlamaCpp(model)
    if modelType=="OpenAI":
        if not api_key=="":
            client = OpenAI(api_key=apiKeyOpenAI)
    if modelType=="DeepInfra":
        if not api_key=="":
            client = OpenAI(api_key=api_key,base_url="https://api.deepinfra.com/v1/openai")


def setPromptModel(newPromptModel, newPromptModelType, api_key=""):
    global promptModel
    global promptModelType
    promptModel=newPromptModel
    promptModelType=newPromptModelType
    global promptModelGuidance 
    global client
    if promptModelType=="Transformers":
        if promptModel==Model:
            promptModelGuidance=ModelGuidance
        else:
            promptModelGuidance = models.Transformers(model, device_map='cuda', torch_dtype=torch.bfloat16, echo=False, trust_remote_code=True)
    if promptModelType == "LlamaCpp":
        if promptModel == model:
            ModelGuidance = models.LlamaCpp(model)
        else:
            promptModelGuidance = models.LlamaCpp(model)
    if modelType=="OpenAI" or promptModelType=="OpenAI":
        if not api_key=="":
            client = OpenAI(api_key=apiKeyOpenAI)
    if modelType=="DeepInfra" or promptModelType=="DeepInfra":
        if not api_key=="":
            client = OpenAI(api_key=api_key,base_url="https://api.deepinfra.com/v1/openai")


    
        
def getAnswer(prompt, topicIndex, constrainedOutput, selectOptions, temperature=0.0):
    if modelType=="OpenAI" or modelType=="DeepInfra":
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=30,
            temperature=temperature,
        )
        generated_answer = completion.choices[0].message.content

        print(generated_answer)
        for option in ast.literal_eval(selectOptions[topicIndex]):
            escaped_option = re.escape(option)

            if re.search(escaped_option, generated_answer, re.IGNORECASE):
                ret = option  
                break
        else:
            ret = "undefined"
        return ret
        
    else:
        if constrainedOutput==True:
            output=ModelGuidance+f' '+prompt+select(options=ast.literal_eval(selectOptions[topicIndex]),name='answer')
            ret=output["answer"]   
        else:
            output=ModelGuidance+f' '+prompt+gen(max_tokens=15,name='answer')
            generated_answer = output["answer"]
            print(generated_answer)
            for option in ast.literal_eval(selectOptions[topicIndex]):
                escaped_option = re.escape(option)

                if re.search(escaped_option, generated_answer, re.IGNORECASE):
                    ret = option  
                    break
            else:
                ret = "undefined"


        return ret
    
    
def getAnswerSingleTopic(prompt, categories, constrainedOutput):
    if modelType in ("OpenAI", "DeepInfra"):
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=30,
            temperature=0,
        )
        generated_answer = completion.choices[0].message.content
        print(generated_answer) 

        for option in categories:
            escaped_option = re.escape(option)
            if re.search(escaped_option, generated_answer, re.IGNORECASE):
                return option
        return "undefined"

    else:
        if constrainedOutput:
            category_str = "[" + ",".join(f"'{cat}'" for cat in categories) + "]"
            output = ModelGuidance + f" {prompt}" + select(options=ast.literal_eval(category_str), name='answer')
            return output["answer"]
        else:
            output = ModelGuidance + f" {prompt}" + gen(max_tokens=15, name='answer')
            generated_answer = output["answer"]
            print(generated_answer)
            for option in categories:
                escaped_option = re.escape(option)
                if re.search(escaped_option, generated_answer, re.IGNORECASE):
                    return option
            return "undefined"

def evaluate_condition(condition):
    if not condition: 
        return True

    if "==" not in condition:
        print(f"Invalid condition format: {condition}")
        return False

    left_side, right_side = condition.split("==", 1)
    left_side = left_side.strip()
    right_side = right_side.strip()

    if left_side not in previous_results:
        print(f"No previous classification result for topic '{left_side}'. Condition: {condition}")
        return False

    chosen_cat_id = previous_results[left_side]

    return chosen_cat_id == right_side


def classify(text, isItASingleClassification=True, constrainedOutput=True, withEvaluation=False, groundTruthRow=None):

    selectOptions = []
    for topic_data in topics:
        tmpSelectOptions = "["
        for category_input, _, _ in topic_data['categories']:
            tmpSelectOptions += "'" + category_input.value + "',"
        tmpSelectOptions = tmpSelectOptions[:-1] + "]"
        selectOptions.append(tmpSelectOptions)

    ret = []

    if withEvaluation and groundTruthRow is not None:
        for i, topic_info in enumerate(topics):
            groundTruthCategoryName = groundTruthRow[i+1] 
            gt_cat_id = None
            for (cat_input, _, cat_id) in topic_info['categories']:
                if cat_input.value == groundTruthCategoryName:
                    gt_cat_id = cat_id
                    break
            previous_results[topic_info['id']] = gt_cat_id

    for l in range(len(selectOptions)):
        condition = topics[l]['condition'].value.strip()
        condition_is_true = evaluate_condition(condition)

        if not condition_is_true:
            ret.append("")
            if interface == True and isItASingleClassification:
                print(f"Skipping {topics[l]['topic_input'].value} due to unmet condition: {condition}")
            continue

        prompt = topics[l]['prompt'].value
        prompt = prompt.replace('[TOPIC]', topics[l]['topic_input'].value)
        prompt = prompt.replace('[CATEGORIES]', selectOptions[l])
        prompt = prompt.replace('[TEXT]', text)

        answer = getAnswer(prompt, l, constrainedOutput, selectOptions, 0.0)
        ret.append(answer)

        if not withEvaluation:
            chosen_category_id = None
            for category_input, _, category_id in topics[l]['categories']:
                if category_input.value == answer:
                    chosen_category_id = category_id
                    break
            previous_results[topics[l]['id']] = chosen_category_id

        if interface == True and isItASingleClassification:
            print(f"{topics[l]['topic_input'].value}: {answer}")

    return ret

        
def get_current_accuracy(topic_info):
    label_text = topic_info['performance_label'].value
    match = re.match(r"Accuracy:\s+([\d.]+)%", label_text)
    if match:
        return float(match.group(1))
    return 0.0



                

def generate_id():
    return str(uuid.uuid4())[:8] 



def number_to_letters(num, uppercase=True):
    letters = ""
    while num > 0:
        num -= 1
        letters = chr((num % 26) + (65 if uppercase else 97)) + letters
        num //= 26
    return letters



def show_topics_and_categories():
    if not topics:
        print("No topics are currently defined.")
        return

    for i, topic_info in enumerate(topics, start=1):
        topic_name = topic_info['topic_input'].value
        topic_id = topic_info.get('id', '?')
        
        condition_val = topic_info['condition'].value if 'condition' in topic_info else None
        prompt_val    = topic_info['prompt'].value    if 'prompt'    in topic_info else None
        
        print(f"Topic {i} (ID={topic_id}): {topic_name}")

        if condition_val:
            print(f"  Condition: {condition_val}")

        if prompt_val:
            print(f"  Prompt: {prompt_val}")

        categories = topic_info.get('categories', [])
        if not categories:
            print("    [No categories in this topic]")
        else:
            for j, (category_input, _, cat_id) in enumerate(categories, start=1):
                cat_name = category_input.value
                print(f"    {j}. {cat_name} (ID={cat_id})")

    print()  

   
def add_topic(topic_name, 
              categories=[], 
              condition="", 
              prompt="INSTRUCTION: You are a helpful classifier. You select the correct of the possible categories "
        "for classifying a piece of text. The topic of the classification is '[TOPIC]'. "
        "The allowed categories are '[CATEGORIES]'. QUESTION: The text to be classified is '[TEXT]'. "
        "ANSWER: The correct category for this text is '"):
   
    global topic_id_counter
    topic_id_counter += 1
    
    if prompt is None:
        prompt = (
            "INSTRUCTION: You are a helpful classifier. You select the correct of the possible categories "
            "for classifying a piece of text. The topic of the classification is '[TOPIC]'. "
            "The allowed categories are '[CATEGORIES]'. QUESTION: The text to be classified is '[TEXT]'. "
            "ANSWER: The correct category for this text is '"
        )

    topic_input_mock = MockText(topic_name)
    condition_mock = MockText(condition)
    prompt_mock = MockText(prompt)
    
    topic_id = number_to_letters(topic_id_counter, uppercase=True)
    
    topic_info = {
        'id': topic_id,
        'topic_input': topic_input_mock,
        'condition': condition_mock,
        'categories': [],
        'prompt': prompt_mock,
        'categories_container': None,
        'topic_box': None,
        'performance_label': None,
        'checkPrompt_button': None,
        'num_iterations_input': None,
        'iteratePromptImprovements_button': None,
        'replacePrompt_button': None,
        
        'best_prompt_found': None,
        'best_prompt_accuracy': None,
        
        'category_counter': 0
    }
    
    for cat_str in categories:
        topic_info['category_counter'] += 1
        cat_id = number_to_letters(topic_info['category_counter'], uppercase=False)  # a, b, c ...
        category_tuple = (MockText(cat_str), None, cat_id)
        
        topic_info['categories'].append(category_tuple)
    
    topics.append(topic_info)
    
    return topic_info


def remove_topic(topic_id_str):
    for i, t in enumerate(topics):
        if t.get('id') == topic_id_str:
            del topics[i]
            print(f"Topic (ID={topic_id_str}) removed.")
            return 

    print(f"No topic found with ID={topic_id_str}.")
    
    
    
def add_category(topicId, categoryName, Condition=""):
    found_topic = None
    for topic_info in topics:
        if topic_info.get('id') == topicId:
            found_topic = topic_info
            break

    if not found_topic:
        print(f"No topic found with ID={topicId}")
        return

    if 'category_counter' not in found_topic:
        found_topic['category_counter'] = 0

    found_topic['category_counter'] += 1
    cat_id = number_to_letters(found_topic['category_counter'], uppercase=False)
    new_category_tuple = (MockText(categoryName), None, cat_id)

    if 'categories' not in found_topic:
        found_topic['categories'] = []
    found_topic['categories'].append(new_category_tuple)

    if Condition:
        if 'condition' not in found_topic or not hasattr(found_topic['condition'], 'value'):
            found_topic['condition'] = MockText("")
        found_topic['condition'].value = Condition

    print(f"Category '{categoryName}' (ID={cat_id}) added to topic '{topicId}'.")
    if Condition:
        print(f"  Updated topic condition to: {Condition}")
        
        
def remove_category(topicId, categoryId):
    for topic_info in topics:
        if topic_info.get('id') == topicId:
            categories = topic_info.get('categories', [])
            for i, (cat_input, cat_box, cat_id) in enumerate(categories):
                if cat_id == categoryId:
                    del categories[i]
                    print(f"Removed category (ID={categoryId}) from topic (ID={topicId}).")
                    return
            
            print(f"Category with ID='{categoryId}' not found in topic (ID={topicId}).")
            return

    print(f"No topic found with ID='{topicId}'.")
    
    
    
def save_topics(filename):
    data = []
    for topic_info in topics:
        topic_data = {
            'id': topic_info.get('id', ''),
            'topic_input': topic_info['topic_input'].value if 'topic_input' in topic_info else '',
            'condition': topic_info['condition'].value if 'condition' in topic_info else '',
            'prompt': topic_info['prompt'].value if 'prompt' in topic_info else '',
            'categories': []
        }

        for (cat_input, _, cat_id) in topic_info.get('categories', []):
            cat_name = cat_input.value
            topic_data['categories'].append({
                'id': cat_id,
                'value': cat_name
            })

        data.append(topic_data)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Topics saved to {filename}")
    
def load_topics(filename):
    global topics
    topics.clear()  

    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return

    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for topic_data in data:
        new_topic = {
            'id': topic_data.get('id', ''),
            'topic_input': MockText(topic_data.get('topic_input', '')),
            'condition': MockText(topic_data.get('condition', '')),
            'prompt': MockText(topic_data.get('prompt', '')),
            'categories': [],
            'category_counter': 0
        }

        for cat_dict in topic_data.get('categories', []):
            cat_id = cat_dict.get('id', '')
            cat_value = cat_dict.get('value', '')
            new_topic['category_counter'] += 1
            new_topic['categories'].append(
                (MockText(cat_value), None, cat_id)
            )

        topics.append(new_topic)

    print(f"Loaded {len(topics)} topic(s) from {filename}")
    
    
def add_condition(topicId, categoryId, conditionStr):
    found_topic = None
    for topic in topics:
        if topic.get('id') == topicId:
            found_topic = topic
            break

    if found_topic is None:
        print(f"No topic found with ID={topicId}.")
        return

    categories = found_topic.get('categories', [])
    
    for i, cat_tuple in enumerate(categories):
        if len(cat_tuple) == 3:
            (cat_input, cat_box, cat_id) = cat_tuple
            cat_condition = ""  # no condition yet
        else:
            (cat_input, cat_box, cat_id, cat_condition) = cat_tuple

        if cat_id == categoryId:
            new_cat_tuple = (cat_input, cat_box, cat_id, conditionStr)
            categories[i] = new_cat_tuple
            print(f"Condition '{conditionStr}' added to category (ID={categoryId}) in topic (ID={topicId}).")
            return

    print(f"No category (ID={categoryId}) found in topic (ID={topicId}).")
    
    
def remove_condition(topicId, categoryId):
    found_topic = None
    for topic in topics:
        if topic.get('id') == topicId:
            found_topic = topic
            break

    if found_topic is None:
        print(f"No topic found with ID={topicId}.")
        return

    categories = found_topic.get('categories', [])

    for i, cat_tuple in enumerate(categories):
        if len(cat_tuple) == 3:
            (cat_input, cat_box, cat_id) = cat_tuple
            cat_condition = None  
        else:
            (cat_input, cat_box, cat_id, cat_condition) = cat_tuple

        if cat_id == categoryId:
            if len(cat_tuple) == 3:
                print(f"Category (ID={categoryId}) in topic (ID={topicId}) has no condition.")
                return
            else:
                new_cat_tuple = (cat_input, cat_box, cat_id, "")
                categories[i] = new_cat_tuple
                print(f"Condition removed from category (ID={categoryId}) in topic (ID={topicId}).")
                return

    print(f"No category (ID={categoryId}) found in topic (ID={topicId}).")

    
    
def classify_table(dataset, withEvaluation=False, constrainedOutput=True):
    csv_file = dataset + ".csv"
    if not os.path.exists(csv_file):
        print(f"No {csv_file} file found.")
        return

    categoryConfusions = []
    for i, topic_info in enumerate(topics):
        cat_map = {}
        for (cat_input, _, _cat_id) in topic_info['categories']:
            cat_name = cat_input.value
            cat_map[cat_name] = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}
        categoryConfusions.append(cat_map)

    numberOfCorrectResults = []
    numberOfRelevantAttempts = []

    resultRows = []

    startcount = 1
    endcount = -1
    saveName = dataset + "_(result)"

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        readerlist = list(reader)

        count = -1
        for row in readerlist:
            count += 1
            if endcount != -1 and count > endcount:
                break

            if count == 0:
                singleResult = [""]
                elementcounter = -1
                for element in row:
                    elementcounter += 1
                    if elementcounter == 0:
                        singleResult.append(element) 
                    else:
                        numberOfCorrectResults.append(0)
                        numberOfRelevantAttempts.append(0)
                        if withEvaluation:
                            singleResult.append(element + "(GroundTruth)")
                        singleResult.append(element)  
                with open(saveName + ".csv", 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
                    writer.writerow(singleResult)

            else:
                if count >= startcount:
                    if withEvaluation:
                        result = classify(
                            row[0],
                            isItASingleClassification=False,
                            constrainedOutput=constrainedOutput,
                            withEvaluation=True,
                            groundTruthRow=row
                        )
                    else:
                        result = classify(
                            row[0],
                            isItASingleClassification=False,
                            constrainedOutput=constrainedOutput
                        )
                    for tIndex, predCategory in enumerate(result):
                        groundTruth = ""
                        if withEvaluation and (tIndex + 1) < len(row):
                            groundTruth = row[tIndex + 1].strip()

                        if groundTruth:
                            for cat_name, conf_map in categoryConfusions[tIndex].items():
                                if cat_name == groundTruth and cat_name == predCategory:
                                    conf_map["TP"] += 1
                                elif cat_name != groundTruth and cat_name == predCategory:
                                    conf_map["FP"] += 1
                                elif cat_name == groundTruth and cat_name != predCategory:
                                    conf_map["FN"] += 1
                                else:
                                    conf_map["TN"] += 1

                    singleResult = [str(count), row[0]] 
                    tmpCount = 0
                    for ret in result:
                        tmpCount += 1
                        if withEvaluation and tmpCount < len(row):
                            ground_truth = row[tmpCount].strip()
                            if ground_truth:
                                numberOfRelevantAttempts[tmpCount - 1] += 1
                                singleResult.append(ground_truth) 
                                singleResult.append(ret)           

                                if ret == ground_truth:
                                    numberOfCorrectResults[tmpCount - 1] += 1
                            else:
                                singleResult.append("")
                                singleResult.append(ret)
                        else:
                            if not withEvaluation:
                                singleResult.append(ret)
                            else:
                                singleResult.append("UNDEFINED")
                                
                    with open(saveName + ".csv", 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
                        writer.writerow(singleResult)

                    resultRows.append(singleResult)

    if withEvaluation:
        with open(saveName + ".csv", 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)

            writer.writerow([
                "Topic", "Accuracy", "Correct Attempts", "Relevant Attempts",
                "Micro Acc", "Micro Prec", "Micro Recall", "Micro F1",
                "TP", "FP", "FN", "TN"
            ])

            for i, topic_info in enumerate(topics):
                sumTP = 0
                sumFP = 0
                sumFN = 0
                sumTN = 0

                cat_map = categoryConfusions[i]
                for cat_name, conf_map in cat_map.items():
                    sumTP += conf_map["TP"]
                    sumFP += conf_map["FP"]
                    sumFN += conf_map["FN"]
                    sumTN += conf_map["TN"]

                if numberOfRelevantAttempts[i] > 0:
                    accuracy = (numberOfCorrectResults[i] / numberOfRelevantAttempts[i]) * 100.0
                else:
                    accuracy = -1

                micro_accuracy = (sumTP / (sumTP + sumFN)) if (sumTP + sumFN) > 0 else 0.0
                micro_precision = (sumTP / (sumTP + sumFP)) if (sumTP + sumFP) > 0 else 0.0
                micro_recall = (sumTP / (sumTP + sumFN)) if (sumTP + sumFN) > 0 else 0.0
                micro_f1 = 0.0
                if micro_precision > 0 and micro_recall > 0:
                    micro_f1 = 2.0 * (micro_precision * micro_recall) / (micro_precision + micro_recall)

                topic_name = topic_info['topic_input'].value
                writer.writerow([
                    topic_name,
                    f"{accuracy:.2f}%",
                    numberOfCorrectResults[i],
                    numberOfRelevantAttempts[i],
                    f"{micro_accuracy*100:.2f}%",
                    f"{micro_precision*100:.2f}%",
                    f"{micro_recall*100:.2f}%",
                    f"{micro_f1*100:.2f}%",
                    sumTP,
                    sumFP,
                    sumFN,
                    sumTN
                ])

    print(f"Classification of '{dataset}.csv' complete. Output written to '{saveName}.csv'.")
    
    
def check_prompt_performance_for_topic(
    topicId,
    dataset,
    constrainedOutput=True,
    groundTruthCol=None
):
    csv_file = dataset + ".csv"
    if not os.path.exists(csv_file):
        print(f"No {csv_file} file found.")
        return

    found_topic = None
    topic_index = None
    for i, t in enumerate(topics):
        if t.get('id') == topicId:
            found_topic = t
            topic_index = i
            break

    if found_topic is None:
        print(f"No topic found with ID={topicId}.")
        return

    if groundTruthCol is None:
        groundTruthCol = (topic_index * 2) + 1

    local_categories = [
        cat_input.value
        for (cat_input, _, cat_id) in found_topic.get('categories', [])
    ]

    relevant_attempts = 0
    correct_predictions = 0

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        rows = list(reader)

    for rowIndex, row in enumerate(rows):
        if rowIndex == 0:
            continue

        if len(row) <= groundTruthCol:
            continue

        text_to_classify = row[0].strip()
        groundTruthCategoryName = row[groundTruthCol].strip()

        if not groundTruthCategoryName:
            continue

        prompt_template = found_topic['prompt'].value
        prompt_categories_str = "[" + ",".join(f"'{cat}'" for cat in local_categories) + "]"
        prompt = prompt_template.replace('[TOPIC]', found_topic['topic_input'].value)
        prompt = prompt.replace('[CATEGORIES]', prompt_categories_str)
        prompt = prompt.replace('[TEXT]', text_to_classify)

        answer = getAnswerSingleTopic(prompt, local_categories, constrainedOutput)

        relevant_attempts += 1
        if answer == groundTruthCategoryName:
            correct_predictions += 1

    if relevant_attempts > 0:
        accuracy = (correct_predictions / relevant_attempts) * 100.0
        print(f"Topic (ID={topicId}) => Accuracy: {accuracy:.2f}%  "
              f"({correct_predictions} / {relevant_attempts} attempts)")
    else:
        print(f"Topic (ID={topicId}): No relevant attempts (no rows with non-empty groundTruth).")
        

        
        
def getLLMImprovedPromptWithFeedback(old_prompt, old_accuracy, topic_info):
    topic_name = topic_info['topic_input'].value
    category_list = [cat_input.value for (cat_input, _, _cat_id) in topic_info['categories']]
    category_str = ", ".join(category_list) if category_list else "No categories defined"

    system_content = (
        f"You are an advanced prompt engineer.\n"
        f"The classification topic is '{topic_name}'.\n"
        f"The available categories for this topic are: {category_str}\n"
        "Rewrite the user's prompt to achieve higher accuracy on classification tasks.\n"
        "You MUST keep the placeholder [TEXT].\n"
        "IMPORTANT: Output ONLY the final prompt, wrapped in triple backticks.\n"
        "No commentary, bullet points, or explanations.\n"
        "The new prompt should be in English.\n"
    )

    user_content = (
        f"Previously, the prompt achieved an accuracy of {old_accuracy:.2f}%. \n"
        "Here is the old prompt:\n\n"
        f"{old_prompt}\n\n"
        "Please rewrite/improve this prompt. Keep [TEXT]. "
        "Wrap your entire revised prompt in triple backticks, with no extra lines."
    )

    if promptModelType in ("OpenAI", "DeepInfra"):
        try:
            completion = client.chat.completions.create(
                model=promptModel,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=250,
                temperature=0.7
            )
            improved_prompt = completion.choices[0].message.content.strip()

            match = re.search(r"```(.*?)```", improved_prompt, flags=re.DOTALL)
            if match:
                improved_prompt = match.group(1).strip()
            else:
                print("Warning: The LLM did not provide triple backticks. Using full text.")

            print("Improved Prompt:", improved_prompt)  # Debug

            if not improved_prompt or "[TEXT]" not in improved_prompt:
                print("Warning: The improved prompt is empty or lacks [TEXT]. Reverting to old prompt.")
                return old_prompt

            return improved_prompt

        except Exception as e:
            print(f"Error calling OpenAI/DeepInfra: {e}")
            return old_prompt

    else:
        try:
            base_instruction = system_content
            improvement_request = (
                f"{base_instruction}\n\n"
                f"Original prompt:\n{old_prompt}\n"
            )


            script = promptModelGuidance + f" {improvement_request}" + gen(max_tokens=250, name='improvedPrompt')
            new_prompt = script["improvedPrompt"]

            if not new_prompt or "[TEXT]" not in new_prompt:
                print("Warning: The improved prompt is empty or lacks [TEXT]. Reverting to old prompt.")
                return old_prompt

            return new_prompt

        except Exception as e:
            print(f"Error calling local approach: {e}")
            return old_prompt
        

        
        



        
def evaluate_prompt_accuracy(topic_info, prompt, dataset, constrainedOutput, groundTruthCol):
    csv_file = dataset + ".csv"
    if not os.path.exists(csv_file):
        print(f"No {csv_file} file found.")
        return 0.0

    local_categories = [cat_input.value for (cat_input, _, _) in topic_info.get('categories', [])]
    relevant_attempts = 0
    correct_predictions = 0

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        rows = list(reader)

    for i, row in enumerate(rows):
        if i == 0: 
            continue
        if len(row) <= groundTruthCol:
            continue

        text_to_classify = row[0].strip()
        groundTruthCategoryName = row[groundTruthCol].strip()
        if not groundTruthCategoryName:
            continue

        prompt_categories_str = "[" + ",".join(f"'{cat}'" for cat in local_categories) + "]"
        final_prompt = prompt.replace('[TOPIC]', topic_info['topic_input'].value)
        final_prompt = final_prompt.replace('[CATEGORIES]', prompt_categories_str)
        final_prompt = final_prompt.replace('[TEXT]', text_to_classify)

        answer = getAnswerSingleTopic(final_prompt, local_categories, constrainedOutput)
        relevant_attempts += 1
        if answer == groundTruthCategoryName:
            correct_predictions += 1

    if relevant_attempts > 0:
        return (correct_predictions / relevant_attempts) * 100.0
    return 0.0    

        
def improve_prompt(topicId, dataset, constrainedOutput=True, groundTruthCol=None, num_iterations=10):
    found_topic = next((t for t in topics if t.get('id') == topicId), None)
    if not found_topic:
        print(f"No topic found with ID {topicId}.")
        return
    
    topic_index = topics.index(found_topic)
    if groundTruthCol is None:
        groundTruthCol = (topic_index * 2) + 1

    old_prompt = found_topic['prompt'].value
    old_accuracy = evaluate_prompt_accuracy(found_topic, old_prompt, dataset, constrainedOutput, groundTruthCol)

    best_prompt = old_prompt
    best_accuracy = old_accuracy

    print("========================================")
    print(f"Starting iterative prompt improvement for topic '{found_topic['id']}'")
    print(f"Baseline accuracy: {best_accuracy:.2f}%")
    print("========================================")

    for iteration in range(1, num_iterations + 1):
        new_prompt = getLLMImprovedPromptWithFeedback(best_prompt, best_accuracy, found_topic)
        if "[TEXT]" not in new_prompt:
            print("Warning: The improved prompt lost [TEXT]. Skipping iteration.")
            continue

        new_accuracy = evaluate_prompt_accuracy(found_topic, new_prompt, dataset, constrainedOutput, groundTruthCol)
        diff = new_accuracy - best_accuracy

        print(f"Iteration {iteration}:")
        print(f"New prompt accuracy: {new_accuracy:.2f}% (was {best_accuracy:.2f}%)")

        if diff > 0.001:
            print(f"Improvement found (+{diff:.2f}%). Updating best prompt.")
            best_prompt = new_prompt
            best_accuracy = new_accuracy
        else:
            print("No improvement. Keeping current best prompt.")
        print("----------------------------------------")

    print("========================================")
    print(f"Final best accuracy: {best_accuracy:.2f}%")
    print("Best prompt:\n", best_prompt)
    print("========================================\n")

    if best_accuracy > old_accuracy:
        found_topic['best_prompt_found'] = best_prompt
        found_topic['best_prompt_accuracy'] = best_accuracy
    else:
        found_topic['best_prompt_found'] = None
        found_topic['best_prompt_accuracy'] = None
        
        
def setPrompt(topicId, newPrompt):
    for topic in topics:
        if topic.get('id') == topicId:
            if 'prompt' in topic and hasattr(topic['prompt'], 'value'):
                topic['prompt'].value = newPrompt
            else:
                topic['prompt'] = MockText(newPrompt)
            print(f"Prompt for topic ID {topicId} updated.")
            return

    print(f"Topic with ID {topicId} not found.")

def removeAllTopics():
    global topics, topic_id_counter, previous_results, selectOptions
    
    topics.clear()            
    topic_id_counter = 0         
    previous_results.clear()    
    if 'selectOptions' in globals():
        selectOptions.clear()   
    
    print("All topics have been removed, counters reset, and related data cleared.")

                
        
class MockText:
    def __init__(self, value: str):
        self.value = value