from ai_service import load_ai_model, build_task_context, analyze_tasks_with_ai, parse_task_with_ai
import datetime
tasks = [
    {
        "name": "Submit project assessment",
        "deadline": "2026-08-11 18:00",
        "priority": "High",
        "status": "Completed"
    },
    {
        "name": "Prepare presentation",
        "deadline": "2026-08-12 10:00",
        "priority": "High",
        "status": "Completed"
    },
    {
        "name": "Buy groceries",
        "deadline": "2026-08-13 19:00",
        "priority": "Low",
        "status": "Completed"
    },
    {
        "name": "Complete SQL practice",
        "deadline": "2026-08-14 20:00",
        "priority": "High",
        "status": "Completed"
    }
]

# def build_verified_facts(tasks):

#     pending_tasks = []
#     completed_tasks = []

#     priority_rank = {
#         "High": 1,
#         "Medium": 2,
#         "Low": 3
#     }

#     for task in tasks:

#         if task["status"] == "Pending":
#             pending_tasks.append(task)

#         elif task["status"] == "Completed":
#             completed_tasks.append(task)

#     ordered_pending_tasks = sorted(
#         pending_tasks,
#         key=lambda task: (
#             priority_rank[task["priority"]],
#             task["deadline"]
#         )
#     )

#     facts = []

#     facts.append(f"Pending tasks: {len(pending_tasks)}")
#     facts.append(f"Completed tasks: {len(completed_tasks)}")

#     if ordered_pending_tasks:

#         most_urgent = ordered_pending_tasks[0]

#         facts.append("")
#         facts.append("Most urgent pending task:")
#         facts.append(f"Name: {most_urgent['name']}")
#         facts.append(f"Priority: {most_urgent['priority']}")
#         facts.append(f"Deadline: {most_urgent['deadline']}")

#         facts.append("")
#         facts.append("Recommended pending-task order:")

#         for i, task in enumerate(ordered_pending_tasks, start=1):
#             facts.append(
#                 f"{i}. {task['name']} | "
#                 f"{task['priority']} | "
#                 f"{task['deadline']}"
#             )

#     if completed_tasks:

#         facts.append("")
#         facts.append("Completed tasks:")

#         for task in completed_tasks:
#             facts.append(f"- {task['name']}")

#     return "\n".join(facts)

# def generate_ai_summary(verified_facts, tokenizer, model):

#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "You are a smart task management assistant. "
#                 "The task facts provided to you have already been verified "
#                 "by the application. "
#                 "Do not change, contradict, or invent task names, statuses, "
#                 "priorities, or deadlines."
#             )
#         },
#         {
#             "role": "user",
#             "content": f"""
# VERIFIED TASK FACTS:

# {verified_facts}

# Using only these facts, write a concise task-management summary.
# Mention the most urgent task and the recommended order.
# Do not invent any additional tasks or information.
# """
#         }
#     ]

#     inputs = tokenizer.apply_chat_template(
#         messages,
#         add_generation_prompt=True,
#         tokenize=True,
#         return_dict=True,
#         return_tensors="pt"
#     )

#     outputs = model.generate(
#         **inputs,
#         max_new_tokens=170,
#         do_sample=False,
#         repetition_penalty=1.1
#     )

#     new_tokens = outputs[0][inputs["input_ids"].shape[-1]:]

#     result = tokenizer.decode(
#         new_tokens,
#         skip_special_tokens=True
#     )

#     return result

# model_name = "Qwen/Qwen2.5-0.5B-Instruct"

# print("Loading tokenizer...")
# tokenizer = AutoTokenizer.from_pretrained(model_name)

# print("Loading model...")
# model = AutoModelForCausalLM.from_pretrained(model_name)

print("Loading AI model...")
tokenizer, model = load_ai_model()

# test_text = "Finish SQL assignment tomorrow at 6 PM high priority"

# parsed_task = parse_natural_language_task(
#     test_text,
#     datetime.datetime(2026, 8, 12, 10, 31),
#     tokenizer,
#     model
# )

# print("\nPARSED TASK:")
# print(parsed_task)

# verified_facts = build_verified_facts(tasks)

# print("\nVERIFIED FACTS:")
# print(verified_facts)

# summary = generate_ai_summary(
#     verified_facts,
#     tokenizer,
#     model
# )

# print("\nAI OUTPUT:")
# print(summary)

# task_context = build_task_context(tasks)

# print("\nTASK CONTEXT:")
# print(task_context)

# summary = analyze_tasks_with_ai(
#     task_context,
#     tokenizer,
#     model
# )

# print("\nAI OUTPUT:")
# print(summary)

test_text = [
    "Finish the report in the next 1 hour high priority",
    "Call the client in 45 minutes",
    "Take a break in 2 hours low priority",
    "Submit the document in 2 days at 10 AM",
    "Send the email tomorrow at 9 AM",
    "Buy groceries Friday at 7 PM",
    "Attend the meeting next Monday at 10 AM"

]

current_datetime = datetime.datetime(2026, 8, 12, 15, 4)

print(current_datetime)

for test in test_text:
    parsed_task = parse_task_with_ai(
        test,
        current_datetime,
        tokenizer,
        model
    )
        
    print("\nNATURAL LANGUAGE INPUT:")
    print(test)

    print("\nPARSED TASK:")
    print(parsed_task)