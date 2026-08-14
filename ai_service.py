from transformers import AutoTokenizer, AutoModelForCausalLM
import json
import datetime

MODEL_NAME = "Qwen/Qwen3-4B"

def load_ai_model():

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

    return tokenizer, model

def build_task_context(tasks):

    lines = []

    for task in tasks:
        lines.append(
            f"Task ID: {task.get('id', 'N/A')} | "
            f"Name: {task['name']} | "
            f"Priority: {task['priority']} | "
            f"Status: {task['status']} | "
            f"Deadline: {task['deadline']}"
        )

    return "\n".join(lines)

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

#     facts.append(f"Pending tasks= {len(pending_tasks)}")
#     facts.append(f"Completed tasks= {len(completed_tasks)}")

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

#     else:
#         facts.append("")
#         facts.append("No pending tasks remain.")
#         facts.append("There is no most urgent pending task.")
#         facts.append("There is no recommended pending-task order.")

#     if completed_tasks:
#         facts.append("")
#         facts.append("Completed tasks:")

#         for task in completed_tasks:
#             facts.append(f"- {task['name']}")

#     return "\n".join(facts)

def analyze_tasks_with_ai(task_context, tokenizer, model):

    messages = [
        {
            "role": "system",
            "content": (
                "You are an intelligent task-management assistant. "
                "Analyze only the task records provided by the application. "
                "Do not invent, change, or omit task names, statuses, priorities, or deadlines."
            )
        },
        {
            "role": "user",
            "content": f"""
TASK RECORDS:

{task_context}

Analyze these tasks and write a concise task-management summary.

Rules:
- Determine which tasks are Pending and which are Completed.
- Completed tasks must not be included in the pending-task recommendation.
- Rank pending tasks primarily by priority: High first, then Medium, then Low.
- If two pending tasks have the same priority, the earlier deadline comes first.
- Identify the most urgent pending task.
- Give the recommended order for all pending tasks.
- Briefly mention completed tasks.
- If no pending tasks exist, clearly state that all tasks are completed and do not provide an urgent task or recommended order.
- Use only the supplied task records.
"""
        }
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        enable_thinking=False
    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        do_sample=False
    )

    new_tokens = outputs[0][inputs["input_ids"].shape[-1]:]

    result = tokenizer.decode(
        new_tokens,
        skip_special_tokens=True
    )

    return result

# def generate_ai_summary(verified_facts, tokenizer, model):

#     messages = [
#         {
#         "role": "system",
#         "content": (
#             "You are a task-management summariser. "
#             "The task facts provided to you have already been verified by the application. "
#             "Do not change, contradict, or invent task names, statuses, priorities, or deadlines."
#         )
#     },
#     {
#         "role": "user",
#         "content": f"""
# VERIFIED TASK FACTS:

# {verified_facts}

# Using only these facts, write a concise task-management summary.

# If the facts show one or more pending tasks:
# - Mention the most urgent pending task.
# - Mention the recommended pending-task order.
# - Briefly mention completed tasks if any exist.

# If the facts contain "No pending tasks remain":
# - State that all tasks are completed.
# - Do not provide a most urgent task.
# - Do not provide a recommended task order.

# Do not invent any additional tasks, statuses, priorities, or deadlines.
# """

#     }
#     ]

#     inputs = tokenizer.apply_chat_template(
#     messages,
#     add_generation_prompt=True,
#     tokenize=True,
#     return_dict=True,
#     return_tensors="pt",
#     enable_thinking=False
#     )

#     outputs = model.generate(
#         **inputs,
#         max_new_tokens=250,
#         do_sample=False,
#         repetition_penalty=1.1
#     )

#     new_tokens = outputs[0][inputs["input_ids"].shape[-1]:]

#     result = tokenizer.decode(
#         new_tokens,
#         skip_special_tokens=True
#     )

#     return result


