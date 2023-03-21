import json
import openai
from translator import LeTranslator
import time


def read_json_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

def split_reviews_by_rating_groups(data, groups): # [[5], [4, 3, 2, 1]]
    groups_result_dict = {x: [] for x in range(len(groups))}
    for entry in data:
        for i, group in enumerate(groups):
            if entry["rating"] in group:
                review = entry["content_no_tags"].strip()
                if review:
                    groups_result_dict[i].append(review)
                break    
    return groups_result_dict

def load_openai_api_key():
    with open("openai.sk", "r", encoding="utf-8") as file:
        return file.read().strip()
    
openai.api_key = load_openai_api_key()

def translate_all_reviews_into_english(translator, reviews):
    return [translator.translate_ro_en(review) for review in reviews]


def summarize_with_chatgpt_normal_reviews(reviews, tendancy): # tendancy = "positive" or "negative"
    prompt = f"""Below there is a list of reviews.
    Please, summarize them focusing on the {tendancy} aspects of the product:\n\n"""
    
    for i, review in enumerate(reviews):
        prompt += f"{i+1}. {review}\n\n"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "user", "content": prompt}
            ]
        )
    
    return response["choices"][0]["message"]["content"]
        

def summarize_with_chatgpt_summarized_reviews(reviews, tendancy): # tendancy = "positive" or "negative"
    prompt = f"""Below there is a list of summaries of multiple reviews.
    Please, summarize them together focusing on the {tendancy} aspects of the product:\n\n"""
    
    for i, review in enumerate(reviews):
        prompt += f"{i+1}. {review}\n\n"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "user", "content": prompt}
            ]
        )
    
    return response["choices"][0]["message"]["content"]

def recursive_summarize_chatgpt_summaries(reviews, tendancy):
    max_len_in_chars = 12000
    reviews_groups = []
    current_length = 0
    reviews_summaries = []
    for review in reviews:
        if not reviews_groups:
            reviews_groups.append(review)
            current_length += len(review)
            continue
        if current_length + len(review) > max_len_in_chars:
            reviews_summaries.append(summarize_with_chatgpt_summarized_reviews(reviews_groups, tendancy))
            reviews_groups = [review]
            current_length = 0
        else:
            reviews_groups.append(review)
            current_length += len(review)
    if reviews_groups:
        reviews_summaries.append(summarize_with_chatgpt_summarized_reviews(reviews_groups, tendancy))
    length_of_reviews_summaries = sum([len(x) for x in reviews_summaries])
    if length_of_reviews_summaries > max_len_in_chars:
        return recursive_summarize_chatgpt_summaries(reviews_summaries, tendancy)
    else:
        return reviews_summaries


def recursive_summarize_with_chatgpt(reviews, tendancy):
    max_len_in_chars = 12000
    reviews_groups = []
    current_length = 0
    reviews_summaries = []
    for review in reviews:
        if not reviews_groups:
            reviews_groups.append(review)
            current_length += len(review)
            continue
        if current_length + len(review) > max_len_in_chars:
            reviews_summaries.append(summarize_with_chatgpt_normal_reviews(reviews_groups, tendancy))
            reviews_groups = [review]
            current_length = 0
        else:
            reviews_groups.append(review)
            current_length += len(review)
    if reviews_groups:
        reviews_summaries.append(summarize_with_chatgpt_normal_reviews(reviews_groups, tendancy))
    length_of_reviews_summaries = sum([len(x) for x in reviews_summaries])
    if length_of_reviews_summaries > max_len_in_chars:
        return recursive_summarize_chatgpt_summaries(reviews_summaries, tendancy)
    else:
        return reviews_summaries
    

