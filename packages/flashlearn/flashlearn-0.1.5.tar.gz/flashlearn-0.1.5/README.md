# FlashLearn  
**Never train another ML model again.**  

---

## 1. Introduction

FlashLearn is a Python library designed to ensure that every Large Language Model (LLM) response is always valid JSON. Whether you are classifying, summarizing, rewriting, or even performing multi-step data transformations, FlashLearn provides a stable, predictable output format so you can store and chain your results without worrying about malformed text or inconsistent formats.

- Zero custom training—use your existing LLM.  
- Compatible with open-source (e.g., DeepSeek) or commercial (e.g., OpenAI) offerings.  
- Scalable concurrency to handle from tens to millions of tasks.  
- A rich library of pre-built skills (classification, rewriting, summarization, etc.).  

---

## 2. Key Features (Simplified)

- **100% JSON Workflows**: Every response is valid JSON—machine-friendly from the start.  
- **Scales Easily**: Concurrency and rate limiting for large-scale projects.  
- **Zero Model Training**: Leverage your LLM directly; define or reuse “skills.”  
- **LearnSkill**: Instant creation of classification/rewriting “skills” from sample data.  
- **Batch or Real-Time**: Process live data, or batch thousands of tasks.  
- **Cost Estimation**: Predict token expenditures before running large jobs.  
- **Skill Library**: 200+ built-in skill definitions ([flashlearn/skills/toolkit](flashlearn/skills/toolkit)).  
- **Multi-Modal**: Handle text, images, and more in consistent JSON pipelines.

---

## 3. High-Level Concept Flow

1. Convert data rows into JSON tasks.  
2. Apply a Skill (classification, rewriting, etc.).  
3. LLM outputs guaranteed JSON.  
4. (Optional) Store or chain the JSON results into your next step.

```
Dataset Rows → JSON Tasks → FlashLearn Skills + LLM → Guaranteed JSON → DB/Next Steps
```

With guaranteed JSON, there’s no need to parse unstructured text. You can immediately save each result to your database or pass it to another pipeline stage.

---

## 4. Installation

1. Install via PyPI:  
   ```bash
   pip install flashlearn
   ```

2. Set up your LLM provider (OpenAI, DeepSeek, etc.):  
   ```bash
   export OPENAI_API_KEY="YOUR_API_KEY"
   ```
   Or define a `base_url` for an open-source endpoint.

---

## 5. “All JSON, All the Time”: Example Classification Workflow

The following example classifies IMDB movie reviews into “positive” or “negative” sentiment. Notice how at each step you can view, store, or chain the partial results—always in JSON format.

```python
from flashlearn.utils import imdb_reviews_50k
from flashlearn.skills import GeneralSkill
from flashlearn.skills.toolkit import ClassifyReviewSentiment
import json
import os

def main():
    os.environ["OPENAI_API_KEY"] = "API-KEY"

    # Step 1: Load or generate your data
    data = imdb_reviews_50k(sample=100)  # 100 sample reviews

    # Step 2: Load JSON definition of skill in dict format
    skill = GeneralSkill.load_skill(ClassifyReviewSentiment)
        
    # Step 3: Save skill definition in JSON for later loading
    #skill.save("BinaryClassificationSkill.json")
    
    # Step 5: Convert data rows into JSON tasks
    tasks = skill.create_tasks(data)
    
    # Step 6: Save results to a JSONL file and run now or later
    with open('tasks.jsonl', 'w') as jsonl_file:
        for entry in tasks:
            jsonl_file.write(json.dumps(entry) + '\n')
            
    # Step 7: Run tasks (in parallel by default)
    results = skill.run_tasks_in_parallel(tasks)

    # Step 8: Every output is strict JSON
    # You can easily map results back to inputs
    # e.g., store results as JSON Lines
    with open('sentiment_results.jsonl', 'w') as f:
        for task_id, output in results.items():
            input_json = data[int(task_id)]
            input_json['result'] = output
            f.write(json.dumps(input_json) + '\n')

    # Step 9: Inspect or chain the JSON results
    print("Sample result:", results.get("0"))

if __name__ == "__main__":
    main()
```

The output is consistently keyed by task ID (`"0"`, `"1"`, etc.), with the JSON content that your pipeline can parse or store with no guesswork.

---

## 6. Use Cases & Real Examples

### 6.1 Discover & Classify Clusters
1. **DiscoverLabelsSkill** automatically identifies emerging labels in text.  
2. Feed the discovered labels into a standard classification skill.  
3. Scale your labeling process quickly, with minimal human effort.

### 6.2 JSON Function Calls (GeneralSkill)
Skills define JSON schemas so the LLM must respond in valid JSON. Examples include rewriting text in comedic form, extracting docstrings, or providing bullet-point lists.

```python
import json
from flashlearn.skills import GeneralSkill
from flashlearn.skills.toolkit import ClassifyDifficultyOfQuestion

def main():
    # Load a pre-defined skill from the toolkit
    skill = GeneralSkill.load_skill(ClassifyDifficultyOfQuestion)
    tasks = skill.create_tasks([{"text": "What is 12 squared?"}])
    results = skill.run_tasks_in_parallel(tasks)
    print(results)
```

Result is valid JSON like:
```json
{"difficulty": "easy"}
```
No disclaimers or random text—just structured data.

### 6.3 Learning a New Skill from Sample Data
If existing categories or rewrites don’t match your needs, create a new classification skill from examples—no model finetuning required.

