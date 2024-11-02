import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Trainer, TrainingArguments
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', required=True)
    args = parser.parse_args()
    model_name = args.model_name        # Например, "Qwen/Qwen2.5-7B-Instruct"


    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name,
        load_in_4bit=True,
        device_map="auto"
    )

    lora_config = LoraConfig(
        r=16,                                 # Ранг LoRA
        lora_alpha=32,                        # Коэффициент масштабирования
        target_modules=["q_proj", "v_proj"],  # На какие модули влияет LoRA
        lora_dropout=0.05,                    # Dropout для регуляризации
        bias="none"                           # Отключаем смещения
    )


    model = get_peft_model(model, lora_config)
    dataset = load_dataset("..")


    def preprocess_data(batch):
        inputs = [doc for doc in batch['article']]
        model_inputs = tokenizer(inputs, max_length=512, truncation=True, padding="max_length")

        labels = tokenizer(batch['highlights'], max_length=150, truncation=True, padding="max_length")
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs


    tokenized_dataset = dataset.map(preprocess_data, batched=True)
    training_args = TrainingArguments(
        output_dir=f"./results_{model_name}",
        evaluation_strategy="epoch",
        learning_rate=2e-4,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        num_train_epochs=3,
        weight_decay=0.01,
        fp16=True,
        logging_dir='./logs',
        save_total_limit=2,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )
    trainer.train()
