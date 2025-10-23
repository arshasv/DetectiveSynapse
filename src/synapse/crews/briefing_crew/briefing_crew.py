from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from synapse.utils.llm import llm
from pydantic import BaseModel
from synapse.utils.llm import gemini_creative

class Briefing(BaseModel):
    CrimeSceneInvestigator : str

@CrewBase
class BriefingCrew():
    """BriefingCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'


    @agent
    def Case_briefing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['Case_briefing_agent'],
            llm=gemini_creative()
        )

    @task
    def Case_briefing(self) -> Task:
        return Task(
            config=self.tasks_config['Case_briefing_task'],
            output_json=Briefing
        )

    @crew
    def crew(self) -> Crew:
        """Creates the BriefingCrew crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