def recommend_product(product_1_positive_aspects, product_1_negative_aspects,
                        product_2_positive_aspects, product_2_negative_aspects, user_preferences):
    prompt_system = "You are a shopping assistant and you have to recommend the right product to a customer."
    prompt = f"""
    The customer is looking for a product that has the following aspects: {user_preferences}
    
    They have two options to choose from. 
    Here are the positive aspects of the first product:
    {product_1_positive_aspects}
    
    Here are the negative aspects of the first product:
    {product_1_negative_aspects}
    
    Here are the positive aspects of the second product:
    {product_2_positive_aspects}
    
    Here are the negative aspects of the second product:
    {product_2_negative_aspects}
    
    Recommend the right product to the customer.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt}
            ]
        )
    
    print(response["choices"][0]["message"]["content"])


def main(dataset_path):
    data = read_json_file(dataset_path)
    groups = [[5], [4, 3, 2, 1]]
    group_results = split_reviews_by_rating_groups(data, groups)
    translator = LeTranslator()
    start = time.time()
    for group in group_results:
        group_results[group] = translate_all_reviews_into_english(translator, group_results[group])
    print(f"Time to translate: {time.time() - start} seconds")
    list_of_summaries = recursive_summarize_with_chatgpt(group_results[0], "positive")
    final_positive_summary = summarize_with_chatgpt_summarized_reviews(list_of_summaries, "positive")
    print(f"Positive summary:\n\n {final_positive_summary}")
    print("\n\n")
    
    list_of_summaries = recursive_summarize_with_chatgpt(group_results[1], "negative")
    final_negative_summary = summarize_with_chatgpt_summarized_reviews(list_of_summaries, "negative")
    print(f"Negative summary:\n\n {final_negative_summary}")

if __name__ == "__main__":
    # main("lenovo_ideapad_3.json")
    # main("macbook_13_air_m1.json")
    lenova_positive = """
    The product has received multiple positive reviews highlighting its excellent gaming performance, good quality-price ratio, and the option to upgrade. It comes with a strong processor and video card, and adding extra RAM can enhance its performance. The battery life is decent and charges quickly. The laptop also features an illuminated keyboard, good volume, and Wi-Fi connectivity. It is compact and can handle all games perfectly. Although the plastic case is not of the best quality, it is still considered a great buy, especially at the Black Friday discount price.
    """

    lenovo_negative = """
    The product has several negative aspects according to reviews, such as a display that is not suitable for professional photo editing, inability to change aspect ratio and resolution in certain games, screen turning off when plugging in a USB cable, below-average battery life, display issues such as bleeding and needing calibration, mediocre plastic and keyboard quality, Wi-Fi connectivity problems for some users, cheapness in screen quality and assembly, and sound problems for some users as it comes without drivers.
    """

    macbook_positive = """
     In summary, the MacBook Air receives overwhelmingly positive reviews for its premium quality, efficient performance, long battery life, lightweight portability, excellent display, keyboard and trackpad, and seamless integration with other Apple devices. Its reliability, durability, and ease of use make it a great choice for everyday tasks, such as browsing the internet, working, and entertainment. The laptop is also well-regarded for its quiet operation and superb customer support. While the high price points for upgraded versions and limited USB ports are noted as drawbacks, users consider them minor compared to the overall benefits of the MacBook Air. In summary, the MacBook Air with M1 chip is a revolutionary product that offers exceptional performance and efficiency, making it an unbeatable value for its price.
    """
    
    macbook_negative = """
    The product has numerous negative aspects, including issues with the Caps Lock key, a small storage space, overheating during large transfers, connectivity problems with the internet connection, and a lack of ports. Additionally, the battery doesn't last as long as advertised, its health decreases quickly, and it requires adapters to connect external hardware. The product is not suitable for programmers, lacks ports, and is not suited for coding. Users also reported annoying automatic brightness adjustment and incorrect keyboard pictures on the computer. Furthermore, the product's heavy operating system and so-called cool apps do not live up to the marketing hype. Despite being overpraised, it remains to be seen how well it performs, and it is unable to handle tasks as a mobile workstation. Finally, users experienced Bluetooth problems and unstable keyboard keys while using it, while it also has weak support for IOS applications.
    """
    
    user_preferences = "I want a laptop with the best value for money. Note that I am a businessman and I need a laptop that is suitable for my work. I travel a lot and the batery life is very important to me. I also want a laptop that is easy to carry around."
    
    recommend_product(lenova_positive, lenovo_negative, macbook_positive, macbook_negative, user_preferences)
    