```python
from flashlearn.skills.learn_skill import LearnSkill
from flashlearn.utils import imdb_reviews_50k

def main():
    learner = LearnSkill(model_name="gpt-4o-mini")
    data = imdb_reviews_50k(sample=100)

    # Provide instructions and sample data for the new skill
    skill = learner.learn_skill(
        data,
        task=(
            'Based on data sample define 3 categories: satirical, quirky, absurd. '
            'Return the category in the key "category".'
        ),
    )

    tasks = skill.create_tasks(data)
    results = skill.run_tasks_in_parallel(tasks)
    print(results)
```

---

## 7. Image Classification Example

```python
from flashlearn.skills.classification import ClassificationSkill

def main():
    images = [...]  # base64-encoded images
    skill = ClassificationSkill(
        model_name="gpt-4o-mini",
        categories=["cat", "dog"],
        system_prompt="Classify images as 'cat' or 'dog'."
    )
    column_modalities = {"image_base64": "image_base64"}
    tasks = skill.create_tasks(images, column_modalities=column_modalities)
    results = skill.run_tasks_in_parallel(tasks)
    print(results)
```

You’ll have JSON results, e.g. `{"category": "cat"}` for each image, which you can export as `.jsonl` or pass to another system.

---

## 8. How It Works

### 8.1 Skills
A “Skill” encapsulates:  
- Which LLM to call (OpenAI, local, or custom).  
- System prompt or instructions.  
- JSON schema or format constraints.  
- Methods to parse the LLM response safely into JSON.

### 8.2 Tasks
Each piece of data is a “Task,” which is turned into a JSON prompt for the LLM. When run in parallel, tasks are grouped into requests respecting concurrency limits.

### 8.3 All JSON, All the Time
With FlashLearn, the LLM must output JSON. You’re never stuck parsing disclaimers, messy text, or swirling disclaimers. You can intercept and store partial or final results in JSON. This is critical for robust pipelines, especially when chaining multiple steps.

### 8.4 Parallel Execution & Cost Estimation
- **Parallel Execution**: `run_tasks_in_parallel` organizes concurrent requests to the LLM.  
- **Cost Estimation**: Quickly preview your token usage:
  ```python
  cost_estimate = skill.estimate_tasks_cost(tasks)
  print("Estimated cost:", cost_estimate)
  ```

---

## 9. Loading & Customizing a Skill

Here’s how the library handles comedic rewrites:

```python
from flashlearn.skills import GeneralSkill
from flashlearn.skills.toolkit import HumorizeText

def main():
    data = [{"original_text": "We are behind schedule."}]
    skill = GeneralSkill.load_skill(HumorizeText)
    tasks = skill.create_tasks(data)
    results = skill.run_tasks_in_parallel(tasks)
    print(results)
```

You’ll see output like:
```json
{
  "0": {
    "comedic_version": "Hilarious take on your sentence..."
  }
}
```
Everything is well-structured JSON, suitable for further analysis.

---

## 10. Contributing & Community

- Licensed under MIT.  
- [Fork us](flashlearn/) to add new skills, fix bugs, or create new examples.  
- We aim to make robust LLM workflows accessible to all startups.  
- Explore the [examples folder](examples/) for more advanced usage patterns.

---

## 11. License

**MIT License**.  
Use it in commercial products, personal projects, or your next YC pitch. Our vision is “unstoppable JSON” for every LLM workflow.

---

## 12. “Hello World” Demos

### 12.1 Image Classification

```python
import os
from openai import OpenAI
from flashlearn.skills.classification import ClassificationSkill
from flashlearn.utils import cats_and_dogs

def main():
    # os.environ["OPENAI_API_KEY"] = 'YOUR API KEY'
    data = cats_and_dogs(sample=6)

    skill = ClassificationSkill(
        model_name="gpt-4o-mini",
        client=OpenAI(),
        categories=["cat", "dog"],
        max_categories=1,
        system_prompt="Classify what's in the picture."
    )

    column_modalities = {"image_base64": "image_base64"}
    tasks = skill.create_tasks(data, column_modalities=column_modalities)
    results = skill.run_tasks_in_parallel(tasks)
    print(results)

    # Save skill definition for reuse
    skill.save("MyCustomSkillIMG.json")

if __name__ == "__main__":
    main()
```

### 12.2 Text Classification

```python
import json
import os
from openai import OpenAI
from flashlearn.skills.classification import ClassificationSkill
from flashlearn.utils import imdb_reviews_50k

def main():
    # os.environ["OPENAI_API_KEY"] = 'YOUR API KEY'
    reviews = imdb_reviews_50k(sample=100)

    skill = ClassificationSkill(
        model_name="gpt-4o-mini",
        client=OpenAI(),
        categories=["positive", "negative"],
        max_categories=1,
        system_prompt="Classify short movie reviews by sentiment."
    )

    # Convert each row into a JSON-based task
    tasks = skill.create_tasks([{'review': x['review']} for x in reviews])
    results = skill.run_tasks_in_parallel(tasks)

    # Compare predicted sentiment with ground truth for accuracy
    correct = 0
    for i, review in enumerate(reviews):
        predicted = results[str(i)]['categories']
        reviews[i]['predicted_sentiment'] = predicted
        if review['sentiment'] == predicted:
            correct += 1

    print(f'Accuracy: {round(correct / len(reviews), 2)}')

    # Store final results as JSON Lines
    with open('results.jsonl', 'w') as jsonl_file:
        for entry in reviews:
            jsonl_file.write(json.dumps(entry) + '\n')

    # Save the skill definition
    skill.save("BinaryClassificationSkill.json")

if __name__ == "__main__":
    main()
```

---

## Final Words

FlashLearn brings clarity to LLM workflows by enforcing consistent JSON output at every step. Whether you run a single classification or a multi-step pipeline, you can store partial results, debug easily, and maintain confidence in your data.  

**Ship faster and smarter with unstoppable JSON clarity.**