def parse_task_with_ai(task_text, current_datetime, tokenizer, model):

    calendar_lines = []

    for i in range(7):
        day = current_datetime + datetime.timedelta(days=i)

        calendar_lines.append(
            day.strftime("%A = %Y-%m-%d")
    )

    calendar_context = "\n".join(calendar_lines)
    messages = [
        {
            "role": "system",
            "content": (
                "You are an intelligent task extraction assistant. "
                "Convert natural-language task descriptions into structured data. "
                "Return only the requested task information and do not invent details."
            )
        },
        {
            "role": "user",
            "content": f"""
Current date and time:
{current_datetime.strftime("%A, %Y-%m-%d %H:%M")}

Upcoming calendar:
{calendar_context}

Task description:
{task_text}

Convert the task description into JSON.

Rules:
- name: contain only the actual task/action.
- Remove deadline wording from the task name.
- Remove priority wording from the task name.
- deadline: use YYYY-MM-DD HH:MM format.
- Correctly resolve relative expressions such as today, tomorrow, tonight, and next Monday using the current date and time above.
- If no deadline is given, deadline must be null.
- priority must be High, Medium, or Low.
- If priority is not specified, use Medium.
- status must be Pending unless the user explicitly says the task is already completed.
- Do not invent information.

Time interpretation rules:

- If the user gives a relative duration such as:
  "in 30 minutes",
  "in 2 hours",
  "in the next 1 hour",
  or "in 3 days":

    deadline_type = "duration"
    duration_value = the numeric amount
    duration_unit = "minutes", "hours", or "days"
    deadline = null

- If a duration-based deadline also contains an explicit clock time,
  such as "in 2 days at 10 AM":
    duration_time = that time in HH:MM format.

- If no explicit clock time accompanies the duration:
    duration_time = null.

- Do not calculate the final deadline for duration-based expressions.

- If the user gives a calendar-based deadline such as:
  "today at 5 PM",
  "tomorrow at 9 AM",
  "Friday at 7 PM",
  "next Monday at 10 AM",
  or an explicit date:

    deadline_type = "absolute"
    duration_value = null
    duration_unit = null
    deadline = the resolved date and time in YYYY-MM-DD HH:MM format
-Duration extraction rules:

  - For relative-duration expressions, copy the duration value and unit EXACTLY
    from the user's task description.
  
  - Do NOT convert, normalize, round, approximate, or simplify durations.
  
  Examples:
  "in 30 minutes"
  → duration_value = 30
  → duration_unit = "minutes"
  
  "in 1 hour"
  → duration_value = 1
  → duration_unit = "hour"
  
  "in the next 2 hours"
  → duration_value = 2
  → duration_unit = "hours"
  
  "in 3 days"
  → duration_value = 3
  → duration_unit = "days"
  
  - "30 minutes" must NEVER be converted to "1 hour".
  - "90 minutes" must remain 90 minutes and must NOT become 1.5 hours.
  - "24 hours" must remain 24 hours and must NOT become 1 day.
  
  - If the user gives an explicit clock time together with a duration,
    such as "in 2 days at 10 AM":
      duration_time = that clock time in HH:MM format.
  
  - Otherwise:
      duration_time = null.

- Do NOT calculate the final deadline for duration-based expressions.

- Use the supplied current date, current weekday, and upcoming calendar for calendar-based deadlines.

- If no deadline is provided:

    deadline_type = "none"
    duration_value = null
    duration_unit = null
    deadline = null

- Do not confuse minutes, hours, and days.

- Do not invent a date or time that the user did not specify.

Return exactly these fields:

{{
    "name": "task name",
    "deadline_type": "duration",
    "duration_value": 2,
    "duration_unit": "days",
    "duration_time": "10:00",
    "deadline": null,
    "priority": "Medium",
    "status": "Pending"
}}

Return JSON only.
"""
        }
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        enable_thinking=False
    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=150,
        do_sample=False
    )

    new_tokens = outputs[0][inputs["input_ids"].shape[-1]:]

    result = tokenizer.decode(
        new_tokens,
        skip_special_tokens=True
    )

    start = result.find("{")
    end = result.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("AI did not return a JSON object.")

    json_text = result[start:end + 1]

    parsed_task = json.loads(json_text)

    if parsed_task["deadline_type"] == "duration":
    
            value = parsed_task["duration_value"]
            unit = parsed_task["duration_unit"].lower()
    
            if unit in ["minute", "minutes"]:
                deadline = current_datetime + datetime.timedelta(minutes=value)
    
            elif unit in ["hour", "hours"]:
                deadline = current_datetime + datetime.timedelta(hours=value)
    
            elif unit in ["day", "days"]:
    
                target_date = (
                    current_datetime + datetime.timedelta(days=value)
                ).date()
    
                if parsed_task["duration_time"]:
                    target_time = datetime.datetime.strptime(
                        parsed_task["duration_time"],
                        "%H:%M"
                    ).time()
    
                    deadline = datetime.datetime.combine(
                        target_date,
                        target_time
                    )
    
                else:
                    deadline = current_datetime + datetime.timedelta(days=value)
    
            else:
                raise ValueError(
                    f"Unsupported duration unit: {unit}"
                )
    
            parsed_task["deadline"] = deadline.strftime("%Y-%m-%d %H:%M")

    if parsed_task["deadline"] is None:
        default_deadline = current_datetime + datetime.timedelta(hours=1)
        parsed_task["deadline"] = default_deadline.strftime("%Y-%m-%d %H:%M")

    return {
    "name": parsed_task["name"],
    "deadline": parsed_task["deadline"],
    "priority": parsed_task["priority"],
    "status": parsed_task["status"]
    } 
    