JSON_SYSTEM_PROMPT = """

You must respond with ONLY a JSON object containing the solution steps and final answer.

The response must match this schema structure, but DO NOT include the schema definition in your response:
{schema}

Rules:
1. Your response must contain ONLY the solution JSON object with steps and final_answer
2. DO NOT include the schema definition in your response
3. Each step should have an explanation and the mathematical output
4. The JSON must be valid and include all required fields
5. Do not include any text or explanations outside the JSON object"""