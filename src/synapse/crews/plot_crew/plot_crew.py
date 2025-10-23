from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from synapse.utils.llm import gemini_creative


@CrewBase
class PlotCrew:
    """Plot Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def Concept_architect_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["Concept_architect_agent"],
            llm=gemini_creative()
        )

    @task
    def Generate_bullseye(self) -> Task:
        return Task(
            config=self.tasks_config["Generate_bullseye_task"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Plot Crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
