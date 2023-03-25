from transformers import AutoTokenizer, AutoModelWithLMHead

tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-emotion")

model = AutoModelWithLMHead.from_pretrained("mrm8488/t5-base-finetuned-emotion")


def get_emotion(text):
    input_ids = tokenizer.encode(text + '</s>', return_tensors='pt')

    output = model.generate(input_ids=input_ids,
                            max_length=2)

    dec = [tokenizer.decode(ids) for ids in output]
    print(dec)
    label = dec[0]
    print(label)
    return label


get_emotion("i feel as if i havent blogged in ages are at least truly blogged i am doing an update cute")

get_emotion("i have a feeling i kinda lost my best friend")