from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from synapse.utils.llm import llm

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
            llm=llm
        )

    @task
    def Case_briefing(self) -> Task:
        return Task(
            config=self.tasks_config['Case_briefing_task'],
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
