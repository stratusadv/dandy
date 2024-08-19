from dandy.llm.prompt import Prompt


def agent_process_job_prompt(role_prompt: Prompt, job_prompt: Prompt) -> Prompt:
    return (
        Prompt()
        .prompt(role_prompt)
        .prompt(job_prompt)
    )
